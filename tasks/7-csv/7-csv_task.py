"""
Script Name: 7-csv_task.py
Purpose: An interactive Object-Oriented Python application stored inside '7-csv'.
         Handles publications, batch processing, and automated CSV analytics reports
         generated locally inside the '7-csv' folder.
"""

from datetime import datetime
import os
import re
from collections import Counter
import csv

# -------------------------------------------------------------------------
# Path Configuration & Module-Level Constants (All local to 7-csv)
# -------------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

WEEKS_PER_MONTH = 4
MIN_FREQUENCY = 1
MAX_FREQUENCY = 7

# All files are stored directly inside the 7-csv folder
OUTPUT_FILENAME = os.path.join(CURRENT_DIR, "newsfeed.txt")
DEFAULT_BATCH_FILE = os.path.join(CURRENT_DIR, "records", "default_input.txt")
WORD_COUNT_CSV = os.path.join(CURRENT_DIR, "word_count.csv")
LETTER_COUNT_CSV = os.path.join(CURRENT_DIR, "letter_count.csv")


# -------------------------------------------------------------------------
# CSV Report Generator Class
# -------------------------------------------------------------------------
class CsvReportGenerator:
    """Handles parsing newsfeed.txt and generating word_count.csv and letter_count.csv reports."""

    def __init__(self, newsfeed_path: str = OUTPUT_FILENAME):
        self.newsfeed_path = newsfeed_path

    def generate_reports(self) -> None:
        """Reads newsfeed.txt, computes analytics, and exports word_count.csv and letter_count.csv."""
        if not os.path.exists(self.newsfeed_path):
            print(f"[Notice] '{self.newsfeed_path}' not found yet. Add a record first!")
            return

        try:
            with open(self.newsfeed_path, 'r', encoding='utf-8') as f:
                text = f.read()

            if not text.strip():
                print("[Notice] newsfeed.txt is empty. Skipping CSV generation.")
                return

            # --- Part 1: Word Count Report ---
            words = re.findall(r'\b\w+\b', text.lower())
            word_counts = Counter(words)

            with open(WORD_COUNT_CSV, 'w', encoding='utf-8') as csvfile:
                for word, count in word_counts.items():
                    csvfile.write(f"{word}-{count}\n")

            # --- Part 2: Letter Analytics Report ---
            total_letters = 0
            letter_all_counts = Counter()
            letter_upper_counts = Counter()

            for char in text:
                if char.isalpha():
                    total_letters += 1
                    lower_char = char.lower()
                    letter_all_counts[lower_char] += 1
                    if char.isupper():
                        letter_upper_counts[lower_char] += 1

            with open(LETTER_COUNT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['letter', 'count_all', 'count_uppercase', 'percentage']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for char_code in range(ord('a'), ord('z') + 1):
                    letter = chr(char_code)
                    count_all = letter_all_counts[letter]
                    count_uppercase = letter_upper_counts[letter]

                    percentage = (count_all / total_letters * 100) if total_letters > 0 else 0.0
                    percentage_str = f"{percentage:.1f}%"

                    writer.writerow({
                        'letter': letter,
                        'count_all': count_all,
                        'count_uppercase': count_uppercase,
                        'percentage': percentage_str
                    })

            print(f"[Analytics] Successfully generated/updated CSV reports in '{CURRENT_DIR}'!")

        except Exception as e:
            print(f"[Error] Failed to generate analytics reports: {e}")


# -------------------------------------------------------------------------
# Base Class (Parent)
# -------------------------------------------------------------------------
class Publication:
    """Base class for all publication types, handling shared file appending behavior and CSV automation."""

    def __init__(self, text: str):
        self.text = text

    def generate_body(self) -> str:
        """To be overridden by child classes to generate specific content format."""
        raise NotImplementedError("Subclasses must implement generate_body()")

    def publish(self, filename: str = OUTPUT_FILENAME) -> None:
        """Appends the formatted publication block to the output file and triggers CSV reporting."""
        content = self.generate_body()
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(content + "\n")
        print(f"\n[Success] Record successfully published to newsfeed.txt!")

        # Trigger automatic CSV analytics update
        reporter = CsvReportGenerator(filename)
        reporter.generate_reports()


# -------------------------------------------------------------------------
# Child Classes
# -------------------------------------------------------------------------
class News(Publication):
    """Represents a news article with city and publication timestamp."""
    def __init__(self, text: str, city: str):
        super().__init__(text)
        self.city = city

    def generate_body(self) -> str:
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M")
        return (
            "News -------------------------\n"
            f"{self.text}\n"
            f"{self.city}, {current_time}\n"
            "------------------------------"
        )


class PrivateAd(Publication):
    """Represents a private advertisement with expiration date and days-left calculation."""
    def __init__(self, text: str, expiration_date_str: str):
        super().__init__(text)
        self.expiration_date_str = expiration_date_str

    @staticmethod
    def parse_date(date_str: str) -> datetime:
        for fmt in ["%Y-%m-%d", "%d/%m/%Y"]:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        raise ValueError("Invalid date format. Expected YYYY-MM-DD or DD/MM/YYYY.")

    def generate_body(self) -> str:
        exp_date = self.parse_date(self.expiration_date_str)
        delta = exp_date - datetime.now()
        days_left = max(0, delta.days)
        formatted_exp_date = exp_date.strftime("%d/%m/%Y")

        return (
            "Private Ad -------------------\n"
            f"{self.text}\n"
            f"Actual until: {formatted_exp_date}, {days_left} days left\n"
            "------------------------------"
        )


class SportsFrequence(Publication):
    """Represents sports activity frequency, calculating monthly practice days."""
    def __init__(self, text: str, frequency_per_week: int):
        super().__init__(text)
        self.frequency_per_week = frequency_per_week

    def generate_body(self) -> str:
        monthly_days = self.frequency_per_week * WEEKS_PER_MONTH
        return (
            "Sports Frequence -------------\n"
            f"Sport / Activity: {self.text}\n"
            f"Practice frequency: {self.frequency_per_week} days/week\n"
            f"Estimated monthly practice: {monthly_days} days/month (approx. {WEEKS_PER_MONTH} weeks)\n"
            "------------------------------"
        )


# -------------------------------------------------------------------------
# Batch Processing Class: TxtFileReader
# -------------------------------------------------------------------------
class TxtFileReader:
    """Handles batch reading, parsing, publishing, and cleanup of multi-record text files."""

    def __init__(self, file_path: str = ""):
        self.file_path = file_path.strip() if file_path else DEFAULT_BATCH_FILE

    def process_batch(self) -> None:
        if not os.path.exists(self.file_path):
            print(f"\n[Error] Sorry, file not found at '{self.file_path}'. Please check the path and try again.")
            return

        print(f"\n[Processing] Reading batch file from: {self.file_path}")

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            raw_records = content.split('---')
            success_count = 0

            for record_text in raw_records:
                lines = [line.strip() for line in record_text.strip().splitlines() if line.strip()]
                if not lines:
                    continue

                record_type = lines[0].lower()

                if "news" in record_type and len(lines) >= 3:
                    News(lines[1], lines[2]).publish()
                    success_count += 1
                elif "private ad" in record_type and len(lines) >= 3:
                    PrivateAd(lines[1], lines[2]).publish()
                    success_count += 1
                elif "sports" in record_type and len(lines) >= 3 and lines[2].isdigit():
                    SportsFrequence(lines[1], int(lines[2])).publish()
                    success_count += 1

            if success_count > 0:
                os.remove(self.file_path)
                print(f"\n[Success] Batch processing complete! Published {success_count} record(s) and deleted input file.")
            else:
                print("\n[Notice] No valid records found to process.")

        except Exception as e:
            print(f"[Error] An unexpected error occurred: {e}")


# -------------------------------------------------------------------------
# Interactive Terminal Menu
# -------------------------------------------------------------------------
def main():
    print("========================================")
    print("   NEWS FEED & CSV ANALYTICS GENERATOR  ")
    print("========================================")

    while True:
        print("\nSelect an option:")
        print("1 - Add News (Interactive)")
        print("2 - Add Private Ad (Interactive)")
        print("3 - Add Sports Frequence (Interactive)")
        print("4 - Process records from file (Batch)")
        print("5 - Force Regenerate CSV Reports")
        print("0 - Exit")

        choice = input("Enter your choice (0-5): ").strip()

        if choice == '0':
            print("\nExiting. Have a great day!")
            break

        elif choice == '1':
            text = input("Enter news text: ").strip()
            city = input("Enter city: ").strip()
            if text and city:
                News(text, city).publish()
            else:
                print("[Error] Fields cannot be empty.")

        elif choice == '2':
            text = input("Enter ad description: ").strip()
            exp_date = input("Enter expiration date (YYYY-MM-DD or DD/MM/YYYY): ").strip()
            if text and exp_date:
                try:
                    PrivateAd(text, exp_date).publish()
                except ValueError as e:
                    print(f"[Error] {e}")
            else:
                print("[Error] Fields cannot be empty.")

        elif choice == '3':
            text = input("Enter sport name/details: ").strip()
            freq_input = input(f"Enter frequency ({MIN_FREQUENCY}-{MAX_FREQUENCY} days/week): ").strip()
            if text and freq_input.isdigit():
                SportsFrequence(text, int(freq_input)).publish()
            else:
                print("[Error] Invalid input.")

        elif choice == '4':
            path_input = input(f"Enter file path (Press Enter for default): ").strip()
            TxtFileReader(path_input).process_batch()

        elif choice == '5':
            print("\n[Processing] Forcing regeneration of CSV analytics reports...")
            CsvReportGenerator().generate_reports()

        else:
            print("[Error] Invalid choice!")


if __name__ == "__main__":
    main()