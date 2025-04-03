# generate_summary.py
import pathlib
import yaml  # type: ignore

INPUT_YAML_PATH = pathlib.Path("synthesized_issues.yaml")
OUTPUT_MD_PATH = pathlib.Path("experiment_summary.md")
MAX_EXAMPLES = 3
MAX_DIFF_LENGTH = 2000  # Adjust as needed (max characters for the diff)


def format_issue(issue_data: dict[str, str] | str) -> str:
    """Formats the synthesized issue dict or string into a Markdown string."""
    if isinstance(issue_data, dict):
        title = issue_data.get("title", "N/A")
        body = issue_data.get("body", "N/A")
        # Perform the replacement *before* the f-string
        formatted_body = body.replace('\n', '\n> ')
        return f"> **Title:** {title}\n>\n> **Body:**\n> {formatted_body}"
    elif isinstance(issue_data, str):
        # Fallback if it's just a string
        # Perform the replacement *before* the f-string here too
        formatted_issue_data = issue_data.replace('\n', '\n> ')
        return f"> {formatted_issue_data}"


def main() -> None:
    """Loads YAML data and generates a Markdown summary."""
    print(f"Loading data from {INPUT_YAML_PATH}...")
    try:
        with open(INPUT_YAML_PATH, 'r') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {INPUT_YAML_PATH}")
        return
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return

    if not isinstance(data, dict) or "system_prompt" not in data or "results" not in data:
        print("Error: YAML structure is not as expected (missing 'system_prompt' or 'results').")
        return

    system_prompt = data.get("system_prompt", "System prompt not found.")
    results = data.get("results", [])

    if not isinstance(results, list) or not results:
        print("Warning: 'results' list is empty or not found.")
        llm_prompt_example = "No results found to extract LLM prompt example."
        selected_examples = []
    else:
        # Extract first llm_prompt as example
        first_result = results[0]
        llm_prompt_example = first_result.get("llm_prompt", "LLM prompt not found in first result.")

        # Select examples with reasonable diff length
        selected_examples = []
        print(f"Selecting up to {MAX_EXAMPLES} examples with diff length <= {MAX_DIFF_LENGTH} chars...")
        for i, result in enumerate(results):
            if len(selected_examples) >= MAX_EXAMPLES:
                break
            diff = result.get("diff", "")
            if diff and len(diff) <= MAX_DIFF_LENGTH:
                selected_examples.append(result)
                print(f"  Selected example {len(selected_examples)} (from result index {i})")
            elif not diff:
                 print(f"  Skipping example from result index {i} (missing diff)")
            else:
                 print(f"  Skipping example from result index {i} (diff length {len(diff)} > {MAX_DIFF_LENGTH})")


    # --- Build Markdown ---
    md_content = f"""# AI GitHub Issue Synthesis Experiment

## Goal

To evaluate the ability of an AI model to synthesize relevant GitHub issue titles and bodies based on code diffs and contextual information.

## Methodology

An AI model was provided with a system prompt and a series of specific prompts (`llm_prompt`) containing code diffs and other context. The model's output (`synthesized_issue`) was recorded. This document summarizes the setup and shows representative examples.

## System Prompt

```yaml
{system_prompt}
```

## LLM Prompt Structure

The prompt provided to the LLM typically included the code diff, repository/PR context, and specific instructions.

<details>
<summary>Click to view full LLM Prompt Example (from first result)</summary>

```yaml
{llm_prompt_example}
```

</details>

## Examples (Input Diff -> Output Issue)

Showing up to {MAX_EXAMPLES} examples where the input diff length is no more than {MAX_DIFF_LENGTH} characters.

"""

    if not selected_examples:
        md_content += "\n*No suitable examples found based on the criteria.*\n"
    else:
        for i, example in enumerate(selected_examples, 1):
            diff = example.get("diff", "Diff not found.")
            synthesized_issue = example.get("synthesized_issue", {"title": "N/A", "body": "Synthesized issue not found."})
            repo = example.get("repository", "N/A")
            pr_info = example.get("pr", "N/A") # Assuming 'pr' might be a number or string

            md_content += f"\n### Example {i} (Repo: {repo}, PR: {pr_info})\n\n"
            md_content += "**Input (Diff):**\n"
            md_content += f"```diff\n{diff}\n```\n\n"
            md_content += "**Output (Synthesized Issue):**\n"
            md_content += f"{format_issue(synthesized_issue)}\n\n"


    # --- Write Markdown File ---
    print(f"Writing summary to {OUTPUT_MD_PATH}...")
    with open(OUTPUT_MD_PATH, 'w') as f:
        f.write(md_content)

    print("Done.")

if __name__ == "__main__":
    main()