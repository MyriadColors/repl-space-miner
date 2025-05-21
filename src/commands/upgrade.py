from typing import Optional, Dict, List
from src.classes.game import Game
from src.data import UPGRADES, Upgrade
from .registry import Argument
from .base import register_command


def upgrade_command(game_state: Game, args: Optional[List[str]] = None) -> None:
    """
    Allow purchasing upgrades for the player's ship when docked at a station.

    Args:
        game_state: The game state object
        args: Command arguments (optional)
            - list: Show list of available upgrades
            - <upgrade_id>: Purchase a specific upgrade
    """
    # Debug: Print arguments to understand what's being passed
    game_state.ui.info_message(f"Debug: Upgrade command received args: {args}")

    player_ship = game_state.get_player_ship()
    if not player_ship.is_docked:
        game_state.ui.error_message(
            "You need to be docked at a station to purchase ship upgrades."
        )
        return

    # Determine if the command is to list upgrades or purchase an item
    action_is_list = False
    purchase_target_id: Optional[str] = None

    if args is None:
        action_is_list = True
    elif isinstance(
        args, str
    ):  # Handle if args is passed as a string (e.g., "list" or "upgrade_id")
        if args.lower() == "list":
            action_is_list = True
        else:
            purchase_target_id = args
    elif isinstance(args, list):
        if not args:  # Empty list
            action_is_list = True
        elif args[0].lower() == "list":  # First element is "list"
            action_is_list = True
        else:
            # Non-empty list, and first arg is not "list", so it's an upgrade_id
            purchase_target_id = args[0]
    # else: args might be an unexpected type.
    # If so, action_is_list is False and purchase_target_id is None,
    # leading to an error message in the purchase path if not listing.

    if action_is_list:
        # This block is the original code for listing available upgrades
        available_upgrades = player_ship.get_available_upgrades()

        if not available_upgrades:
            game_state.ui.warn_message(
                "No upgrades available for your ship at this time."
            )
            return

        game_state.ui.info_message("=== AVAILABLE SHIP UPGRADES ===")
        game_state.ui.info_message(f"Credits available: {game_state.get_credits():.2f}")
        game_state.ui.info_message("")

        # Group upgrades by category for better presentation
        by_category: Dict[str, List[Upgrade]] = {}
        for upgrade in available_upgrades:
            category = upgrade.category.name
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(upgrade)

        for (
            category,
            upgrades_in_cat,
        ) in by_category.items():  # Renamed 'upgrades' to 'upgrades_in_cat' for clarity
            game_state.ui.info_message(f"--- {category} UPGRADES ---")
            for (
                current_upgrade_obj
            ) in upgrades_in_cat:  # Renamed 'upgrade' to 'current_upgrade_obj'
                level_info = ""
                current_level = 1
                if current_upgrade_obj.id in player_ship.applied_upgrades:
                    current_level = player_ship.applied_upgrades[
                        current_upgrade_obj.id
                    ].level
                    level_info = f" (Current: Level {current_level}/{current_upgrade_obj.max_level})"

                price = (
                    current_upgrade_obj.get_next_level_price()
                    if current_level > 1
                    and current_upgrade_obj.id in player_ship.applied_upgrades
                    else current_upgrade_obj.price
                )
                game_state.ui.info_message(  # Changed formatting to make ID more explicit
                    f"ID: {current_upgrade_obj.id} - {current_upgrade_obj.name}{level_info} - {price:.2f} credits"
                )
                game_state.ui.info_message(f"  {current_upgrade_obj.description}")

                # Show preview of effects (only if not maxed out)
                if not (
                    current_level >= current_upgrade_obj.max_level
                    and current_upgrade_obj.id in player_ship.applied_upgrades
                ):
                    preview = player_ship.get_upgrade_effect_preview(
                        current_upgrade_obj
                    )
                    attribute_name = preview["attribute"].replace("_", " ").title()

                    precision = preview.get("display_precision", 2)
                    unit = preview.get("unit", "")

                    if preview["is_positive"] == False:
                        value_format = f"  Effect: {attribute_name} {{:.{precision}f}} → {{:.{precision}f}} ({{:+.1f}}%)"
                        if unit:
                            value_format = f"  Effect: {attribute_name} {{:.{precision}f}} {unit} → {{:.{precision}f}} {unit} ({{:+.1f}}%)"

                        game_state.ui.info_message(
                            value_format.format(
                                preview["before"],
                                preview["after"],
                                preview["percent_change"],
                            )
                        )

                        change_symbol = (
                            "▼" if preview["after"] < preview["before"] else "▲"
                        )
                        game_state.ui.info_message(
                            f"  {change_symbol} {'Improved efficiency! ✓' if preview['after'] < preview['before'] else 'Reduced efficiency! ⚠'}"
                        )
                    else:
                        value_format = f"  Effect: {attribute_name} {{:.{precision}f}} → {{:.{precision}f}} ({{:+.1f}}%)"
                        if unit:
                            value_format = f"  Effect: {attribute_name} {{:.{precision}f}} {unit} → {{:.{precision}f}} {unit} ({{:+.1f}}%)"

                        game_state.ui.info_message(
                            value_format.format(
                                preview["before"],
                                preview["after"],
                                preview["percent_change"],
                            )
                        )

                        change_symbol = (
                            "▲" if preview["after"] > preview["before"] else "▼"
                        )
                        evaluation = (
                            "Improved! ✓"
                            if preview["after"] > preview["before"]
                            else "Reduced! ⚠"
                        )
                        game_state.ui.info_message(f"  {change_symbol} {evaluation}")

                game_state.ui.info_message("")  # Blank line after each upgrade

        game_state.ui.info_message("To purchase an upgrade, use: upgrade <upgrade_id>")
        return
    # else, (if not action_is_list) proceed to purchase logic

    # Purchase a specific upgrade
    if purchase_target_id is None:
        # This case implies args was not 'list', not a valid ID string/list, or an unexpected type.
        game_state.ui.error_message(
            "Invalid arguments for upgrade command. Specify an upgrade ID or use 'upgrade list'."
        )
        return

    upgrade_id = purchase_target_id  # Use the determined ID for purchase

    if upgrade_id not in UPGRADES:
        game_state.ui.error_message(f"Unknown upgrade: {upgrade_id}")
        game_state.ui.info_message("Use 'upgrade list' to see available upgrades.")
        return

    # Check if upgrade can be applied
    if not player_ship.can_apply_upgrade(upgrade_id):
        # Check if it's due to max level
        if upgrade_id in player_ship.applied_upgrades:
            if (
                player_ship.applied_upgrades[upgrade_id].level
                >= UPGRADES[upgrade_id].max_level
            ):
                game_state.ui.error_message(
                    f"You've already reached the maximum level for {UPGRADES[upgrade_id].name}."
                )
                return

        # Check for prerequisites
        upgrade = UPGRADES[upgrade_id]
        if upgrade.prerequisites is not None:
            missing = [
                prereq_id
                for prereq_id in upgrade.prerequisites
                if prereq_id not in player_ship.applied_upgrades
            ]
            if missing:
                prereq_names = [UPGRADES[m].name for m in missing]
                game_state.ui.error_message(
                    f"You need the following upgrades first: {', '.join(prereq_names)}"
                )
                return

        game_state.ui.error_message(
            "This upgrade cannot be applied to your ship right now."
        )
        return

    # Calculate price
    base_price = UPGRADES[upgrade_id].price
    current_level = 1
    if upgrade_id in player_ship.applied_upgrades:
        current_level = player_ship.applied_upgrades[upgrade_id].level

    price = base_price
    if current_level > 1:
        price = UPGRADES[upgrade_id].get_next_level_price()

    # Check if player can afford it
    player_credits = game_state.get_credits()
    if player_credits is None:
        game_state.ui.error_message("Error: Unable to get player credits.")
        return

    if player_credits < price:
        game_state.ui.error_message(
            f"You don't have enough credits. The upgrade costs {price:.2f} credits."
        )
        return

    # Show detailed upgrade preview with confirmation
    upgrade = UPGRADES[upgrade_id]
    preview = player_ship.get_upgrade_effect_preview(upgrade)

    # Prepare a formatted display of the upgrade effect
    attribute_name = preview["attribute"].replace("_", " ").title()
    precision = preview.get("display_precision", 2)
    unit = preview.get("unit", "")

    # Show confirmation message with formatted values
    game_state.ui.info_message(f"=== UPGRADE CONFIRMATION ===")
    game_state.ui.info_message(f"Purchase {upgrade.name} for {price:.2f} credits?")

    # Display level information if applicable
    if upgrade_id in player_ship.applied_upgrades:
        current_level = player_ship.applied_upgrades[upgrade_id].level
        next_level = current_level + 1
        game_state.ui.info_message(
            f"This will upgrade from Level {current_level} to Level {next_level}."
        )

    game_state.ui.info_message(f"\nUpgrade effect on your ship:")

    # Format the display based on the attribute type
    if unit:
        value_format = f"{attribute_name}: {{:.{precision}f}} {unit} → {{:.{precision}f}} {unit} ({{:+.1f}}%)"
    else:
        value_format = (
            f"{attribute_name}: {{:.{precision}f}} → {{:.{precision}f}} ({{:+.1f}}%)"
        )

    game_state.ui.info_message(
        value_format.format(
            preview["before"], preview["after"], preview["percent_change"]
        )
    )

    # Provide evaluation of the effect
    if preview["is_positive"] == False:  # For attributes where lower is better
        if preview["after"] < preview["before"]:
            game_state.ui.info_message(
                "✓ This upgrade will improve your ship's efficiency."
            )
        else:
            game_state.ui.warn_message(
                "⚠ Warning: This upgrade will reduce your ship's efficiency."
            )
    else:  # For attributes where higher is better
        if preview["after"] > preview["before"]:
            game_state.ui.info_message(
                "✓ This upgrade will improve your ship's performance."
            )
        else:
            game_state.ui.warn_message(
                "⚠ Warning: This upgrade will reduce your ship's performance."
            )

    # Financial impact
    game_state.ui.info_message(f"\nFinancial impact:")
    credits = game_state.get_credits()
    if credits is not None:
        game_state.ui.info_message(f"Credits: {credits:.2f} → {credits - price:.2f}")
    else:
        game_state.ui.warn_message(
            "Warning: Unable to determine credits for financial impact."
        )

    # Confirmation prompt
    game_state.ui.info_message(f"\nConfirm purchase? (y/n)")
    response = input("Your choice: ")
    if response.lower() != "y":
        game_state.ui.info_message("Purchase cancelled.")
        return

    # Apply upgrade and deduct credits
    result = player_ship.apply_upgrade(upgrade)
    if result:
        if game_state.player_character is None:
            game_state.ui.error_message("Error: Player character not found.")
            return

        game_state.player_character.credits -= price

        # Show success message with details about the upgrade effect
        level_str = ""
        if upgrade_id in player_ship.applied_upgrades:
            level = player_ship.applied_upgrades[upgrade_id].level
            if level > 1:
                level_str = f" (Level {level})"

        game_state.ui.success_message(
            f"Successfully installed {upgrade.name}{level_str}!"
        )

        # Show the actual effect that was applied
        if unit:
            effect_str = f"{attribute_name} is now {preview['after']:.{precision}f} {unit} (+{preview['percent_change']:.1f}%)"
        else:
            effect_str = f"{attribute_name} is now {preview['after']:.{precision}f} (+{preview['percent_change']:.1f}%)"

        game_state.ui.info_message(effect_str)
        game_state.ui.info_message(f"Credits remaining: {game_state.get_credits():.2f}")
    else:
        game_state.ui.error_message(
            "Failed to apply upgrade. Please report this as a bug."
        )


# Register upgrade command
register_command(
    ["upgrade", "upg"],
    upgrade_command,
    [Argument("args", list, True)],
)
