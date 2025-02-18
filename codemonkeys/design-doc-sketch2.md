# Codemonkeys Redesign Proposal

## Executive Summary

We propose a modular redesign of the Codemonkeys execution harness to enable:

1. Independent optimization of pipeline stages
2. Flexible composition of experimental configurations
3. Rigorous evaluation through pseudo-rewards
4. Seamless integration with our ML infrastructure

## Core Components

### 1. Localization Stage

**Objective**: Identify relevant code context for task resolution

**Interface**:

```python
class LocalizationProtocol(Protocol):
    @classmethod
    async def run(cls, instance_id: str) -> LocalizationResult:
        """Returns either:
        - List[CodePointer] (file/line/AST references)
        - ContextString (ready-to-use prompt content)"""

class LocalizationResult(TypedDict):
    content: str | list[CodePointer]
    metadata: dict[str, Any]
```

**Pseudo-Rewards**:

- % of gold-patch lines included in context
- Context compression ratio (relevant lines/total lines)

### 2. Patch Generation

**Objective**: Produce candidate fixes with associated tests

**Interface**:

```python
class PatchGenerationProtocol(Protocol):
    @classmethod
    async def run(
        cls,
        localization: LocalizationResult,
        instance_id: str
    ) -> tuple[list[Patch], list[Message]]:
```

**Pseudo-Rewards**:

- Pass/fail against gold-standard test
- Code coverage of generated tests
- Levenshtein similarity to gold-patch

### 3. Patch Selection

**Objective**: Choose optimal patch from candidates

**Interface**:

```python
class SelectionProtocol(Protocol):
    @classmethod
    def run(
        cls,
        patches: list[Patch],
        instance_id: str
    ) -> Patch:
```

**Pseudo-Rewards**:

- Selection accuracy vs human judgment
- Runtime efficiency of selection process

## System Redesign

### Modular Stage Interfaces

Key design decisions:

1. Strict input/output contracts between stages
2. Dual context representations:
   - Raw strings for immediate use
   - Code pointers for dynamic presentation
3. Pseudo-reward instrumentation points

### Experiment Framework

**Experiment Contract**:

```python
class ExperimentProtocol(Protocol):
    model_endpoint: str
    sequence_storage: SequenceStorage
    hypers: Callable[[], Coroutine[list[dict[str, Any]]]]

    async def run(instance_id: str) -> Patch:
```

**Example Usage**:

```python
class AgentlessLocalizationExperiment:
    async def run(instance_id: str) -> Patch:
        ctx = await AgentlessLocalizer.run(instance_id)
        patches, messages = await GPT4PatchGenerator.run(ctx, instance_id)
        with SequenceStorage.writer(instance_id) as writer:
            writer.log_messages(messages)
        return MajorityVoteSelector.run(patches)
```

## Validation & Experiments

### Immediate Experiments

| Experiment                | Objective                                              | Metrics                        |
| ------------------------- | ------------------------------------------------------ | ------------------------------ |
| Hybrid Localization       | Compare embedding-based vs LLM-based context selection | Context recall, token usage    |
| Patch Generation Ablation | Test independent vs combined fix/test generation       | Test coverage, edit similarity |
| Selection Heuristics      | Evaluate majority vote vs LLM ranking                  | Selection accuracy, latency    |

### Future Directions

1. Iterative refinement loops
2. Sandbox-integrated debugging
3. Cross-stage attention patterns
4. Human-in-the-loop validation

## Roadmap & Implementation

### High Priority

1. **Dependency Cleanup**

   - Remove pydra in favor of native async
   - Standardize on httpx for HTTP clients

2. **Testing Infrastructure**

   - Add integration tests for all stage interfaces
   - Implement golden dataset validation

3. **Data Passing**

   ```python
   # Before
   def run_stage():
       with open("temp/localization.json") as f:
           data = json.load(f)

   # After
   async def pipeline(instance_id: str):
       localization = await Localization.run(instance_id)
       patches = await Generation.run(localization)
   ```

4. **Storage Improvements**
   - Migrate from GCS zips to Firestore
   - Add metadata indexing for experiment runs

### Future Work

- Dynamic context presentation strategies
- Cross-experiment analysis toolkit
- Training data generation pipeline
