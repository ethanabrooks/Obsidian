Our task is to create an AI "workflow" that optimizes code in a given code base. Optimization should not change the functionality of the code but improvements in performance are measurable along two dimensions (number of data points and something else which I forget I will look it up).

The roadmap for implementation looks like this:

1. We will start by casting a wide net for existing solutions like `claude code` (https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) Aider (https://aider.chat/) Cursor composer (https://docs.cursor.com/chat/overview) windsurf (https://codeium.com/windsurf) and others, as well as our own `generate_traces_train` agent.
2. We will implement a docker-sandboxed environment in which we can run the agent with the breaks off
3. We will benchmark all of the existing solutions and choose the solution that performs best.
4. We will analyze the best performing solution for failure modes and develop hypothesis around solutions, e.g. more frequent evaluations, adjusted prompting, etc.
5. We will implement the solutions and go back to step 3.
   Concurrently, we will:

- build integrations with gitlab for seemlessly generating PRs
- adapt Icarus to expose the logic of our agent to the customer

While we want to keep an open mind about different failure modes and what the optimal form factor of the solution will be, we do have a rough hypothesis about its key abstractions:

- Localization: the process of marshalling relevant information from a codebase and potentially external resources
- Code editing: the process of updating files based on a natural language intent
- Evaluation: the process of assessing code correctness and, in this case, the measurable effectiveness of an implementation
- Selection (contingent on evaluation): the process of selecting from several alternative proposals (and possible combining them where appropriate) for the final proposal delivered to a customer.

In our current case, we can mostly punt on localization because code is contained within a single file (this assessment may change if the file is large or contains lots of irrelevant code).
Code editing should be a topic of careful research. There are several possible alternatives:

- Whole file edits, similar to Cursor or Aider: https://aider.chat/docs/benchmarks.html. This has the disadvantage that edits will often contain extraneous changes that should be excluded from the final submission. Another disadvantage is that the agent will sometimes use language like "... existing code..." when suggesting an edit. These comments have to detected and the appropriate functionality must be implemented, e.g. detecting what "existing code" refers to and inserting it into the agent's proposal (or preventing the agent from saying things like this, although unintelligent string-munging approaches to detecting this kind of language are likely to be brittle). A third disadvantage is that this is an expensive operation. All that said, this approach appears to be the most reliable way to actually edit a file.
- "Diff"-style edits in which the agent proposes text to replace and text to replace it with. This is an approach used by our current Reflection agent and by code-monkeys. This approach can run into issues when the text-to-replace does not match existing text or matches multiple locations within the existing text. There is also a challenge in zipping together multiple replace commands, especially when they touch overlapping pieces of code. In contrast, whole edits have the advantage of ensuring that no two proposed edits touch the same file. Another challenge with this approach is that a draconian insistence on exact string match for the text-to-replce can often be a high-bar for the agent while more "magical" approaches to guessing the agent's intent can often make the tool opaque to the agent and to behave mysteriously in certain hard-to-anticipate corner cases. In general we advocate an approach in which the tool functions very simply and transparently but suggestions are made to the agent (particularly when the tool-use attempt fails) which are the product of opaque, "magical" logic since the agent doesn't have to understand where the suggestion came from.
- A hybrid approach between whole file and diff wherein an agent rewrites a whole class, function, or method. One question here is how the agent "points" to the object that it wishes to rewrite -- should it write out the existing object in its entirety or use some kind of pointer syntax like path.to.file.Class.method.
- Using existing bash tools like `sed`. This has the advantage of leveraging the immense expressivity of these tools as well as the agent's prior knowledge about their operation. That said, these tools perhaps give the agent too much freedom, allowing it to make unintentional changes. Some mechanism has to be implemented to detect changes when they are made, display them to the agent, and revert them when they are unintended.

Evaluation needs to be the most flexible abstraction, as the appropriate logic varies widely between workflows. In this particular workflow, the evaluation has two components:

- The performance benchmark, which needs to measure along both components and weight them appropriately in order to combine into a single number
- Correctness -- we need to implement tests that check that the underlying logic of the code has not changed. These tests can be written by a human and remain static across agent runs.
  One hypothesis that we will test is that frequent evaluation will be key to improving agent performance. However, the question of what should trigger an evaluation remains open. A few candidates are:
- let the agent run tests but encourage it to do so frequently
- run tests every time code changes (or ask the agent if we should run tests)
- Run tests every `n` steps in which case this needs to be clearly communicated to the agent to avoid confusion

Finally, selection should basically juse use the evaluation to select among agent proposals. While this is relatively straightforward, one thing that needs to be determined empirically is the right tradeoff between parallel and sequential logic. Given enough compute for e.g. 100 timesteps, one approach would be to run a single agent for 100 timesteps, another would be to run 10 agents for 10 timesteps, another would be to run 100 agents for 1 timestep. If agents were perfectly intelligent the first would be the best approach because the agent is given the most information and can learn from its mistakes. In practice, we find that agents have a nasty habit of getting tunnel vision and varying little from an existing proposal, even if it is fundamentally flawed. A good way to escape this tunnel vision is to wipe the slate clean and start the agent from scratch.
