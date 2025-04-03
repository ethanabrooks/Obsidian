# AI GitHub Issue Synthesis Experiment - Summary

## Problem & Motivation

A key limitation to the scale of our data pipeline is the requirement for each PR that we train on to have an associated GitHub issue. One approach to potentially overcome this hurdle is to synthesize plausible GitHub Issues for PRs that lack them.
This experiment explores the feasibility of using AI for this synthesis task. We investigated whether an AI model could generate relevant issue titles and bodies using information from a PR, primarily its code diff.

## Goal of this Document

While the ultimate measure of success for this synthetic data is improved performance on our benchmark "Verified" dataset, this document serves as an initial qualitative "vibe check". We present several examples of AI-synthesized issues alongside the code diffs that prompted them. This allows colleagues to assess the realism and relevance of the generated text. The full system prompt and example LLM prompts used are included in the appendix for context.
