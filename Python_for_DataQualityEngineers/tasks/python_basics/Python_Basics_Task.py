import random
# 1. Generate a list of 100 random numbers from 0 to 1000
random_numbers = [random.randint(0, 1000) for _ in range(100)]

# 2. Sort the list from min to max using the Bubble Sort algorithm
n = len(random_numbers)
for i in range(n):
    for j in range(0, n - i - 1):
        if random_numbers[j] > random_numbers[j + 1]:
            # Swap the elements if they are in the wrong order
            random_numbers[j], random_numbers[j + 1] = random_numbers[j + 1], random_numbers[j]

# 3. Separate the numbers into even and odd lists
even_numbers = [num for num in random_numbers if num % 2 == 0]
odd_numbers = [num for num in random_numbers if num % 2 != 0]

# 4. Calculate the averages safely (handling potential division by zero)
average_even = sum(even_numbers) / len(even_numbers) if even_numbers else 0
average_odd = sum(odd_numbers) / len(odd_numbers) if odd_numbers else 0

# 5. Print both results to the console with a trailing comment description
print(f"{average_even:<10} # Average of even numbers calculated from the random list")
print(f"{average_odd:<10} # Average of odd numbers calculated from the random list")
