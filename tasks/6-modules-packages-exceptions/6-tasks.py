"""
Script Name: news_feed_task.py
Purpose: An interactive Object-Oriented Python application that prompts the user
         for various publication types or processes batch records from a .txt file,
         calculates dynamic fields, appends formatted records to newsfeed.txt,
         and cleans up processed batch files.
"""

from datetime import datetime
import os

# -------------------------------------------------------------------------
# Module-Level Constants
# -------------------------------------------------------------------------
WEEKS_PER_MONTH = 4
MIN_FREQUENCY = 1
MAX_FREQUENCY = 7
OUTPUT_FILENAME = "newsfeed.txt"
DEFAULT_BATCH_FILE = os.path.join("records", "default_input.txt")


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
        print(f"[Success] Record successfully published to {filename}!")


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
# Batch Processing Class: TxtFileReader
# -------------------------------------------------------------------------
class TxtFileReader:
    """Handles batch reading, parsing, publishing, and cleanup of multi-record text files."""

    def __init__(self, file_path: str = ""):
        self.file_path = file_path.strip() if file_path else DEFAULT_BATCH_FILE

    def process_batch(self) -> None:
        """Opens batch file, parses records separated by '---', publishes them, and deletes the file."""
        if not os.path.exists(self.file_path):
            print(f"\n[Error] Sorry, file not found at '{self.file_path}'. Please check the path and try again.")
            return

        print(f"\n[Processing] Reading batch file from: {self.file_path}")

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split records using '---' as the separator
            raw_records = content.split('---')
            success_count = 0

            for record_text in raw_records:
                lines = [line.strip() for line in record_text.strip().splitlines() if line.strip()]
                if not lines:
                    continue

                record_type = lines[0].lower()

                # Parse and instantiate based on record type
                if "news" in record_type:
                    if len(lines) >= 3:
                        text = lines[1]
                        city = lines[2]
                        item = News(text, city)
                        item.publish()
                        success_count += 1
                    else:
                        print("[Warning] Skipping malformed News record in file.")

                elif "private ad" in record_type:
                    if len(lines) >= 3:
                        text = lines[1]
                        exp_date = lines[2]
                        item = PrivateAd(text, exp_date)
                        item.publish()
                        success_count += 1
                    else:
                        print("[Warning] Skipping malformed Private Ad record in file.")

                elif "sports frequence" in record_type or "sports" in record_type:
                    if len(lines) >= 3:
                        text = lines[1]
                        freq_str = lines[2]
                        if freq_str.isdigit():
                            frequency = int(freq_str)
                            item = SportsFrequence(text, frequency)
                            item.publish()
                            success_count += 1
                        else:
                            print("[Warning] Frequency in Sports Frequence record must be an integer.")
                    else:
                        print("[Warning] Skipping malformed Sports Frequence record in file.")
                else:
                    print(f"[Warning] Unknown record type encountered: '{lines[0]}'")

            # Cleanup: Delete file if records were successfully processed
            if success_count > 0:
                os.remove(self.file_path)
                print(
                    f"\n[Success] Batch processing complete! Successfully published {success_count} record(s) and cleaned up (deleted) '{self.file_path}'.")
            else:
                print("\n[Notice] No valid records found to process. File was not deleted.")

        except Exception as e:
            print(f"\n[Error] An unexpected error occurred while processing the file: {e}")


# -------------------------------------------------------------------------
# Interactive Terminal Menu
# -------------------------------------------------------------------------
def main():
    """Runs the interactive command-line interface for the News Feed Generator."""
    print("========================================")
    print("      WELCOME TO THE NEWS FEED TOOL     ")
    print("========================================")

    while True:
        print("\nSelect an option:")
        print("1 - Add News (Interactive)")
        print("2 - Add Private Ad (Interactive)")
        print("3 - Add Sports Frequence (Interactive)")
        print("4 - Process records from file (Batch)")
        print("0 - Exit")

        choice = input("Enter your choice (0-4): ").strip()

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

            if not (MIN_FREQUENCY <= frequency <= MAX_FREQUENCY):
                print(
                    f"[Warning] Unusual frequency detected ({frequency} days/week). Expected range is {MIN_FREQUENCY}-{MAX_FREQUENCY}.")
                proceed = input("Do you still want to publish this? (y/n): ").strip().lower()
                if proceed != 'y':
                    continue

            sports_item = SportsFrequence(text, frequency)
            sports_item.publish()

        elif choice == '4':
            print("\n--- Batch Processing from File ---")
            path_input = input(f"Enter file path (Press Enter to use default '{DEFAULT_BATCH_FILE}'): ").strip()

            reader = TxtFileReader(path_input)
            reader.process_batch()

        else:
            print("[Error] Invalid choice! Please enter a number between 0 and 4.")


if __name__ == "__main__":
    main()