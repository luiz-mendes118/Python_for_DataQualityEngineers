"""
Script Name: 9-xml_task.py
Purpose: An interactive Object-Oriented Python application stored inside '9-xml'.
         Supports manual input, text batch processing, JSON ingestion, XML parsing
         via XmlFileReader, and automated CSV analytics report generation.
"""

from datetime import datetime
import os
import re
from collections import Counter
import csv
import json
import xml.etree.ElementTree as ET

# -------------------------------------------------------------------------
# Path Configuration & Module-Level Constants (All local to 9-xml & project root)
# -------------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))  # Root of the repo

WEEKS_PER_MONTH = 4
MIN_FREQUENCY = 1
MAX_FREQUENCY = 7

# Files stored locally in 9-xml
OUTPUT_FILENAME = os.path.join(CURRENT_DIR, "newsfeed.txt")
DEFAULT_XML_FILE = os.path.join(CURRENT_DIR, "records", "default_input.xml")
WORD_COUNT_CSV = os.path.join(CURRENT_DIR, "word_count.csv")
LETTER_COUNT_CSV = os.path.join(CURRENT_DIR, "letter_count.csv")


# -------------------------------------------------------------------------
# CSV Report Generator Class (Analytics Module)
# -------------------------------------------------------------------------
class CsvReportGenerator:
    """Handles parsing newsfeed.txt and generating word_count.csv and letter_count.csv reports."""

    def __init__(self, newsfeed_path: str = OUTPUT_FILENAME):
        self.newsfeed_path = newsfeed_path

    def generate_reports(self) -> None:
        """Reads newsfeed.txt, computes analytics, and exports word_count.csv and letter_count.csv."""
        if not os.path.exists(self.newsfeed_path):
            return

        try:
            with open(self.newsfeed_path, 'r', encoding='utf-8') as f:
                text = f.read()

            if not text.strip():
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

            print(f"[Analytics] Successfully updated CSV reports in '{CURRENT_DIR}'!")

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
# XML Batch Reader Class (New in Module 9)
# -------------------------------------------------------------------------
class XmlFileReader:
    """Handles reading, parsing, publishing, and cleanup of multi-record XML input files."""

    def __init__(self, file_path: str = ""):
        self.file_path = file_path.strip() if file_path else DEFAULT_XML_FILE

    def process_file(self) -> None:
        """Parses XML tree, extracts records using tags and attributes, publishes them, and deletes the file."""
        if not os.path.exists(self.file_path):
            print(f"\n[Error] Sorry, file not found at '{self.file_path}'. Please check the path and try again.")
            return

        print(f"\n[Processing] Reading XML file from: {self.file_path}")

        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            success_count = 0

            for record in root:
                # Extract record type from attribute ('type') or tag name
                rec_type = record.attrib.get("type", "").strip().lower()
                if not rec_type:
                    rec_type = record.tag.strip().lower()

                # Extract text element if present
                text_elem = record.find("text")
                text = text_elem.text.strip() if text_elem is not None and text_elem.text else ""

                if "news" in rec_type:
                    city_elem = record.find("city")
                    city = city_elem.text.strip() if city_elem is not None and city_elem.text else ""
                    if text and city:
                        News(text, city).publish()
                        success_count += 1
                    else:
                        print("[Warning] Skipping News record due to missing 'text' or 'city'.")

                elif "private" in rec_type or "ad" in rec_type:
                    # Check expiration_date in attributes or sub-tags
                    exp_date = record.attrib.get("expiration_date", "")
                    if not exp_date:
                        exp_elem = record.find("expiration_date")
                        if exp_elem is not None and exp_elem.text:
                            exp_date = exp_elem.text.strip()

                    if text and exp_date:
                        try:
                            PrivateAd(text, exp_date).publish()
                            success_count += 1
                        except ValueError as e:
                            print(f"[Warning] Skipping Private Ad record due to date error: {e}")
                    else:
                        print("[Warning] Skipping Private Ad record due to missing text or expiration date.")

                elif "sport" in rec_type:
                    freq_val = record.attrib.get("frequency_per_week", "")
                    if not freq_val:
                        freq_elem = record.find("frequency_per_week")
                        if freq_elem is not None and freq_elem.text:
                            freq_val = freq_elem.text.strip()

                    if text and freq_val.isdigit():
                        SportsFrequence(text, int(freq_val)).publish()
                        success_count += 1
                    else:
                        print("[Warning] Skipping Sports record due to missing text or invalid frequency.")
                else:
                    print(f"[Warning] Unknown record type encountered: '{rec_type}'")

            # Cleanup: Delete file if successfully processed
            if success_count > 0:
                os.remove(self.file_path)
                print(
                    f"\n[Success] XML batch processing complete! Published {success_count} record(s) and deleted '{self.file_path}'.")
            else:
                print("\n[Notice] No valid records were processed. File was not deleted.")

        except ET.ParseError as pe:
            print(f"\n[Error] XML Syntax Error: Failed to parse file due to malformed XML tags. Details: {pe}")
        except Exception as e:
            print(f"\n[Error] An unexpected error occurred while processing the XML file: {e}")


# -------------------------------------------------------------------------
# Interactive Terminal Menu
# -------------------------------------------------------------------------
def main():
    print("========================================")
    print("    NEWS FEED & XML DATA INTEGRATION    ")
    print("========================================")

    while True:
        print("\nSelect an option:")
        print("1 - Add News (Interactive)")
        print("2 - Add Private Ad (Interactive)")
        print("3 - Add Sports Frequence (Interactive)")
        print("4 - Process records from XML file (Enterprise Feed)")
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
            path_input = input(f"Enter XML file path (Press Enter for default): ").strip()
            XmlFileReader(path_input).process_file()

        elif choice == '5':
            print("\n[Processing] Forcing regeneration of CSV analytics reports...")
            CsvReportGenerator().generate_reports()

        else:
            print("[Error] Invalid choice!")


if __name__ == "__main__":
    main()