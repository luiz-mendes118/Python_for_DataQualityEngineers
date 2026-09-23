import random

# 1. Mock Data Generation: Create 100 random integers from 0 to 1000
random_numbers = [random.randint(0, 1000) for _ in range(100)]

# 2. Sort the list from min to max using the Bubble Sort algorithm
# Conceptually, Bubble Sort repeatedly steps through the list, compares adjacent elements,
# and swaps them if they are in the wrong order. We implement this manually to
# practice core algorithmic thinking and list manipulation without relying on built-in functions.
n = len(random_numbers)
for i in range(n):
    for j in range(0, n - i - 1):
        if random_numbers[j] > random_numbers[j + 1]:
            # Swap the elements if they are in the wrong order
            random_numbers[j], random_numbers[j + 1] = random_numbers[j + 1], random_numbers[j]

# 3. Basic Metrics: Find Min and Max using a for loop (Bonus Challenge)
min_value = random_numbers[0]
max_value = random_numbers[0]

for num in random_numbers:
    if num < min_value:
        min_value = num
    if num > max_value:
        max_value = num

# 4. Aggregation: Separate into even and odd lists and calculate averages safely
even_numbers = [num for num in random_numbers if num % 2 == 0]
odd_numbers = [num for num in random_numbers if num % 2 != 0]

average_even = sum(even_numbers) / len(even_numbers) if even_numbers else 0
average_odd = sum(odd_numbers) / len(odd_numbers) if odd_numbers else 0

# 5. Console Output: Print a clear Data Quality report
print("--- Data Profiling Report ---")
print(f"Total records: {len(random_numbers)}")
print(f"Min value: {min_value}")
print(f"Max value: {max_value}")
print(f"Average of EVEN numbers: {average_even:.1f}")
print(f"Average of ODD numbers: {average_odd:.1f}")
print("-----------------------------")