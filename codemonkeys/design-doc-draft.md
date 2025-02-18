This is a draft design doc skeleton for an upcoming meeting. We have imported "Codemonkeys" -- an execution harness for using AI to solve github issues -- into our codebase. We now want to transition to redesigning the code to be more modular. The doc should have at least three sections:

- Review of existing code
- Design Sketch
- Anticipated experiments
- Short-term todos

# Review of existing logic

Two things that have to go in this section:

- discussion of "pseudo-rewards" for independently evaluating each section of the harness
- a sketch of a proposed "experiment script" that someone might use to create a custom harness cobbled together from the existing modules

## high level overview of codemonkeys

3 main "sequential subtasks":

### "Context"

Identifies the files that need to be edited and constructs a "context" or prompt to be given to the AI. The procedure is basically to pass each file in the repo through an LLM to determine if it should be included in the context.
There is then some logic to stitch these files together, prioritized by majority vote, until the context limit is reached.

### "Generation"

This iteratively generates code patches (both fix- and test- patch in the same patch), permitting the agent to revise previous attempts each iteration.

### "Selection"

Takes the set of patches generated in the "Generation" stage and selects the "best" one according to several different heuristics, including majority voting for the patch that passes the most tests and asking a language model to select among the prposed patches

## relationship to agentless

These stages map closely to the four stages of the agentless framework: "localization", "repair", "testing", and "selection" with "Generation" combining the "repair" and "testing" stages (agentless separately generates the repair and test patches).

# Design Sketch

## Interface between "subtasks" or stages

At the lowest level we want to develop a clear interface or contract for each of the three stages that clearly specifies expected inputs and outputs.

### Localization (We will go with this name because it is less overloaded than "context")

- Input: instance_id
- Output: list of pointers to files and parts of files (either by line number or AST node) that are relevant to the task. We could also potentially label these with metadata indicating whether they are relevant to the fix- or test-patch or both, although I suspect that most would be relevant to both and when in doubt we should include rather than exclude. An alternative would be to expect a _raw string_ that contains the actual content of those files. This has the advantage of being a cleaner interface but not allowing the subsequent "Generation" stage to customize the presentation of those files. I could imagine a situation in which a Generation stage has a longer instruction and therefore needs to show less of each file in order to conserve context.
- Pseudo-reward: what percentage of the gold-patch (the ground truth fix-patch) is included in the localization output.

### Patch Generation (Again a little less overloaded than "Generation")

- Input: either a raw localization string or a list of pointers to files and parts of files.
- Output: a list of patches. A patch should probably be an exact Git diff.
- Pseudo-reward:
  - whether any of the patches pass the gold-test (the actual test that the final proposed patch will be run against (not shown to the agent cuz that would be cheating)).
  - alternatively, in order to run very quick evaluations that do not require test execution, we could explore various methods of comparing the proposed patches to the gold-patch, including simply levenshtein distance or asking an LLM to compare the patches.
  - We can also isolate the testing component by checking the test written actually exercises the fix-patch using a code-coverage tool.

### Patch Selection

- Input: a list of patches
- Output: a single patch.
- Pseudo-reward: basically this would have the same pseudo-reward as the "Selection" stage of the agentless framework, except applied to the selected patch instead of the full list of patches generated.
  - another interesting "isolated evalution" strategy would be to provide the agent the gold-patch and test it's capability to pass the gold-patch while exercising it (using a code-coverage tool to check).

Each of these stages would also have implicit inputs, namely the instance_id and all that can be accessed from that, to include the associated repo, etc.

## Experiment interface

Currently we use one script `generate_traces_train.py` to launch all of the episodes in our environment. I think it will give researchers the most flexibility if everyone could write their own script to launch their own experiments. But this
requires a clear interface for these scripts. Broadly, an experiment of this kind has to conform to the following contract:

- receive a model flag that specified a Dromeus (Dromeus is our in-house inference engine) endpoint that could be pointed to a model in training and use this model to perform inference somewhere
- Write the input and the output of at least that model to sequence_storage (our in-house sequence database)
- Finally mathesis (our in-house training library) would need to be responsible for writing a "renderer" mapping these sequences to actual tensor batches for training.

There are lots of other details that need to be added to the experiment interface, e.g.
a hypers function needs to be defined with signature async def hypers() -> list[dict[str, Any]]:. It would be ideal if we could specify these using a module Protocol a la
["Modules as implementations of protocols"](https://peps.python.org/pep-0544/#modules-as-implementations-of-protocols)

### Example script:

```python
async def main(instance_id: str):
  localization_output = LocalizationSubtask.run(instance_id)
  async with s2_writer(
    collection_name=collection_name,
    instance_id=instance_id,
  ) as writer:
    # TODO: replace this with our docker setup and teardown
    patches, patch_generation_messages = PatchGenerationSubtask.run(
      localization_output, instance_id
    )
    writer.write(patch_generation_messages)
    final_patch = SelectionSubtask.run(patches, instance_id)
```

Note that any of these subtasks could implement an interactive loop with a sandbox
environment as in `generate_traces_train.py`, e.g.:

```python
class InteractiveLocalizationSubtask(LocalizationSubtask):
  def run(instance_id: str)
    sandbox_environment = IssueTaskEnvironment.make(instance_id)
    done = False
    observation = await sandbox_environment.initial_observation()
    while not done:
      message = await agent.step(env=environment, messages=observation)
      observation, done = await sandbox_environment.step(action=message.content)

    return sandbox_environment.output()
```

# Anticipated experiments

## Validate online RL

Currently we are blocked on cache population, which will take at least a week barring changes to our rate-limits. A temporary workaround is to provide some context around the gold-patch in place of the files selected by the Codemonkeys localization stage.

## Run Codemonkeys but using Agentless Localization

While the Agentless harness is very poorly written, its localization stage has some
advantages over the Codemonkeys harness. Codemonkeys localization dumps entire
files into the agent's context. This significantly exceeds our agent's context limits in the case of large files which often contain lots of irrelevant code. In contrast, Agentless Localization actually provides pointers to relevant AST nodes. Another advantage of Agentless is that it uses embeddings to select files, which are much
cheaper than running entire files through an LLM as does Codemonkeys.

## Independently optimize each stage against its pseudo-reward

## Other ideas (not imminent but our design should accomodate them)

- mix and match subtasks, e.g. Localization -> Generation -> Localization -> Generation -> Selection
- Use an interactive sandbox for one of the stages
- The test patch "isolation evaluation" mentioned earlier

# Short-term todos

In the next week, there are lots of immediate engineering tasks that are either
high priority or which will make the redesign go much more smoothly:

- remove the `pydra` dependency cuz it just sucks
- implement lots and lots of tests
- Currently both Codemonkeys and Agentless pass information between subtasks by serializing outputs to disk and then loading them back up in the subsequent stage. Would be much cleaner to just pass the data around in memory.
- Rewrite the current localization caches to use a database or some other other storage that is has better ergonomics than saving zip files to gcloud buckets as we are doing now.
