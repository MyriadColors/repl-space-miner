from src.classes.game import Game
from src.events.skill_events import process_skill_xp_from_activity, notify_skill_progress

from .registry import Argument
from .base import register_command


def mine_command(
    game_state: Game,
    time_to_mine: int,
    mine_until_full: bool,
    ore_selected: str | None,
) -> None:
    """Handle mining command execution."""
    player_ship = game_state.get_player_ship()

    # Check if ship is in an asteroid field
    is_in_field, field = player_ship.check_field_presence(game_state)
    if not is_in_field or field is None:
        game_state.ui.error_message("You must be in an asteroid field to mine.")
        return

    # Check if cargo is full
    if player_ship.is_cargo_full():
        game_state.ui.error_message("Your cargo hold is full.")
        return

    # Convert ore_selected to list if provided
    ores_selected_list = [ore_selected] if ore_selected else None

    # Execute mining
    time_spent = player_ship.mine_belt(
        game_state,
        field,
        time_to_mine,
        mine_until_full,
        ores_selected_list,
    )    # Check for debt interest after mining (time has passed)
    if game_state.player_character:
        # Process skill experience from mining
        skill_results = process_skill_xp_from_activity(
            game_state, 
            "mining", 
            difficulty=field.rarity_score * 0.5  # MODIFIED: Use rarity_score
        )
        notify_skill_progress(game_state, skill_results)
        
        # Calculate debt interest
        interest_result = game_state.player_character.calculate_debt_interest(
            int(game_state.global_time / 3600)  # Convert seconds to hours and cast to int
        )
        if interest_result:
            interest_amount, new_debt = interest_result
            game_state.ui.warn_message(f"\n⚠️ DEBT ALERT! ⚠️")
            game_state.ui.warn_message(
                f"While mining, {interest_amount:.2f} credits of interest has accumulated on your debt!"
            )
            game_state.ui.warn_message(
                f"Your current debt is now {new_debt:.2f} credits."
            )

            # Suggest selling ore to pay debt if cargo is valuable
            if player_ship.cargohold:
                total_cargo_value = sum(
                    cargo.quantity * cargo.sell_price for cargo in player_ship.cargohold
                )
                if total_cargo_value > 0:
                    game_state.ui.info_message(
                        f"Your current cargo is worth approximately {total_cargo_value:.2f} credits."
                    )
                    if (
                        total_cargo_value > new_debt * 0.2
                    ):  # If cargo can pay off at least 20% of debt
                        game_state.ui.info_message(
                            "Consider selling your cargo and paying down your debt at a station."
                        )

            # Additional warnings based on debt level
            if new_debt > 12000:
                game_state.ui.error_message(
                    "URGENT: Your debt has reached critical levels! Debt collectors may be dispatched soon!"
                )
                game_state.ui.info_message(
                    "Return to a station immediately to manage your finances."
                )
            elif new_debt > 8000:
                game_state.ui.error_message(
                    "Your debt is at dangerous levels. Pay it down soon to avoid penalties."
                )

    return


def scan_mining_field_command(game_state: Game) -> None:
    """Handle scanning asteroid field command."""
    player_ship = game_state.get_player_ship()
    if not player_ship:
        game_state.ui.error_message("Error: Player ship not found.")
        return
    player_ship.scan_field(game_state)


# Register mining commands
register_command(
    ["mine", "m"],
    mine_command,
    [
        Argument("time_to_mine", int, False),
        Argument("mine_until_full", bool, True),
        Argument("ore_selected", str, True),
    ],
)

register_command(
    ["scan_mining", "sm"],
    scan_mining_field_command,
    [],
)
