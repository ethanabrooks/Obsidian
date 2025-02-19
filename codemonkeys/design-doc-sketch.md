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

# Proposed Trace Generation Design

Our goal is to create a modular system that allows researchers to mix and match components from both frameworks or new ones that emerge, while maintaining compatibility with our online RL infrastructure.

**Key Challenges for Existing Implementation:**

- Components are tightly coupled, making experimentation difficult
- Expensive localization stage causes rate-limiting bottlenecks
- Long contexts from the Codemonkeys “Context” stage will exceed the limits of our in-house model.
- File-based data passing between stages adds unnecessary complexity
- Need to support pseudo-rewards in order to debug credit assignment

## Proposed Component Interfaces

These interfaces aim to standardize communication between components while allowing flexibility in implementation. Each component returns both its primary output (e.g., CodePointers for Localization) and the sequence of LLM interactions that produced that output.

```py
class LocalizationProtocol:
    def locate(
        instance_id: str
    ) -> list[CodePointer]:  # CodePointer could be line numbers, AST nodes, etc.
        ...

class PatchGenerationProtocol:
    def generate(
        context: list[CodePointer],
        instance_id: str
    ) -> list[Patch]:  # Patch = structured diff
        ...

class SelectionProtocol:
    def select(
        patches: list[Patch],
        instance_id: str
    ) -> Patch:
        ...
```

Note that each component is responsible for writing its own messages to storage. We can discuss the best way to indicate this requirement in the interface.

## Trace Generation Framework

Key requirements for trace generation scripts:

1. Must integrate with `Machina` for model inference
2. Must log to `sequence_storage` for training
3. Must implement standard protocols for hyper-parameters

Example minimal trace generator:

```py
class TraceGenerator(Protocol):
  async def run(
      instance_id: str,
      model_endpoint: str,
      writer: Writer,
  ):
    ...

  async def hypers() -> list[dict[str, Any]]:
    ...
```

Example experiment script:

```py
async def run(
    instance_id: str,
    model_endpoint: str,
    writer: Writer,
):
    context = await Localizer(writer).locate(instance_id)
    # In this example, the PatchGenerator uses the model endpoint
    # to route requests to the model hosted on the Dromeus server.
    patches = await PatchGenerator(
      model_endpoint, writer
    ).generate(context, instance_id)
    await Selector(writer).select(patches, instance_id)
```

## Alternative Functional Interface

An alternative approach favors functional design that abstracts away storage details. This would, among other things, simplify testing since components can be tested without mocking a writer.  
`class TraceGenerator(Protocol):`  
 `async def run(`  
 `instance_id: str,`  
 `model_endpoint: str,`  
 `) -> list[Message]:`  
 `...`

`async def hypers() -> list[dict[str, Any]]:`  
 `...`

```py

def locate(
    instance_id: str
model_name: str | None = ...
) -> tuple[list[CodePointer], list[Message]]:
    ...

def generate(
    context: list[CodePointer],
    instance_id: str
) -> tuple[list[Patch], list[Message]]:
    ...

def select(
    patches: list[Patch],
    instance_id: str
) -> tuple[Patch, list[Message]]:
    ...
```

Example usage:

```py
from agentless import locate
from codemonkeys import generate, select

async def run(
    instance_id: str,
    model_endpoint: str,
 ):
    context, localization_messages = await locate(instance_id, model_name='claude')
    patches, patch_generation_messages = await generate(context, instance_id, model_name=model_endpoint)
    selected_patch, selection_messages = await select(patches, instance_id, model='gpt4o')

    messages = localization_messages + patch_generation_messages + selection_messages
    return score, dict(sequence_name=list[messages], ...)
```

- _Where to put information that is not needed for training but useful for debugging?_
- _Put it in message metadata?_
- _Maybe we need to pass a writer in to `run` in order to give control over multiple collections/sequences per episode._
- _Maybe we need to refactor the configuration of launch scripts_
- _Two places this needs to work:_
  - _Online RL_
  - _Google Batch_
  - _(locally)_
