from typing import Optional
import time
from datetime import datetime

from colorama import Fore, Style
from src.classes.game import Game
from src.helpers import is_valid_float

from .base import register_command


class BankingTransaction:
    """Class to track banking transactions"""

    def __init__(self, transaction_type: str, amount: float, description: str = ""):
        self.timestamp = datetime.now()
        self.transaction_type = (
            transaction_type  # "deposit", "withdraw", "loan", "repayment", "interest"
        )
        self.amount = amount
        self.description = description

    def to_string(self) -> str:
        """Format the transaction as a string"""
        time_str = self.timestamp.strftime("%Y-%m-%d %H:%M")
        return f"{time_str} | {self.transaction_type:10} | {self.amount:10.2f} | {self.description}"


def banking_menu_command(game_state: Game) -> None:
    """Main banking menu interface for all financial operations."""
    # Check if player is docked
    player_ship = game_state.get_player_ship()
    if not player_ship.is_docked:
        game_state.ui.error_message(
            "You need to be docked at a station to access banking services."
        )
        return

    character = game_state.get_player_character()
    if character is None:
        game_state.ui.error_message("Error: Player character not found.")
        return

    # Get station name
    docked_station = player_ship.get_docked_station()
    if docked_station is None:
        station_name = "UNKNOWN STATION"
    else:
        station_name = docked_station.name

    # Initialize transaction history if it doesn't exist
    if not hasattr(character, "bank_transactions"):
        character.bank_transactions = []

    # Initialize savings account if it doesn't exist
    if not hasattr(character, "savings"):
        character.savings = 0.0

    # Initialize savings interest rate if it doesn't exist
    if not hasattr(character, "savings_interest_rate"):
        character.savings_interest_rate = 0.02  # 2% weekly interest rate

    while True:
        game_state.ui.clear_screen()
        game_state.ui.info_message(f"\n{'=' * 50}")
        game_state.ui.info_message(
            f"{Fore.CYAN}GALACTIC BANKING NETWORK - {station_name}{Style.RESET_ALL}"
        )
        game_state.ui.info_message(f"{'=' * 50}")

        # Display financial summary
        display_financial_summary(game_state, character)

        # Main menu options
        game_state.ui.info_message(f"\n{Fore.YELLOW}Banking Services:{Style.RESET_ALL}")
        game_state.ui.info_message(f"1. Debt Management")
        game_state.ui.info_message(f"2. Loans")
        game_state.ui.info_message(f"3. Savings Account")
        game_state.ui.info_message(f"4. Transaction History")
        game_state.ui.info_message(f"5. Return to Station")

        choice = input(Fore.YELLOW + "Enter your choice (1-5): " + Style.RESET_ALL)

        if choice == "1":
            debt_management_menu(game_state, character)
        elif choice == "2":
            loan_menu(game_state, character)
        elif choice == "3":
            savings_menu(game_state, character)
        elif choice == "4":
            view_transaction_history(game_state, character)
        elif choice == "5":
            game_state.ui.info_message(
                "Thank you for using the Galactic Banking Network."
            )
            break
        else:
            game_state.ui.error_message("Invalid option. Please try again.")
            time.sleep(1)


def display_financial_summary(game_state: Game, character) -> None:
    """Display current financial status."""
    game_state.ui.info_message(f"\n{Fore.CYAN}Your Financial Status:{Style.RESET_ALL}")
    game_state.ui.info_message(f"Available Credits: {character.credits:.2f}")

    # Show savings with appropriate color
    if character.savings > 0:
        game_state.ui.success_message(
            f"Savings Account: {character.savings:.2f} credits (Interest: {character.savings_interest_rate:.1%}/week)"
        )
    else:
        game_state.ui.info_message(
            f"Savings Account: {character.savings:.2f} credits (Interest: {character.savings_interest_rate:.1%}/week)"
        )

    # Highlight debt with color based on amount
    debt = character.debt
    if debt <= 0:
        game_state.ui.success_message(f"Current Debt: {debt:.2f} credits (Debt-free!)")
    elif debt > 10000:
        game_state.ui.error_message(f"Current Debt: {debt:.2f} credits (HIGH)")
        game_state.ui.warn_message(
            f"Warning: High debt levels. Interest is accumulating rapidly!"
        )
    elif debt > 5000:
        game_state.ui.warn_message(f"Current Debt: {debt:.2f} credits (Moderate)")
    else:
        game_state.ui.info_message(
            f"Current Debt: {debt:.2f} credits (Low)"
        )  # Calculate daily interest
    daily_rate = 0.007 * character.debt_interest_mod
    daily_interest = debt * daily_rate

    if debt > 0:
        game_state.ui.info_message(f"Interest Rate: {daily_rate:.1%}/day")
        game_state.ui.info_message(f"Daily Interest: {daily_interest:.2f} credits")

        # Calculate time to pay off at current rate
        if game_state.global_time > 0 and character.credits > 0:
            # Very rough calculation based on current average income
            total_game_time_hours = game_state.global_time / 3600  # Convert to hours
            if total_game_time_hours > 0:
                credits_per_hour = character.credits / total_game_time_hours
                if credits_per_hour > 0:
                    hours_to_payoff = character.debt / credits_per_hour
                    days_to_payoff = hours_to_payoff / 24
                    game_state.ui.info_message(
                        f"At your current earning rate, you could pay off your debt in approximately {days_to_payoff:.1f} game days."
                    )


