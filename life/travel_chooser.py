# travel_chooser.py
import argparse
import sys
import yaml  # Requires PyYAML (pip install pyyaml)
from pathlib import Path
from typing import NamedTuple, Dict, Any

# Pydantic is now assumed to be installed
from pydantic import BaseModel, ValidationError, Field, field_validator


# --- Type Definition for Calculated Results ---
class CalculatedCosts(NamedTuple):
    base_cost: float
    time_cost: float
    effective_cost: float
    total_time: int
    # Components for printing
    round_trip_journey_cost: float
    round_trip_general_hassle: float
    dep_travel_cost: float
    dep_travel_time_min: int
    dep_fixed_travel_hassle: float
    dep_buffer_min: int
    ret_travel_cost: float
    ret_travel_time_min: int
    ret_fixed_travel_hassle: float
    arr_buffer_min: int
    total_combined_hassle: float  # Sum of fixed + general
    journey_duration_min: int  # Stores the RT duration


# --- Type Definition for Terminal Data (Used internally after validation) ---
class TerminalData(NamedTuple):
    travel_time_min: int
    travel_cost: float
    travel_hassle_cost: float
    departure_buffer_min: int


# --- Pydantic Models for Terminal Validation ---
class TerminalModel(BaseModel):
    travel_time_min: int = Field(..., ge=0)  # Ensure non-negative
    travel_cost: float = Field(..., ge=0.0)  # Ensure non-negative
    # Default to 0.0 if not provided, ensure non-negative if provided
    travel_hassle_cost: float = Field(default=0.0, ge=0.0)
    departure_buffer_min: int = Field(default=90, ge=0)


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


