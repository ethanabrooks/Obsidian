# Integrating Agentless-Style Frameworks into Olympus

This document outlines a proposed redesign of our AI issue resolution system to support flexible experimentation and modular components. The goal is to create clear interfaces between components while maintaining compatibility with our online RL infrastructure.

# Review of Incoming Frameworks

We have implemented both Agentless and Codemonkeys frameworks by forking their codebases with minimal modifications. Ultimately we want to rewrite both, with priority on Codemonkeys.

### [Agentless](https://github.com/OpenAutoCoder/Agentless)

The original framework for automated code repair, introducing the key stages that Codemonkeys later refined. While it underperforms Codemonkeys, we may want to borrow from it in some of our experiments.

1. **Localization**:

- Uses embeddings to select relevant files (more efficient than LLM evaluation)
- Identifies specific AST nodes rather than entire files
- Better handling of large files with targeted selection

2. **Repair**: Generates fix patches independently

3. **Testing**:

- Separate stage for test generation
- Tests are "blind" to the patch

4. **Selection**: Uses majority voting among candidates

### [Codemonkeys](https://scalingintelligence.stanford.edu/pubs/codemonkeys/)

1. **Context Stage**:

- Passes each repo file through an LLM to determine relevance
- Uses majority voting to prioritize files
- Concatenates files until context limit is reached
- Challenge: Includes entire files, often exceeding context limits

2. **Generation Stage**:

- Iteratively generates both fix and test patches
- Allows revision of previous attempts
- Combines Agentless' repair and testing into single stage

3. **Selection Stage**: Uses multiple heuristics including:

- Majority voting based on test pass rates
- LLM evaluation of proposed patches

### Relationship Between Systems

The stages roughly align:

- Codemonkeys "Context" ≈ Agentless "Localization"
- Codemonkeys "Generation" combines Agentless "Repair" and "Testing"
- Both have similar "Selection" stages

Key differences:

- Granularity of file selection
- Separation of fix and test generation
- Codemonkeys patch generation is iterative, while Agentless generates each patch IID.

Having reviewed both frameworks, we now turn to the kinds of experiments we want to enable with our new design. These experiments will help us understand which aspects of each framework are most effective and how they might be combined.

# Anticipated Experiments

The following experiments represent possible research directions our design should support. While neither exhaustive nor prioritized, these examples illustrate the kinds of flexibility and modularity our system needs to enable.

**Validate Online RL**:

