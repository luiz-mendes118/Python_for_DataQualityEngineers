"""
Script Name: text_cleaner_task.py
Purpose: Cleans raw messy text by preserving paragraph structure, normalizing
         sentence cases correctly, safely replacing 'iz' with 'is', extracting ending words
         from sentences locally within paragraph 2 to form a summary sentence, and profiling whitespaces.
"""

import re

# -------------------------------------------------------------------------
# Part 1: Raw Data Definition
# -------------------------------------------------------------------------
raw_text = """homEwork:
  tHis iz your homeWork, copy these Text to variable.

  You NEED TO normalize it fROM letter CASEs point oF View. also, create one MORE senTENCE witH LAST WoRDS of each existING SENtence and add it to the END OF this Paragraph.

  it iZ misspeLLing here. fix“iZ” with correct “is”, but ONLY when it Iz a mistAKE.

  last iz TO calculate nuMber OF Whitespace characteRS in this Tex. caREFULL, not only Spaces, but ALL whitespaces. I got 87."""


# -------------------------------------------------------------------------
# Part 2: Data Profiling - Whitespace Counter (Step 4)
# -------------------------------------------------------------------------
# Count all whitespace characters (spaces, tabs, newlines) in the original raw text
whitespace_count = sum(1 for char in raw_text if char.isspace())


# -------------------------------------------------------------------------
# Part 3: Helper Function for Typo Fixing (Step 2)
# -------------------------------------------------------------------------
def fix_iz_typos(text_segment: str) -> str:
    """Replaces standalone 'iz', 'iZ', or 'Iz' typos with 'is' while preserving casing/punctuation."""
    words = text_segment.split()
    fixed_words = []
    for word in words:
        stripped_word = word.strip('.,:;“”"‘’')
        if stripped_word.lower() == "iz":
            # Replace case-insensitively while keeping surrounding punctuation
            word = re.sub(r'(?i)iz', 'is', word)
        fixed_words.append(word)
    return " ".join(fixed_words)


# -------------------------------------------------------------------------
# Part 4: Text Cleaning & Normalization (Steps 1, 2, and 3)
# -------------------------------------------------------------------------
# Split the raw text into paragraphs by blank lines (preserving multi-paragraph structure)
paragraphs = raw_text.split('\n\n')
cleaned_paragraphs = []

for p_idx, para in enumerate(paragraphs):
    # Clean up leading/trailing indentation per paragraph
    para_clean = para.strip()

    # Check if this paragraph is a header or multi-sentence block
    # Split paragraph into sentences using period followed by space or end of string
    sentences = [s.strip() for s in re.split(r'(?<=\.)\s+', para_clean) if s.strip()]

    cleaned_sentences = []
    local_last_words = []

    for sentence in sentences:
        # Step 2: Fix typos ("iz" -> "is")
        fixed_sentence = fix_iz_typos(sentence)

        # Step 1: Normalize capitalization correctly
        # Capitalize the first letter of the sentence, and ensure the rest of the text
        # is lowercased WITHOUT blindly lowercasing the trailing punctuation or whole string at once.
        if fixed_sentence:
            # Lowercase the body (excluding potential trailing punctuation) and capitalize first letter
            body = fixed_sentence[:-1].lower() + fixed_sentence[-1] if fixed_sentence.endswith(('.', '!', '?')) else fixed_sentence.lower()
            normalized_sentence = body[0].upper() + body[1:] if len(body) > 1 else body.upper()

            # Step 3: Extract the last word of every period-ending sentence locally (if this is paragraph 2)
            # Paragraph index 1 is the second paragraph in 0-based indexing
            if p_idx == 1 and normalized_sentence.endswith('.'):
                # Split words and get the last word (strip punctuation)
                words_in_sentence = normalized_sentence.split()
                if words_in_sentence:
                    last_word = words_in_sentence[-1].strip('.,:;“”"‘’')
                    local_last_words.append(last_word)

            cleaned_sentences.append(normalized_sentence)

    # Reassemble paragraph from cleaned sentences
    reconstructed_para = " ".join(cleaned_sentences)

    # Handle heading lines or paragraphs that don't end with a period (like "Homework:")
    if not reconstructed_para.endswith('.'):
        reconstructed_para = fix_iz_typos(reconstructed_para)
        reconstructed_para = reconstructed_para[0].upper() + reconstructed_para[1:].lower() if len(reconstructed_para) > 1 else reconstructed_para.upper()

    # Step 3 (Targeted Placement): Add the new sentence of last words to the END OF the second paragraph (p_idx == 1)
    if p_idx == 1 and local_last_words:
        new_sentence = " " + " ".join(local_last_words).capitalize() + "."
        reconstructed_para += new_sentence

    cleaned_paragraphs.append(reconstructed_para)

# Reassemble the final text with original paragraph spacing (double newline)
final_cleaned_text = "\n\n".join(cleaned_paragraphs)


# -------------------------------------------------------------------------
# Part 5: Console Output & Report
# -------------------------------------------------------------------------
print("--- Data Cleaning & Profiling Report ---")
print(f"Total Whitespace Characters Counted: {whitespace_count}")
print("\n[Cleaned Paragraph Output]:\n")
print(final_cleaned_text)
print("\n----------------------------------------")