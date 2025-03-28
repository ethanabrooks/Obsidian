Mar 25, 2025

## Meeting Mar 25, 2025 at 11:01 EDT

Meeting records [Transcript](?tab=t.n7pgp5hoic7d)

### Summary

Ethan Brooks and George Antoniadis met to discuss Bridgewater's request to integrate multiple systems within an 8-week deadline, a timeline deemed impossible due to scope and readiness issues. After exploring and rejecting on-prem and external API solutions due to various concerns including code access and security, they proposed a self-hosted runner solution using a Debian package for data retrieval and debugging, leveraging Dagger for CI/CD integration. Ethan Brooks will create a design document outlining a portable, self-hostable/cloud-based solution (potentially a Docker image) before presenting a concrete proposal to Bridgewater, following discussion of labor division.

### Details

- **Meeting Goal:** Ethan Brooks initiated the meeting to have a more open discussion with George Antoniadis about a project with Bridgewater, aiming to identify unknowns and high-risk tasks ([00:01:07](?tab=t.n7pgp5hoic7d#heading=h.l66vx2mktfam)).

- **Bridgewater's Initial Request:** The initial request from Bridgewater was to integrate "every single thing" built, including Icarus, Reflection API, and Everest, within an 8-week deadline. This was deemed impossible by George Antoniadis due to the scope and lack of production readiness ([00:03:59](?tab=t.n7pgp5hoic7d#heading=h.yfxr64x0kzx3)).

- **On-Prem Concerns:** George Antoniadis and Richie strongly opposed an on-prem solution due to significant challenges with production readiness, support, monitoring, and debugging ([00:05:53](?tab=t.n7pgp5hoic7d#heading=h.if5ag1eqt5r3)). This was also a point of concern for Ethan Brooks ([00:09:10](?tab=t.n7pgp5hoic7d#heading=h.ssdihof6e2ag)).

- **External API Rejection:** Bridgewater rejected the use of an external API, citing concerns about the sensitivity of their code and the desire to keep it within their systems ([00:07:33](?tab=t.n7pgp5hoic7d#heading=h.3mz85ld33qk2)).

- **Limited Options:** The discussion narrowed down to two primary options: on-prem deployment (rejected due to concerns outlined above) and sending Bridgewater's code to an external API (rejected by Bridgewater) ([00:09:10](?tab=t.n7pgp5hoic7d#heading=h.ssdihof6e2ag)).

- **Code Access Limitations:** A major point of contention was the level of code access required. Bridgewater insisted on minimizing exposure of their code, while the developers needed access for debugging and improvement ([00:10:05](?tab=t.n7pgp5hoic7d#heading=h.tg590gd7jib4)) ([00:13:55](?tab=t.n7pgp5hoic7d#heading=h.t0to5t2rrugd)).

- **Alternative Approach (Self-Hosted Runners):** George Antoniadis proposed a solution using self-hosted runners similar to GitHub CI/CD, where the agent loop runs on Bridgewater's infrastructure, but the developers maintain API access for data retrieval ([00:18:29](?tab=t.n7pgp5hoic7d#heading=h.z0detgq0qtvd)).

- **Legal and Regulatory Compliance:** The discussion touched upon legal requirements for financial technology companies and their suppliers regarding ISO 27001 compliance. It was unclear whether Bridgewater's requirements were legally mandated in the US ([00:21:29](?tab=t.n7pgp5hoic7d#heading=h.lno3gepg9mmk)).

- **Data Access and Observability:** George Antoniadis emphasized the importance of data visibility for debugging and product improvement. Without sufficient access to logs and traces, they were concerned about their ability to effectively address issues ([00:24:08](?tab=t.n7pgp5hoic7d#heading=h.pma3dijiaf6b)).

- **Proposed Solution (Debian Package):** A Debian package containing a lightweight agent and Icarus integration was proposed as a compromise. This approach would allow for updates and provide sufficient logging for debugging, while minimizing the need to access Bridgewater's entire codebase ([00:42:55](?tab=t.n7pgp5hoic7d#heading=h.20mb9kpuunmu)). The focus shifted to a smaller, more isolated system instead of the more extensive "generate traces train" system ([00:38:50](?tab=t.n7pgp5hoic7d#heading=h.3yyvd29xwym)).

- **Telemetry and Logging:** The final proposal centered around using telemetry to track agent interactions and collect necessary debugging information. While Bridgewater's code would remain on their systems, crucial logs and traces would be transmitted to the developers via a self-contained Debian package ([00:45:03](?tab=t.n7pgp5hoic7d#heading=h.d4igum9j2eoo)) ([00:52:09](?tab=t.n7pgp5hoic7d#heading=h.kzqzl1mypvrk)). This solution would allow for iteration and improvement of the system without direct access to their full repository ([00:53:11](?tab=t.n7pgp5hoic7d#heading=h.9qvekyoc3qlt)). However, the success of this approach depended on Bridgewater's willingness to share this information ([00:45:58](?tab=t.n7pgp5hoic7d#heading=h.gu3m3wucwmrn)) ([00:55:11](?tab=t.n7pgp5hoic7d#heading=h.e3gjlh65xr0w)).

- **Self-Hosted and Cloud-Based Solution Design** Ethan Brooks and George Antoniadis discussed a design for a solution that can be self-hosted or cloud-based . They agreed that a portable binary, potentially packaged as a Docker image, would be the best approach ([01:01:20](?tab=t.n7pgp5hoic7d#heading=h.daf9vgos83ec)), allowing it to run on various environments. Ethan will create a design document to share with George before wider distribution. They aim for team consensus and to present a concrete proposal to Bridgewater ([01:02:09](?tab=t.n7pgp5hoic7d#heading=h.fcn6ncacxhte)).

- **Dagger Integration** The conversation included a discussion of integrating Dagger into the solution. George had previously explored options, including wrapping Dagger in an API or providing direct access. Ethan, having reviewed Dagger's documentation, favored its use due to its suitability for CI/CD processes, contrasting it with Langchain ([01:03:07](?tab=t.n7pgp5hoic7d#heading=h.jdgkv7w24x9r)). They agreed that Dagger would be a suitable implementation for the binary package. Ethan expressed a preference for leveraging open-source solutions whenever possible ([01:04:02](?tab=t.n7pgp5hoic7d#heading=h.s3hvwll47ii2)).

- **Interface Design and Next Steps** Ethan plans to design a clean interface for the scripts to interact with Icarus, bypassing the API. This requires understanding Iris's Firebase data expectations ([01:05:19](?tab=t.n7pgp5hoic7d#heading=h.nlghef43aoj5)). Following the design document's completion and communication with Bridgewater, they will discuss labor division ([01:04:02](?tab=t.n7pgp5hoic7d#heading=h.s3hvwll47ii2)). They acknowledged the complexities of working with financial technology companies but agreed to proceed ([01:05:19](?tab=t.n7pgp5hoic7d#heading=h.nlghef43aoj5)).

### Suggested next steps

- [ ] Ethan Brooks will create a document outlining a concrete proposal for the project with Bridgewater, detailing a Debian package solution that prioritizes data security and allows for iterative improvements while considering the client's needs and the team's capabilities. This proposal will include a plan for handling updates and version control, and address the issue of future clients where on-prem solutions are not required.
- [ ] George Antoniadis and Ethan Brooks will determine the minimum requirements for the project, focusing on what data needs to be shared to allow for debugging and improvement, and explore alternative approaches to avoid on-prem solutions and sending client code to external APIs while balancing Bridgewater's security concerns with the need for iterative product development.
- [ ] Ethan Brooks will create a design document, share it with George Antoniadis for review and feedback before sharing it with others, and then get buy-in from the team.
- [ ] Ethan Brooks will design a clean interface for scripts to interact with Icarus without requiring an API, contingent upon the team adopting the proposed solution. This will involve understanding Icarus's Firebase data expectations.
- [ ] Ethan Brooks and George Antoniadis will determine how to divide the labor for implementing the solution, after receiving feedback from Bridgewater.

_You should review Gemini's notes to make sure they're accurate. [Get tips and learn how Gemini takes notes](https://support.google.com/meet/answer/14754931)_

_Please provide feedback about using Gemini to take notes in a [short survey.](https://google.qualtrics.com/jfe/form/SV_9vK3UZEaIQKKE7A?confid=DKi-U64M5XbGpGYSdtW7DxIQOA8MCwMyBwiKAiAAGAEI)_
