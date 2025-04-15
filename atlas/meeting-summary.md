# Meeting Summary

**Date:** Apr 11, 2025  
**Attendees:** [Misha Laskin](mailto:misha@reflection.ai)[Ioannis Antonoglou](mailto:ioannis@reflection.ai)[Aakanksha Chowdhery](mailto:chowdhery@reflection.ai)[Ethan Brooks](mailto:ethan@reflection.ai)  
**Key Themes:**

The meeting focused on the core capabilities and future direction for the code understanding system, centered around three main pillars identified on the whiteboard:

1. **Capability:**

   - Accurately answer questions about the codebase.
   - Reliably link answers back to specific source code snippets/locations.
   - Identify and communicate when knowledge is absent or uncertain.
   - Understand code dependencies: What other code is needed to understand a specific piece? What other code is affected when a piece changes?

2. **Persistence:**

   - Develop a persistent understanding of the codebase, potentially involving indexing and caching (RAG vectors mentioned \- George).
   - Explore linking this persistent state to code versions (e.g., git commits/branches) so that the understanding remains relevant as the code evolves.
   - Make the persistent state transparent and verifiable by the user.

3. **Accumulation:**
   - Building on persistence, the system should accumulate knowledge about the codebase over time.
   - Handle knowledge invalidation/updates when the underlying codebase changes.

**Discussion Points & Decisions:**

- **Deep Research:** Discussed refining the "deep research" flow, potentially including a step where the system presents its plan or intermediate findings to the user for confirmation before providing a full answer.
- **User Experience:**
  - Provide a web UI for interacting with the code, potentially similar to Google CodeSearch.
  - Design the UI to be interactive, specifically aiding users in learning and onboarding to new codebases.
  - Reduce verbosity in responses. Feedback on responses should be collected in the primary user channel (e.g., \#atlas-questions, formerly \#devnull).
  - Ensure some form of knowledge representation persists across related user questions to improve efficiency and reduce query times.
- **Evaluation:**
  - Acknowledged the difficulty in objectively measuring answer quality ("fuzzy").
  - Agreed to prioritize user experience and anecdotal feedback (internal users, own intuition) initially.

**Action Items & Next Steps:**

- **Optimize Agentless Query Time:**
  - Ethan: Explore parallelization of API calls (much of Agentless is embarrassingly parallel)
  - George: Implement caching for RAG vectors.
- **User experience:**
  - Ethan: cut down on verbosity of agent responses
  - Chris: cite code in response using code snippets
- **Evaluation:**
  - Elicit feedback from users in the \#atlas-questions channel (or designated successor to \#devnull).
- **Persistence:**
  - Maintain cache of past question-answers/knowledge representations.
  - Include these cached representations in RAG searches to improve relevance and speed.
