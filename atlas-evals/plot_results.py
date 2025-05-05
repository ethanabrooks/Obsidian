import json
import pathlib
import csv  # Import csv module

import matplotlib.pyplot as plt
import numpy as np  # Import numpy for arranging bars

# Define types
RubricResults = dict[str, bool]
QuestionResults = dict[str, RubricResults]
ModelCounts = dict[str, int]  # e.g., {'true': 10, 'false': 5}
ProcessedData = dict[
    str, dict[str, ModelCounts]
]  # {question: {model: {'true': T, 'false': F}}}
TinaCorrectMap = dict[int, bool]  # {question_id: is_correct}


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


def load_tina_correctness(file_path: pathlib.Path) -> TinaCorrectMap:
    """Loads Tina correctness data from a CSV file."""
    correctness_map: TinaCorrectMap = {}
    if not file_path.exists():
        print(
            f"Warning: Tina eval file not found: {file_path}. No outlines will be added."
        )
        return correctness_map

    print(f"Processing Tina eval file: {file_path}...")
    try:
        with file_path.open("r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Check if essential columns exist and have values
                    if (
                        "question_id" in row
                        and row["question_id"]
                        and "tina_correct" in row
                        and row["tina_correct"]
                    ):
                        q_id = int(row["question_id"])
                        # Convert 'TRUE'/'FALSE' (case-insensitive) to boolean
                        is_correct = row["tina_correct"].strip().upper() == "TRUE"
                        correctness_map[q_id] = is_correct
                    # else: skip row if missing key data
                except (ValueError, KeyError) as e:
                    print(
                        f"Warning: Skipping row in {file_path} due to parsing error: {e} - Row: {row}"
                    )
    except Exception as e:
        print(f"Error reading Tina eval file {file_path}: {e}")

    return correctness_map


def plot_grouped_stacked_results(
    data: ProcessedData,
    questions: list[str],
    models: list[str],
    tina_correct_map: TinaCorrectMap,
) -> None:
    """Plots results grouped by model, with questions as bars within groups."""
    n_questions = len(questions)
    n_models = len(models)

    # Prepare data: shape (n_models, n_questions)
    false_counts = np.zeros((n_models, n_questions))
    true_counts = np.zeros((n_models, n_questions))

    for question_index, question in enumerate(questions):
        for model_index, model in enumerate(models):
            if model in data.get(question, {}):
                counts = data[question][model]
                false_counts[model_index, question_index] = counts.get("false", 0)
                true_counts[model_index, question_index] = counts.get("true", 0)

    # Plotting setup
    total_bars = n_models * n_questions
    bar_width = 0.8  # Width relative to space for one bar
    group_gap = 0.2  # Gap between model groups (relative to bar width)
    # index variable removed as it was unused

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

    # Create figure and axes - Remove unused fig variable
    _fig, ax = plt.subplots(
        figsize=(8 + total_bars * 0.3, 8)
    )  # Dynamic width based on total bars

    # Plot bars using calculated positions
    for bar_idx, abs_pos in enumerate(bar_positions):
        # Determine model and question index for this specific bar
        model_idx = bar_idx // n_questions
        question_idx = bar_idx % n_questions

        # Check Tina correctness for this question index
        is_tina_correct = tina_correct_map.get(question_idx, False)
        bar_kwargs = {}
        if is_tina_correct:
            bar_kwargs = dict(
                edgecolor="lime", linewidth=4, zorder=10
            )  # Use lime green, bring to front

        # Get counts for this specific bar
        f_count = flat_false_counts[bar_idx]
        t_count = flat_true_counts[bar_idx]

        # Stacked bars: plot 'false' (red) first, then 'true' (blue) on top
        ax.bar(
            abs_pos,  # Plot one bar at a time
            f_count,
            bar_width,
            color="red",
            label="Failed" if bar_idx == 0 else "_nolegend_",  # Label only once
            alpha=0.7,
            **bar_kwargs,  # Apply outline if tina_correct
        )
        ax.bar(
            abs_pos,  # Plot one bar at a time
            t_count,
            bar_width,
            bottom=f_count,
            color="blue",
            label="Passed" if bar_idx == 0 else "_nolegend_",  # Label only once
            alpha=0.7,
            **bar_kwargs,  # Apply outline if tina_correct
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
    # Add entry for Tina Correct outline if any exist
    if any(tina_correct_map.values()):
        from matplotlib.lines import Line2D

        tina_handle = Line2D([0], [0], color="lime", lw=1.5, label="Tina Correct")
        # Insert Tina handle/label before others or at the end
        # unique_labels['Tina Correct'] = tina_handle # Alternative: add to dict
        existing_handles = list(unique_labels.values())
        existing_labels = list(unique_labels.keys())
        ax.legend(
            handles=[tina_handle] + existing_handles,
            labels=["Tina Correct"] + existing_labels,
            title="Rubric Status",
        )
    else:
        ax.legend(unique_labels.values(), unique_labels.keys(), title="Rubric Status")

    # --- Question Text Annotation Removed ---

    plt.tight_layout()  # Use default layout adjustment
    plt.savefig("plot.png")


def main() -> None:
    """Main function to load data and generate plot."""
    # Script is inside atlas-evals, so data files are in the current dir
    data_dir = pathlib.Path(".")  # Current directory
    model_files: dict[str, pathlib.Path] = {
        "Claude Code": data_dir / "claude-code-results.json",
        "Full Context": data_dir / "full-context-results.json",
        "RAGrep": data_dir / "ragrep-results.json",
    }
    tina_eval_file = data_dir / "tina-eval.csv"

    processed_data, questions, models = load_all_results(model_files)
    tina_correct_map = load_tina_correctness(tina_eval_file)

    if not processed_data or not questions:
        print("Error: No valid data found to plot.")
        return

    print("Generating plot...")
    plot_grouped_stacked_results(processed_data, questions, models, tina_correct_map)
    print("Plot displayed.")


if __name__ == "__main__":
    main()
