import json
import pathlib
import math  # Import math for calculating subplot grid size

import matplotlib.pyplot as plt
import numpy as np  # Import numpy for arranging bars

# Define types
RubricResults = dict[str, bool]
QuestionResults = dict[str, RubricResults]
ModelCounts = dict[str, int]  # e.g., {'true': 10, 'false': 5}
ProcessedData = dict[
    str, dict[str, ModelCounts]
]  # {question: {model: {'true': T, 'false': F}}}


def load_all_results(
    model_files: dict[str, pathlib.Path],
) -> tuple[ProcessedData, list[str], list[str]]:
    """Loads results from multiple JSON files and processes them per question."""
    all_data: ProcessedData = {}
    all_questions_set: set[str] = set()
    models = list(model_files.keys())

    for model_name, file_path in model_files.items():
        if file_path.exists():
            print(f"Processing {file_path}...")
            try:
                data: QuestionResults = json.loads(
                    file_path.read_text(encoding="utf-8")
                )
                for question, rubric_results in data.items():
                    # Handle empty question strings if necessary
                    if not question:
                        question = "[Empty Question]"  # Assign placeholder if needed

                    all_questions_set.add(question)
                    if question not in all_data:
                        all_data[question] = {}

                    true_count = 0
                    false_count = 0
                    # Ensure loop correctly counts false cases
                    for passed in rubric_results.values():
                        if passed:
                            true_count += 1
                        else:
                            false_count += 1

                    # Ensure model entry exists even if counts are zero
                    if model_name not in all_data[question]:
                        all_data[question][model_name] = {"true": 0, "false": 0}

                    all_data[question][model_name]["true"] += true_count
                    all_data[question][model_name]["false"] += false_count

            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from {file_path}")
            except Exception as e:
                print(f"An unexpected error occurred processing {file_path}: {e}")
        else:
            print(f"Warning: File not found for model '{model_name}': {file_path}")

    # Ensure all questions have entries for all models, even if 0 counts
    all_questions = sorted(list(all_questions_set))
    for q in all_questions:
        if (
            q not in all_data
        ):  # Should not happen based on above logic, but defensive check
            all_data[q] = {}
        for m in models:
            if m not in all_data[q]:
                all_data[q][m] = {"true": 0, "false": 0}

    return all_data, all_questions, models


def plot_grouped_stacked_results(
    data: ProcessedData, questions: list[str], models: list[str]
) -> None:
    """Plots the results as a grouped, stacked bar chart."""
    n_questions = len(questions)
    n_models = len(models)

    # Prepare data for plotting
    false_counts = np.zeros((n_questions, n_models))
    true_counts = np.zeros((n_questions, n_models))

    for i, question in enumerate(questions):
        for j, model in enumerate(models):
            # Check if model data exists for the question
            if model in data.get(question, {}):
                counts = data[question][model]
                false_counts[i, j] = counts.get("false", 0)
                true_counts[i, j] = counts.get("true", 0)
            # else: counts remain 0

    # Plotting setup
    bar_width = 0.25  # Width of each individual bar
    index = np.arange(n_questions)  # x locations for the groups

    fig, ax = plt.subplots(figsize=(12 + n_questions * 0.5, 8))  # Dynamic width

    # Plot bars for each model within the groups
    for i, model in enumerate(models):
        # Calculate the x position for this model's bars within each group
        x_pos = index + (i - (n_models - 1) / 2) * bar_width

        # Stacked bars: plot 'false' first, then 'true' on top
        ax.bar(
            x_pos,
            false_counts[:, i],
            bar_width,
            color="red",
            label=f"{model} - Failed"
            if i == 0
            else "_nolegend_",  # Only label once per color
            alpha=0.7,
        )
        ax.bar(
            x_pos,
            true_counts[:, i],
            bar_width,
            bottom=false_counts[:, i],
            color="blue",
            label=f"{model} - Passed"
            if i == 0
            else "_nolegend_",  # Only label once per color
            alpha=0.7,
        )

    # Adding labels and title
    ax.set_xlabel("Question")
    ax.set_ylabel("Number of Rubric Items")
    ax.set_title("Rubric Pass/Fail Counts per Question by Model")
    ax.set_xticks(index)

    # Use shortened question text for labels if too long, or rotate
    xtick_labels = [
        q[:80] + "..." if len(q) > 80 else q for q in questions
    ]  # Truncate long questions
    ax.set_xticklabels(xtick_labels, rotation=45, ha="right")

    # Create a combined legend
    handles, labels = ax.get_legend_handles_labels()
    # Need custom legend handles for stacked groups
    from matplotlib.patches import Patch

    legend_handles = [
        Patch(facecolor="red", alpha=0.7),
        Patch(facecolor="blue", alpha=0.7),
    ]
    legend_labels = ["Failed", "Passed"]
    # Add model info to the legend? Maybe just title and colors are enough.
    # Could add model patches, but might clutter. Let's keep it simple.
    ax.legend(handles=legend_handles, labels=legend_labels, title="Rubric Status")

    plt.tight_layout()
    plt.show()


def main() -> None:
    """Main function to load data and generate plot."""
    # Script is inside atlas-evals, so data files are in the current dir
    data_dir = pathlib.Path(".")  # Current directory
    model_files: dict[str, pathlib.Path] = {
        "Claude Code": data_dir / "claude-code-results.json",
        "Full Context": data_dir / "full-context-results.json",
        "RAGrep": data_dir / "ragrep-results.json",
    }

    processed_data, questions, models = load_all_results(model_files)

    if not processed_data or not questions:
        print("Error: No valid data found to plot.")
        return

    print("Generating plot...")
    plot_grouped_stacked_results(processed_data, questions, models)
    print("Plot displayed.")


if __name__ == "__main__":
    main()