def debt_management_menu(game_state: Game, character) -> None:
    """Handle debt repayment options."""
    if character.debt <= 0:
        game_state.ui.success_message("\nYou are debt-free! Congratulations!")
        input(
            Fore.YELLOW + "Press Enter to return to banking menu..." + Style.RESET_ALL
        )
        return

    while True:
        game_state.ui.clear_screen()
        game_state.ui.info_message(f"\n{'=' * 50}")
        game_state.ui.info_message(f"{Fore.CYAN}DEBT MANAGEMENT{Style.RESET_ALL}")
        game_state.ui.info_message(f"{'=' * 50}")  # Show current debt status
        daily_rate = 0.007 * character.debt_interest_mod
        daily_interest = character.debt * daily_rate

        game_state.ui.info_message(f"\nCurrent Debt: {character.debt:.2f} credits")
        game_state.ui.info_message(f"Interest Rate: {daily_rate:.1%}/day")
        game_state.ui.info_message(f"Daily Interest: {daily_interest:.2f} credits")
        game_state.ui.info_message(f"Available Credits: {character.credits:.2f}")

        # Debt repayment options
        game_state.ui.info_message(
            f"\n{Fore.YELLOW}Repayment Options:{Style.RESET_ALL}"
        )
        game_state.ui.info_message(f"1. Make Custom Payment")
        game_state.ui.info_message(f"2. Pay in Full ({character.debt:.2f} credits)")
        game_state.ui.info_message(
            f"3. Pay Minimum (Interest Only: {daily_interest:.2f} credits)"
        )
        game_state.ui.info_message(f"4. Return to Banking Menu")

        choice = input(Fore.YELLOW + "Enter your choice (1-4): " + Style.RESET_ALL)

        if choice == "1":
            # Custom payment
            amount = get_valid_amount(
                game_state,
                "Enter amount to repay",
                0,
                min(character.credits, character.debt),
            )
            if amount is not None:
                repay_debt(game_state, character, amount)
        elif choice == "2":
            # Pay in full
            if character.credits >= character.debt:
                repay_debt(game_state, character, character.debt)
            else:
                game_state.ui.error_message(
                    "You don't have enough credits to pay your debt in full."
                )
                time.sleep(1.5)
        elif choice == "3":
            # Pay minimum (interest only)
            if character.credits >= daily_interest:
                repay_debt(game_state, character, daily_interest)
            else:
                game_state.ui.error_message(
                    "You don't have enough credits to make the minimum payment."
                )
                time.sleep(1.5)
        elif choice == "4":
            # Return to main menu
            break
        else:
            game_state.ui.error_message("Invalid option. Please try again.")
            time.sleep(1)


