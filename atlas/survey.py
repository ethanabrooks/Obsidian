import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib.lines as mlines # Import for creating line handles

# Raw data
queries = [
    "gpt4o version?",
    "GenerationParams test?",
    "dromeus --model dir structure?",
    "grob cleanup affect lepton?",
    "Cause of missing sequence file?"
]

times_data = {
    'Cursor': [35, 60, 76, 35, 41],
    'Claude Code': [29, 26, 58, 15, 58],
    'Cline': [69, 155, 94, 45, 70],
    'Agentless': [76, 84, 86, 75, 90]
}

correctness_data = {
    'Cursor': [True, False, True, True, False],
    'Claude Code': [True, True, True, True, True],
    'Cline': [True, True, True, True, True],
    'Agentless': [True, True, True, False, False]
}

models = ['Cursor', 'Claude Code', 'Cline', 'Agentless']

# Restructure data into a long format DataFrame
data: list[dict[str, str | int | bool]] = []
for i, query in enumerate(queries):
    for model in models:
        data.append({
            'Agent': model,
            'Query': query,
            'Time (s)': times_data[model][i],
            'Correct': correctness_data[model][i]
        })

df_long = pd.DataFrame(data)

# Define colors for models and markers for correctness
model_colors = {
    'Cursor': '#3498db',
    'Claude Code': '#2ecc71',
    'Cline': '#9b59b6',
    'Agentless': '#e74c3c'
}
correctness_markers = {True: 'o', False: 'X'}

# Plotting
plt.figure(figsize=(14, 8))
ax = plt.gca() # Get current axes

# 1. Plot the lines connecting points for each model
sns.lineplot(
    data=df_long,
    x='Query',
    y='Time (s)',
    hue='Agent',
    palette=model_colors,
    legend=False, # We'll create a combined legend later
    markers=False, # Don't draw markers on the lines themselves
    dashes=False,
    linewidth=1.5,
    ax=ax
)

# 2. Overlay a scatter plot to add markers indicating correctness
sns.scatterplot(
    data=df_long,
    x='Query',
    y='Time (s)',
    hue='Agent',          # Color points by model (matches lines)
    style='Correct',      # Use different markers for True/False
    palette=model_colors,
    markers=correctness_markers,
    s=150,                # Size of the markers
    legend=False,         # Disable scatterplot legend, create manually
    ax=ax
)


plt.title('Query Response Time and Correctness Across Agents', fontsize=16)
plt.ylabel('Response Time (seconds)')
plt.xlabel('Query')
plt.xticks(rotation=15, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# --- Manual Legend Creation ---
# Create line handles for Agents
agent_handles = [mlines.Line2D([], [], color=model_colors[agent], marker=None,
                              linestyle='-', linewidth=1.5, label=agent)
                 for agent in models]

# Create marker handles for Correctness (using black for generic marker representation)
correct_handles = [mlines.Line2D([], [], color='black', marker=marker, linestyle='None',
                                markersize=10, label=str(correct)) # Label is 'True' or 'False'
                   for correct, marker in correctness_markers.items()]

# Combine handles and labels
handles = agent_handles + correct_handles
labels = [h.get_label() for h in handles]

# Add titles for legend sections manually is tricky, use a combined title
ax.legend(handles=handles, labels=labels, title='Agent / Correctness',
          bbox_to_anchor=(1.05, 1), loc='upper left')
# --- End Manual Legend Creation ---


plt.tight_layout(rect=[0, 0, 0.85, 1]) # Adjust layout to make space for legend
plt.savefig('survey.png', dpi=300)
