#!/usr/bin/env python3

import argparse
import asyncio
import logging
import os
import sys
from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import TypedDict, Optional
import json

import github
import pydantic_ai
from github import Github
from github.Issue import Issue
from github.IssueComment import IssueComment
from github.PaginatedList import PaginatedList
from rich.logging import RichHandler
import pydantic

# --- Constants ---

DEFAULT_MODEL_ID: str = "openai:o1"
DEFAULT_REPO: str = "pytorch/pytorch"
DEFAULT_MAX_ISSUES: int = 100
# Limit concurrent API calls to avoid rate limits/overload
# This will be updated by args if --concurrency is used
max_concurrent_assessments: int = 10
ASSESSMENT_PROMPT: str = """
Issue Title: {title}
Issue Body:
{body}

--- Potential Answer Comment(s) ---
{answer_text}
--- End of Comment(s) ---

Consider the following criteria for a "qualifying answer":
1.  **Reference Standard:** Is the answer clear and complete enough to verify other potential answers to the same issue?
2.  **Code-Based & Static:** Is the answer derivable *solely* from analyzing source code, without running code or tests or checking external states (like CI results)?

Based *only* on the text provided in "Potential Answer Comment(s)", does it meet BOTH criteria for a qualifying answer to the issue described?
Respond with only 'true' or 'false'.
"""

# --- Setup ---

logging.basicConfig(
    level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")


# --- Data Models ---


class Answer(pydantic.BaseModel):
    """Structured assessment of whether comments answer an issue."""

    in_what_way_question_is_answered_or_not: str = pydantic.Field(
        description="Explain whether the comment(s) meet the criteria (Reference Standard AND Code-Based/Static). If not, explain why."
    )
    answer_summary: Optional[str] = pydantic.Field(
        default=None,
        description="If BOTH criteria are met, provide a concise summary of the answer derived from the comment(s). Otherwise, leave this as null.",
    )


class AssessedIssue(TypedDict):
    """Structure to hold assessment results."""

    url: str
    title: str
    assessment: Optional[Answer]
    issue_body: Optional[str]
    answer_text: Optional[str]


# --- LLM Assessment ---


def _create_llm_agent() -> pydantic_ai.Agent[None, Answer]:
    """Initializes the LLM agent for answer assessment."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        log.error(
            "ANTHROPIC_API_KEY environment variable not set. Please set it to your Anthropic API key."
        )
        sys.exit(1)

    # Configure the underlying litellm client for Anthropic
    # Note: pydantic_ai might use litellm defaults; explicitly setting model and key.
    # Removed setting pydantic_ai.llm_config = {...} as it might conflict with Agent internal config

    return pydantic_ai.Agent[None, Answer](
        # The model ID is now often passed via llm_config or during run,
        # but let's keep it here for clarity if pydantic_ai supports it directly.
        # If error, move model_id config solely into llm_config.
        # DEFAULT_MODEL_ID, # Removed based on user feedback/pydantic_ai usage
        DEFAULT_MODEL_ID,
        system_prompt=(
            "You are assessing GitHub issue comments to determine if they provide a definitive, code-based answer, conforming to the provided JSON schema."
            "A qualifying answer must satisfy two criteria: "
            "1. Reference Standard: It must be clear and complete enough to verify the correctness of other potential answers. "
            "2. Code-Based & Static: It must be derivable *solely* from analyzing the code in the codebase, without requiring code execution, tests, or external state checks (like CI). "
            "Focus ONLY on the provided comment text. "
            "Respond using the JSON schema, providing an explanation in 'in_what_way_question_is_answered_or_not'. "
            "Provide a summary in 'answer_summary' ONLY IF BOTH criteria are met, otherwise leave 'answer_summary' as null."
        ),
        instrument=False,  # Keep output clean
        result_type=Answer,
        # Explicitly set parsing model if needed, assuming it uses llm_config otherwise
        # parsing_model_id=DEFAULT_MODEL_ID,
    )


async def _assess_answer(
    agent: pydantic_ai.Agent[None, Answer],
    issue_title: str,
    issue_body: str | None,
    answer_text: str,
) -> Answer | None:
    """Uses the LLM agent to assess if the provided text answers an issue."""
    try:
        prompt = ASSESSMENT_PROMPT.format(
            title=issue_title,
            body=issue_body or "No body provided.",
            answer_text=answer_text,
        )
        result = await agent.run(prompt)
        log.debug(f"Assessment for '{issue_title}': {result.data}")
        return result.data
    except Exception as e:
        # Include issue title for better error tracking
        log.error(f"Error assessing issue '{issue_title}': {e}")
        # Consider how to handle assessment errors; returning None might skew results.
        # Could return None or raise to signal failure. Defaulting to None for now.
        return None


# --- GitHub Interaction ---


def _create_github_client() -> Github:
    """Initializes the GitHub client."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        log.warning(
            "GITHUB_TOKEN environment variable not set. Using anonymous access (may be rate-limited)."
        )
        return Github()
    else:
        log.info("Using GitHub token for authenticated access.")
        return Github(token)


