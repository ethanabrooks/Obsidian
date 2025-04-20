from pydantic import BaseModel, TypeAdapter, Field
import argparse
import sys
from pathlib import Path
import yaml

# Import necessary components from the calculation script
from travel_chooser import (
    TerminalData,
    TravelOption,
    CalculatedCosts,  # Import the new type
    load_terminals,
    calculate_costs,  # Use the function that returns costs
)

# Rich is now assumed to be installed for formatted output
from rich.console import Console
from rich.table import Table
# from rich.text import Text # Not currently used


# --- Pydantic Models for Input Options File Validation ---
class InputOptionModel(BaseModel):
    name: str
    terminal: str
    return_terminal: str | None = None
    cost: float = Field(..., ge=0.0)
    duration: int = Field(..., ge=0)
    hassle: float = Field(default=0.0, ge=0.0)


InputOptionsConfig = TypeAdapter(list[InputOptionModel])


# --- Functions ---


def load_options_file(filepath: Path) -> list[InputOptionModel]:  # Use lowercase list
    """Loads and validates the list of travel options from a YAML file."""
    with open(filepath, "r") as f:
        raw_data = yaml.safe_load(f)
        # Ensure raw_data is a dictionary with the 'options' key
        validated_config = InputOptionsConfig.validate_python(raw_data)
        return validated_config


def create_full_travel_option(
    input_option: InputOptionModel,
    terminals: dict[str, TerminalData],
    arrival_buffer: int,
) -> TravelOption | None:
    """Creates a full TravelOption object from input data and terminal info."""
    dep_terminal_name = input_option.terminal
    ret_terminal_name = (
        input_option.return_terminal
        if input_option.return_terminal
        else dep_terminal_name
    )

    if dep_terminal_name not in terminals:
        print(
            f"Error: Departure terminal '{dep_terminal_name}' for option '{input_option.name}' not found in terminals data.",
            file=sys.stderr,
        )
        return None

    if ret_terminal_name not in terminals:
        print(
            f"Error: Return terminal '{ret_terminal_name}' for option '{input_option.name}' not found in terminals data.",
            file=sys.stderr,
        )
        return None

    dep_terminal_info = terminals[dep_terminal_name]
    ret_terminal_info = terminals[ret_terminal_name]

    # Create a temporary instance (as in travel_chooser)
    temp_option = TravelOption(
        option_name=input_option.name,
        terminal_name=dep_terminal_name,
        round_trip_journey_cost=input_option.cost,
        round_trip_journey_duration_min=input_option.duration,
        round_trip_general_hassle=input_option.hassle,
        dep_fixed_travel_hassle=0.0,
        return_terminal_name="",
        ret_fixed_travel_hassle=0.0,
    )

    # Populate the rest from terminal data
    final_option = temp_option._replace(
        dep_travel_time_min=dep_terminal_info.travel_time_min,
        dep_travel_cost=dep_terminal_info.travel_cost,
        dep_fixed_travel_hassle=dep_terminal_info.travel_hassle_cost,
        dep_buffer_min=dep_terminal_info.departure_buffer_min,
        return_terminal_name=ret_terminal_name,
        ret_travel_time_min=ret_terminal_info.travel_time_min,
        ret_travel_cost=ret_terminal_info.travel_cost,
        ret_fixed_travel_hassle=ret_terminal_info.travel_hassle_cost,
        arr_buffer_min=arrival_buffer,
    )
    return final_option


