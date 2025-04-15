#!/usr/bin/env python3

import argparse
import asyncio
import logging
import os
import sys
from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import TypedDict

import github
import pydantic_ai
from github import Github
from github.Issue import Issue
from github.IssueComment import IssueComment
from github.PaginatedList import PaginatedList
from rich.logging import RichHandler

# --- Constants ---

DEFAULT_MODEL_ID: str = "anthropic:claude-3-5-sonnet-latest"
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

Based *only* on the text provided in "Potential Answer Comment(s)", does it contain an unambiguous and verifiable answer to the issue described?
Respond with only 'true' or 'false'.
"""

# --- Setup ---

logging.basicConfig(
    level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")


class AssessedIssue(TypedDict):
    """Structure to hold assessment results."""

    url: str
    title: str
    is_answered: bool


# --- LLM Assessment ---


def _create_llm_agent() -> pydantic_ai.Agent[None, bool]:
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

    return pydantic_ai.Agent[None, bool](
        # The model ID is now often passed via llm_config or during run,
        # but let's keep it here for clarity if pydantic_ai supports it directly.
        # If error, move model_id config solely into llm_config.
        # DEFAULT_MODEL_ID, # Removed based on user feedback/pydantic_ai usage
        DEFAULT_MODEL_ID,
        system_prompt=(
            "You are assessing whether the provided comment text contains an answer "
            "to the GitHub issue that is unambiguous and verifiable. "
            "Focus solely on the comment text provided. Respond ONLY with 'true' or 'false'."
        ),
        instrument=False,  # Keep output clean
        result_type=bool,
        # Explicitly set parsing model if needed, assuming it uses llm_config otherwise
        # parsing_model_id=DEFAULT_MODEL_ID,
    )


async def _assess_answer(
    agent: pydantic_ai.Agent[None, bool],
    issue_title: str,
    issue_body: str | None,
    answer_text: str,
) -> bool:
    """Uses the LLM agent to assess if the provided text answers an issue."""
    try:
        prompt = ASSESSMENT_PROMPT.format(
            title=issue_title,
            body=issue_body or "No body provided.",
            answer_text=answer_text,
        )
        result = await agent.run(prompt)
        log.debug(f"Assessment for '{issue_title}': {result}")
        return result.data
    except Exception as e:
        # Include issue title for better error tracking
        log.error(f"Error assessing issue '{issue_title}': {e}")
        # Consider how to handle assessment errors; returning False might skew results.
        # Could return None or raise to signal failure. Defaulting to False for now.
        return False


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
    log.info(
        f"Fetching up to {limit} most recently updated closed issues from {repo_name}..."
    )
    try:
        repo = gh.get_repo(repo_name)
        # Note: PyGithub's get_issues might not directly support complex search queries well.
        # Fetching closed issues sorted by update time is standard. Filtering PRs happens client-side.
        issues = repo.get_issues(state="closed", sort="updated", direction="desc")

        count = 0
        for issue in issues:
            if count >= limit:
                log.info(f"Reached limit of {limit} issues.")
                break
            # Ensure it's an issue, not a pull request
            if not hasattr(issue, "pull_request") or issue.pull_request is None:
                yield issue
                count += 1
            else:
                log.debug(f"Skipping PR: {issue.html_url}")

        if count == 0:
            log.warning(
                f"No closed issues (non-PRs) found matching criteria in {repo_name}."
            )
        else:
            log.info(f"Finished fetching. Found {count} issues to process.")

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
    issue: Issue, agent: pydantic_ai.Agent[None, bool], semaphore: asyncio.Semaphore
) -> AssessedIssue | None:
    """Processes a single issue: gets comments, assesses answer, returns result."""
    async with semaphore:
        log.info(f"Processing issue: {issue.html_url}")
        answer_text = _get_potential_answer_text(issue)  # Keeping sync for now

        if not answer_text:
            log.warning(
                f"No potential answer comments found for {issue.html_url}, skipping assessment."
            )
            # Return None or a specific status? Returning None to filter out later.
            return None

        # Run assessment asynchronously
        is_answered = await _assess_answer(agent, issue.title, issue.body, answer_text)
        breakpoint()

        return AssessedIssue(
            url=issue.html_url, title=issue.title, is_answered=is_answered
        )


async def _process_issues_concurrently(
    gh: Github, agent: pydantic_ai.Agent[None, bool], repo_name: str, max_issues: int
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

    answered_issues: list[AssessedIssue] = []
    unanswered_issues: list[AssessedIssue] = []
    issues_counted = 0

    log.info("Starting concurrent issue processing...")
    async for result in _process_issues_concurrently(gh, agent, repo_name, max_issues):
        issues_counted += 1
        if result["is_answered"]:
            answered_issues.append(result)
            log.info(
                f"[bold green]Answered:[/bold green] ({issues_counted}) {result['url']} - {result['title'][:80]}..."
            )
        else:
            unanswered_issues.append(result)
            log.info(
                f"[bold red]Not Answered:[/bold red] ({issues_counted}) {result['url']} - {result['title'][:80]}..."
            )

    log.info("-" * 30)
    log.info("Assessment Summary (Processed {issues_counted} issues):")
    log.info(f"  Clearly Answered: {len(answered_issues)}")
    log.info(f"  Not Clearly Answered: {len(unanswered_issues)}")

    if output_file:
        log.info(f"Writing results to {output_file}...")
        try:
            # Ensure correct newline handling
            with output_file.open("w", encoding="utf-8") as f:
                f.write("--- Answered Issues ---\n")
                for issue in answered_issues:
                    f.write(f"- {issue['url']} : {issue['title']}\n")
                f.write("\n--- Not Clearly Answered Issues ---\n")
                for issue in unanswered_issues:
                    f.write(f"- {issue['url']} : {issue['title']}\n")
            log.info("Results written successfully.")
        except IOError as e:
            log.error(f"Failed to write results to {output_file}: {e}")


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
