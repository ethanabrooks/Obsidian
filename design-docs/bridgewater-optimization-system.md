# Code Optimization System Design

**Status**: Draft  
**Author**: [Your Name]  
**Last Updated**: [Date]

## Overview

This document proposes a system that enables code optimization while balancing two competing requirements:

1. Bridgewater's need to protect proprietary code
2. Our need to observe and improve the optimization process through Icarus

## Current Challenge

Our existing system requires full access to codebases to perform optimizations. This works well for open-source projects but presents challenges for companies with proprietary code. The key challenge is enabling effective optimization while limiting code exposure.

## Proposed Solution

### Core Architecture

1. **Self-Contained Optimization Package**

   - Debian package containing optimization logic
   - Similar to GitHub's self-hosted runners: runs on client infrastructure but maintains connection to our systems
   - Only requires access to:
     - code segments targeted for optimization
     - benchmark execution environment (e.g., CI/CD pipeline)
     - external AI APIs (includes internet connectivity and API keys)
   - Potentially use Dagger for CI/CD integration, providing a standardized way to:
     - Execute benchmarks
     - Validate optimizations
     - Report results

2. **Telemetry via Icarus**
   - Uses our existing Icarus system for monitoring agent behavior
   - Primary option: Store traces in Firebase (our current solution)
   - Alternative: Configure Icarus to use client-preferred storage (e.g., AWS services)
     - Note: Custom storage solutions require significant engineering effort

### Possible Workflow

1. Trigger:

   - Client creates Jira/GitLab issue identifying code to optimize
   - Issue webhook notifies optimization package

2. Optimization Process:

   - Package receives optimization request
   - Agent analyzes code segment
   - Agent runs benchmarks through client's CI/CD
   - Agent proposes and validates optimizations
   - Results recorded in Icarus

3. Monitoring:
   - All agent actions visible in Icarus
   - Benchmark results and improvements tracked
   - Error states captured for debugging

## Core Trade-off

The key challenge is balancing client code privacy with our ability to improve the optimization process. Our solution:

- Runs optimization logic within client infrastructure, protecting proprietary code
- Uses Icarus for monitoring agent behavior, which is essential for:
  - Debugging issues when optimizations fail or underperform
  - Understanding common optimization patterns
  - Improving the agent's decision-making process
  - Developing better optimization strategies that benefit all users

This approach allows clients to maintain full control of their code while giving us the insights needed to continuously improve the optimization capabilities - both for the specific client and for the product as a whole.

If needed, we can:

- Implement trace redaction for sensitive information
- Configure TTL-based retention policies
- Use client-preferred storage solutions

## Questions for Bridgewater

1. Is a Debian package acceptable as the distribution mechanism for our optimization logic?
2. Can we store agent traces in Firebase, or do you require an alternative storage solution?
3. What restrictions exist around what code can be included in traces viewed through Icarus?
4. Would a self-hosted runner approach similar to GitHub's CI/CD system align with your security requirements?
