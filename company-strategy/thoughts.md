My company is working on developing super-human coding AI agents. Our approach has frankly not deviated that much from what everyone else is doing: using reinforcement learning to train open source LLMs on the SWE-bench benchmark. That said, we have sourced a dataset of about 16k open-source github issues that can be used for training. The main bottleneck on these has been that each requires an "install script" which we run inside a docker build to bring the container to a point where we can run unit tests, which are then used as the reward to train the agent. The current status is that we can get an 8b model to self-improve and generalize to SWE-bench verified, but the numbers are nowhere near SOTA. There are some questions about how reliable these experiments are as they take a few shortcuts:

- they use "golden context" -- they take the ground-truth diff and supply the agent context around thoses lines so that the agent only has to edit those lines.
- they use Sonnet to write some tests that are used in the editting pipeline
- the model eventually overfits, getting more reliably good at a smaller number of github issues
  Meanwhile, we are working feverishly on getting DeepSeek-v3, a very large Mixture-of-Experts model running on our infrastructure so that we can train it and hopefully get something closer to SOTA.

Meanwhile, we developed a beautiful web app that allows a potential customer to resolve a given github issue using an AI agent. Because our in-house agent isn't very good yet, we are using Anthropic's Sonnet model. Even with Sonnet, the product was not extremely reliable, but we started engaging with customers anyway. From those meetings, we learned that actually a general-purpose (and unreliable) issue-resolution agent is not very useful. What customers really want, especially in enterprise, are more focused "workflows." Customers provided some very interesting examples to include:

- An agent that checks if submitted PRs comply with the style guide
  In some ways, this was an exciting development because these workflows are actually _more_ achievable by AI than the wide open issue resolution workflow. It also distinguishes us from one of our primary competitors, Cognition, which is very focused on the issue resolution problem. That said, workflow development presents its own intimidating landscape of competitors. In particular, larger companies like Google, Microsoft, and OpenAI are already working hand-in-hand to work with large enterprises to develop these sorts of custom workflow solutions. They have several advantages over us:
- They have more manpower
- They are using their own AI models
- They are already trusted enterprise partners (while we are a scrappy startup)
  Embarassingly, as we work with these customers, I realized that the logic required to satisfy their requirements basically used _none_ of our existing code, which suggests that we really have no head-start on developing any of this stuff, and we don't really benefit at all from our last year of hard work...

So what should our strategy be in this situation? What is the most likely path to success? In particular:

- How do we stand out from our larger competitors
- How do we leverage our research to benefit our product
- How do we make sure that our workflow design process scales so that we don't just degenerate into a consultancy

I have thoughts on all of these topics and I will go one-by-one. First, how do we stand out from our larger competitors?

As long as our product gets shared in smokey back-rooms with enterprise customers, it will be hard to distinguish ourselves from the Googles and OpenAIs of the worls. But if we have a product that acquires a broader reputation for quality and reliability, I think that we may bve able to acquire an advantage. This is where we can leverage open-source. As far as I can tell, no one has released a robust suite of plug-and-play AI-powered github tooling. By this I primarily mean routine background tasks and github actions that, with a few minimal inputs, can perform complex AI powered tasks. We have already thought of several of these beyond the two that I shared earlier:

- Going through a code base and improving type-safety by e.g. removing `# type: ignore`
- Identifying dependencies which can be upgraded, upgrading them, and fixing the code where necessary
- Taking over a PR and fixing small lint- and type- errors that might be causing the CI to fail
- Taking an initial pass over a PR to identify obvious issues before a human takes a look
- Going through github Issues and identifying obsolete ones
- Identifying missing or incorrect documentation in a repo and fixing it

Each of these can either be packaged as a github action or as a routine action that runs daily, weekly or continuously. How would we implement this? I am actually less clear how "routine actions" would work in Github, although I know there are integrations for e.g. dependabot.

The required inputs vary per workflow. Some are read-only, e.g. the obsolete issues workflow. In that case, all that is needed is a pointer to the repo and the commit hash. For those that require some kind of code-running e.g. fixing failing tests, we can focus on repos that already have CI (this has to be the case for workflows that are packaged as Github Actions) and leverage the fact that CI already has to specify how to setup and run code within a repo. Therefore we actually get those tricky install scripts that took us so much time to harvest from the wild FOR FREE. So the input is still basically just a repo and a commit hash. As a crude starting point, just running CI using something like the Act tool (https://github.com/nektos/act) is probably a sufficient, albeit slow, method of checking the correctness of code that our agent produces. We need some kind of mechanism (probably defining env variables) for ensuring that e.g. this has access to necessary secrets. We can work on developing capabilities however, using a combination of AI and programmatic logic, that basically selectively comments out parts of the CI that are less relevant to the current wowrkflow. For example, the type-safety workflow would primarily be interested in just running a linter, although we will eventually want to make sure that all CI passes.

The goal of this effort would be an ever-growing suite of generally useful, time-saving github integrations that not only enterprise but also open-source customers could seemlessly install into their github-based projects. As far as I know, nothing like this exists or has gained widespread attention, although it surely will soon. Going open-source has several advantages:

- It allows us to battle-test our product
- It forces us to implement tools that scale and don't require case-by-case implementation
- It enables us to build reputation that will attract enterprise customers and hopefully distinguish us from the AI titans that we are competing with who have workflow development initiatives, but basically at the consultancy, not the product level.

Regarding research... this is a whole nother bag of worms. The current effort of maximizing SWE-bench should probably continue, as a robust SWE-bench solving agent would probably be quite useful on many of these tasks. However, we still need a way to make our agent better than the powerful fronteir models that already exist adn which we are already falling back on. To this end, I think that specialization is essentially unavoidable: we have to train our models on our workflows. How can we do this, given that many of these workflows have only a handful of datapoints? In my mind there is a progression that has to occur, where initially we attract customers using frontier models and this allows us to collect data. Note that what we are collecting is not anything proprietary. We are just collecting the inputs to our github integrations: the repo-name, the commit hash, possibly an associated PR or Issue. None of this would be a problem for an open-source customer.