def _get_closed_issues(gh: Github, repo_name: str, limit: int) -> Iterator[Issue]:
    """Fetches closed issues (not PRs) from the specified repository, yielding them."""
    # Exclude issues with the 'module: flaky-tests' label
    query = f'repo:{repo_name} is:issue is:closed -label:"module: flaky-tests"'
    log.info(f"Searching for issues matching query: '{query}' (limit {limit})...")

    try:
        # Use search_issues for label filtering, sort by updated time
        issues_result = gh.search_issues(query=query, sort="updated", order="desc")

        count = 0
        # PaginatedList needs iteration; respect the limit
        for issue in issues_result:
            if count >= limit:
                log.info(f"Reached limit of {limit} issues.")
                break
            # Double-check it's not a PR (search should handle is:issue, but belt-and-suspenders)
            if not hasattr(issue, "pull_request") or issue.pull_request is None:
                yield issue
                count += 1
            else:
                # This case should be rare with 'is:issue' in query
                log.debug(
                    f"Skipping unexpected PR found in issue search: {issue.html_url}"
                )

        if count == 0:
            log.warning(
                f"No closed issues (non-PR, non-flaky-test) found matching criteria in {repo_name}."
            )

    except github.GithubException as e:
        log.error(f"GitHub API error fetching issues: {e}")
        # Propagate the error or return empty? Returning empty for graceful degradation.
        return iter([])
    except Exception as e:
        log.error(f"Unexpected error fetching issues: {e}")
        return iter([])


def _get_potential_answer_text(issue: Issue) -> str | None:
    """
    Fetches the last two comments of an issue, concatenates them, and returns the text.
    Returns None if no comments are found.
    """
    try:
        # Fetch comments (API doesn't support sorting by creation desc directly)
        comments_paginated: PaginatedList[IssueComment] = issue.get_comments()

        if comments_paginated.totalCount == 0:  # type: ignore[attr-defined]
            log.debug(f"No comments found for issue {issue.number}.")
            return None

        # Convert to list to easily get the last elements. This loads all comments.
        # For issues with extreme comment counts, this could be memory-intensive.
        # Alternative: iterate through pages backwards if PyGithub supported it easily,
        # or use .get_page(last_page_index) but calculating last_page_index is needed.
        all_comments: list[IssueComment] = list(comments_paginated)

        if not all_comments:
            # Should not happen if totalCount > 0, but defensively check.
            log.warning(
                f"Comment totalCount > 0 but list conversion yielded empty for issue {issue.number}"
            )
            return None

        # Get the last 1 or 2 comments from the full list
        last_comments = all_comments[-2:]

        if len(last_comments) == 1:
            log.debug(f"Found 1 comment for issue {issue.number}.")
            # Type checker might complain about accessing .body if IssueComment type hints are incomplete
            return f"Last comment:\n{last_comments[0].body}"
        elif len(last_comments) == 2:
            log.debug(f"Found 2 comments for issue {issue.number}.")
            # last_comments[0] is second-to-last, last_comments[1] is the last
            return (
                f"Last comment:\n{last_comments[1].body}\n\n"
                f"---\nSecond-to-last comment:\n{last_comments[0].body}"
            )
        # Should not be reachable if all_comments was not empty
        return None

    except github.GithubException as e:
        log.error(f"GitHub API error fetching comments for issue {issue.number}: {e}")
        return None
    except Exception as e:
        # Catching broad Exception is generally discouraged, but useful here for robustness.
        log.error(f"Unexpected error fetching comments for issue {issue.number}: {e}")
        return None


