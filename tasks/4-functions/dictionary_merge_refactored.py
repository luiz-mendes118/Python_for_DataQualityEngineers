"""
Part 1: Dictionary Merge Refactored
Script Name: dictionary_merge_refactored.py
Purpose: Refactored version of Module 2 using functional decomposition.
         Generates mock dictionaries and merges them using distinct, reusable functions.
"""

import random
import string


def generate_mock_dictionaries() -> list:
    """Generates a list of a random number of dictionaries with random keys and integer values."""
    num_dicts = random.randint(2, 10)
    dicts_list = []

    for _ in range(num_dicts):
        current_dict = {}
        num_keys = random.randint(1, 5)

        selected_keys = random.sample(string.ascii_lowercase, num_keys)
        for key in selected_keys:
            current_dict[key] = random.randint(0, 100)

        dicts_list.append(current_dict)

    return dicts_list


def merge_dictionaries(dicts_list: list) -> dict:
    """
    Merges a list of dictionaries based on data quality rules:
    - Unique keys: preserved as-is.
    - Duplicate keys: keeps max value and renames key with 1-based source dictionary index.
    """
    key_tracker = {}

    # Track all occurrences of keys, values, and source dictionary numbers
    for dict_idx, d in enumerate(dicts_list, start=1):
        for key, value in d.items():
            if key not in key_tracker:
                key_tracker[key] = []
            key_tracker[key].append((value, dict_idx))

    common_dict = {}

    # Build final dictionary applying conflict resolution rules
    for key, occurrences in key_tracker.items():
        if len(occurrences) == 1:
            val, dict_num = occurrences[0]
            common_dict[key] = val
        else:
            max_val, max_dict_num = max(occurrences, key=lambda x: x[0])
            new_key = f"{key}_{max_dict_num}"
            common_dict[new_key] = max_val

    return common_dict


# -------------------------------------------------------------------------
# Main Execution Block
# -------------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Generate mock data
    input_dicts = generate_mock_dictionaries()

    print("--- Generated List of Dictionaries (Input) ---")
    for idx, d in enumerate(input_dicts, start=1):
        print(f"Dict {idx}: {d}")

    # 2. Merge dictionaries using business logic function
    output_dict = merge_dictionaries(input_dicts)

    # 3. Print final report
    print("\n--- Merged Common Dict (Output) ---")
    print(output_dict)