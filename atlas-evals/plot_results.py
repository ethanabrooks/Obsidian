import json
import pathlib

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
    """Plots results grouped by model, with questions as bars within groups."""
    n_questions = len(questions)
    n_models = len(models)

    # Prepare data: shape (n_models, n_questions)
    false_counts = np.zeros((n_models, n_questions))
    true_counts = np.zeros((n_models, n_questions))

    for j, question in enumerate(questions):
        for i, model in enumerate(models):
            if model in data.get(question, {}):
                counts = data[question][model]
                false_counts[i, j] = counts.get("false", 0)
                true_counts[i, j] = counts.get("true", 0)

    # Plotting setup
    total_bars = n_models * n_questions
    bar_width = 0.8  # Width relative to space for one bar
    group_gap = 0.2  # Gap between model groups (relative to bar width)
    index = np.arange(total_bars)  # Absolute index for each bar

    # Calculate positions accounting for gaps
    bar_indices_within_group = np.arange(n_questions)
    group_centers = np.arange(n_models) * (n_questions + group_gap)
    # Bar positions: start of group + index within group
    bar_positions = np.concatenate(
        [group_centers[i] + bar_indices_within_group for i in range(n_models)]
    )

    # Flatten data for plotting
    flat_false_counts = false_counts.flatten()
    flat_true_counts = true_counts.flatten()

    fig, ax = plt.subplots(
        figsize=(8 + total_bars * 0.3, 8)
    )  # Dynamic width based on total bars

    # Plot bars using calculated positions
    # Stacked bars: plot 'false' (red) first, then 'true' (blue) on top
    ax.bar(
        bar_positions,
        flat_false_counts,
        bar_width,
        color="red",
        label="Failed",
        alpha=0.7,
    )
    ax.bar(
        bar_positions,
        flat_true_counts,
        bar_width,
        bottom=flat_false_counts,
        color="blue",
        label="Passed",
        alpha=0.7,
    )

    # --- X-axis Labeling ---
    # Major ticks: Model names at the center of each group
    ax.set_xticks([center + (n_questions - 1) / 2 for center in group_centers])
    ax.set_xticklabels(models)
    ax.tick_params(axis="x", which="major", pad=15)  # Pad major labels down

    # Minor ticks: Question numbers centered under each bar
    ax.set_xticks(bar_positions, minor=True)
    question_labels = [str(i + 1) for i in range(n_questions)] * n_models
    ax.set_xticklabels(question_labels, minor=True)
    ax.tick_params(axis="x", which="minor", labelsize=8)  # Smaller font for numbers

    # Y-axis and Title
    ax.set_ylabel("Number of Rubric Items")
    ax.set_title("Rubric Pass/Fail Counts by Model (Questions Numbered Within Groups)")

    # --- Legend ---
    # Get unique handles/labels for color legend
    handles, labels = plt.gca().get_legend_handles_labels()
    # Keep only unique labels (Passed, Failed)
    from collections import OrderedDict

    unique_labels = OrderedDict(zip(labels, handles))
    ax.legend(unique_labels.values(), unique_labels.keys(), title="Rubric Status")

    # --- Question Text Annotation ---
    question_text = "\n".join(
        [
            f"{i + 1}: {q[:100]}{'...' if len(q) > 100 else ''}"
            for i, q in enumerate(questions)
        ]
    )
    # Add text below the plot
    fig.text(
        0.5,
        0.01,
        f"Questions:\n{question_text}",
        ha="center",
        va="bottom",
        fontsize=8,
        wrap=True,
    )

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])  # Adjust layout for annotation/title
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