- [ ] Use gold patch context as temporary workaround for cache population (see [Caching Strategy section](#caching-strategy))
- [ ] Focus on training Patch Generation components first

**Component Optimization**:

- [ ] Train each component independently using pseudo-rewards (described in [Pseudo-Rewards section](#pseudo-rewards) below)
- [ ] Compare performance of mixed configurations
- [ ] Better behavior cloning (or SFT) data for the golden model to make sure the base model is strong in its reasoning capabilities for that stage

**Use Agentless Localization**:

- [ ] Agentless localization context is much smaller because it doesn't pass entire files
- [ ] It's also much cheaper because it full files are only passed through the embedding API instead of using LLM calls

**Ablating different stages of Agentless Localization**:

Ablatable components include:

- Relevance scoring
- Irrelevance scoring
- Embedding scoring

**Alternative Architectures**:

- [ ] Test different stage orderings (e.g., multiple localization-generation cycles)
- [ ] Evaluate separate vs. combined fix/test generation

# Pseudo-Rewards {#pseudo-rewards}

To enable independent optimization of components, we propose "pseudo-rewards" \- approximate metrics for the success of each stage:

**Localization**: Percent of lines in gold patch included in output ("recall" in the Codemonkeys paper)

**Patch Generation**

- The proportion of tasks where at least one generated edit (out of N sampled) passes the gold test (the "ground-truth" test used to evaluate submissions for the benchmark). This measure is called "coverage" in the CodeMonkeys paper.
- More approximate metrics that bypass test execution (for speed):
  - Textual similarity to gold patch (as measured by Levenshtein distance or LLM)
  - Test coverage of proposed fixes

**Selection**

- Directly running the gold test on the selected patch (ground-truth reward)
- Include gold patch among proposed patches and test ability of selection to identify it

# Proposed Trace Generation Design

Having laid out our experimental goals and the metrics we'll need to achieve them, we now turn to designing a system that can support this kind of flexible experimentation. Our goal is to create a modular system that allows researchers to mix and match components from both frameworks or new ones that emerge, while maintaining compatibility with our online RL infrastructure.

**Key Challenges for Existing Implementation:**

- Components are tightly coupled, making experimentation difficult
- Expensive localization stage causes rate-limiting bottlenecks
- Long contexts from the Codemonkeys "Context" stage will exceed the limits of our in-house model
- File-based data passing between stages adds unnecessary complexity
- Need to support pseudo-rewards in order to debug credit assignment

## Component Design

To address these challenges, we propose standardizing how components communicate while maintaining flexibility in their implementation. Each component should return both its primary output (e.g., str for Localization) and the sequence of LLM interactions that produced that output:

```py
class Sequence(pydantic.BaseModel):
    messages: list[Message]
    metadata: dict[str, Any]

def locate(
    instance_id: str,
    model_name: str,
) -> tuple[str, Sequence]:
    ...

def generate(
    localization_context: str,
    instance_id: str,
    model_name: str
) -> tuple[list[Patch], Sequence]:
    ...

def select(
    patches: list[Patch],
    instance_id: str,
    model_name: str
) -> tuple[Patch, Sequence]:
    ...
```

## Trace Generation Framework

Now we describe how these components might be integrated into a trace-generation script in order to implement experiments. There are several key existing requirements for a trace generation script. It must:

1. integrate with `Machina` for model inference
2. log to `sequence_storage` for training
3. implement standard protocols for hyper-parameters

Example implementation:

```py
from agentless import locate
from codemonkeys import generate, select

class TraceData(pydantic.BaseModel):
    sequences: list[Sequence]  # The LLM interactions that produced the trace
    score: float              # The evaluation score for the trace
    metadata: dict           # Additional trace-specific data

async def generate_trace(
    instance_id: str,
    model_name: str,  # this potentially points at Dromeus
) -> TraceData:
    context, localization_sequence = await locate(instance_id, model_name='text-embedding-3-large')
    patches, patch_generation_sequence = await generate(context, instance_id, model_name=model_name)
    selected_patch, selection_sequence = await select(patches, instance_id, model_name='claude-3.5-sonnet')
    score = evaluate(selected_patch, instance_id)

    return TraceData(
        sequences=[
          localization_sequence,
          patch_generation_sequence,
          selection_sequence,
        ],
        score=score,
        metadata={},
    )
```

# Design Direction

Having reviewed both frameworks and outlined our experimental goals, we can now sketch the broad strokes of our design. While some implementation details are still under discussion, there are several key principles we agree should guide the redesign:

## Core Design Principles

1. **Component Isolation**: Each stage (localization, generation, selection) should be independently:

   - Testable with clear pseudo-rewards
   - Optimizable through online RL
   - Replaceable with alternative implementations

2. **Standardized Communication**: Components should communicate through well-defined interfaces that:

   - Support both immediate outputs (patches, context) and training data (message sequences)
   - Allow flexible metadata attachment
   - Maintain compatibility with our ML infrastructure

3. **Infrastructure Integration**: The system must integrate smoothly with:
   - Machina for model inference
   - Sequence storage for training data
   - Online RL for component optimization

## Open Implementation Questions

Several important implementation details are still under discussion:

1. **Storage Abstraction**:

   - Whether to completely hide storage details from trace generators
   - How to handle different storage requirements (e.g., online RL's model_address)
   - Trade-offs between abstraction and flexibility

2. **Framework Integration**:
   - How to make infrastructure requirements explicit in interfaces
   - Best way to enforce compatibility with existing systems
   - Supporting different kinds of experiments (batch, online RL, etc.)

These questions will be resolved through prototyping and discussion as we proceed with the implementation.

# Near-Term Priorities

## Caching Strategy {#caching-strategy}

Caching is critical for both development velocity and cost management. The localization stage in particular is expensive, requiring multiple LLM calls per file. Without caching, we would quickly hit rate limits and incur significant costs when training models on our \~15k instance dataset.
Caching is critical for both development velocity and cost management. The localization stage in particular is expensive, requiring multiple LLM calls per file. Without caching, we would quickly hit rate limits and incur significant costs when training models on our ~15k instance dataset.

Currently we cache localization results as zip files in GCloud buckets, an approach which has many several limitations.

- [ ] poor queryability
- [ ] no support for conditioning the cache on the configuration used to generate it
- [ ] no support for partial cache hits

To address these issues, we propose implementing a context cache in some big-data-storage system like GCP Bigtable. This system would cache all calls made to `Machina`. Each cache would be mapped to the configuration used to generate it. This solution has the advantage of being agnostic to the system that uses it, sparing us from re-implementing a new cache for each new system.

## To Do List

Before embarking on a full refactor of the existing code, we should complete the following tasks:

- [ ] Remove `pydra` dependency (mostly unused, poorly typed)
- [ ] Replace file-based communication between stages with in-memory
- [ ] Get existing code to implement basic protocol interfaces
- [ ] Implement end-to-end and component-level tests
- [ ] Identify a better storage solution for caching localization results
- [ ] Implement cache migration from current system
- [ ] Write scripts for evaluating and training pseudo-rewards
- [ ] Refactor the codebase content logic to enable general access to file content without invoking docker. E.g., refactor the gold patch context logic to use in-memory files.
- [ ] Use `machina_schema.Message` inside codemonkeys. Currently codemonkeys introduces a different kind of message that does not add any benefit over machina messages.
