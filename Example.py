from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Tuple
import numpy as np
from time import sleep

class TrainPhase(Enum):
    CRUISING = "cruising"
    COASTING = "coasting"
    BRAKING = "braking"

@dataclass
class PowerConfig:
    cruising_power: float  # MW
    coasting_power: float  # MW
    braking_regeneration: float  # MW (negative value)

@dataclass
class SubstationConfig:
    max_power: float  # MW threshold before congestion
    normal_voltage: float = 1.5  # kV
    min_voltage: float = 1.0  # kV
    max_current: float = 5000  # A

@dataclass
class Position:
    x: float  # km along track
    
    def distance_to(self, other: 'Position') -> float:
        return abs(self.x - other.x)

class Train:
    def __init__(self, train_id: str, power_config: PowerConfig, position: Position):
        self.train_id = train_id
        self.power_config = power_config
        self.position = position
        self.current_phase = TrainPhase.CRUISING
        self.current_section = None
        
    def get_current_power_draw(self) -> float:
        if self.current_phase == TrainPhase.CRUISING:
            return self.power_config.cruising_power
        elif self.current_phase == TrainPhase.COASTING:
            return self.power_config.coasting_power
        else:  # BRAKING
            return self.power_config.braking_regeneration
        
    def move_to(self, new_position: Position):
        self.position = new_position

class Substation:
    def __init__(self, sub_id: str, config: SubstationConfig, position: Position):
        self.sub_id = sub_id
        self.config = config
        self.position = position
        self.is_congested = False
        self.current_load = 0.0
        
    def calculate_power_contribution(self, train: Train) -> float:
        """Calculate power contribution based on distance to train"""
        distance = self.position.distance_to(train.position)
        # Power contribution decreases with distance
        # Using a simple inverse relationship with maximum range of 10km
        max_range = 10.0  # km
        if distance > max_range:
            return 0.0
        
        power_factor = (max_range - distance) / max_range
        return train.get_current_power_draw() * power_factor
    
    def update_congestion_status(self) -> None:
        self.is_congested = self.current_load > self.config.max_power

class NetworkController:
    def __init__(self):
        self.substations: Dict[str, Substation] = {}
        self.trains: Dict[str, Train] = {}
        self.track_length: float = 0.0
        
    def add_substation(self, substation: Substation) -> None:
        self.substations[substation.sub_id] = substation
        self.track_length = max(self.track_length, substation.position.x)
        
    def add_train(self, train: Train) -> None:
        self.trains[train.train_id] = train
    
    def get_nearest_substations(self, position: Position, max_distance: float = 10.0) -> List[Tuple[Substation, float]]:
        """Get substations within range, sorted by distance"""
        nearby_subs = []
        for sub in self.substations.values():
            distance = sub.position.distance_to(position)
            if distance <= max_distance:
                nearby_subs.append((sub, distance))
        return sorted(nearby_subs, key=lambda x: x[1])
    
    def update_power_distribution(self):
        """Update power distribution based on train positions"""
        # Reset all substation loads
        for sub in self.substations.values():
            sub.current_load = 0.0
        
        # Calculate power contribution for each train
        for train in self.trains.values():
            nearby_subs = self.get_nearest_substations(train.position)
            if not nearby_subs:
                print(f"Warning: Train {train.train_id} is out of range of any substation!")
                continue
            
            power_draw = train.get_current_power_draw()
            remaining_power = power_draw
            
            # Distribute power among nearby substations
            for sub, distance in nearby_subs:
                if remaining_power <= 0:
                    break
                    
                contribution = sub.calculate_power_contribution(train)
                actual_contribution = min(contribution, remaining_power)
                sub.current_load += actual_contribution
                remaining_power -= actual_contribution
    
    def print_network_status(self):
        print("\n=== Network Status ===")
        print(f"Track Length: {self.track_length} km")
        
        print("\nSubstations:")
        for sub_id, sub in sorted(self.substations.items()):
            status = "CONGESTED" if sub.is_congested else "Normal"
            print(f"\nSubstation {sub_id} at {sub.position.x}km:")
            print(f"  Current Load: {sub.current_load:.2f} MW")
            print(f"  Max Power: {sub.config.max_power} MW")
            print(f"  Status: {status}")
        
        print("\nTrains:")
        for train_id, train in sorted(self.trains.items()):
            print(f"\nTrain {train_id} at {train.position.x}km:")
            print(f"  Phase: {train.current_phase.value}")
            print(f"  Power Draw: {train.get_current_power_draw():.2f} MW")
            nearby_subs = self.get_nearest_substations(train.position)
            print("  Nearest substations:")
            for sub, distance in nearby_subs[:2]:  # Show 2 nearest
                print(f"    - {sub.sub_id} at {distance:.1f}km")

def main():
    controller = NetworkController()
    
    # Get substation information
    num_substations = int(input("Enter number of substations: "))
    for i in range(num_substations):
        sub_id = f"SUB_{i+1}"
        position = float(input(f"Enter position for Substation {sub_id} (km): "))
        threshold = float(input(f"Enter power threshold for Substation {sub_id} (MW): "))
        
        config = SubstationConfig(max_power=threshold)
        substation = Substation(sub_id, config, Position(position))
        controller.add_substation(substation)
    
    # Get train information
    num_trains = int(input("Enter number of trains: "))
    cruising_power = float(input("Enter power usage during cruising (MW): "))
    
    power_config = PowerConfig(
        cruising_power=cruising_power,
        coasting_power=cruising_power * 0.2,
        braking_regeneration=-cruising_power * 0.15
    )
    
    # Create and position trains
    for i in range(num_trains):
        train_id = f"TRAIN_{i+1}"
        position = float(input(f"Enter position for Train {train_id} (km): "))
        train = Train(train_id, power_config, Position(position))
        controller.add_train(train)
    
    # Run simulation
    print("\nStarting simulation...")
    for timestep in range(3):
        print(f"\nTimestep {timestep + 1}")
        
        # Update power distribution
        controller.update_power_distribution()
        
        # Update substation congestion status
        for substation in controller.substations.values():
            substation.update_congestion_status()
        
        # Display network status
        controller.print_network_status()
        sleep(2)

if __name__ == "__main__":
    main()