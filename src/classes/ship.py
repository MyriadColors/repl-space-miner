from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict

from pygame import Vector2

from src.classes.asteroid import Asteroid, AsteroidField
from src.classes.engine import Engine, EngineType
from src.classes.station import Station
from src.classes.space_object import IsSpaceObject, CanMove
from src.data import OreCargo, Upgrade, UpgradeTarget, ENGINES, SHIP_TEMPLATES
from src.helpers import euclidean_distance, vector_to_string, format_seconds


class Ship:
    ship_id_counter: int = 0

    def __init__(
        self,
        name: str,
        position: Vector2 = Vector2(0, 0),  # Default position
        speed: float = 1.0,  # Default speed
        max_fuel: float = 100.0,  # Default max_fuel
        fuel_consumption: float = 1.0,  # Default fuel_consumption
        cargo_capacity: float = 100.0,  # Default cargo_capacity
        value: float = 10000.0,  # Default value
        mining_speed: float = 1.0,  # Default mining_speed
        sensor_range: float = 1.0,  # Default sensor_range
        appearance: str = "Rust Bucket"  # Default appearance, describes the visual style of the ship
    ):
        """
        Initialize a new Ship instance.

        Args:
            name (str): The name of the ship.
            position (Vector2): The initial position of the ship in 2D space (default: (0, 0)).
            speed (float): The base speed of the ship in AU/s (default: 1.0).
            max_fuel (float): The maximum hydrogen fuel capacity in cubic meters (default: 100.0 m³).
            fuel_consumption (float): The hydrogen fuel consumption rate in m³/AU (default: 1.0 m³/AU).
            cargo_capacity (float): The maximum cargo capacity in cubic meters (default: 100.0 m³).
            value (float): The monetary value of the ship (default: 10,000.0 credits).
            mining_speed (float): The mining speed of the ship (default: 1.0 units/s).
            sensor_range (float): The detection range of the ship's sensors in AU (default: 1.0 AU).
            appearance (str): The visual style or description of the ship (default: "Rust Bucket").
        """
        self.name = name
        self.space_object = IsSpaceObject(position, self.ship_id_counter)
        Ship.ship_id_counter += 1
        self.moves = CanMove(speed)  # in AU/s

        # Standard fuel (Hydrogen Cells) for sub-FTL travel
        self.fuel = max_fuel  # in m3
        self.max_fuel = max_fuel  # in m3
        self.fuel_consumption = fuel_consumption  # in m3/AU

        # Antimatter fuel system for FTL (Faster-Than-Light) travel
        # Units: antimatter in grams (g), consumption in grams per FTL jump        self.antimatter = 0.0  # in g (grams)
        self.max_antimatter = 5.0  # in g (grams)
        self.antimatter_consumption = 0.5  # in g/FTL jump
        self.antimatter = 5.0  # in g (grams)

        # Power system for ship operations and containment
        self.power = 100.0  # Current power level (units)
        self.max_power = 100.0  # Maximum power capacity (units)
        
        # Antimatter containment system
        # Ensures safe storage of antimatter; integrity is a percentage (0-100%)
        self.containment_integrity = 100.0  # percentage
        self.containment_power_draw = (
            0.001  # fuel consumed per hour to maintain containment
        )
        self.containment_failure_risk = (
            0.0  # Percentage chance of containment failure; increases with damage or time
        )
        self.last_containment_check = 0  # game time of last integrity check

        self.cargohold: list = []
        self.cargohold_occupied: float = 0
        self.cargohold_capacity = cargo_capacity
        self.value = value
        self.mining_speed = mining_speed
        self.appearance = appearance  # Appearance attribute, used to define the ship's visual style
        self.interaction_radius = 0.001  # Radius in AUs around the player ship where it can interact with other objects
        self.is_docked = False
        self.docked_at: Station | None = None
        self.calculate_cargo_occupancy()
        self.sensor_range = sensor_range  # If any entity enters this range around the ship, it is detected
        # Track applied upgrades
        self.applied_upgrades: Dict[str, Upgrade] = {}
        self.hull_integrity: float = 100.0  # Base hull integrity (percentage)
        self.shield_capacity: float = 0.0  # Base shield capacity (percentage)        # Engine-related attributes
        self.base_speed: float = speed  # Store original base speed
        self.base_fuel_consumption: float = fuel_consumption  # Store original base fuel consumption
        self.sensor_signature: float = 1.0  # Base sensor signature (affects detection)
        if "standard" in ENGINES:
            std_engine_obj = ENGINES["standard"]
            self.engine = Engine(
                id=std_engine_obj.id,
                name=std_engine_obj.name,
                engine_type=std_engine_obj.engine_type,
                price=std_engine_obj.price,
                speed_modifier=std_engine_obj.speed_modifier,
                fuel_consumption_modifier=std_engine_obj.fuel_consumption_modifier,
                sensor_signature_modifier=std_engine_obj.sensor_signature_modifier,
                description=std_engine_obj.description,
                maintenance_cost_modifier=std_engine_obj.maintenance_cost_modifier,
                magneton_resistance=std_engine_obj.magneton_resistance
            )
        else:
            self.engine = Engine(
                id="default",
                name="Default Engine",
                engine_type=EngineType.STANDARD,
                price=50_000,
                speed_modifier=1.0,
                fuel_consumption_modifier=1.0,
                sensor_signature_modifier=1.0,
                description="A basic, reliable engine.",
                maintenance_cost_modifier=1.0,
                magneton_resistance=0.0
            )

    def get_ore_cargo_by_id(self, ore_id: int) -> OreCargo | None:
        return next((cargo for cargo in self.cargohold if cargo.ore.id == ore_id), None)

    def set_name(self, new_name):
        self.name = new_name

    def dock_into_station(self, station: Station):
        assert station is not None
        self.is_docked = True
        self.docked_at = station

    def get_station_docked_at(self):
        return self.docked_at

    def undock_from_station(self):
        self.is_docked = False
        self.docked_at = None

    def consume_fuel(self, value):
        self.fuel -= value

    def move_unit(self):
        self.space_object.position.x += self.moves.speed

    def refuel(self, value):
        self.fuel += value

    def calculate_travel_data(self, destination: Vector2):
        distance = round(euclidean_distance(self.space_object.position, destination), 3)
        time = round(distance / self.moves.speed, 3)
        fuel_consumed = round(distance * self.fuel_consumption, 3)
        return distance, time, fuel_consumed

    def calculate_adjusted_fuel_consumption(
        self, character, fuel_consumed: float
    ) -> float:
        """Adjust fuel consumption based on character traits and skills."""
        # Apply character's fuel consumption modifier if applicable
        if hasattr(character, "fuel_consumption_mod"):
            fuel_consumed *= character.fuel_consumption_mod

            # Apply piloting skill bonus (0.5% reduction per point above 5)
            if character.piloting > 5:
                piloting_bonus = 1 - ((character.piloting - 5) * 0.005)
                fuel_consumed *= piloting_bonus

        # Round to 3 decimal places
        return round(fuel_consumed, 3)

    def travel(self, game_state, destination: Vector2):
        distance, travel_time, fuel_consumed = self.calculate_travel_data(destination)

        # Apply character's fuel consumption modifier if applicable
        character = game_state.get_player_character()
        if hasattr(character, "fuel_consumption_mod"):
            # Apply the modifier to the fuel consumption
            fuel_consumed *= character.fuel_consumption_mod

            # Apply piloting skill bonus (0.5% reduction per point above 5)
            if character.piloting > 5:
                piloting_bonus = 1 - ((character.piloting - 5) * 0.005)
                fuel_consumed *= piloting_bonus

            # Round to 3 decimal places
            fuel_consumed = self.calculate_adjusted_fuel_consumption(
                character, fuel_consumed
            )

        # Check if destination is within system boundaries
        system_size = game_state.get_current_solar_system().size  # MODIFIED
        # Assumption: The solar system's center is at (0,0).
        # This is used to calculate the distance of the destination from the center for boundary checking.
        if destination.length() > system_size:
            print(
                f"Destination is outside system boundaries. Maximum distance from center is {system_size} AU."
            )
            return

        if self.fuel - fuel_consumed < 0:
            print("Not enough fuel to travel. Please refuel.")
            return

        confirm = input(f"Confirm travel? (y/n) ")
        if confirm != "y":
            print("Travel cancelled.")
            return
            
        # Apply Methodical trait message if applicable
        if (
            hasattr(character, "positive_trait")
            and character.positive_trait == "Methodical"
            and character.fuel_consumption_mod < 1.0
        ):
            print(
                "Your methodical approach to navigation optimizes the journey, saving fuel."
            )

        self.consume_fuel(fuel_consumed)
        self.space_object.position = destination
        game_state.global_time += travel_time
        print(f"The ship has arrived at {vector_to_string(destination)}")

    def status_to_string(self) -> list[str]:
        ore_units_on_cargohold = sum(cargo.quantity for cargo in self.cargohold)
        docked_at_name = "Not docked" if self.docked_at is None else self.docked_at.name
        return [
            f"Ship Name: {self.name}",
            f"Position: {vector_to_string(self.space_object.get_position())}",
            f"Engine: {self.engine.name}",
            f"Speed: {self.moves.speed:.2f} AU/s",
            f"Hydrogen Fuel: {self.fuel:.2f}/{self.max_fuel} m3",
            f"Fuel Consumption: {self.fuel_consumption:.4f} m3/AU",            
            f"Antimatter: {self.antimatter:.2f}/{self.max_antimatter} g",
            f"Power: {self.power:.2f}/{self.max_power}",
            f"Containment Integrity: {self.containment_integrity:.1f}%",
            f"Cargohold: {self.cargohold_occupied:.2f}/{self.cargohold_capacity} m3",
            f"Amount of Ores: {ore_units_on_cargohold}",
            f"Docked at: {docked_at_name}",
            f"Hull Integrity: {self.hull_integrity:.1f}%",
            f"Shield Capacity: {self.shield_capacity:.1f}%",
            f"Sensor Range: {self.sensor_range:.2f} AU",
            f"Sensor Signature: {self.sensor_signature:.2f}",
        ]

    def cargo_to_string(self):
        return "\n".join(
            f"{cargo.quantity} units of {cargo.ore.name}" for cargo in self.cargohold
        )

    def get_docked_station(self) -> Station | None:
        return self.docked_at

    def mine_belt(
        self,
        game_state,
        asteroid_field: AsteroidField,
        time_to_mine: int,
        mine_until_full: bool,
        ores_selected_list: list[str] | None,
    ):
        # Ensure the asteroid field contains asteroids
        if not asteroid_field.asteroids:
            print("This field is empty.")
            return

        # Check if the cargo is already full
        if self.is_cargo_full():
            print("You have no cargo space left.")
            return

        # Validate ores if a list of selected ores is provided
        if ores_selected_list:
            available_ores = {ore.name.lower() for ore in asteroid_field.ores_available}
            invalid_ores = [
                ore for ore in ores_selected_list if ore.lower() not in available_ores
            ]
            if invalid_ores:
                print(
                    f"The following ores are not available in this field: {', '.join(invalid_ores)}"
                )
                return
        else:
            print("No ores were selected. All available ores will be mined.")
            print("List of available ores: ")
            for ore in asteroid_field.ores_available:
                print(f"- {ore.name}")
            ores_selected_list = None

        # Get character trait modifiers for mining
        character = game_state.get_player_character()
        mining_yield_mod = 1.0
        if hasattr(character, "mining_yield_mod"):
            mining_yield_mod = character.mining_yield_mod

        # Apply engineering skill bonus (1% per point above 5)
        if character.engineering > 5:
            engineering_bonus = 1 + ((character.engineering - 5) * 0.01)
            mining_yield_mod *= engineering_bonus

        # Adjust mining speed based on traits
        effective_mining_speed: float = self.mining_speed * mining_yield_mod

        # Check for Forgetful negative trait - 5% chance to lose ore while mining
        forgetful_chance = 0.0
        if (
            hasattr(character, "negative_trait")
            and character.negative_trait == "Forgetful"
        ):
            forgetful_chance = 0.05  # 5% chance to lose ore
            print(
                "Warning: Your forgetful nature might cause you to misplace some minerals."
            )

        # Initialize mining variables
        asteroid_being_mined: Asteroid | None = None
        ores_mined: list[OreCargo] = []
        mined_volume: float = 0
        time_spent = 0
        lost_ore_count = 0

        # Begin mining loop
        while (not mine_until_full and int(time_spent) < int(time_to_mine)) or (
            mine_until_full and not self.is_cargo_full()
        ):
            # Find a new asteroid to mine if needed
            if asteroid_being_mined is None or asteroid_being_mined.volume <= 0:
                asteroid_being_mined = next(
                    (
                        asteroid
                        for asteroid in asteroid_field.asteroids
                        if asteroid.volume > 0
                    ),
                    None,
                )
                if asteroid_being_mined is None:
                    print("No more asteroids available to mine.")
                    continue

            # Access the ore in the asteroid
            ore = asteroid_being_mined.ore

            # If specific ores are selected, validate they match the current asteroid's ore
            if ores_selected_list is not None:
                if ore.name.lower() not in (
                    ore_name.lower() for ore_name in ores_selected_list
                ):
                    print(
                        f"Skipping {ore.name}, as it is not in the selected ores list."
                    )
                    asteroid_being_mined = None
                    break

            # Check if the ore fits in the remaining cargo capacity
            if self.cargohold_occupied + ore.volume > self.cargohold_capacity:
                print(
                    f"Cannot mine more {ore.name} because it exceeds the ship's cargo capacity."
                )
                break  # Stop mining if no further ores can be added safely

            # Apply forgetful trait - chance to lose ore
            import random

            if forgetful_chance > 0 and random.random() < forgetful_chance:
                # Ore is mined but "lost"
                lost_ore_count += 1
                asteroid_being_mined.volume -= ore.volume
                time_spent += 1
                continue  # Skip adding to cargo

            # Add the ore to mined cargo
            ore_cargo = next(
                (cargo for cargo in ores_mined if cargo.ore.id == ore.id), None
            )
            if ore_cargo:
                ore_cargo.quantity += 1
            else:
                ores_mined.append(OreCargo(ore, 1, ore.base_value, ore.base_value))

            # Decrease the asteroid's volume and update ship's cargo data
            asteroid_being_mined.volume -= ore.volume
            self.cargohold_occupied += ore.volume
            mined_volume += effective_mining_speed
            time_spent += 1

        # Summarize mined results
        total_volume = sum(cargo.quantity * cargo.ore.volume for cargo in ores_mined)
        total_quantity = sum(cargo.quantity for cargo in ores_mined)
        ore_names = {cargo.ore.name for cargo in ores_mined}

        # Update the ship's cargo hold with mined ores
        for ore_cargo in ores_mined:
            existing_cargo = self.get_ore_cargo_by_id(ore_cargo.ore.id)
            if existing_cargo:
                existing_cargo.quantity += ore_cargo.quantity
            else:
                self.cargohold.append(ore_cargo)

        if total_quantity > 0:
            print(
                f"Mined {total_quantity} units of {', '.join(ore_names)} for {total_volume:.2f} m³"
            )
            if lost_ore_count > 0:
                print(
                    f"You somehow misplaced {lost_ore_count} units of ore during mining. How forgetful!"
                )
        else:
            print("No ores were mined.")

        # Recalculate cargo occupancy and update global game time
        self.calculate_cargo_occupancy()
        print(f"Time spent mining: {time_spent} seconds.")
        game_state.global_time += time_spent

    def calculate_cargo_occupancy(self):
        self.cargohold_occupied = sum(
            cargo.quantity * cargo.ore.volume for cargo in self.cargohold
        )

    def is_cargo_full(self) -> bool:
        return self.cargohold_occupied == self.cargohold_capacity

    def check_field_presence(self, game_state) -> Tuple[bool, Optional[AsteroidField]]:
        for field in game_state.get_current_solar_system().asteroid_fields:  # MODIFIED
            if self.interaction_radius > euclidean_distance(
                self.space_object.position, field.space_object.position
            ):
                return True, field
        return False, None

    def scan_field(self, game_state) -> None:
        fields: list[AsteroidField] = game_state.get_current_solar_system().asteroid_fields  # MODIFIED

        is_inside_field, field = self.check_field_presence(game_state)

        if not is_inside_field or field is None:
            print("You are not inside a field.")
            return

        for ore in field.ores_available:
            print(f"{ore.name} - {ore.volume} m3")

    def to_dict(self):
        return {
            "name": self.name,
            "position": {
                "x": self.space_object.position.x,
                "y": self.space_object.position.y,
            },
            "speed": self.moves.speed,            "max_fuel": self.max_fuel,
            "fuel": self.fuel,
            "fuel_consumption": self.fuel_consumption,
            "power": self.power,
            "max_power": self.max_power,
            "cargo_capacity": self.cargohold_capacity,
            "cargohold_occupied": self.cargohold_occupied,
            "cargohold": [cargo.to_dict() for cargo in self.cargohold],
            "value": self.value,
            "mining_speed": self.mining_speed,
            "sensor_range": self.sensor_range,
            "is_docked": self.is_docked,
            "docked_at_id": self.docked_at.space_object.id if self.docked_at else None,
            "applied_upgrades": {
                upgrade_id: upgrade.to_dict()
                for upgrade_id, upgrade in self.applied_upgrades.items()
            },
            "hull_integrity": self.hull_integrity,
            "shield_capacity": self.shield_capacity,
        }

    @classmethod
    def from_dict(cls, data, game_state):  # Added game_state parameter
        ship = cls(
            name=data["name"],
            position=Vector2(data["position"]["x"], data["position"]["y"]),
            speed=data["speed"],
            max_fuel=data["max_fuel"],
            fuel_consumption=data["fuel_consumption"],
            cargo_capacity=data["cargo_capacity"],
            value=data["value"],            mining_speed=data["mining_speed"],
            sensor_range=data["sensor_range"],
        )
        ship.fuel = data["fuel"]
        
        # Load power attributes if they exist in saved data, otherwise use defaults
        if "power" in data:
            ship.power = data["power"]
        if "max_power" in data:
            ship.max_power = data["max_power"]
            
        ship.cargohold_occupied = data["cargohold_occupied"]
        ship.cargohold = [
            OreCargo.from_dict(cargo_data) for cargo_data in data["cargohold"]
        ]
        ship.is_docked = data["is_docked"]

        # Load applied upgrades if present
        if "applied_upgrades" in data:
            from src.data import Upgrade

            ship.applied_upgrades = {
                upgrade_id: Upgrade.from_dict(upgrade_data)
                for upgrade_id, upgrade_data in data["applied_upgrades"].items()
            }

        # Load hull and shield stats if present
        if "hull_integrity" in data:
            ship.hull_integrity = data["hull_integrity"]
        if "shield_capacity" in data:
            ship.shield_capacity = data["shield_capacity"]

        if data["docked_at_id"] is not None:
            # Find the station instance from the game_state
            docked_station = next(
                (
                    s
                    for s in game_state.get_current_solar_system().stations  # MODIFIED
                    if s.space_object.id == data["docked_at_id"]
                ),
                None,
            )
            if docked_station:
                ship.docked_at = docked_station
            else:
                # Handle case where station might not be found (e.g. corrupted save)
                print(
                    f"Warning: Docked station with ID {data['docked_at_id']} not found during ship deserialization."
                )
                ship.docked_at = None
        else:
            ship.docked_at = None
        return ship
        
    @classmethod
    def from_template(
        cls, template_id: str, name: Optional[str] = None
    ) -> "Ship":
        """
        Create a ship from a predefined template in SHIP_TEMPLATES

        Args:
            template_id (str): ID of the template in SHIP_TEMPLATES
            name (str, optional): Custom name for the ship. If None, uses template name.

        Returns:
            Ship: A new Ship instance with properties from the template
        """
        if template_id not in SHIP_TEMPLATES:
            raise ValueError(f"Template {template_id} not found in SHIP_TEMPLATES")

        template = SHIP_TEMPLATES[template_id]
        ship_name: str = str(name) if name is not None else str(template["name"])

        # Create the ship with properties from the template, safely converting to expected types
        ship = cls(
            name=ship_name,
            speed=template["speed"] if isinstance(template["speed"], (int, float)) else 1.0,
            max_fuel=template["max_fuel"] if isinstance(template["max_fuel"], (int, float)) else 100.0,
            fuel_consumption=template["fuel_consumption"] if isinstance(template["fuel_consumption"], (int, float)) else 1.0,
            cargo_capacity=template["cargo_capacity"] if isinstance(template["cargo_capacity"], (int, float)) else 100.0,
            value=template["value"] if isinstance(template["value"], (int, float)) else 10000.0,
            mining_speed=template["mining_speed"] if isinstance(template["mining_speed"], (int, float)) else 1.0,
            sensor_range=template["sensor_range"] if isinstance(template["sensor_range"], (int, float)) else 1.0,
            appearance=str(template["description"]),
        )

        # Set additional properties that aren't part of the __init__ params
        ship.hull_integrity = template["hull_integrity"] if isinstance(template["hull_integrity"], (int, float)) else 100.0
        ship.shield_capacity = template["shield_capacity"] if isinstance(template["shield_capacity"], (int, float)) else 0.0
        
        signature = template.get("sensor_signature", 1.0)
        ship.sensor_signature = signature if isinstance(signature, (int, float)) else 1.0
        antimatter = template.get("antimatter_capacity", 5.0)
        ship.max_antimatter = antimatter if isinstance(antimatter, (int, float)) else 5.0
        ship.antimatter = ship.max_antimatter  # Start with full antimatter
        
        # Set antimatter consumption rate from template (default 0.05g per LY)
        antimatter_consumption = template.get("antimatter_consumption", 0.05)
        ship.antimatter_consumption = antimatter_consumption if isinstance(antimatter_consumption, (int, float)) else 0.05

        # Set the engine if specified
        engine_id = str(template.get("engine_id", "standard"))
        if engine_id in ENGINES:
            engine_obj = ENGINES[engine_id]
            ship.engine = Engine(
                id=engine_obj.id,
                name=engine_obj.name,
                description=engine_obj.description,
                engine_type=engine_obj.engine_type,
                price=engine_obj.price,
                speed_modifier=engine_obj.speed_modifier,
                fuel_consumption_modifier=engine_obj.fuel_consumption_modifier,
                sensor_signature_modifier=engine_obj.sensor_signature_modifier,
                maintenance_cost_modifier=engine_obj.maintenance_cost_modifier,
                magneton_resistance=getattr(engine_obj, "magneton_resistance", 0.0),
            )
            # Apply engine modifiers
            ship.moves.speed *= engine_obj.speed_modifier
            ship.fuel_consumption *= engine_obj.fuel_consumption_modifier
            ship.sensor_signature *= engine_obj.sensor_signature_modifier

        return ship

    def apply_upgrade(self, upgrade: Upgrade) -> bool:
        """Apply an upgrade to the ship if eligible

        Args:
            upgrade: The upgrade to apply

        Returns:
            bool: True if upgrade was applied, False otherwise
        """
        # Check if upgrade already at max level
        if upgrade.id in self.applied_upgrades:
            existing_upgrade = self.applied_upgrades[upgrade.id]
            if existing_upgrade.level >= existing_upgrade.max_level:
                return False

        # Apply upgrade effects based on target
        if upgrade.target == UpgradeTarget.SPEED:
            self.moves.speed *= upgrade.multiplier

        elif upgrade.target == UpgradeTarget.MINING_SPEED:
            self.mining_speed *= upgrade.multiplier

        elif upgrade.target == UpgradeTarget.FUEL_CONSUMPTION:
            self.fuel_consumption *= upgrade.multiplier

        elif upgrade.target == UpgradeTarget.FUEL_CAPACITY:
            old_capacity = self.max_fuel
            self.max_fuel *= upgrade.multiplier
            # Refill the added capacity
            self.fuel += self.max_fuel - old_capacity

        elif upgrade.target == UpgradeTarget.CARGO_CAPACITY:
            self.cargohold_capacity *= upgrade.multiplier

        elif upgrade.target == UpgradeTarget.SENSOR_RANGE:
            self.sensor_range *= upgrade.multiplier

        elif upgrade.target == UpgradeTarget.HULL_INTEGRITY:
            self.hull_integrity *= upgrade.multiplier

        elif upgrade.target == UpgradeTarget.SHIELD_CAPACITY:
            self.shield_capacity = max(0.1, self.shield_capacity * upgrade.multiplier)

        # Store the applied upgrade
        if upgrade.id in self.applied_upgrades:
            self.applied_upgrades[upgrade.id].level += 1
        else:
            self.applied_upgrades[upgrade.id] = upgrade.copy()

        return True

    def get_upgrade_effect_preview(self, upgrade: Upgrade) -> dict:
        """Preview the effects of applying an upgrade without actually applying it

        Args:
            upgrade: The upgrade to preview

        Returns:
            dict: Dictionary with before/after values for the affected attribute
        """
        result = {
            "attribute": upgrade.target.name.lower(),
            "before": 0.0,  # Initialize as float
            "after": 0.0,  # Initialize as float
        }

        # Get current value based on target
        if upgrade.target == UpgradeTarget.SPEED:
            result["before"] = float(self.moves.speed)
            result["after"] = float(self.moves.speed * upgrade.multiplier)

        elif upgrade.target == UpgradeTarget.MINING_SPEED:
            result["before"] = float(self.mining_speed)
            result["after"] = float(self.mining_speed * upgrade.multiplier)

        elif upgrade.target == UpgradeTarget.FUEL_CONSUMPTION:
            result["before"] = float(self.fuel_consumption)
            result["after"] = float(self.fuel_consumption * upgrade.multiplier)

        elif upgrade.target == UpgradeTarget.FUEL_CAPACITY:
            result["before"] = float(self.max_fuel)
            result["after"] = float(self.max_fuel * upgrade.multiplier)

        elif upgrade.target == UpgradeTarget.CARGO_CAPACITY:
            result["before"] = float(self.cargohold_capacity)
            result["after"] = float(self.cargohold_capacity * upgrade.multiplier)

        elif upgrade.target == UpgradeTarget.SENSOR_RANGE:
            result["before"] = float(self.sensor_range)
            result["after"] = float(self.sensor_range * upgrade.multiplier)

        elif upgrade.target == UpgradeTarget.HULL_INTEGRITY:
            result["before"] = float(self.hull_integrity)
            result["after"] = float(self.hull_integrity * upgrade.multiplier)

        elif upgrade.target == UpgradeTarget.SHIELD_CAPACITY:
            result["before"] = float(self.shield_capacity)
            result["after"] = float(max(0.1, self.shield_capacity * upgrade.multiplier))

        return result

    def can_apply_upgrade(self, upgrade_id: str) -> bool:
        """Check if an upgrade can be applied based on prerequisites

        Args:
            upgrade_id: The ID of the upgrade to check

        Returns:
            bool: True if the upgrade can be applied
        """
        from src.data import UPGRADES

        if upgrade_id not in UPGRADES:
            return False

        upgrade = UPGRADES[upgrade_id]

        # Check if already at max level
        if upgrade_id in self.applied_upgrades:
            if self.applied_upgrades[upgrade_id].level >= upgrade.max_level:
                return False

        # Check prerequisites
        if upgrade.prerequisites:
            for prereq_id in upgrade.prerequisites:
                if prereq_id not in self.applied_upgrades:
                    return False

        return True

    def get_available_upgrades(self) -> List[Upgrade]:
        """Get list of upgrades that can be applied to this ship

        Returns:
            List[Upgrade]: List of available upgrades
        """
        from src.data import UPGRADES

        available = []
        for upgrade_id, upgrade in UPGRADES.items():
            if self.can_apply_upgrade(upgrade_id):
                available.append(upgrade)

        return available

    def add_credits(self, game_state, amount: float) -> float:
        """Add credits to the player and ensure they're rounded properly

        Args:
            game_state: The game state containing the player character
            amount: The amount of credits to add

        Returns:
            float: New credit balance
        """
        return float(game_state.get_player_character().add_credits(amount))

    def remove_credits(self, game_state, amount: float) -> float:
        """Remove credits from the player and ensure they're rounded properly

        Args:
            game_state: The game state containing the player character
            amount: The amount of credits to remove

        Returns:
            float: New credit balance
        """
        return float(game_state.get_player_character().remove_credits(amount))
        
    def repair_containment(self, repair_amount: float) -> None:
        """Repair the antimatter containment system by the specified amount
        
        Args:
            repair_amount: The percentage points to repair
        """
        self.containment_integrity = min(100.0, self.containment_integrity + repair_amount)
        self.containment_failure_risk = max(0.0, self.containment_failure_risk - (repair_amount / 2.0))
        self.last_containment_check = 0  # Reset the check timer
        
    def emergency_antimatter_ejection(self) -> bool:
        """Emergency procedure to eject all antimatter from the ship
        
        Returns:
            bool: True if successful, False if failed
        """
        if self.antimatter <= 0:
            return False
            
        # Reset antimatter to 0
        self.antimatter = 0.0
        
        # Stabilize containment
        self.containment_failure_risk = 0.0
        
        # Apply some wear on the containment system from emergency procedures
        self.containment_integrity = max(70.0, self.containment_integrity - 10.0)
        
        return True
        
    def check_containment_status(self, game_state) -> tuple[bool, float]:
        """Check the status of the antimatter containment system
        
        Args:
            game_state: The game state containing global time
            
        Returns:
            tuple: (is_safe, failure_risk_percentage)
        """
        # Calculate time since last check
        time_since_check = game_state.global_time - self.last_containment_check
        
        # Update last check time
        self.last_containment_check = game_state.global_time
        
        # Calculate risk based on integrity and time passed
        base_risk = 100.0 - self.containment_integrity
        time_factor = time_since_check / 3600.0  # Convert to hours
        
        # Increase risk over time (0.1% per hour at 100% integrity, more at lower integrity)
        added_risk = time_factor * (0.1 + (1.0 - self.containment_integrity / 100.0))
        
        # Update the containment failure risk
        self.containment_failure_risk = min(100.0, base_risk + added_risk)
        
        # Containment is considered safe if the risk is below 10%
        is_safe = self.containment_failure_risk < 10.0
        
        return is_safe, self.containment_failure_risk
        
    def ftl_jump(self, game_state, destination: str, distance: float) -> tuple[bool, str]:
        """Perform an FTL jump to another system
        
        Args:
            game_state: The game state
            destination: Name of the destination system
            distance: Distance to the destination in light-years
            
        Returns:
            tuple: (success, message)
        """
        # Check if there's enough antimatter
        required_antimatter = distance * self.antimatter_consumption
        if self.antimatter < required_antimatter:
            return False, f"Insufficient antimatter. Need {required_antimatter:.2f}g for this jump."
            
        # Check containment integrity
        containment_ok, risk = self.check_containment_status(game_state)
        if not containment_ok:
            return False, f"Antimatter containment unstable ({risk:.1f}% failure risk)."
            
        # Calculate risk of jump failure based on containment integrity
        jump_risk = risk * 0.1  # 10% of containment risk affects jump success
        
        # Apply character's piloting skill to reduce risk if applicable
        character = game_state.get_player_character()
        if character and hasattr(character, "piloting"):
            # Reduce risk based on piloting skill (higher is better)
            piloting_factor = max(0.5, 1.0 - (character.piloting * 0.02))
            jump_risk *= piloting_factor
        
        # If random chance exceeds risk, the jump is successful
        import random
        if random.random() > (jump_risk / 100.0):
            # Consume antimatter
            self.antimatter -= required_antimatter
            
            # Add travel time (FTL is fast but not instant)
            ftl_travel_time = distance * 60.0  # 1 light-year takes 60 seconds
            game_state.global_time += ftl_travel_time
            
            # Apply some wear to containment from the jump
            self.containment_integrity = max(0, self.containment_integrity - (distance * 0.5))
            
            return True, f"Successfully jumped to {destination} in {format_seconds(ftl_travel_time)}."
        else:
            # Failed jump still consumes antimatter but less than a successful one
            self.antimatter -= required_antimatter * 0.5
            
            # Damage containment system due to failure
            self.containment_integrity = max(0, self.containment_integrity - (distance * 2.0))
            self.containment_failure_risk += distance * 1.5
            
            return False, "FTL jump failed. Drive malfunction caused partial antimatter loss."

    def consume_antimatter(self, value: float) -> None:
        """Consume a specified amount of antimatter fuel."""
        self.antimatter -= value

    def refuel_antimatter(self, value: float) -> None:
        """Refuel the ship's antimatter supply."""
        self.antimatter = min(self.max_antimatter, self.antimatter + value)

    def check_containment_integrity(self, current_time: int) -> None:
        """Check and update the containment integrity of the antimatter system."""
        time_elapsed = current_time - self.last_containment_check
        self.containment_integrity -= time_elapsed * self.containment_power_draw
        self.last_containment_check = current_time

