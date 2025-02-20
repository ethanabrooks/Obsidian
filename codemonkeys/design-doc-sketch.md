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
- Long contexts from the Codemonkeys "Context" stage will exceed the limits of our in-house model
- File-based data passing between stages adds unnecessary complexity
- Need to support pseudo-rewards in order to debug credit assignment

## Proposed Component Interfaces

These interfaces aim to standardize communication between components while allowing flexibility in implementation. Each component returns both its primary output (e.g., str for Localization) and the sequence of LLM interactions that produced that output.

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

Key requirements for trace generation scripts:

1. Must integrate with `Machina` for model inference
2. Must log to `sequence_storage` for training
3. Must implement standard protocols for hyper-parameters

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

## Storage Abstraction

The `generate_trace` function we proposed addresses the first of our requirements by taking a `model_name` parameter, but is notably silent on storage and configuration. This is intentional \- we want to separate the core logic of trace generation from these infrastructure concerns. However, our current implementation in `generate_traces_train.py` interweaves storage throughout its logic:

```py
# Storage details scattered throughout the code
await writer.write(message.model_dump(mode='json'))
writer.metadata.setdefault('ckpt_step', step)
last_message.update_metadata(**evaluation.model_dump())
writer.metadata.update(metadata_update)
```

This approach has several problems:

- Components need to know storage implementation details
- Storage decisions are mixed with business logic
- Testing requires mocking complex writer behavior
- Changes to storage requirements affect multiple parts of the code

To address these issues, we propose a new architecture where trace generation is split into two layers:

1. A core layer focused purely on generating traces:

```py
class TraceGenerator(Protocol):
    async def generate_trace(
        instance_id: str,
        model_name: str,
        **kwargs
    ) -> TraceData:
        """Generate a trace for a given instance."""
```

This layer will have many implementations \- different scripts combining components in various ways to experiment with trace generation strategies.

2. A single, shared infrastructure layer that handles storage and execution:
   - Loads the appropriate generator
   - Handles all storage operations
   - Manages configuration and job launching
   - Provides consistent interfaces to other systems

This separation means that trace generators can focus solely on the logic of producing data, while the framework handles all storage and infrastructure concerns. Researchers can create new trace generation strategies without worrying about storage or execution details, as all generators use the same infrastructure layer. The `TraceData` return-type acts as a contract between these layers \- generators organize their data into this structure, and the framework guarantees to preserve that organization when storing and retrieving the data.

The power of this contract is that it completely hides storage implementation details. For instance, while `score` might ultimately be stored in sequence metadata by the storage system, the trace generation scripts don't need to know this \- they just set it as a field on `TraceData`. This separation of concerns makes components easier to test and reason about, as they can treat `TraceData` as a pure in-memory data structure.

## Trace Generator Registry

With our storage abstraction in place, we need a way to organize different trace generation implementations. We propose using a registry pattern similar to what we use in `Mathesis` for experiment configurations:

```py
# registry.py
_REGISTRY: dict[str, Type[TraceGenerator]] = {}
def register(name: str): ...  # Standard decorator pattern
def get_generator(name: str) -> Type[TraceGenerator]: ...

# run_codemonkeys.py
@register("codemonkeys_v1")
class CodemonkeysTraceGenerator(TraceGenerator):
    async def generate_trace(...) -> TraceData:
        ...
```

The registry provides a standard interface for trace generators, making different implementations discoverable and interchangeable while keeping generation logic separate from execution details.

## Standard Execution Framework

Rather than having each trace generator implement its own execution logic, we provide a standard runner that handles common concerns:

```py
# trace_runner.py - Standard entry point for all trace generation
async def main():
    trace_generator = get_generator(FLAGS.module_name)

    # Generator produces pure data structure
    trace_data = await trace_generator.generate_trace(
        instance_id=FLAGS.instance_id,
        model_name=FLAGS.model_name,
        **FLAGS.flag_values_dict()
    )

    # Runner handles storage
    await writer.write_trace(trace_data)
```

The centralized runner loads generators from the registry and handles all infrastructure concerns like flag parsing and storage, letting generators focus purely on trace generation.

## Infrastructure Integration

Finally, we need to package this framework in a way that works with our existing infrastructure. Currently, systems like `launch.py` and `online_rl.py` expect complete, standalone scripts. We can maintain compatibility while using our new framework through careful BUILD rules:

```py
def experiment(name: str):
    ...  # Package the trace runner as `/bin/trace_runner` pex

    # Create container with standard environment
    docker_image(
        name=f'{name}_docker',
        instructions=[
            # ... standard setup ...
            f'ENTRYPOINT ["/bin/trace_runner", "--module_name={name}"]',
            # Launch e.g. `codemonkeys_v1` with the trace runner
        ],
    )
```

This approach provides several benefits:

- Each trace-generator gets its own container but shares common infrastructure
- The standard runner ensures consistent handling of storage and configuration
- Existing systems can launch these containers with minimal modification
- New trace-generators only need to implement core logic, not infrastructure

The primary motivation is to maintain the flexibility of our current system while dramatically reducing duplication and complexity. Instead of each script implementing its own storage and execution logic, they just register trace generators that plug into our standard framework.

## Limitations and Concerns

One trade-off of this design is that sequences are written all at once at the end of the trace. If the trace fails partway through, nothing gets written to sequence_storage. However, this could be seen as a feature rather than a bug, as it ensures we only store complete traces.

Another potential concern is that our clean abstraction might be too rigid for some use cases. While separating storage from generation logic works well for standard cases, there might be cases where storage and generation logic are fundamentally intertwined -- for example, scripts that need to write partial results for long-running traces. For these cases, we provide an escape hatch: researchers can write their own `trace_runner.py` implementation while still benefiting from the registry and BUILD infrastructure. This flexibility ensures that our abstraction doesn't become a straightjacket for experimental work.

# Pseudo-Rewards

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

# Caching Strategy

Caching is critical for both development velocity and cost management. The localization stage in particular is expensive, requiring multiple LLM calls per file. Without caching, we would quickly hit rate limits and incur significant costs when training models on our \~15k instance dataset.

Currently we cache localization results as zip files in GCloud buckets, an approach which has many several limitations.

- poor queryability
- no support for conditioning the cache on the configuration used to generate it
- no support for partial cache hits

To address these issues, we propose implementing a context cache in some big-data storage system like GCP Bigtable. This system would cache all calls made to `Machina`. Each cache would be mapped to the configuration used to generate it. This solution has the advantage of being agnostic to the system that uses it, sparing us from re-implementing a new cache for each new system.

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

**Ablating different stages of Agentless Localization**:

Ablatable components include:

- [ ] Relevance scoring
- [ ] Irrelevance scoring
- [ ] Embedding scoring

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
