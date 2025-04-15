# The State of Our Build System: A Critical Analysis

## Executive Summary

Our current build system, while designed for scalability, has become a significant bottleneck for developer productivity. This document outlines key pain points and proposes potential solutions.

## Core Issues with CI/CD

<!--  In addition running `pants generate-lockfiles` takes 5-10 minutes -->

The most pressing issues with our current CI/CD pipeline center around test execution and reliability. Every dependency update, no matter how minor, triggers a complete test run across the entire repository. These runs typically take between 20 and 60 minutes to complete, creating substantial delays in the development process. This behavior stems from our lack of intelligent test selection and dependency tracking.

<!-- The behavior happens in part because none of our dependencies are pinned so whenver we run generate-lockfiles, several dependencies update. THis is one possible cause or maybe our CI is just set up so that every test in a resolve runs whenever the lockfile for this resolve changes. -->

Test reliability presents another major challenge, particularly in the mathesis codebase. Tests frequently either time out or produce inconsistent results, forcing developers to waste valuable time re-running tests and investigating failures that often turn out to be unrelated to their changes.

## Development Environment Friction

The development environment itself introduces several obstacles to efficient coding. The code review process, while important, creates unnecessary overhead even for experimental branches.

<!-- No code in the `experimental/` directory which is supposed to be exempt from code-review but no one has sat down and figured out how to set up github to not require it for these directories. -->

Despite having an informal "rubber stamp" agreement for certain changes, developers still need to wait for approvals, slowing down the development cycle.

Our IDE integration with Cursor is particularly problematic.

<!-- Say Cursor/VS code. It's the same for both but some people use one and some people use the other -->

Import path inference consistently fails, requiring manual addition of import paths – a stark contrast to the experience in smaller, non-pants repositories where auto-imports work seamlessly. The IDE's performance suffers from attempting to scan files outside the relevant scope, leading to sluggish performance and reduced productivity.

Workspace configuration presents its own set of challenges. When creating subdirectory workspaces, developers encounter mysterious "missing stub files" errors. Even experimental code requires sandbox configuration, adding unnecessary complexity and setup overhead for new features. BUILD files require constant maintenance and manual intervention for tasks that could be automated.

<!-- It's not that the tasks could be automated. It's that you don't need a BUILD file for experimental logic -->

## Impact on Developer Productivity

My recent attempt to implement Agentless localization logic serves as a telling example of these issues. Before writing any actual feature code, I spent hours wrestling with dependency setup. Multiple CI/CD cycles were wasted dealing with unrelated test failures, and a disproportionate amount of time went into environment setup rather than actual development work.

## Proposed Solutions

<!-- My proposed solution is that initial development should happen in repos separate from Olympus. We should also fix the problem where every test runs every time a dependency is added either by pinning dependencies so that they don't all update or by fixing whatever misconfiguration is causing every single test to run. We should also   -->
