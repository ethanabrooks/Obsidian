import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib.lines as mlines  # Import for creating line handles

# Raw data
queries = [
    "gpt4o version?",
    "GenerationParams test?",
    "dromeus --model dir structure?",
    "grob cleanup affect lepton?",
    "Cause of missing sequence file?",
]

times_data = {
    "Cursor": [35, 60, 76, 35, 41],
    "Claude Code": [29, 26, 58, 15, 58],
    "Cline": [69, 155, 94, 45, 70],
    "Agentless": [76, 84, 86, 75, 90],
    "RAGrep": [35, 38, 32, 33, 36],
}

correctness_data = {
    "Cursor": [True, False, True, True, False],
    "Claude Code": [True, True, True, True, True],
    "Cline": [True, True, False, True, True],
    "Agentless": [True, True, True, False, False],
    "RAGrep": [True, True, True, True, True],
}

models = ["Cursor", "Claude Code", "Cline", "Agentless", "RAGrep"]

# Restructure data into a long format DataFrame
data: list[dict[str, str | int | bool]] = []
for i, query in enumerate(queries):
    for model in models:
        data.append(
            {
                "Agent": model,
                "Query": query,
                "Time (s)": times_data[model][i],
                "Correct": correctness_data[model][i],
            }
        )

df_long = pd.DataFrame(data)

# Define colors for models and markers for correctness
model_colors = {
    "Cursor": "#3498db",
    "Claude Code": "#2ecc71",
    "Cline": "#9b59b6",
    "Agentless": "#e74c3c",
    "RAGrep": "#f1c40f",
}
# Map boolean to desired labels and markers
correctness_mapping = {
    True: {"label": "Correct", "marker": "o"},
    False: {"label": "Incorrect", "marker": "X"},
}
correctness_markers = {
    details["label"]: details["marker"] for details in correctness_mapping.values()
}

# Plotting configuration
plt.figure(figsize=(16, 10))  # Slightly larger figure for bigger text
ax = plt.gca()

# Text Size Parameters
TITLE_FONTSIZE = 24
AXIS_LABEL_FONTSIZE = 18
TICK_LABEL_FONTSIZE = 14
LEGEND_TITLE_FONTSIZE = 16
LEGEND_LABEL_FONTSIZE = 14
MARKER_SIZE = 180  # Increased marker size slightly

# 1. Plot the lines connecting points for each model
sns.lineplot(
    data=df_long,
    x="Query",
    y="Time (s)",
    hue="Agent",
    palette=model_colors,
    legend=False,
    markers=False,
    dashes=False,
    linewidth=2,  # Slightly thicker line
    ax=ax,
)

# Add Correct/Incorrect labels to the dataframe for the scatterplot style
df_long["Correctness Label"] = df_long["Correct"].map(
    {True: "Correct", False: "Incorrect"}
)

# 2. Overlay a scatter plot to add markers indicating correctness
sns.scatterplot(
    data=df_long,
    x="Query",
    y="Time (s)",
    hue="Agent",
    style="Correctness Label",
    palette=model_colors,
    markers=correctness_markers,
    s=MARKER_SIZE,  # Use marker size variable
    legend=False,
    ax=ax,
)

# --- Apply Larger Text Sizes ---
plt.title("Query Response Time and Correctness Across Agents", fontsize=TITLE_FONTSIZE)
plt.ylabel("Response Time (seconds)", fontsize=AXIS_LABEL_FONTSIZE)
plt.xlabel("Query", fontsize=AXIS_LABEL_FONTSIZE)

# Increase tick label sizes
plt.xticks(
    rotation=20, ha="right", fontsize=TICK_LABEL_FONTSIZE
)  # Increased rotation slightly
plt.yticks(fontsize=TICK_LABEL_FONTSIZE)

plt.grid(axis="y", linestyle="--", alpha=0.7)

# --- Manual Legend Creation ---
agent_handles = [
    mlines.Line2D(
        [],
        [],
        color=model_colors[agent],
        marker=None,
        linestyle="-",
        linewidth=2,  # Match line thickness
        label=agent,
    )
    for agent in models
]

correct_handles = [
    mlines.Line2D(
        [],
        [],
        color="black",
        marker=details["marker"],
        linestyle="None",
        markersize=12,  # Slightly larger legend marker
        label=details["label"],
    )
    # Iterate using values() if the key (correct_bool) is not needed
    for details in correctness_mapping.values()
]

handles = agent_handles + correct_handles
labels = [h.get_label() for h in handles]

ax.legend(
    handles=handles,
    labels=labels,
    title="Agent / Correctness",
    bbox_to_anchor=(1.04, 1),  # Adjusted anchor slightly
    loc="upper left",
    fontsize=LEGEND_LABEL_FONTSIZE,  # Set legend item font size
    title_fontsize=LEGEND_TITLE_FONTSIZE,  # Set legend title font size
)
# --- End Manual Legend Creation ---


# Adjust layout more aggressively for larger text
plt.tight_layout(rect=(0, 0, 0.83, 0.96))  # Adjusted rect: more space on right and top

plt.savefig(
    "survey_large_text.png", dpi=300, bbox_inches="tight"
)  # Use bbox_inches='tight' for savefig
# plt.show()
