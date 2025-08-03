"""
Main CLI entry point for the Mars Crisis Emergency Response ABM.
This file makes the package executable with: python -m mars_crisis_abm
"""

from .model import MarsModel
from .utils.model_utils import load_config, load_grid_layout_csv
import sys


def main():
    print("Welcome to the Mars Crisis Emergency Response ABM simulation")

    try:
        print("Loading configuration...")
        config_params = load_config("config/params.json")
        grid_data, equipment_positions = load_grid_layout_csv("config/grid_layout.csv")
        print("Configuration loaded successfully")
    except:
        print("Program startup failed due to a configuration error")
        sys.exit(1)

    model = MarsModel(config_params, grid_data, equipment_positions)

    print("Running simulation...")
    print(f"Robot fleet: {model.robot_counts}")
    print("-" * 50)

    step = 1
    while model.running == True:
        model.step()
        if step % 10 == 0:
            df = model.datacollector.get_model_vars_dataframe()
            print(
                f"Step {step}: "
                f"Critical Humans: {df['Critical Humans'].iloc[-1]}, "
                f"Atmosphere: {df['Atmospheric Condition'].iloc[-1]:.1f}%, "
                f"Power: {df['Power Level'].iloc[-1]:.1f}%"
            )

        step += 1

    print("-" * 50)
    print(f"Simulation complete! -- Status: {model.mission_status} ")


if __name__ == "__main__":
    main()