# --- Main Execution ---
def main(args: argparse.Namespace) -> None:
    """Loads data, processes options, calculates costs, compares, and prints."""
    console = Console()

    terminals_file_path = Path(args.terminals_file)
    options_file_path = Path(args.options_file)

    # Load static terminal data
    terminals = load_terminals(terminals_file_path)

    # Load options to compare from input file
    input_options = load_options_file(options_file_path)

    # Process each option
    all_results: dict[str, CalculatedCosts] = {}
    valid_options_data: dict[str, TravelOption] = {}

    console.print(
        f"\nProcessing {len(input_options)} options from '{options_file_path.name}'..."
    )

    for input_opt in input_options:
        full_option = create_full_travel_option(
            input_opt, terminals, args.arrival_buffer
        )
        if full_option:
            calculated = calculate_costs(full_option, args.value_of_time)
            if calculated:
                all_results[full_option.option_name] = calculated
                valid_options_data[full_option.option_name] = (
                    full_option  # Store for later printing
                )
            else:
                print(
                    f"Warning: Could not calculate costs for option '{full_option.option_name}'. Skipping."
                )
        else:
            print(
                f"Warning: Could not create full option data for input '{input_opt.name}'. Skipping."
            )

    if len(all_results) < 2:
        print(
            "\nError: Fewer than two options could be successfully processed for comparison.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Print detailed breakdown for all processed options, sorted by effective cost
    console.print("\n--- Options Comparison Breakdown (Sorted by Effective Cost) ---")
    # Sort the option names based on their effective cost
    sorted_option_names = sorted(
        all_results.keys(),
        key=lambda name: all_results[name].effective_cost,
        # reverse=True, # Keep ascending order (lowest cost first)
    )

    # Prepare Rich table if available
    table = None
    if Table:
        table = Table(
            title="Travel Options Comparison",
            show_header=True,
            header_style="bold cyan",
            show_lines=True,
        )
        table.add_column("Option", style="dim", width=20)
        table.add_column("Terminals (Dep / Ret)")
        table.add_column("Base Cost", justify="right")
        table.add_column("Hassle Cost", justify="right")
        table.add_column("Time Value", justify="right")
        table.add_column("Total Time", justify="right")
        table.add_column("Effective Cost", justify="right", style="bold")

    best_option_name = sorted_option_names[0]  # Lowest cost is first

    for name in sorted_option_names:
        costs = all_results[name]
        # Retrieve the corresponding full option to pass terminal name etc.
        option_details = valid_options_data[name]

        if table:
            # Format data for table cells
            terminals_str = f"{option_details.terminal_name} / {option_details.return_terminal_name}"
            if option_details.terminal_name == option_details.return_terminal_name:
                terminals_str = option_details.terminal_name
            base_cost_str = f"${costs.base_cost - costs.total_combined_hassle:.2f}"  # Base without hassle
            hassle_str = (
                f"${costs.total_combined_hassle:.2f}"
                if costs.total_combined_hassle > 0
                else "-"
            )
            time_value_str = f"${costs.time_cost:.2f}"
            total_time_hrs = costs.total_time / 60.0
            total_time_str = f"{costs.total_time}m ({total_time_hrs:.1f}h)"
            effective_cost_str = f"${costs.effective_cost:.2f}"

            # Highlight the best row
            style = "on green" if name == best_option_name else ""

            table.add_row(
                name,
                terminals_str,
                base_cost_str,
                hassle_str,
                time_value_str,
                total_time_str,
                effective_cost_str,
                style=style,
            )
        else:  # Fallback if rich is not installed
            print(
                f"--- {name} (Dep: {option_details.terminal_name}, Ret: {option_details.return_terminal_name}) ---"
            )
            print(f"  Effective Cost: ${costs.effective_cost:.2f}")
            print(f"  Total Time: {costs.total_time} min")
            print("...")  # Basic fallback

    # Find the best option
    if table:
        console.print(table)
    else:
        console.print("\n(Install 'rich' library for a formatted table output)")

    min_effective_cost = all_results[best_option_name].effective_cost

    # Print Recommendation
    console.print("\n--- Recommendation ---")
    console.print(
        f"Comparing {len(all_results)} options using data from '{terminals_file_path.name}' and '{options_file_path.name}'."
    )
    console.print(f"Based on a time value of ${args.value_of_time:.2f}/hour:")
    console.print(
        f"The [bold green]best option is '{best_option_name}'[/bold green] "
        f"with an effective cost of [bold green]${min_effective_cost:.2f}[/bold green]"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare multiple travel options from a file."
    )

    # --- Input Files ---
    parser.add_argument(
        "--options-file",
        type=str,
        required=True,
        help="Path to the YAML file containing the list of travel options.",
    )
    parser.add_argument(
        "--terminals-file",
        type=str,
        default="terminals.yaml",
        help="Path to the terminals configuration file (YAML).",
    )

    # --- Shared Parameters ---
    parser.add_argument(
        "--arrival-buffer",
        type=int,
        default=0,
        help="Time buffer after arrival at return terminal (minutes).",
    )
    parser.add_argument(
        "--value-of-time",
        type=float,
        default=50.0,
        help="Value of your time ($ per hour).",
    )

    args = parser.parse_args()
    main(args)