# --- Main Orchestration ---


async def _process_single_issue(
    issue: Issue, agent: pydantic_ai.Agent[None, Answer], semaphore: asyncio.Semaphore
) -> AssessedIssue | None:
    """Processes a single issue: gets comments, assesses answer, returns result."""
    async with semaphore:
        log.info(f"Processing issue: {issue.html_url}")
        answer_text = _get_potential_answer_text(issue)  # Keeping sync for now

        if not answer_text:
            log.warning(
                f"No potential answer comments found for {issue.html_url}, skipping assessment."
            )
            # Return AssessedIssue with inputs but no assessment
            return AssessedIssue(
                url=issue.html_url,
                title=issue.title,
                assessment=None,
                issue_body=issue.body,
                answer_text=None,
            )

        # Run assessment asynchronously
        assessment_result = await _assess_answer(
            agent, issue.title, issue.body, answer_text
        )
        if assessment_result and assessment_result.answer_summary is not None:
            breakpoint()

        return AssessedIssue(
            url=issue.html_url,
            title=issue.title,
            assessment=assessment_result,  # Store Answer object or None
            issue_body=issue.body,  # Store issue body
            answer_text=answer_text,  # Store concatenated comment text
        )


async def _process_issues_concurrently(
    gh: Github, agent: pydantic_ai.Agent[None, Answer], repo_name: str, max_issues: int
) -> AsyncIterator[AssessedIssue]:
    """Fetches issues and processes them concurrently using a streaming pipeline."""
    semaphore = asyncio.Semaphore(max_concurrent_assessments)
    tasks: set[asyncio.Task[AssessedIssue | None]] = set()
    issues_processed_count = 0
    issues_yielded_count = 0

    # Start fetching issues (synchronously for now, yields one by one)
    issue_iterator = _get_closed_issues(gh, repo_name, max_issues)

    while True:
        # Add new tasks if concurrency limit allows and issues are available
        while len(tasks) < max_concurrent_assessments:
            try:
                issue = next(issue_iterator)
                if issue:
                    task = asyncio.create_task(
                        _process_single_issue(issue, agent, semaphore)
                    )
                    tasks.add(task)
                    issues_processed_count += 1
                else:  # Should not happen with current _get_closed_issues logic unless empty iterator returned
                    break
            except StopIteration:
                # No more issues from the iterator
                log.info("All available issues have been fetched and tasks created.")
                break  # Exit inner while loop
            except Exception as e:
                log.error(f"Error getting next issue: {e}")
                # Decide whether to continue or stop
                break  # Stop adding new tasks on error

        if not tasks:
            # No more issues to fetch and no running tasks left
            break  # Exit outer while loop

        # Wait for any task to complete
        done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            try:
                result = await task
                if result:  # Filter out None results (e.g., issues skipped)
                    yield result
                    issues_yielded_count += 1
            except Exception as e:
                # Log error from the task processing itself
                log.error(f"Error processing an issue task: {e}")
                # Continue processing other tasks

    log.info(
        f"Finished processing. Total issues considered: {issues_processed_count}, Assessed issues yielded: {issues_yielded_count}"
    )


