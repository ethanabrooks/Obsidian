# Developing a Modular Framework for AI-Powered Issue Resolution

This document outlines a proposed redesign of our AI issue resolution system to support flexible experimentation and modular components. The goal is to create clear interfaces between components while maintaining compatibility with our online RL infrastructure.

# Current System Review

<!-- Please write some intro text here. We implemented both Agentless and Codemonkeys by forking their code and changing it as little as possible. Now we want to make it our own and make
it modular -->

### [Codemonkeys](https://scalingintelligence.stanford.edu/pubs/codemonkeys/)

<!-- Also need an intro. This is currently one of the strongest performing
"agentless"-style frameworks.
 -->

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

### [Agentless](https://github.com/OpenAutoCoder/Agentless)

<!-- Need an intro: Agentless came before Codemonkeys. Codemonkeys is better but Agentless has some logic that we might want to use. Also, please put this section before the Codemonkeys section and rewrite both so that they make sense in the new order -->

1. **Localization**:

   - Uses embeddings to select relevant files (more efficient than LLM evaluation)
   - Identifies specific AST nodes rather than entire files
   - Better handling of large files with targeted selection

2. **Repair**: Generates fix patches independently

3. **Testing**:

   - Separate stage for test generation
   - Tests are "blind" to the patch

4. **Selection**: Uses majority voting similarly to Codemonkeys

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

<!-- Again need some intro: why are we proposing the design? Because we want to
make the code that we forked from these other codebases our own and we want the results
to be modular adn clean -->

**Key Challenges for Existing Systems:**

- Components are tightly coupled, making experimentation difficult
- Expensive localization stage causes rate-limiting bottlenecks
- File-based data passing between stages adds unnecessary complexity
- Need to support pseudo-rewards in order to debug credit assignment

<!-- I also think before we start throwing code at people we need a bit of high-level explanation like I gave you: we have this structure where at the componenet level,
things get sequenced in a certain way but we want some flexibility with that sequence
meanwhile we want the whole thing to fit into our Online RL framework so it has to
conform to certain assumptions. -->

## Proposed Component Interfaces

<!-- Again could you include some of the thinking behind these protocols here? Ask me if I haven't given you enough info -->

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

<!-- Could you include the python code that I suggested? It is there to show how these interfaces might instantiate actual logic -->

# Pseudo-Rewards

To enable independent optimization of components, we propose "pseudo-rewards" - approximate metrics for the success of each stage:

**Localization**: Percent of of gold patch included in output ("recall" in the Codemonkeys paper)

**Patch Generation**

- Pass rate on gold tests
- More approximate metrics that bypass test execution (for speed):
  - Textual similarity to gold patch (as measured by Levenshtein distance or LLM)
  - Test coverage of proposed fixes

**Selection**

- Quality of selection vs random baseline
- Include gold patch among proposed patches and test ability of selection to identify it

<!-- What about Anticipated Experiments? That is one of the required sections bro -->

# Near-Term Priorities

- Replace file-based communication between stages with in-memory
- Get existing code to implement basic protocol interfaces
- Implment end-to-end and component-level tests
- Identify a better storage solution for caching localization results
- Implement cache migration from current system
- Write scripts for evaluating and training pseudo-rewards
<!-- What about pydra ?-->
