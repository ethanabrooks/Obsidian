# flight_chooser.py
import argparse
from typing import NamedTuple


class FlightOption(NamedTuple):
    name: str
    flight_cost: float
    travel_time_min: int
    travel_cost: float
    total_air_time_min: int
    airport_buffer_min: int

    def total_time_min(self) -> int:
        """Calculates total door-to-door time in minutes."""
        return self.travel_time_min + self.airport_buffer_min + self.total_air_time_min

    def base_cost(self) -> float:
        """Calculates base cost (flight + travel)."""
        return self.flight_cost + self.travel_cost


def calculate_effective_costs(
    options: list[FlightOption], value_of_time_per_hour: float
) -> dict[str, float]:
    """Calculates the effective cost for each option, including time value."""
    if not options:
        return {}

    # Find the minimum total time
    min_total_time = min(opt.total_time_min() for opt in options)
    value_of_time_per_min = value_of_time_per_hour / 60.0

    effective_costs: dict[str, float] = {}
    print("\n--- Calculation Breakdown ---")
    for option in options:
        time_diff_min = option.total_time_min() - min_total_time
        time_cost = time_diff_min * value_of_time_per_min
        effective_cost = option.base_cost() + time_cost
        effective_costs[option.name] = effective_cost
        print(f"{option.name}:")
        print(f"  Base Cost (Flight + Travel): ${option.base_cost():.2f}")
        print(f"  Total Time: {option.total_time_min()} min")
        print(f"  Time Difference vs Fastest: {time_diff_min} min")
        print(f"  Value of Time Difference: ${time_cost:.2f}")
        print(f"  Effective Cost: ${effective_cost:.2f}")
        print("-" * 10)

    return effective_costs


def main(args: argparse.Namespace) -> None:
    """Parses arguments, calculates costs, and prints the recommendation."""

    lga_option = FlightOption(
        name="LGA (1-Stop)",
        flight_cost=args.lga_flight_cost,
        travel_time_min=args.lga_travel_time,
        travel_cost=args.lga_travel_cost,
        total_air_time_min=args.lga_total_air_time,
        airport_buffer_min=args.airport_buffer,
    )

    jfk_option_uber = FlightOption(
        name="JFK (Nonstop, Uber)",
        flight_cost=args.jfk_flight_cost,
        travel_time_min=args.jfk_travel_time_uber,
        travel_cost=args.jfk_travel_cost_uber,
        total_air_time_min=args.jfk_total_air_time,
        airport_buffer_min=args.airport_buffer,
    )

    jfk_option_subway = FlightOption(
        name="JFK (Nonstop, Subway)",
        flight_cost=args.jfk_flight_cost,
        travel_time_min=args.jfk_travel_time_subway,
        travel_cost=args.jfk_travel_cost_subway,
        total_air_time_min=args.jfk_total_air_time,
        airport_buffer_min=args.airport_buffer,
    )

    options = [lga_option, jfk_option_uber, jfk_option_subway]

    effective_costs = calculate_effective_costs(options, args.value_of_time)

    if not effective_costs:
        print("No options to compare.")
        return

    # Find the best option
    best_option_name = min(effective_costs, key=lambda k: effective_costs[k])
    min_effective_cost = effective_costs[best_option_name]

    print("\n--- Recommendation ---")
    print(f"Based on a time value of ${args.value_of_time:.2f}/hour:")
    print(
        f"The best option is {best_option_name} "
        f"with an effective cost of ${min_effective_cost:.2f}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare flight options considering time value."
    )

    # Flight Costs
    parser.add_argument(
        "--lga-flight-cost",
        type=float,
        required=True,
        help="Cost of the LGA flight ($)",
    )
    parser.add_argument(
        "--jfk-flight-cost",
        type=float,
        required=True,
        help="Cost of the JFK flight ($)",
    )

    # LGA Travel
    parser.add_argument(
        "--lga-travel-time",
        type=int,
        default=20,
        help="Travel time to LGA (minutes)",
    )
    parser.add_argument(
        "--lga-travel-cost",
        type=float,
        default=55.0,
        help="Travel cost to LGA ($)",
    )

    # JFK Travel (Uber)
    parser.add_argument(
        "--jfk-travel-time-uber",
        type=int,
        default=40,
        help="Travel time to JFK via Uber (minutes)",
    )
    parser.add_argument(
        "--jfk-travel-cost-uber",
        type=float,
        default=70.0,
        help="Travel cost to JFK via Uber ($)",
    )

    # JFK Travel (Subway)
    parser.add_argument(
        "--jfk-travel-time-subway",
        type=int,
        default=50,
        help="Travel time to JFK via Subway (minutes)",
    )
    parser.add_argument(
        "--jfk-travel-cost-subway",
        type=float,
        default=2.50,
        help="Travel cost to JFK via Subway ($)",
    )

    # Flight Durations (Total air + layover)
    parser.add_argument(
        "--lga-total-air-time",
        type=int,
        default=450,  # 1h47m + 43m + 5h = 7h30m
        help="Total time in air + layover for LGA option (minutes)",
    )
    parser.add_argument(
        "--jfk-total-air-time",
        type=int,
        default=393,  # 6h33m
        help="Total time in air for JFK option (minutes)",
    )

    # Shared Parameters
    parser.add_argument(
        "--airport-buffer",
        type=int,
        default=90,
        help="Time buffer at airport before flight (minutes)",
    )
    parser.add_argument(
        "--value-of-time",
        type=float,
        default=50.0,
        help="Value of your time ($ per hour)",
    )

    args = parser.parse_args()
    main(args)