def loan_menu(game_state: Game, character) -> None:
    """Handle loan application and management."""
    while True:
        game_state.ui.clear_screen()
        game_state.ui.info_message(f"\n{'=' * 50}")
        game_state.ui.info_message(f"{Fore.CYAN}LOAN SERVICES{Style.RESET_ALL}")
        game_state.ui.info_message(f"{'=' * 50}")

        # Show current debt status
        max_loan = calculate_max_loan(game_state, character)
        daily_rate = 0.007 * character.debt_interest_mod

        game_state.ui.info_message(f"\nCurrent Debt: {character.debt:.2f} credits")
        game_state.ui.info_message(f"Available Credits: {character.credits:.2f}")
        game_state.ui.info_message(f"Interest Rate: {daily_rate:.1%}/day")

        # Credit score based on debt and repayment history
        credit_score = calculate_credit_score(game_state, character)
        credit_rating = get_credit_rating(credit_score)

        color = (
            Fore.GREEN
            if credit_score > 700
            else Fore.YELLOW if credit_score > 500 else Fore.RED
        )
        game_state.ui.info_message(
            f"Credit Score: {color}{credit_score}{Style.RESET_ALL} ({credit_rating})"
        )

        if max_loan > 0:
            game_state.ui.info_message(
                f"Maximum Loan Available: {max_loan:.2f} credits"
            )
        else:
            game_state.ui.warn_message(
                "You do not qualify for additional loans at this time."
            )

        # Loan options
        game_state.ui.info_message(f"\n{Fore.YELLOW}Loan Options:{Style.RESET_ALL}")
        game_state.ui.info_message(f"1. Apply for New Loan")
        game_state.ui.info_message(f"2. View Loan Terms")
        game_state.ui.info_message(f"3. Return to Banking Menu")

        choice = input(Fore.YELLOW + "Enter your choice (1-3): " + Style.RESET_ALL)

        if choice == "1":
            # Apply for loan
            if max_loan <= 0:
                game_state.ui.error_message(
                    "Your current credit rating does not qualify for a new loan."
                )
                time.sleep(1.5)
            else:
                apply_for_loan(game_state, character, max_loan)
        elif choice == "2":
            # View loan terms
            display_loan_terms(game_state, character)
        elif choice == "3":
            # Return to main menu
            break
        else:
            game_state.ui.error_message("Invalid option. Please try again.")
            time.sleep(1)


def savings_menu(game_state: Game, character) -> None:
    """Handle savings account operations."""
    while True:
        game_state.ui.clear_screen()
        game_state.ui.info_message(f"\n{'=' * 50}")
        game_state.ui.info_message(f"{Fore.CYAN}SAVINGS ACCOUNT{Style.RESET_ALL}")
        game_state.ui.info_message(f"{'=' * 50}")

        # Show current savings status
        game_state.ui.info_message(
            f"\nSavings Balance: {character.savings:.2f} credits"
        )
        game_state.ui.info_message(
            f"Interest Rate: {character.savings_interest_rate:.1%}/week"
        )
        game_state.ui.info_message(
            f"Available Credits: {character.credits:.2f}"
        )  # Calculate projected interest
        daily_interest_savings = character.savings * (
            character.savings_interest_rate / 7
        )  # Assuming weekly rate, convert to daily
        game_state.ui.info_message(
            f"Projected Daily Interest (Savings): +{daily_interest_savings:.2f} credits"
        )

        # Savings options
        game_state.ui.info_message(f"\n{Fore.YELLOW}Account Options:{Style.RESET_ALL}")
        game_state.ui.info_message(f"1. Deposit Credits")
        game_state.ui.info_message(f"2. Withdraw Credits")
        game_state.ui.info_message(f"3. Return to Banking Menu")

        choice = input(Fore.YELLOW + "Enter your choice (1-3): " + Style.RESET_ALL)

        if choice == "1":
            # Deposit funds
            amount = get_valid_amount(
                game_state, "Enter amount to deposit", 0, character.credits
            )
            if amount is not None:
                deposit_to_savings(game_state, character, amount)
        elif choice == "2":
            # Withdraw funds
            amount = get_valid_amount(
                game_state, "Enter amount to withdraw", 0, character.savings
            )
            if amount is not None:
                withdraw_from_savings(game_state, character, amount)
        elif choice == "3":
            # Return to main menu
            break
        else:
            game_state.ui.error_message("Invalid option. Please try again.")
            time.sleep(1)