- _What is a CodePointer? It’s a string\!_
-

This approach has several advantages:

1. Components are pure functions, easier to test and reason about
2. Storage concerns are completely separated from component logic
3. Message handling is explicit in the interface

The main trade-off is that sequences are written all at once at the end of the trace. If the trace fails partway through, nothing gets written to sequence_storage. However, this could be seen as a feature rather than a bug, as it ensures we only store complete traces.

# Pseudo-Rewards

To enable independent optimization of components, we propose "pseudo-rewards" \- approximate metrics for the success of each stage:

**Localization**: Percent of lines in gold patch included in output ("recall" in the Codemonkeys paper)

**Patch Generation**

- The proportion of tasks where at least one generated edit (out of N sampled) passes the gold test (the “ground-truth” test used to evaluate submissions for the benchmark). This measure is called “coverage” in the CodeMonkeys paper.
- More approximate metrics that bypass test execution (for speed):
  - Textual similarity to gold patch (as measured by Levenshtein distance or LLM)
  - Test coverage of proposed fixes

**Selection**

- Directly running the gold test on the selected patch (ground-truth reward)
- Include gold patch among proposed patches and test ability of selection to identify it

# Caching Strategy

Caching is critical for both development velocity and cost management. The localization stage in particular is expensive, requiring multiple LLM calls per file. Without caching, we would quickly hit rate limits and incur significant costs when training models on our \~15k instance dataset.

Currently we cache localization results as zip files in GCloud buckets. This approach has several limitations:

1. **Poor Queryability**:

   - Zip files are opaque \- can't easily search through cached results
   - Directory/file naming becomes a poor substitute for proper metadata
   - Difficult to filter for specific configurations (e.g., by model or context length)

2. **Config Management**:

   - Each configuration change requires a new cache directory
   - No clear way to track which configs produced which caches
   - Storage becomes fragmented across many directories

3. **Performance**:
   - Must download and unzip files to access cached results
   - No partial cache hits \- must regenerate entire cache for config changes

To address these issues, we propose moving to a database-backed caching system that supports:

- [ ] Rich metadata and config versioning
- [ ] Efficient querying by any parameter
- [ ] Partial cache hits
- [ ] Good performance under high load
- [ ] Results from multiple pipeline stages

This design would also make it easier to cache results from other stages when needed, such as caching Generation results while training the Selection stage.

# Anticipated Experiments

The following experiments represent possible research directions our design should support. While neither exhaustive nor prioritized, these examples illustrate the kinds of flexibility and modularity our system needs to enable.

**Validate Online RL**:

- [ ] Use gold patch context as temporary workaround for cache population
- [ ] Focus on training Patch Generation components first

**Use Agentless Localization**:

- [ ] Agentless localization context is much smaller because it doesn't pass entire files
- [ ] It's also much cheaper because it full files are only passed through the embedding API instead of using LLM calls

**Component Optimization**:

- [ ] Train each component independently using pseudo-rewards
- [ ] Compare performance of mixed configurations

**Ablating different stages of Localization**:

- TODO

**Alternative Architectures**:

- [ ] Test different stage orderings (e.g., multiple localization-generation cycles)
- [ ] Evaluate separate vs. combined fix/test generation

# Near-Term Priorities

Here we list all the tasks that we should probably complete before embarking on a full refactor of the existing code.

- [ ] Remove `pydra` dependency (mostly unused, poorly typed)
- [ ] Replace file-based communication between stages with in-memory
- [ ] Get existing code to implement basic protocol interfaces
- [ ] Implement end-to-end and component-level tests
- [ ] Identify a better storage solution for caching localization results
- [ ] Implement cache migration from current system
- [ ] Write scripts for evaluating and training pseudo-rewards
- [ ] Refactor the codebase content logic to enable general access to file content without invoking docker. E.g., refactor the gold patch context logic to use in-memory files.
- [ ] Use `machina_schema.Message` inside codemonkeys. Currently codemonkeys introduces a different kind of message that does not add any benefit over machina messages.
