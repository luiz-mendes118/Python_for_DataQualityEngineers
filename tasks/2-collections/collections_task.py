"""
Script Name: dictionary_merge_task.py
Purpose: Generates mock dictionaries with overlapping keys and resolves conflicts
         by deduplicating data, keeping maximum values, and appending source indices.
"""

import random
import string

# -------------------------------------------------------------------------
# Part 1: Mock Data Generation
# -------------------------------------------------------------------------
# Generate a random number of dictionaries and populate them with random keys/values
num_dicts = random.randint(2, 10)
dicts_list = []

for _ in range(num_dicts):
    current_dict = {}
    # Generate a random number of keys for each dictionary
    num_keys = random.randint(1, 5)

    # Pick random unique lowercase letters for keys and random integers (0-100) for values
    selected_keys = random.sample(string.ascii_lowercase, num_keys)
    for key in selected_keys:
        current_dict[key] = random.randint(0, 100)

    dicts_list.append(current_dict)

print("--- Generated List of Dictionaries (Input) ---")
for idx, d in enumerate(dicts_list, start=1):
    print(f"Dict {idx}: {d}")

# -------------------------------------------------------------------------
# Part 2: Data Merging & Conflict Resolution
# -------------------------------------------------------------------------
# Track all occurrences of keys, their values, and source dictionary numbers
# Data structure format: key_tracker['a'] = [(value1, dict_num1), (value2, dict_num2), ...]
key_tracker = {}

for dict_idx, d in enumerate(dicts_list, start=1):
    for key, value in d.items():
        if key not in key_tracker:
            key_tracker[key] = []
        key_tracker[key].append((value, dict_idx))

# Build final dictionary by applying merge rules:
# - Unique keys: preserve as-is
# - Duplicate keys: keep max value and rename with source dict number
common_dict = {}

for key, occurrences in key_tracker.items():
    if len(occurrences) == 1:
        val, dict_num = occurrences[0]
        common_dict[key] = val
    else:
        max_val, max_dict_num = max(occurrences, key=lambda x: x[0])
        new_key = f"{key}_{max_dict_num}"
        common_dict[new_key] = max_val

# -------------------------------------------------------------------------
# Part 3: Console Output
# -------------------------------------------------------------------------
print("\n--- Merged Common Dict (Output) ---")
print(common_dict)