def view_transaction_history(game_state: Game, character) -> None:
    """Display transaction history."""
    game_state.ui.clear_screen()
    game_state.ui.info_message(f"\n{'=' * 50}")
    game_state.ui.info_message(f"{Fore.CYAN}TRANSACTION HISTORY{Style.RESET_ALL}")
    game_state.ui.info_message(f"{'=' * 50}")

    if (
        not hasattr(character, "bank_transactions")
        or len(character.bank_transactions) == 0
    ):
        game_state.ui.warn_message("\nNo transaction history available.")
    else:
        # Header
        game_state.ui.info_message(
            f"\n{'Timestamp':19} | {'Type':10} | {'Amount':10} | Description"
        )
        game_state.ui.info_message("-" * 70)

        # List transactions in reverse chronological order
        for transaction in reversed(
            character.bank_transactions[-20:]
        ):  # Show last 20 transactions
            transaction_str = transaction.to_string()

            # Color-code by transaction type
            if (
                transaction.transaction_type == "deposit"
                or transaction.transaction_type == "interest"
            ):
                game_state.ui.success_message(transaction_str)
            elif (
                transaction.transaction_type == "withdraw"
                or transaction.transaction_type == "loan"
            ):
                game_state.ui.error_message(transaction_str)
            elif transaction.transaction_type == "repayment":
                game_state.ui.warn_message(transaction_str)
            else:
                game_state.ui.info_message(transaction_str)

    input(Fore.YELLOW + "\nPress Enter to return to banking menu..." + Style.RESET_ALL)


# Helper functions


def repay_debt(game_state: Game, character, amount: float) -> None:
    """Process debt repayment."""
    # Confirm payment
    confirm = input(
        Fore.YELLOW
        + f"Confirm payment of {amount:.2f} credits toward your debt? (y/n): "
        + Style.RESET_ALL
    )
    if confirm.lower() != "y":
        game_state.ui.info_message("Transaction cancelled.")
        time.sleep(1)
        return

    # Apply the payment
    character.remove_credits(amount)
    character.remove_debt(amount)

    # Record the transaction
    transaction = BankingTransaction("repayment", amount, "Debt repayment")
    if not hasattr(character, "bank_transactions"):
        character.bank_transactions = []
    character.bank_transactions.append(transaction)

    game_state.ui.success_message(
        f"\nPayment successful! {amount:.2f} credits applied to your debt."
    )

    # Show updated status
    if character.debt <= 0:
        game_state.ui.success_message("Congratulations! You are now debt free!")
        # Reset debt to exactly zero to avoid floating point errors resulting in tiny negative values
        character.debt = 0.0
    else:
        game_state.ui.info_message(f"Remaining debt: {character.debt:.2f} credits")

    time.sleep(2)


def calculate_max_loan(game_state: Game, character) -> float:
    """Calculate maximum loan amount available based on credit score and existing debt."""
    credit_score = calculate_credit_score(game_state, character)

    # Base max loan on credit score
    if credit_score >= 800:  # Excellent
        base_max = 50000.0
    elif credit_score >= 700:  # Good
        base_max = 25000.0
    elif credit_score >= 600:  # Fair
        base_max = 10000.0
    elif credit_score >= 500:  # Poor
        base_max = 5000.0
    else:  # Bad
        base_max = 1000.0

    # Reduce by existing debt ratio
    debt_ratio = character.debt / (base_max * 2)
    max_loan = base_max * max(0, 1 - debt_ratio)

    # If player has too much debt, they may not qualify for any loan
    if character.debt > base_max * 1.5:
        max_loan = 0

    return round(float(max_loan), 2)


def calculate_credit_score(game_state: Game, character) -> int:
    """Calculate credit score based on debt and repayment history."""
    base_score = 650  # Starting score

    # Adjust for current debt ratio
    # We'll assume a "good" amount of debt for a player is about 5000 credits
    if character.debt <= 0:
        debt_modifier = 100  # No debt is great
    elif character.debt < 1000:
        debt_modifier = 50  # Small debt is good
    elif character.debt < 5000:
        debt_modifier = 0  # Moderate debt is neutral
    elif character.debt < 10000:
        debt_modifier = -50  # Significant debt is bad
    else:
        debt_modifier = -100  # Large debt is very bad

    # Adjust for repayment history
    repayment_bonus = 0
    if hasattr(character, "bank_transactions"):
        # Count recent repayments (last 10 transactions)
        recent_transactions = (
            character.bank_transactions[-10:]
            if len(character.bank_transactions) > 10
            else character.bank_transactions
        )
        repayments = [
            t for t in recent_transactions if t.transaction_type == "repayment"
        ]
        repayment_bonus = min(
            100, len(repayments) * 20
        )  # Up to +100 points for consistent repayments

    # Bonus for savings (up to +50)
    savings_bonus = min(50, int(character.savings / 200))

    # Calculate final score
    score = base_score + debt_modifier + repayment_bonus + savings_bonus

    # Ensure score is in valid range
    return max(300, min(850, score))