# --- Travel Option Representation (Now includes return leg info) ---
class TravelOption(NamedTuple):
    option_name: str  # User-defined name (e.g., "Flight_SEA")
    terminal_name: str  # Key from terminals.yaml (e.g., "JFK_Subway")
    round_trip_journey_cost: float  # Cost of the main round trip leg(s)
    round_trip_journey_duration_min: int  # Duration of the main round trip leg(s)
    round_trip_general_hassle: float  # Hassle of main round trip leg(s)

    # Populated after looking up terminal data for DEPARTURE leg
    dep_travel_time_min: int = 0
    dep_travel_cost: float = 0.0
    dep_fixed_travel_hassle: float = 0.0
    dep_buffer_min: int = 0  # Departure buffer

    # Populated after looking up terminal data for RETURN leg
    return_terminal_name: str = ""  # Set during creation
    ret_travel_time_min: int = 0
    ret_travel_cost: float = 0.0
    ret_fixed_travel_hassle: float = 0.0
    arr_buffer_min: int = 0  # Arrival buffer

    def total_time_min(self) -> int:
        """Calculates total door-to-door time for the round trip in minutes."""
        # Ensure components are non-negative before summing
        components = [
            self.dep_travel_time_min,
            self.dep_buffer_min,
            self.round_trip_journey_duration_min,
            self.arr_buffer_min,
            self.ret_travel_time_min,
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
        """Combines fixed travel hassles (dep/ret) and general round trip hassle."""
        return (
            self.dep_fixed_travel_hassle
            + self.ret_fixed_travel_hassle
            + self.round_trip_general_hassle
        )

    def base_cost(self) -> float:
        """Calculates base cost (round trip journey + dep/ret travel + combined hassle)."""
        return (
            self.round_trip_journey_cost
            + self.dep_travel_cost
            + self.ret_travel_cost
            + self.total_hassle_cost()
        )


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
                    departure_buffer_min=model.departure_buffer_min,
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
    except ValueError as e:  # Handle missing 'terminals' key or empty dict
        print(f"Error in terminals file '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)


def calculate_costs(
    option: TravelOption, value_of_time_per_hour: float
) -> CalculatedCosts | None:  # Returns typed object or None
    """Calculates the effective cost and components for a single option."""
    total_time = option.total_time_min()
    if total_time < 0:
        print(
            f"Error: Cannot calculate costs for '{option.option_name}' due to invalid total time.",
            file=sys.stderr,
        )
        return None  # Indicate failure

    value_of_time_per_min = value_of_time_per_hour / 60.0

    # Calculate costs for the single option
    base_cost = option.base_cost()

    # Time cost is the value of the total duration of this specific option
    time_cost = total_time * value_of_time_per_min
    effective_cost = base_cost + time_cost

    # Return the strongly typed object
    return CalculatedCosts(
        base_cost=base_cost,
        time_cost=time_cost,
        effective_cost=effective_cost,
        total_time=total_time,
        # Components for printing
        round_trip_journey_cost=option.round_trip_journey_cost,
        round_trip_general_hassle=option.round_trip_general_hassle,
        dep_travel_cost=option.dep_travel_cost,
        dep_travel_time_min=option.dep_travel_time_min,
        dep_fixed_travel_hassle=option.dep_fixed_travel_hassle,
        dep_buffer_min=option.dep_buffer_min,
        ret_travel_cost=option.ret_travel_cost,
        ret_travel_time_min=option.ret_travel_time_min,
        ret_fixed_travel_hassle=option.ret_fixed_travel_hassle,
        arr_buffer_min=option.arr_buffer_min,
        total_combined_hassle=option.total_hassle_cost(),
        journey_duration_min=option.round_trip_journey_duration_min,  # Assign RT duration here
    )


def print_option_costs(
    option: TravelOption,
    calculated_costs: CalculatedCosts,
    value_of_time_per_hour: float,
):
    """Prints the formatted breakdown of costs for a single option."""
    print(f"\n--- Option Cost Breakdown: {option.option_name} ---")
    print(f"  Departure via: {option.terminal_name}")
    print(f"  Return via:    {option.return_terminal_name}")
    print("  -----------------------------------")
    print(f"  Round Trip Journey Cost: ${calculated_costs.round_trip_journey_cost:.2f}")
    print(f"  Dep. Travel Cost:       ${calculated_costs.dep_travel_cost:.2f}")
    print(f"  Ret. Travel Cost:       ${calculated_costs.ret_travel_cost:.2f}")
    if calculated_costs.dep_fixed_travel_hassle > 0:
        print(
            f"  Dep. Fixed Travel Hassle:${calculated_costs.dep_fixed_travel_hassle:.2f}"
        )
    if calculated_costs.ret_fixed_travel_hassle > 0:
        print(
            f"  Ret. Fixed Travel Hassle:${calculated_costs.ret_fixed_travel_hassle:.2f}"
        )
    if calculated_costs.round_trip_general_hassle > 0:
        print(
            f"  Round Trip Gen. Hassle: ${calculated_costs.round_trip_general_hassle:.2f}"
        )
    if calculated_costs.total_combined_hassle > 0:
        print(
            f"  Total Hassle Cost:      ${calculated_costs.total_combined_hassle:.2f}"
        )
    print("  -----------------------------------")
    print(f"  Total Base Cost:        ${calculated_costs.base_cost:.2f}")
    print("  -----------------------------------")
    print(f"  Dep. Travel Time:       {calculated_costs.dep_travel_time_min} min")
    print(f"  Dep. Buffer:            {calculated_costs.dep_buffer_min} min")
    print(f"  Round Trip Journey Time:{calculated_costs.journey_duration_min} min")
    print(f"  Arr. Buffer:            {calculated_costs.arr_buffer_min} min")
    print(f"  Ret. Travel Time:       {calculated_costs.ret_travel_time_min} min")
    print(
        f"  Total Time (Door-to-Door):{calculated_costs.total_time} min ({calculated_costs.total_time / 60.0:.2f} hours)"
    )
    print(
        f"  Value of Total Time:     ${calculated_costs.time_cost:.2f} (at ${value_of_time_per_hour:.2f}/hr)"
    )
    print("  ===================================")
    print(f"  EFFECTIVE COST:          ${calculated_costs.effective_cost:.2f}")
    print("===================================")


def create_option_from_args(
    args: argparse.Namespace,
    terminals: dict[str, TerminalData],
    arrival_buffer: int,
) -> TravelOption | None:
    """Creates a TravelOption from command line args and terminal data."""
    # Get attributes directly from args
    option_name = args.name
    dep_terminal_name = args.terminal
    ret_terminal_name = (
        args.return_terminal if args.return_terminal else dep_terminal_name
    )

    journey_cost = args.cost  # Renamed conceptually to round_trip_cost
    journey_duration = args.duration  # Renamed conceptually to round_trip_duration
    general_hassle = args.hassle  # Renamed conceptually to round_trip_hassle

    # Basic validation
    if (
        not dep_terminal_name
        or not isinstance(journey_cost, (int, float))
        or not isinstance(journey_duration, int)
    ):
        print(
            "Error: Missing required arguments (terminal, cost, duration).",
            file=sys.stderr,
        )
        return None
    if journey_duration < 0 or journey_cost < 0:
        print(
            "Error: Journey cost and duration must be non-negative.",
            file=sys.stderr,
        )
        return None

    if dep_terminal_name not in terminals:
        print(
            f"Error: Departure terminal '{dep_terminal_name}' (for option '{option_name}') not found in terminals file.",
            file=sys.stderr,
        )
        return None

    if ret_terminal_name not in terminals:
        print(
            f"Error: Return terminal '{ret_terminal_name}' (for option '{option_name}') not found in terminals file.",
            file=sys.stderr,
        )
        return None

    dep_terminal_info = terminals[dep_terminal_name]
    ret_terminal_info = terminals[ret_terminal_name]

    # Use replace to create a new instance with updated fields from NamedTuple defaults
    temp_option = TravelOption(
        option_name=option_name,
        terminal_name=dep_terminal_name,  # Store departure terminal name
        round_trip_journey_cost=journey_cost,
        round_trip_journey_duration_min=journey_duration,
        round_trip_general_hassle=general_hassle,
        # Placeholders below will be replaced
        dep_fixed_travel_hassle=0.0,
        return_terminal_name="",
        ret_fixed_travel_hassle=0.0,
    )

    # Create the final option with all fields populated
    final_option = temp_option._replace(
        # Departure fields
        dep_travel_time_min=dep_terminal_info.travel_time_min,
        dep_travel_cost=dep_terminal_info.travel_cost,
        dep_fixed_travel_hassle=dep_terminal_info.travel_hassle_cost,
        dep_buffer_min=dep_terminal_info.departure_buffer_min,
        # Return fields
        return_terminal_name=ret_terminal_name,
        ret_travel_time_min=ret_terminal_info.travel_time_min,
        ret_travel_cost=ret_terminal_info.travel_cost,
        ret_fixed_travel_hassle=ret_terminal_info.travel_hassle_cost,
        arr_buffer_min=arrival_buffer,
    )

    return final_option


def main(args: argparse.Namespace) -> None:
    """Loads data, creates a single option, calculates costs, and prints the details."""
    terminals_file_path = Path(args.terminals_file)
    terminals = load_terminals(terminals_file_path)

    # Create the single option from args
    option = create_option_from_args(args, terminals, args.arrival_buffer)

    if option is None:
        print("Error: Could not create travel option from arguments.", file=sys.stderr)
        sys.exit(1)

    # Calculate costs for the single option
    calculated_costs = calculate_costs(option, args.value_of_time)

    # Print the results if calculation was successful
    if calculated_costs:
        print_option_costs(option, calculated_costs, args.value_of_time)
    else:
        # Error message already printed by calculate_costs
        sys.exit(1)


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
        "--return-terminal",
        type=str,
        default=None,
        help="Return terminal name (if different from departure). Defaults to departure terminal.",
    )
    parser.add_argument(
        "--cost",
        type=float,
        required=True,
        help="Cost of the main ROUND TRIP journey leg(s) ($)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        required=True,
        help="Duration of the main ROUND TRIP journey leg(s) (minutes)",
    )
    parser.add_argument(
        "--hassle",
        type=float,
        default=0.0,
        help="General hassle cost for the ROUND TRIP journey (layovers, timing, comfort) ($)",
    )

    # --- Shared Parameters ---
    parser.add_argument(
        "--arrival-buffer",
        type=int,
        default=0,
        help="Time buffer after arrival at return terminal (minutes)",
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
