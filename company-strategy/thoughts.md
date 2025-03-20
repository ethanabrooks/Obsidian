I need your help organizing my thoughts into something I can present to my boss. Let's try to put together a short doc explaining and connecting my ideas and then my goal would be to actually create a presentation to share with him (which we can design in slidev).

My company is working on developing super-human coding AI agents. Our approach has frankly not deviated that much from what everyone else is doing: using reinforcement learning to train open source LLMs on the SWE-bench benchmark. That said, we have sourced a dataset of about 16k open-source github issues that can be used for training. The main bottleneck on these has been that each requires an "install script" which we run inside a docker build to bring the container to a point where we can run unit tests, which are then used as the reward to train the agent. The current status is that we can get an 8b model to self-improve and generalize to SWE-bench verified, but the numbers are nowhere near SOTA. There are some questions about how reliable these experiments are as they take a few shortcuts:

- they use "golden context" -- they take the ground-truth diff and supply the agent context around thoses lines so that the agent only has to edit those lines.
- they use Sonnet to write some tests that are used in the editting pipeline
- the model eventually overfits, getting more reliably good at a smaller number of github issues
  Meanwhile, we are working feverishly on getting DeepSeek-v3, a very large Mixture-of-Experts model running on our infrastructure so that we can train it and hopefully get something closer to SOTA.

Meanwhile, we developed a beautiful web app that allows a potential customer to resolve a given github issue using an AI agent. Because our in-house agent isn't very good yet, we are using Anthropic's Sonnet model. Even with Sonnet, the product was not extremely reliable, but we started engaging with customers anyway. From those meetings, we learned that actually a general-purpose (and unreliable) issue-resolution agent is not very useful. What customers really want, especially in enterprise, are more focused "workflows." Customers provided some very interesting examples to include:

- An agent that iterates on a piece of code, optimizing its performance
- An agent that checks if submitted PRs comply with the style guide
  In some ways, this was an exciting development because these workflows are actually _more_ achievable by AI than the wide open issue resolution workflow. It also distinguishes us from one of our primary competitors, Cognition, which is very focused on the issue resolution problem. That said, workflow development presents its own intimidating landscape of competitors. In particular, larger companies like Google, Microsoft, and OpenAI are already working hand-in-hand to work with large enterprises to develop these sorts of custom workflow solutions. They have several advantages over us:
- They have more manpower
- They are using their own AI models
- They are already trusted enterprise partners (while we are a scrappy startup)
  Embarassingly, as we work with these customers, I realized that the logic required to satisfy their requirements basically used _none_ of our existing code, which suggests that we really have no head-start on developing any of this stuff, and we don't really benefit at all from our last year of hard work...

So what should our strategy be in this situation? What is the most likely path to success? In particular:

- How do we leverage our research to benefit our product
- How do we stand out from our larger competitors
- How do we make sure that our workflow design process scales so that we don't just degenerate into a consultancy
