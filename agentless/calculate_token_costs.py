def calculate_token_costs() -> dict[str, dict[str, float]]:
    models = {
        "gpt4-2024": {
            "input_regular": 0.0025,  # $2.50 per 1M tokens
            "input_cached": 0.00125,  # $1.25 per 1M tokens
            "input_batch": 0.00125,   # $1.25 per 1M tokens
            "output_regular": 0.01,    # $10 per 1M tokens
            "output_batch": 0.005,     # $5 per 1M tokens
        },
        "claude35": {
            "input_regular": 0.003,    # $0.003 per 1K tokens = $3 per 1M
            "input_cached": 0.0003,    # $0.0003 per 1K tokens
            "input_batch": 0.0015,     # $0.0015 per 1K tokens
            "output_regular": 0.015,   # $0.015 per 1K tokens = $15 per 1M
            "output_batch": 0.0075,    # $0.0075 per 1K tokens
        }
    }
    return models

def print_costs(models: dict[str, dict[str, float]]) -> None:
    for model, costs in models.items():
        print(f"\n{model} costs per token:")
        print(f"Regular input: ${costs['input_regular']:.6f}")
        print(f"Cached input: ${costs['input_cached']:.6f}")
        print(f"Batch input: ${costs['input_batch']:.6f}")
        print(f"Regular output: ${costs['output_regular']:.6f}")
        print(f"Batch output: ${costs['output_batch']:.6f}")

if __name__ == "__main__":
    models = calculate_token_costs()
    print_costs(models)
