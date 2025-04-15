# Research Plan: Enterprise Code Understanding Agent

## Project Overview

Our goal is to create an AI agent that can effectively answer questions about large-scale codebases. The fundamental challenge we face is that enterprise codebases are too large to process all at once, even for advanced language models. Therefore, we need a system that can maintain a persistent, hierarchical understanding of the code that can be efficiently queried when questions arise.

### Core Requirements

1. The system must maintain an up-to-date understanding of the codebase as it evolves
2. The system must be able to view and explain code at different levels of abstraction. This requirement stems from two competing needs:
   - The question-answering agent needs high-level context to understand how specific components fit into the larger system
   - The size of enterprise codebases makes it infeasible to view all source code simultaneously
3. The system must be able to provide specific implementation details with accurate source code citations

### Proposed Approach

We propose creating a tree-structured knowledge base where each node represents a distillation of some portion of the code. At the root, we store the broadest possible overview of the system. As we descend the tree, each level provides increasingly detailed information until we reach the leaves, which link directly to the source code. When answering questions, the agent will traverse this tree to find relevant information while maintaining appropriate context.

## System Functionality

### Knowledge Representation

Understanding and maintaining knowledge about large codebases requires addressing two distinct needs:

1. **Hierarchical Understanding**: Large codebases cannot be understood all at once. We need a way to view the code at different levels of abstraction, from high-level architecture down to implementation details.

2. **Dependency Management**: Code components are interconnected. Understanding or modifying any component requires understanding both its dependencies and how changes might affect dependent code.

To address these distinct requirements, we propose maintaining two separate graph structures:

1. **Abstraction Hierarchy**

   - A directed tree where edges represent increasing specificity
   - Each edge connects a broader summary to a more detailed summary
   - Root contains complete codebase overview
   - Leaves contain individual source file summaries
   - Used by the querying agent to navigate from general to specific information

2. **Dependency Graph**
   The dependency graph serves two critical functions:

   - Enabling accurate code understanding by tracking dependencies between components
   - Supporting systematic propagation of changes through the codebase

   Structure:

   - An edge A→B indicates that component A depends on component B
   - Captures both explicit dependencies (imports) and implicit dependencies (shared resources like files, databases, environment variables, etc.)

We propose starting with the filesystem hierarchy for the Abstraction Hierarchy, where each node represents either a directory or a file. This provides a straightforward, language-agnostic implementation that we can build upon.

> **Research Question:** Can we discover more effective organizational structures than the filesystem hierarchy, given that the organization of large enterprise codebases tends to evolve organically over long time scales, often leading to suboptimal structure?

> **Research Question:** Is there a reliable way to identify well-established libraries that are sufficiently documented in the AI's training data that we can exclude them from our dependency graph? This is not a v0 feature but could significantly improve efficiency if feasible.

> **Research Question:** How can we identify dependencies that aren't captured by static analysis? Examples include:
>
> - Components that share database tables or schemas
> - Code that produces files consumed by other components
> - Services that share environment variables or configuration

### Initial Knowledge Construction

We propose a two-phase bottom-up construction process:

1. **Dependency Graph Construction**

   - Start by analyzing low-level primitives that have no dependencies (except built-ins and external libraries)
   - Create summaries for these primitive components
   - Iterate upward, creating summaries for components that depend only on already-processed code
   - Continue until reaching code with no dependents

2. **Abstraction Hierarchy Construction**
   - Begin with raw source code at the leaves
   - Create summaries for each level of the filesystem hierarchy
   - Iterate upward until reaching the root, which contains a complete codebase summary

### Knowledge Maintenance

Our system will support tracking one or more GitHub branches. When a PR is about to merge into a tracked branch, a hook will trigger the following update process:

1. Update summaries for changed files
2. Traverse the dependency graph to update summaries of all dependent code (as necessary)
3. Traverse up the Abstraction Hierarchy from the updated summaries, potentially stopping when changes no longer affect higher-level summaries

> **Research Question:** How should we handle large PRs that touch many files? We need to update the knowledge base atomically to maintain consistency. Should we attempt to partition large changes into independent components that can be processed sequentially? If so, how?

> **Research Question:** How can we prevent knowledge degradation over time? As our system operates, it will probabilistically miss some code changes, leading to a gradual degradation of accuracy as these misses compound. We need to investigate:
>
> - Methods for detecting when knowledge has become stale
> - Strategies for periodic revalidation of our knowledge base
> - Ways to identify and correct inconsistencies

### Query Processing

When answering a query, the agent will be provided with two primary actions:

1. Move up the Abstraction Hierarchy (every node has exactly one parent)
2. Move down the Abstraction Hierarchy (parameterized by a list of children to visit)

The agent will generate structured output to ensure accurate source code citations. Using tools like Langchain or Pydantic-AI, one possible schema for this output is:

```python
class Citation(pydantic.BaseModel):
    code: str
    path: pathlib.Path

class Answer(pydantic.BaseModel):
    answer: str
    citations: list[Citation]
```

Context Window Management:

- The agent always starts at the root node for high-level context
- When visiting children nodes, their text is added to the context window
- If all children of a parent node are present in the context, the parent's text can be removed
- The system ensures no node's text is ever added to the context twice
- When the agent branches (visits multiple children), all visited nodes' text remains in context

## Evaluation Framework

### Internal Testing Program (Slack-based)

Version 0:

- Users can ask questions about the codebase through Slack
- Team members can react with +/- to indicate answer quality
- A dashboard tracks and displays vote statistics for agent responses

Version 1:

- Questions are answered by both our agent and a Claude Code baseline
- Team members vote for their preferred response

### Automated Quality Checks

We will explore the possibility of a "red team" agent that:

- Searches for inconsistencies in our knowledge base
- Identifies potential hallucinations by comparing summaries to source
- Posts findings to Slack for team verification

> **Research Question:** What indicators could guide the red team's search for inconsistencies and hallucinations? Potential indicators to investigate:
>
> - Temporal inconsistencies (e.g., references to removed code)
> - Logical contradictions between different levels of the Abstraction Hierarchy
> - Mismatches between summaries and actual code structure
> - References to non-existent files or functions

### PR-Based Testing

This evaluation specifically targets the system's ability to adapt to code changes:

1. When submitting a PR, developers identify questions whose answers should change because of their PR
2. After the PR is merged, the system answers these questions
3. The PR author is tagged to verify the new answers
4. Results are tracked to measure adaptation accuracy

## Engineering Challenges

Several technical challenges need to be addressed during implementation:

1. **Cross-Language Dependency Analysis**: We need to either:

   - Identify existing language-agnostic dependency analysis tools
   - Create a modular system that can integrate language-specific analyzers

2. **Version Control Synchronization**: Since `.reflection/` needs to be version-controlled alongside source code, we need to ensure that code changes and their corresponding `.reflection/` updates remain synchronized. The key challenge is:

   If we generate `.reflection/` updates after a PR is merged:

   - We must create a new PR for these `.reflection/` changes
   - Before this new PR can be merged, other code PRs might be merged
   - These intervening changes could affect or invalidate our `.reflection/` updates

   Ideally, code changes and their corresponding `.reflection/` updates would be included in the same PR, but this raises implementation questions:

   - How can we automatically generate `.reflection/` updates as part of the PR creation process?
   - How can we ensure these updates remain valid if the PR is modified during review?
