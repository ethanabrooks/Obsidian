# travel_chooser.py
import argparse
import sys
import yaml  # Requires PyYAML (pip install pyyaml)
from pathlib import Path
from typing import NamedTuple, Dict, Any

# Pydantic is now assumed to be installed
from pydantic import BaseModel, ValidationError, Field, field_validator


# --- Type Definition for Terminal Data (Used internally after validation) ---
class TerminalData(NamedTuple):
    travel_time_min: int
    travel_cost: float
    travel_hassle_cost: float


# --- Pydantic Models for Validation ---
class TerminalModel(BaseModel):
    travel_time_min: int = Field(..., ge=0)  # Ensure non-negative
    travel_cost: float = Field(..., ge=0.0)  # Ensure non-negative
    # Default to 0.0 if not provided, ensure non-negative if provided
    travel_hassle_cost: float = Field(default=0.0, ge=0.0)


class TerminalsConfig(BaseModel):
    # Use a dictionary where keys are terminal names (str) and values are TerminalModel
    terminals: Dict[str, TerminalModel]

    @field_validator("terminals", mode="before")
    @classmethod
    def check_terminals_not_empty(cls, v: Any) -> Any:
        if not v:
            raise ValueError(
                "Terminals dictionary cannot be empty in the configuration file."
            )
        return v


# --- Travel Option Representation ---
class TravelOption(NamedTuple):
    option_name: str  # User-defined name (e.g., "Flight_SEA")
    terminal_name: str  # Key from terminals.yaml (e.g., "JFK_Subway")
    journey_cost: float  # Cost of the main leg (e.g., flight/bus ticket)
    journey_duration_min: int  # Duration of the main leg
    general_journey_hassle: float  # Hassle of main leg (layovers, comfort, timing)

    # Populated after looking up terminal data
    travel_time_min: int = 0
    travel_cost: float = 0.0
    fixed_travel_hassle: float = 0.0
    terminal_buffer_min: int = 0  # Added during calculation

    def total_time_min(self) -> int:
        """Calculates total door-to-door time in minutes."""
        # Ensure components are non-negative before summing
        components = [
            self.travel_time_min,
            self.terminal_buffer_min,
            self.journey_duration_min,
        ]
        if any(c < 0 for c in components):
            print(
                f"Warning: Negative time component detected for {self.option_name}. Calculation might be invalid.",
                file=sys.stderr,
            )
            # Decide how to handle this - return -1, raise error, or proceed?
            # Returning -1 to signal invalid time during comparison phase.
            return -1
        return sum(components)

    def total_hassle_cost(self) -> float:
        """Combines fixed travel hassle and general journey hassle."""
        return self.fixed_travel_hassle + self.general_journey_hassle

    def base_cost(self) -> float:
        """Calculates base cost (journey + travel + combined hassle)."""
        # Note: self.travel_cost is populated from terminal data
        return self.journey_cost + self.travel_cost + self.total_hassle_cost()


