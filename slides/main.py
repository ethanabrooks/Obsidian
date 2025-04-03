# generate_summary.py
import pathlib
import yaml  # type: ignore

INPUT_YAML_PATH = pathlib.Path("synthesized_issues.yaml")
OUTPUT_MD_PATH = pathlib.Path("experiment_summary.md")
MAX_EXAMPLES_TO_SHOW = 5 # How many Issue->Diff pairs to display
MAX_DIFF_LENGTH = 2000  # Max characters for the diff in displayed examples
NUM_LLM_PROMPT_EXAMPLES = 2 # How many LLM prompts for the appendix


def format_issue(issue_data: dict[str, str] | str) -> str:
    """Formats the synthesized issue dict or string into a Markdown string."""
    if isinstance(issue_data, dict):
        title = issue_data.get("title", "N/A")
        body = issue_data.get("body", "N/A")
        formatted_body = body.replace('\n', '\n> ')
        return f"> **Title:** {title}\n>\n> **Body:**\n> {formatted_body}"
    elif isinstance(issue_data, str):
        formatted_issue_data = issue_data.replace('\n', '\n> ')
        return f"> {formatted_issue_data}"
    else:
        # Added handling for unexpected types
        return f"> (Could not format issue data: type {type(issue_data)})"


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
        llm_prompt_examples = ["No results found to extract LLM prompt example."] * NUM_LLM_PROMPT_EXAMPLES
        selected_examples = []
    else:
        # Select examples to show and LLM prompts for appendix
        selected_examples: list[dict] = []
        llm_prompt_examples: list[str] = []
        print(f"Selecting up to {MAX_EXAMPLES_TO_SHOW} examples with diff length <= {MAX_DIFF_LENGTH} chars...")
        print(f"Selecting first {NUM_LLM_PROMPT_EXAMPLES} LLM prompts from suitable examples...")

        llm_prompts_collected = 0
        for i, result in enumerate(results):
            diff = result.get("diff", "")
            llm_prompt = result.get("llm_prompt", "")

            is_suitable_example = diff and len(diff) <= MAX_DIFF_LENGTH

            # Collect LLM prompts for appendix from the first suitable examples
            if is_suitable_example and llm_prompt and llm_prompts_collected < NUM_LLM_PROMPT_EXAMPLES:
                 llm_prompt_examples.append(llm_prompt)
                 llm_prompts_collected += 1
                 print(f"  Collected LLM prompt example {llm_prompts_collected} (from result index {i})")


            # Collect examples to show (Issue -> Diff)
            if is_suitable_example and len(selected_examples) < MAX_EXAMPLES_TO_SHOW:
                selected_examples.append(result)
                print(f"  Selected example {len(selected_examples)} to show (from result index {i})")

            # Stop searching if we have everything we need
            if len(selected_examples) >= MAX_EXAMPLES_TO_SHOW and llm_prompts_collected >= NUM_LLM_PROMPT_EXAMPLES:
                 break

            # Print skip reasons only if we still need examples or prompts
            if len(selected_examples) < MAX_EXAMPLES_TO_SHOW or llm_prompts_collected < NUM_LLM_PROMPT_EXAMPLES:
                if not diff:
                    print(f"  Skipping example from result index {i} (missing diff)")
                elif len(diff) > MAX_DIFF_LENGTH:
                    print(f"  Skipping example from result index {i} (diff length {len(diff)} > {MAX_DIFF_LENGTH})")
                # We don't necessarily skip if llm_prompt is missing, unless needed for appendix

        # Pad LLM prompt examples if fewer than desired were found
        while len(llm_prompt_examples) < NUM_LLM_PROMPT_EXAMPLES:
            llm_prompt_examples.append(f"Suitable LLM prompt example {len(llm_prompt_examples) + 1} not found.")


    # --- Build Markdown ---
    # Use refined introduction text incorporating user comments
    introduction_text = pathlib.Path(__file__).parent.joinpath("intro.md").read_text()

    examples_section = f"""
# Examples (Synthesized Issue -> Corresponding Diff)

Below are up to {MAX_EXAMPLES_TO_SHOW} examples demonstrating the AI's synthesized GitHub issue based on a code diff. Examples are selected where the input diff is no more than {MAX_DIFF_LENGTH} characters.

"""
    if not selected_examples:
        examples_section += "\n*No suitable examples found based on the criteria.*\n"
    else:
        for i, example in enumerate(selected_examples, 1):
            diff = example.get("diff", "Diff not found.")
            try:
                synthesized_issue_formatted = format_issue(example.get("synthesized_issue"))
            except Exception as e:
                synthesized_issue_formatted = f"> Error formatting issue: {e}"

            repo = example.get("repository", "N/A")
            pr_info = example.get("pr", {}) # Default to empty dict if missing

            # --- Format PR info nicely ---
            pr_details_str = "N/A" # Default value
            if isinstance(pr_info, dict):
                pr_number = pr_info.get('number')
                pr_title = pr_info.get('title')
                pr_url = pr_info.get('url')

                if pr_number and pr_title and pr_url:
                    # Format as: #Number: [Title](URL)
                    pr_details_str = f"#{pr_number}: [{pr_title}]({pr_url})"
                elif pr_number and pr_title:
                     # Format as: #Number: Title (if URL missing)
                    pr_details_str = f"#{pr_number}: {pr_title}"
                elif pr_number:
                    # Format as: #Number (if title missing)
                    pr_details_str = f"#{pr_number}"
                elif pr_info: # If dict is not empty but lacks expected keys
                    pr_details_str = str(pr_info) # Fallback to string representation
                # If pr_info was an empty dict initially, it stays "N/A"
            elif pr_info: # If pr_info was provided but wasn't a dict
                 pr_details_str = str(pr_info)
            # --- End PR info formatting ---

            examples_section += f"\n## Example {i} (Repo: {repo}, PR {pr_details_str})\n\n" # Use the formatted string
            examples_section += "**Output (Synthesized Issue):**\n"
            examples_section += f"{synthesized_issue_formatted}\n\n"
            examples_section += "**Input (Diff that generated the above issue):**\n"
            examples_section += f"```diff\n{diff}\n```\n\n"

    appendix_section = f"""
---

# Appendix: Prompts Used

## System Prompt

The overall instruction given to the model:

```yaml
{system_prompt}
```

## LLM Prompt Examples

These are examples of the specific, detailed prompts provided to the model for individual tasks, typically including the code diff and context.

```yaml
{llm_prompt_examples[0].replace("```", "")}
```

```yaml
{llm_prompt_examples[1].replace("```", "")}
```

"""

    # Combine sections using the refined introduction text
    md_content = introduction_text + examples_section + appendix_section

    # --- Write Markdown File ---
    print(f"Writing summary to {OUTPUT_MD_PATH}...")
    with open(OUTPUT_MD_PATH, 'w') as f:
        f.write(md_content)

    print("Done.")

if __name__ == "__main__":
    main()