def get_credit_rating(score: int) -> str:
    """Convert credit score to a rating."""
    if score >= 800:
        return "Excellent"
    elif score >= 700:
        return "Good"
    elif score >= 600:
        return "Fair"
    elif score >= 500:
        return "Poor"
    else:
        return "Bad"


def apply_for_loan(game_state: Game, character, max_loan: float) -> None:
    """Process loan application."""
    amount = get_valid_amount(game_state, "Enter loan amount", 0, max_loan)
    if amount is None:
        return

    # Calculate interest rate with possible adjustments
    weekly_rate = 0.05 * character.debt_interest_mod

    # Show loan terms
    game_state.ui.info_message(f"\nLoan Terms:")
    game_state.ui.info_message(f"Principal: {amount:.2f} credits")
    game_state.ui.info_message(f"Interest Rate: {weekly_rate:.1%}/week")
    game_state.ui.warn_message(f"Weekly Interest: {amount * weekly_rate:.2f} credits")

    # Calculate potential debt
    potential_debt = character.debt + amount
    game_state.ui.warn_message(f"Your total debt will be: {potential_debt:.2f} credits")

    # Confirm loan
    confirm = input(
        Fore.YELLOW
        + f"Do you accept these terms and wish to proceed with the loan? (y/n): "
        + Style.RESET_ALL
    )
    if confirm.lower() != "y":
        game_state.ui.info_message("Loan application cancelled.")
        time.sleep(1)
        return

    # Apply the loan
    character.add_credits(amount)
    character.add_debt(amount)

    # Record the transaction
    transaction = BankingTransaction(
        "loan", amount, f"New loan at {weekly_rate:.1%} interest"
    )
    if not hasattr(character, "bank_transactions"):
        character.bank_transactions = []
    character.bank_transactions.append(transaction)

    game_state.ui.success_message(
        f"\nLoan approved! {amount:.2f} credits have been added to your account."
    )
    game_state.ui.info_message(
        f"Your new debt balance is {character.debt:.2f} credits."
    )

    time.sleep(2)


def display_loan_terms(game_state: Game, character) -> None:
    """Display loan terms and conditions."""
    game_state.ui.clear_screen()
    game_state.ui.info_message(f"\n{'=' * 50}")
    game_state.ui.info_message(f"{Fore.CYAN}LOAN TERMS & CONDITIONS{Style.RESET_ALL}")
    game_state.ui.info_message(f"{'=' * 50}")

    # Base interest rate
    base_rate = 0.05  # 5%
    adjusted_rate = base_rate * character.debt_interest_mod

    game_state.ui.info_message(f"\nStandard Interest Rate: {base_rate:.1%}/week")

    # Show personalized rate if different from base
    if character.debt_interest_mod != 1.0:
        if character.debt_interest_mod > 1.0:
            game_state.ui.warn_message(
                f"Your Personalized Rate: {adjusted_rate:.1%}/week (+{(character.debt_interest_mod-1)*100:.0f}%)"
            )
            if character.negative_trait == "Indebted":
                game_state.ui.warn_message(
                    f"Your 'Indebted' trait increases your interest rates."
                )
        else:
            game_state.ui.success_message(
                f"Your Personalized Rate: {adjusted_rate:.1%}/week (-{(1-character.debt_interest_mod)*100:.0f}%)"
            )

    game_state.ui.info_message(f"\nLoan Terms:")
    game_state.ui.info_message(f"- Interest is calculated and applied weekly")
    game_state.ui.info_message(f"- No early repayment penalties")
    game_state.ui.info_message(f"- Loan eligibility depends on credit score")
    game_state.ui.info_message(
        f"- Failure to make regular payments may affect credit score"
    )
    game_state.ui.warn_message(
        f"- High debt levels may attract attention from debt collectors"
    )

    game_state.ui.info_message(f"\nCredit Score Factors:")
    game_state.ui.info_message(f"- Total debt amount")
    game_state.ui.info_message(f"- Regular debt repayment history")
    game_state.ui.info_message(f"- Savings account balance")

    input(Fore.YELLOW + "\nPress Enter to return to loan menu..." + Style.RESET_ALL)


