import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def get_environment_name(collection_name: str) -> str:
    """Map collection name to a readable environment name for the legend."""
    match collection_name:
        case "/swe-bench/swe-agent/run-v2-verified-sonnet6c51a-":
            return "v2"
        case "/swe-bench/swe-agent/no-print-object-source-verified-05d5b4":
            return "v4"
        case "/swe-bench/swe-agent/run-v4-verified-sonnet6c51a-":
            return "v4 with print_object_source"
    raise ValueError(f"Unknown collection name: {collection_name}")


def main() -> None:
    # Read the data
    df = pd.read_csv("verified-scores.csv")
    
    # Create a more readable version of collection names
    df["environment"] = df["collection_name"].apply(get_environment_name)

    # Order environments by overall score (lowest to highest)
    env_order = df.sort_values("grand_mean_score")["environment"].tolist()
    
    # Prepare data for plotting
    plot_data = pd.melt(
        df,
        id_vars=["environment"],
        value_vars=[
            "grand_mean_score",
            "easy_score",
            "medium_score",
            "hard_score",
            "maybe_impossible_score",
        ],
        var_name="difficulty",
        value_name="score",
    )

    # Clean up difficulty labels
    plot_data["difficulty"] = plot_data["difficulty"].apply(
        lambda x: x.replace("_score", "").replace("grand_mean", "overall")
    )

    # Set up the plot style
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")

    # Create the grouped bar chart with ordered environments
    ax = sns.barplot(
        x="difficulty", 
        y="score", 
        hue="environment", 
        data=plot_data, 
        palette="viridis",
        hue_order=env_order  # Order from lowest to highest overall score
    )

    # Add labels and title
    plt.title("SWE-Bench Environment Performance Comparison", fontsize=16)
    plt.xlabel("Difficulty Level", fontsize=14)
    plt.ylabel("Score (%)", fontsize=14)
    plt.ylim(0, 105)  # Set y-axis to go from 0 to 105 to give some space above 100

    # Add value labels on top of bars
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f", fontsize=10)

    # Improve legend
    plt.legend(title="Environment", fontsize=12)

    # Add a note about confidence intervals
    ci_text = "Note: Overall scores shown with 95% CI: "
    for i, env in enumerate(env_order):
        if i > 0:
            ci_text += " and "
        row = df[df["environment"] == env].iloc[0]
        if "ci_95_lower_bound" in row and "ci_95_upper_bound" in row:
            ci_text += f"{env}: {row['ci_95_lower_bound']:.2f}-{row['ci_95_upper_bound']:.2f}"
        else:
            ci_text += f"{env}: CI not available"
    
    plt.figtext(
        0.5,
        0.01,
        ci_text,
        ha="center",
        fontsize=10,
    )

    # Save the figure
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig("score_comparison.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    main()
