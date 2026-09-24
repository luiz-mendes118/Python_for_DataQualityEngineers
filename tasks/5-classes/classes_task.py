"""
Script Name: news_feed_task.py
Purpose: An interactive Object-Oriented Python application that prompts the user
         for various publication types, calculates dynamic fields (dates, days left,
         monthly frequencies), and appends formatted records to a newsfeed.txt file.
"""

from datetime import datetime

# -------------------------------------------------------------------------
# Module-Level Constants
# -------------------------------------------------------------------------
WEEKS_PER_MONTH = 4
MIN_FREQUENCY = 1
MAX_FREQUENCY = 7
OUTPUT_FILENAME = "newsfeed.txt"


# -------------------------------------------------------------------------
# Base Class (Parent)
# -------------------------------------------------------------------------
class Publication:
    """Base class for all publication types, handling shared file appending behavior."""

    def __init__(self, text: str):
        self.text = text

    def generate_body(self) -> str:
        """To be overridden by child classes to generate specific content format."""
        raise NotImplementedError("Subclasses must implement generate_body()")

    def publish(self, filename: str = OUTPUT_FILENAME) -> None:
        """Appends the formatted publication block to the output file."""
        content = self.generate_body()
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(content + "\n")
        print(f"\n[Success] Record successfully published to {filename}!")


# -------------------------------------------------------------------------
# Child Class 1: News
# -------------------------------------------------------------------------
class News(Publication):
    """Represents a news article with city and publication timestamp."""

    def __init__(self, text: str, city: str):
        super().__init__(text)
        self.city = city

    def generate_body(self) -> str:
        # Get current date and time formatted as DD/MM/YYYY HH:MM
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M")

        block = (
            "News -------------------------\n"
            f"{self.text}\n"
            f"{self.city}, {current_time}\n"
            "------------------------------"
        )
        return block


# -------------------------------------------------------------------------
# Child Class 2: Private Ad
# -------------------------------------------------------------------------
class PrivateAd(Publication):
    """Represents a private advertisement with expiration date and days-left calculation."""

    def __init__(self, text: str, expiration_date_str: str):
        super().__init__(text)
        self.expiration_date_str = expiration_date_str

    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """Parse date from multiple formats cleanly using a helper loop."""
        for fmt in ["%Y-%m-%d", "%d/%m/%Y"]:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        raise ValueError("Invalid date format. Expected YYYY-MM-DD or DD/MM/YYYY.")

    def generate_body(self) -> str:
        # Use helper method for robust date parsing
        exp_date = self.parse_date(self.expiration_date_str)
        current_date = datetime.now()

        # Calculate days left (difference between expiration date and today)
        delta = exp_date - current_date
        days_left = delta.days
        if days_left < 0:
            days_left = 0  # Prevent negative days if expired

        formatted_exp_date = exp_date.strftime("%d/%m/%Y")

        block = (
            "Private Ad -------------------\n"
            f"{self.text}\n"
            f"Actual until: {formatted_exp_date}, {days_left} days left\n"
            "------------------------------"
        )
        return block


# -------------------------------------------------------------------------
# Child Class 3: Sports Frequence (Custom Unique Publication)
# -------------------------------------------------------------------------
class SportsFrequence(Publication):
    """Represents sports activity frequency, calculating monthly practice days."""

    def __init__(self, text: str, frequency_per_week: int):
        super().__init__(text)
        self.frequency_per_week = frequency_per_week

    def generate_body(self) -> str:
        # Calculate how many days per month using module constant
        monthly_days = self.frequency_per_week * WEEKS_PER_MONTH

        block = (
            "Sports Frequence -------------\n"
            f"Sport / Activity: {self.text}\n"
            f"Practice frequency: {self.frequency_per_week} days/week\n"
            f"Estimated monthly practice: {monthly_days} days/month (approx. {WEEKS_PER_MONTH} weeks)\n"
            "------------------------------"
        )
        return block


# -------------------------------------------------------------------------
# Interactive Terminal Menu
# -------------------------------------------------------------------------
def main():
    """Runs the interactive command-line interface for the News Feed Generator."""
    print("========================================")
    print("      WELCOME TO THE NEWS FEED TOOL     ")
    print("========================================")

    while True:
        print("\nSelect the type of record to add:")
        print("1 - News")
        print("2 - Private Ad")
        print("3 - Sports Frequence (Custom)")
        print("0 - Exit")

        choice = input("Enter your choice (0-3): ").strip()

        if choice == '0':
            print("\nExiting News Feed Generator. Have a great day!")
            break

        elif choice == '1':
            print("\n--- Creating News Record ---")
            text = input("Enter news text: ").strip()
            city = input("Enter city: ").strip()

            if not text or not city:
                print("[Error] Text and city cannot be empty. Please try again.")
                continue

            news_item = News(text, city)
            news_item.publish()

        elif choice == '2':
            print("\n--- Creating Private Ad Record ---")
            text = input("Enter ad description: ").strip()
            exp_date = input("Enter expiration date (YYYY-MM-DD or DD/MM/YYYY): ").strip()

            if not text or not exp_date:
                print("[Error] Description and expiration date cannot be empty. Please try again.")
                continue

            try:
                ad_item = PrivateAd(text, exp_date)
                ad_item.publish()
            except ValueError as e:
                print(f"[Error] {e}")

        elif choice == '3':
            print("\n--- Creating Sports Frequence Record ---")
            text = input("Enter sport name/details: ").strip()
            freq_input = input(f"Enter how many days per week you practice ({MIN_FREQUENCY}-{MAX_FREQUENCY}): ").strip()

            if not text or not freq_input.isdigit():
                print("[Error] Sport name cannot be empty and frequency must be a valid integer.")
                continue

            frequency = int(freq_input)

            # Input validation for realistic frequency range
            if not (MIN_FREQUENCY <= frequency <= MAX_FREQUENCY):
                print(f"[Warning] Unusual frequency detected ({frequency} days/week). Expected range is {MIN_FREQUENCY}-{MAX_FREQUENCY}.")
                proceed = input("Do you still want to publish this? (y/n): ").strip().lower()
                if proceed != 'y':
                    continue

            sports_item = SportsFrequence(text, frequency)
            sports_item.publish()

        else:
            print("[Error] Invalid choice! Please enter a number between 0 and 3.")


if __name__ == "__main__":
    main()