def deposit_to_savings(game_state: Game, character, amount: float) -> None:
    """Deposit credits into savings account."""
    # Confirm deposit
    confirm = input(
        Fore.YELLOW
        + f"Confirm deposit of {amount:.2f} credits to your savings account? (y/n): "
        + Style.RESET_ALL
    )
    if confirm.lower() != "y":
        game_state.ui.info_message("Transaction cancelled.")
        time.sleep(1)
        return

    # Process deposit
    character.remove_credits(amount)
    character.savings += amount
    character.savings = character.round_credits(character.savings)

    # Record the transaction
    transaction = BankingTransaction("deposit", amount, "Savings deposit")
    if not hasattr(character, "bank_transactions"):
        character.bank_transactions = []
    character.bank_transactions.append(transaction)

    game_state.ui.success_message(
        f"\nDeposit successful! {amount:.2f} credits added to your savings account."
    )
    game_state.ui.info_message(f"New savings balance: {character.savings:.2f} credits")

    time.sleep(1.5)


def withdraw_from_savings(game_state: Game, character, amount: float) -> None:
    """Withdraw credits from savings account."""
    # Confirm withdrawal
    confirm = input(
        Fore.YELLOW
        + f"Confirm withdrawal of {amount:.2f} credits from your savings account? (y/n): "
        + Style.RESET_ALL
    )
    if confirm.lower() != "y":
        game_state.ui.info_message("Transaction cancelled.")
        time.sleep(1)
        return

    # Process withdrawal
    character.savings -= amount
    character.savings = character.round_credits(character.savings)
    character.add_credits(amount)

    # Record the transaction
    transaction = BankingTransaction("withdraw", amount, "Savings withdrawal")
    if not hasattr(character, "bank_transactions"):
        character.bank_transactions = []
    character.bank_transactions.append(transaction)

    game_state.ui.success_message(
        f"\nWithdrawal successful! {amount:.2f} credits withdrawn from your savings account."
    )
    game_state.ui.info_message(f"New savings balance: {character.savings:.2f} credits")
    game_state.ui.info_message(f"Available credits: {character.credits:.2f}")

    time.sleep(1.5)


def get_valid_amount(
    game_state: Game,
    prompt: str,
    min_amount: float = 0,
    max_amount: float = float("inf"),
) -> Optional[float]:
    """Get a valid amount input from the user."""
    while True:
        amount_input = input(
            Fore.YELLOW + f"{prompt} (max {max_amount:.2f}): " + Style.RESET_ALL
        )
        if not amount_input.strip():
            game_state.ui.info_message("Transaction cancelled.")
            return None

        if is_valid_float(amount_input):
            amount = float(amount_input)
            if amount <= 0:
                game_state.ui.error_message("Amount must be positive.")
            elif amount < min_amount:
                game_state.ui.error_message(
                    f"Amount must be at least {min_amount:.2f}."
                )
            elif amount > max_amount:
                game_state.ui.warn_message(
                    f"Amount exceeds maximum. Adjusting to {max_amount:.2f}."
                )
                return max_amount
            else:
                return amount
        else:
            game_state.ui.error_message("Invalid amount. Please enter a number.")


def calculate_savings_interest(
    game_state: Game, character
) -> Optional[tuple[float, float]]:
    """Calculate and apply interest to savings account."""
    if not hasattr(character, "last_savings_interest_time"):
        character.last_savings_interest_time = game_state.global_time
        return None

    # Define a week as 168 hours (7 days * 24 hours)
    WEEK_LENGTH = 168

    # Check if a week has passed since last interest calculation
    weeks_passed = (
        game_state.global_time - character.last_savings_interest_time
    ) // WEEK_LENGTH

    if weeks_passed >= 1:
        # Apply interest for each week passed
        total_interest = 0.0
        current_savings = character.savings

        for _ in range(weeks_passed):
            interest = current_savings * character.savings_interest_rate
            current_savings += interest
            total_interest += interest

        # Update savings and last interest time
        character.savings = character.round_credits(current_savings)
        character.last_savings_interest_time = game_state.global_time

        # Record the transaction
        if total_interest > 0:
            transaction = BankingTransaction(
                "interest", total_interest, "Savings interest payment"
            )
            if not hasattr(character, "bank_transactions"):
                character.bank_transactions = []
            character.bank_transactions.append(transaction)

        return (character.round_credits(total_interest), character.savings)

    return None


# Register the banking command
register_command(
    ["bank", "banking"],
    banking_menu_command,
    [],
)