async def main(repo_name: str, max_issues: int, output_file: Path | None) -> None:
    """Main function to orchestrate the issue crawling and assessment."""
    gh = _create_github_client()
    agent = _create_llm_agent()

    # Store all results, categorization happens during reporting/output
    all_results: list[AssessedIssue] = []
    issues_counted = 0

    log.info("Starting concurrent issue processing...")
    async for result in _process_issues_concurrently(gh, agent, repo_name, max_issues):
        issues_counted += 1
        all_results.append(result)
        # Log based on the assessment result
        if result["assessment"] and result["assessment"].answer_summary is not None:
            log.info(
                f"[bold green]Answer Found ({issues_counted}):[/bold green] {result['url']} - {result['assessment'].in_what_way_question_is_answered_or_not[:100]}..."
            )
        else:
            explanation = "Assessment failed or missing."
            if result["assessment"]:
                explanation = result[
                    "assessment"
                ].in_what_way_question_is_answered_or_not
            log.info(
                f"[bold yellow]No Answer Found ({issues_counted}):[/bold yellow] {result['url']} - {explanation[:100]}..."
            )

    log.info("-" * 30)
    # Recalculate counts based on final results
    answered_count = sum(
        1
        for r in all_results
        if r["assessment"] and r["assessment"].answer_summary is not None
    )
    unanswered_count = len(all_results) - answered_count
    log.info(f"Assessment Summary (Processed {issues_counted} issues):")
    log.info(f"  Issues with Qualifying Answers: {answered_count}")
    log.info(f"  Issues without Qualifying Answers: {unanswered_count}")

    if output_file:
        log.info(f"Writing detailed results to {output_file} as JSON Lines...")
        try:
            # Write as JSON Lines (one JSON object per line)
            with output_file.open("w", encoding="utf-8") as f:
                for result in all_results:
                    # Convert Pydantic model to dict for JSON serialization
                    assessment_dict = (
                        result["assessment"].dict() if result["assessment"] else None
                    )
                    # Create dict compatible with JSON Lines
                    output_data = {
                        "url": result["url"],
                        "title": result["title"],
                        "issue_body": result["issue_body"],
                        "answer_text": result["answer_text"],
                        "assessment": assessment_dict,
                    }
                    json.dump(output_data, f)
                    f.write("\n")  # Add newline for JSON Lines format
            log.info("Results written successfully.")
        except IOError as e:
            log.error(f"Failed to write results to {output_file}: {e}")
        except TypeError as e:
            log.error(f"Failed to serialize results to JSON: {e}")  # Catch JSON errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crawl a GitHub repository for closed issues and assess if the last two comments provide a clear answer using an LLM.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-r",
        "--repo",
        type=str,
        default=DEFAULT_REPO,
        help="GitHub repository name (e.g., 'owner/repo').",
    )
    parser.add_argument(
        "-n",
        "--max-issues",
        type=int,
        default=DEFAULT_MAX_ISSUES,
        help="Maximum number of recent closed issues to check.",
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        # Default is now the lowercase variable
        default=max_concurrent_assessments,
        help="Maximum number of concurrent assessments.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Optional file path to save the results.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )

    args = parser.parse_args()

    # Update logging level if verbose flag is set
    if args.verbose:
        log.setLevel(logging.DEBUG)
        log.debug("Verbose logging enabled.")

    # Update global concurrency limit from args
    # Modify the lowercase global variable, not the original constant name
    max_concurrent_assessments = (
        args.concurrency
    )  # This needs to be accessible by the processing function

    try:
        # Pass concurrency limit explicitly if needed, or rely on the global modification
        # For simplicity here, modifying the global constant before calling main.
        asyncio.run(
            main(
                repo_name=args.repo, max_issues=args.max_issues, output_file=args.output
            )
        )
    except KeyboardInterrupt:
        log.info("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        log.exception(f"An unexpected error occurred: {e}")  # Log full traceback
        sys.exit(1)
