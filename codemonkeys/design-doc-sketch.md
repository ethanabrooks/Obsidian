# Developing a Modular Framework for AI-Powered Issue Resolution

This document outlines a proposed redesign of our AI issue resolution system to support flexible experimentation and modular components. The goal is to create clear interfaces between components while maintaining compatibility with our online RL infrastructure.

# Current System Review

We have implemented both Agentless and Codemonkeys frameworks by forking their codebases with minimal modifications. Ultimately we want to rewrite both, with priority on
Codemonkeys.

### [Agentless](https://github.com/OpenAutoCoder/Agentless)

The original framework for automated code repair, introducing the key stages that Codemonkeys later refined. While it underperforms Codemonkeys, we may want to borrow from it in
some of our experiments.

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

3. **Selection Stage**:
   - Uses multiple heuristics including:
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

# Proposed Design

Our goal is to create a modular system that allows researchers to mix and match components from both frameworks or new ones that emerge, while maintaining compatibility with our online RL infrastructure.

**Key Challenges for Existing Systems:**

- Components are tightly coupled, making experimentation difficult
- Expensive localization stage causes rate-limiting bottlenecks
- File-based data passing between stages adds unnecessary complexity
- Need to support pseudo-rewards in order to debug credit assignment

## Proposed Component Interfaces

These interfaces aim to standardize communication between components while allowing flexibility in implementation.

```python
class LocalizationProtocol:
    async def locate(
        instance_id: str
    ) -> list[CodePointer]:  # CodePointer could be line numbers, AST nodes, etc.
        ...

class PatchGenerationProtocol:
    async def generate(
        context: list[CodePointer],
        instance_id: str
    ) -> list[Patch]:  # Patch = structured diff
        ...

class SelectionProtocol:
    async def select(
        patches: list[Patch],
        instance_id: str
    ) -> Patch:
        ...
```

## Experiment Framework

Key requirements for experiment scripts:

1. Must integrate with `Dromeus` for model inference
2. Must log to `sequence_storage` for training
3. Must implement standard protocols for hyper-parameters

Example minimal experiment:

```python
class Experiment(Protocol):
  async def run(
      instance_id: str,
      model_endpoint: str,
  ):
    """
    Needs to write messages to sequence_storage. Can we enforce this assumption
    with the type system?
    """
    ...

  async def hypers() -> list[dict[str, Any]]:
    ...
```

Example experiment script:

```python
async def run(
    instance_id: str,
    model_endpoint: str,
) -> Patch:
    context = await Localizer().locate(instance_id)
    # in this example, the PatchGenerator will be trained
    # because it actually uses the dromeus endpoint
    patches = await PatchGenerator(model_endpoint).generate(context, instance_id)
    return await Selector().select(patches, instance_id)
```

# Pseudo-Rewards

To enable independent optimization of components, we propose "pseudo-rewards" - approximate metrics for the success of each stage:

**Localization**: Percent of gold patch included in output ("recall" in the Codemonkeys paper)

**Patch Generation**

- Pass rate on gold tests
- More approximate metrics that bypass test execution (for speed):
  - Textual similarity to gold patch (as measured by Levenshtein distance or LLM)
  - Test coverage of proposed fixes

**Selection**

- Quality of selection vs random baseline
- Include gold patch among proposed patches and test ability of selection to identify it

# Anticipated Experiments

1. **Validate Online RL**:

   - Use gold patch context as temporary workaround for cache population
   - Focus on training Patch Generation components first

2. **Use Agentless Localization**:

   - Agentless localization context is much smaller because it doesn't pass entire files
   - It's also much cheaper because it uses embeddings instead of LLM calls

3. **Component Optimization**:

   - Train each component independently using pseudo-rewards
   - Compare performance of mixed configurations

4. **Alternative Architectures**:
   - Test different stage orderings (e.g., multiple localization-generation cycles)
   - Evaluate separate vs. combined fix/test generation

# Near-Term Priorities

- Remove `pydra` dependency
- Replace file-based communication between stages with in-memory
- Get existing code to implement basic protocol interfaces
- Implement end-to-end and component-level tests
- Identify a better storage solution for caching localization results
- Implement cache migration from current system
- Write scripts for evaluating and training pseudo-rewards
