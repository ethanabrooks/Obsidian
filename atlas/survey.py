import matplotlib

# --- Force Agg Backend BEFORE importing pyplot ---
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib.lines as mlines  # Import for creating line handles

# --- Text Size Parameters (Increased Significantly) ---
TITLE_FONTSIZE = 28
AXIS_LABEL_FONTSIZE = 22
TICK_LABEL_FONTSIZE = 18
LEGEND_TITLE_FONTSIZE = 20
LEGEND_LABEL_FONTSIZE = 18
MARKER_SIZE = 200
LINE_WIDTH = 2.5
LEGEND_MARKER_SIZE = 14

# --- Update rcParams (Keep this as a baseline) ---
matplotlib.rcParams.update(
    {
        "figure.titlesize": TITLE_FONTSIZE,
        "axes.titlesize": TITLE_FONTSIZE,
        "axes.labelsize": AXIS_LABEL_FONTSIZE,
        "xtick.labelsize": TICK_LABEL_FONTSIZE,
        "ytick.labelsize": TICK_LABEL_FONTSIZE,
        "legend.fontsize": LEGEND_LABEL_FONTSIZE,
        "legend.title_fontsize": LEGEND_TITLE_FONTSIZE,
        "figure.dpi": 150,  # Increase base DPI slightly
    }
)
# --- End rcParams Update ---

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
plt.figure(figsize=(18, 12))  # Increased figure size further
ax = plt.gca()

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
    linewidth=LINE_WIDTH,
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
    s=MARKER_SIZE,
    legend=False,
    ax=ax,
)

# --- Apply Larger Text Sizes ---
plt.title("Query Response Time and Correctness Across Agents", fontsize=TITLE_FONTSIZE)
plt.ylabel("Response Time (seconds)", fontsize=AXIS_LABEL_FONTSIZE)
plt.xlabel("Query", fontsize=AXIS_LABEL_FONTSIZE)

# Increase tick label sizes
plt.xticks(rotation=25, ha="right", fontsize=TICK_LABEL_FONTSIZE)
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
        linewidth=LINE_WIDTH,
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
        markersize=LEGEND_MARKER_SIZE,
        label=details["label"],
    )
    for details in correctness_mapping.values()
]

handles = agent_handles + correct_handles
labels = [h.get_label() for h in handles]

# Adjust legend properties
ax.legend(
    handles=handles,
    labels=labels,
    title="Agent / Correctness",
    bbox_to_anchor=(1.03, 1),
    loc="upper left",
    fontsize=LEGEND_LABEL_FONTSIZE,
    title_fontsize=LEGEND_TITLE_FONTSIZE,
)
# --- End Manual Legend Creation ---

# Adjust layout even more aggressively for larger text
plt.tight_layout(rect=(0.02, 0.02, 0.82, 0.95))

plt.savefig("survey_large_text_v2.png", dpi=300, bbox_inches="tight")
# plt.show()

# --- Reset rcParams if needed ---
# If running other plots later in the same script, you might want to reset
# matplotlib.rcParams.update(matplotlib.rcParamsDefault)
