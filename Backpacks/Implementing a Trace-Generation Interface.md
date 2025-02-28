# Implementing a Trace-Generation Interface

This document explores a possible implementation of the trace generation framework outlined in [Experiment Design Doc](https://docs.google.com/document/d/1KfHekWeKvlwh9LIpXL_RStV3dA8cGud3oi3_I-MSaRs/edit?tab=t.0#heading=h.628l8i8f0jl1). While the high-level design principles are agreed upon (component isolation, standardized communication, infrastructure integration), this proposal represents one way to realize those goals, focusing particularly on storage abstraction and framework integration.

The key idea is to separate trace generation into two distinct layers: a core layer focused purely on generating traces, and an infrastructure layer that handles storage and execution concerns. This document outlines how such a separation might work and discusses its implications.

## Core Interface Design

Our current trace generation scripts must satisfy several key requirements:

1. Integrate with `Machina` for model inference
2. Log to `sequence_storage` for training
3. Implement standard protocols for hyper-parameters

The foundation of our proposed design is a simple interface that satisfies these requirements while separating core logic from infrastructure concerns. A trace generator takes basic inputs like instance ID and model name, and returns a structured representation of the trace. For example:

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

This interface addresses the first requirement by taking a `model_name` parameter, but is notably silent on storage and configuration. This silence is intentional - we want to separate the core logic of trace generation from these infrastructure concerns.

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

- A core layer focused purely on generating traces:

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

- A single, shared infrastructure layer that handles storage and execution:
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

With the registry in place, we can implement a standard way to run any registered trace generator. Rather than each implementation handling its own execution details, we provide a shared runner that handles common concerns:

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

Finally, we need to package `trace_runner.py` in a way that works with our existing infrastructure. Our current systems have specific expectations:

- `launch.py` requires Python modules that define `absl` flags and provide a `hypers()` function for parallel job launching
- `online_rl.py` expects Docker images that accept standard configuration flags
- Both systems assume scripts handle their own storage operations

The `hypers()` requirement can be satisfied by adding it to our `TraceGenerator` protocol, while the Docker image requirements for `online_rl.py` can be met through careful `BUILD` rules:

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

Another potential concern is that our clean abstraction might be too rigid for some use cases. While separating storage from generation logic works well for standard cases, there might be cases where storage and generation logic are fundamentally intertwined \- for example, scripts that need to write partial results for long-running traces. For these cases, a possible escape hatch is for researchers to write their own `trace_runner.py` implementation while still benefiting from the registry and BUILD infrastructure. This flexibility ensures that our abstraction doesn't become a straightjacket for experimental work.

A third concern is that different consumers of trace data have different metadata requirements. For example, online RL expects a `model_address` string to be stored in the metadata of each message. Rather than baking these requirements into our base abstractions, we could make the `TraceGenerator` type generic:

```py
class OnlineRLMessage(Message):
    model_address: str  # Required by online RL

class TraceGenerator(pydantic.BaseModel, Generic[M]):  # M is the message type
    async def generate_trace(...) -> TraceData[M]: # Propagate the type down
        ...
```

This would allow the registry to contain different kinds of experiments (batch-launchable, online-rl-trainable, etc.), with each implementing the appropriate message type. For instance, experiments registered for online RL would implement `TraceGenerator[OnlineRLMessage]`. The registry could then filter experiments based on their message type, ensuring that only compatible experiments are shown to each consumer.