def load_terminals(filepath: Path) -> dict[str, TerminalData]:
    """Loads terminal data from a YAML file using Pydantic for validation."""
    try:
        with open(filepath, "r") as f:
            raw_data = yaml.safe_load(f)
            # Wrap the raw data under a 'terminals' key for the validator
            config_data = {"terminals": raw_data}
            # Validate the structure and types using Pydantic
            validated_config = TerminalsConfig.model_validate(config_data)

            # Convert validated Pydantic models back to internal TerminalData NamedTuple format
            terminals_dict: dict[str, TerminalData] = {}
            for name, model in validated_config.terminals.items():
                terminals_dict[name] = TerminalData(
                    travel_time_min=model.travel_time_min,
                    travel_cost=model.travel_cost,
                    travel_hassle_cost=model.travel_hassle_cost,
                )
            return terminals_dict

    except FileNotFoundError:
        print(f"Error: Terminals file not found at '{filepath}'", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(
            f"Error: Could not parse terminals YAML file '{filepath}': {e}",
            file=sys.stderr,
        )
        sys.exit(1)
    except ValidationError as e:  # Catch Pydantic validation errors
        print(
            f"Error: Invalid format or data in terminals file '{filepath}':\n{e}",
            file=sys.stderr,
        )
        sys.exit(1)


def calculate_and_print_option_costs(
    option: TravelOption, value_of_time_per_hour: float
) -> None:  # Returns nothing, just prints
    """Calculates and prints the effective cost for a single option."""
    total_time = option.total_time_min()
    if total_time < 0:
        print(
            f"Error: Cannot calculate costs for '{option.option_name}' due to invalid total time.",
            file=sys.stderr,
        )
        return

    value_of_time_per_min = value_of_time_per_hour / 60.0

    print("\n--- Option Cost Breakdown ---")
    # Calculate costs for the single option
    base_cost = option.base_cost()

    # Time cost is the value of the total duration of this specific option
    time_cost = total_time * value_of_time_per_min
    effective_cost = base_cost + time_cost

    print(f"{option.option_name} (via {option.terminal_name}):")
    print(f"  Journey Cost:           ${option.journey_cost:.2f}")
    print(f"  Travel to Terminal Cost: ${option.travel_cost:.2f}")
    if option.fixed_travel_hassle > 0:
        print(f"  Fixed Travel Hassle:     ${option.fixed_travel_hassle:.2f}")
    if option.general_journey_hassle > 0:
        print(f"  General Journey Hassle:  ${option.general_journey_hassle:.2f}")
    if option.total_hassle_cost() > 0:
        print(f"  Total Hassle Cost:       ${option.total_hassle_cost():.2f}")
    print(f"  -----------------------------------")
    print(f"  Total Base Cost:         ${base_cost:.2f}")
    print(f"  -----------------------------------")
    print(f"  Travel Time:             {option.travel_time_min} min")
    print(f"  Terminal Buffer:         {option.terminal_buffer_min} min")
    print(f"  Journey Duration:        {option.journey_duration_min} min")
    print(
        f"  Total Time:              {total_time} min ({total_time / 60.0:.2f} hours)"
    )
    print(
        f"  Value of Total Time:     ${time_cost:.2f} (at ${value_of_time_per_hour:.2f}/hr)"
    )
    print(f"  ===================================")
    print(f"  EFFECTIVE COST:          ${effective_cost:.2f}")
    print("===================================")


def create_option_from_args(
    args: argparse.Namespace,
    terminals: dict[str, TerminalData],
    terminal_buffer: int,
) -> TravelOption | None:
    """Creates a TravelOption from command line args and terminal data."""
    # Get attributes directly from args
    option_name = args.name
    terminal_name = args.terminal
    journey_cost = args.cost
    journey_duration = args.duration
    general_hassle = args.hassle

    # Basic validation
    if (
        not terminal_name
        or not isinstance(journey_cost, (int, float))
        or not isinstance(journey_duration, int)
    ):
        print(
            f"Error: Missing required arguments (terminal, cost, duration).",
            file=sys.stderr,
        )
        return None
    if journey_duration < 0 or journey_cost < 0:
        print(
            f"Error: Journey cost and duration must be non-negative.",
            file=sys.stderr,
        )
        return None

    if terminal_name not in terminals:
        print(
            f"Error: Terminal '{terminal_name}' (for option '{option_name}') not found in terminals file.",
            file=sys.stderr,
        )
        return None

    terminal_info = terminals[terminal_name]

    # Use replace to create a new instance with updated fields from NamedTuple defaults
    temp_option = TravelOption(
        option_name=option_name,
        terminal_name=terminal_name,
        journey_cost=journey_cost,
        journey_duration_min=journey_duration,
        general_journey_hassle=general_hassle,
        fixed_travel_hassle=0.0,  # Placeholder, will be replaced
    )

    # Create the final option with all fields populated
    final_option = temp_option._replace(
        travel_time_min=terminal_info.travel_time_min,
        travel_cost=terminal_info.travel_cost,
        fixed_travel_hassle=terminal_info.travel_hassle_cost,
        terminal_buffer_min=terminal_buffer,
    )

    return final_option


def main(args: argparse.Namespace) -> None:
    """Loads data, creates a single option, calculates costs, and prints the details."""
    terminals_file_path = Path(args.terminals_file)
    terminals = load_terminals(terminals_file_path)

    # Create the single option from args
    option = create_option_from_args(args, terminals, args.terminal_buffer)

    if option is None:
        print("Error: Could not create travel option from arguments.", file=sys.stderr)
        sys.exit(1)

    # Calculate and print costs for the single option
    calculate_and_print_option_costs(option, args.value_of_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate the effective cost of a single travel option."
    )

    # --- Single Option Arguments ---
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Unique name for the travel option (e.g., Flight_SEA)",
    )
    parser.add_argument(
        "--terminal",
        type=str,
        required=True,
        help="Terminal name (must match key in terminals file)",
    )
    parser.add_argument(
        "--cost", type=float, required=True, help="Cost of the main journey leg ($)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        required=True,
        help="Duration of the main journey leg (minutes)",
    )
    parser.add_argument(
        "--hassle",
        type=float,
        default=0.0,
        help="General hassle cost for the journey (layover, timing, comfort) ($)",
    )

    # --- Shared Parameters ---
    parser.add_argument(
        "--terminal-buffer",
        type=int,
        default=90,
        help="Time buffer at departure terminal (minutes)",
    )
    parser.add_argument(
        "--value-of-time",
        type=float,
        default=50.0,
        help="Value of your time ($ per hour)",
    )
    parser.add_argument(
        "--terminals-file",
        type=str,
        default="terminals.yaml",
        help="Path to the terminals configuration file (YAML)",
    )

    args = parser.parse_args()
    main(args)
