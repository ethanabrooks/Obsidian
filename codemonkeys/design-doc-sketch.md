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
- Long contexts from the Codemonkeys "Context" stage will exceed the limits of our in-house model.
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

Example minimal trace generator:

```py
class TraceData(pydantic.BaseModel):
  sequences: list[Sequence]
  score: float
  metadata: dict

class TraceGenerator(Protocol):
  async def generate_trace(
      instance_id: str,
      model_endpoint: str,
  ) -> TraceData:
    ...
```

Example implementation:

```py
from agentless import locate
from codemonkeys import generate, select

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

The current trace generation script (`generate_traces_train.py`) interweaves storage concerns throughout its logic:

```python
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

The new signature for `generate_trace` and the `TraceData` abstraction serve several purposes:

**Storage Implementation Details**: Components focus on producing data, not storing it. For example, they shouldn't need to know that large metadata must be stored in message metadata rather than sequence metadata.

**Data Contract**: The storage system guarantees that data structure and relationships are preserved across serialization boundaries, regardless of physical storage decisions.

**Schema Design**:

- Required fields (like `score`) are explicit in the type
- Optional component-specific data goes in `metadata`
- Interface requirements are clear while maintaining flexibility

For example, while `score` might ultimately be stored in sequence metadata by the storage system, components don't need to know this - they just set it as a field on `TraceData`. This separation of concerns makes components easier to test and reason about, as they can treat `TraceData` as a pure in-memory data structure.

## Trace Generator Registry

To support this abstraction, we propose organizing trace generators using a registry pattern similar to mathesis:

```py
# trace_generator_registry.py
from typing import Protocol, Type

class TraceGenerator(Protocol):
    """Core interface for trace generation logic."""
    @staticmethod
    async def hypers() -> list[dict[str, Any]]:
        """Return hyperparameters for parallel job launching."""
        ...

    @staticmethod
    async def generate_trace(
        instance_id: str,
        model_name: str,
        **kwargs
    ) -> TraceData:
        """Core trace generation logic."""
        ...

_REGISTRY: dict[str, Type[TraceGenerator]] = {}

def register(name: str):
    def decorator(cls: Type[TraceGenerator]) -> Type[TraceGenerator]:
        _REGISTRY[name] = cls
        return cls
    return decorator

def get_generator(name: str) -> Type[TraceGenerator]:
    return _REGISTRY[name]
```

## Standard Execution Framework

The registry enables a standard execution framework that handles storage concerns:

```python
# trace_runner.py
from absl import app, flags
from sequence_storage import Writer
from trace_generator_registry import get_generator

FLAGS = flags.FLAGS
flags.DEFINE_string('module_name', None, 'Name of trace generator module')

async def main(_):
    generator_cls = get_generator(FLAGS.module_name)
    trace = await generator_cls.generate_trace(
        instance_id=FLAGS.instance_id,
        model_name=FLAGS.model_name,
        **FLAGS.flag_values_dict()
    )

    writer = Writer(collection_name=FLAGS.collection)
    await writer.write_trace(trace)

if __name__ == '__main__':
    app.run(main)
```

## Infrastructure Integration

Finally, we package this framework into Docker images that can be launched by our infrastructure:

```python
# BUILD
def experiment(name):
    """Creates a trace generation image combining the runner with a specific generator."""
    python_sources(
        name=f'{name}_runner',
        sources=['trace_runner.py', f'{name}.py'],
        resolve='base',
        dependencies=[
            f'//olympus/experiments/{name}',
            '//olympus/swebench/trace_generator_registry',
            '//olympus/sequence_storage',
        ],
    )

    pex_binary(
        name=f'{name}_pex',
        entry_point='olympus.swebench.trace_runner',
        dependencies=[f':{name}_runner'],
        layout='packed',
        execution_mode='venv',
    )

    docker_image(
        name=f'{name}_docker',
        skip_push=True,
        dependencies=[f':{name}_pex'],
        instructions=[
            'FROM python:3.12-slim',
            # ... standard setup ...
            f'ENTRYPOINT ["/usr/local/bin/python3.12", "/bin/app", "--module_name={name}"]',
            f'COPY olympus.swebench.experiments/{name}_pex.pex /bin/app',
        ],
    )
    return f':{name}'
```

This approach:

1. Centralizes execution logic in the trace runner
2. Uses BUILD rules to combine runners with specific generators
3. Maintains compatibility with existing infrastructure
4. Makes generator implementations purely about generating traces

The key change is that instead of each script implementing its own execution logic, they just register trace generators that get combined with our standard runner at build time.

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

Caching is critical for both development velocity and cost management. The localization stage in particular is expensive, requiring multiple LLM calls per file. Without caching, we would quickly hit rate limits and incur significant costs when training models on our ~15k instance dataset.

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
