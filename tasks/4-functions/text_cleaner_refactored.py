"""
Part 2: Text Cleaner Refactored
Script Name: text_cleaner_refactored.py
Purpose: Refactored version of Module 3 using functional decomposition.
         Breaks text cleaning, normalization, typo fixing, and profiling into independent functions.
"""

import re


def count_whitespaces(raw_text: str) -> int:
    """Takes raw text and returns the exact integer count of whitespace characters."""
    return sum(1 for char in raw_text if char.isspace())


def fix_iz_typos(text_segment: str) -> str:
    """Replaces standalone 'iz', 'iZ', or 'Iz' typos with 'is' while preserving casing/punctuation."""
    words = text_segment.split()
    fixed_words = []
    for word in words:
        stripped_word = word.strip('.,:;“”"‘’')
        if stripped_word.lower() == "iz":
            word = re.sub(r'(?i)iz', 'is', word)
        fixed_words.append(word)
    return " ".join(fixed_words)


def normalize_and_clean_text(raw_text: str) -> str:
    """
    Normalizes letter casing, fixes typos, extracts ending words from sentences
    in paragraph 2 to build a summary sentence, and preserves paragraph structure.
    """
    paragraphs = raw_text.split('\n\n')
    cleaned_paragraphs = []

    for p_idx, para in enumerate(paragraphs):
        para_clean = para.strip()
        sentences = [s.strip() for s in re.split(r'(?<=\.)\s+', para_clean) if s.strip()]

        cleaned_sentences = []
        local_last_words = []

        for sentence in sentences:
            fixed_sentence = fix_iz_typos(sentence)

            if fixed_sentence:
                body = fixed_sentence[:-1].lower() + fixed_sentence[-1] if fixed_sentence.endswith(
                    ('.', '!', '?')) else fixed_sentence.lower()
                normalized_sentence = body[0].upper() + body[1:] if len(body) > 1 else body.upper()

                # Extract last words locally from paragraph 2 (index 1)
                if p_idx == 1 and normalized_sentence.endswith('.'):
                    words_in_sentence = normalized_sentence.split()
                    if words_in_sentence:
                        last_word = words_in_sentence[-1].strip('.,:;“”"‘’')
                        local_last_words.append(last_word)

                cleaned_sentences.append(normalized_sentence)

        reconstructed_para = " ".join(cleaned_sentences)

        # Handle headers or lines without periods
        if not reconstructed_para.endswith('.'):
            reconstructed_para = fix_iz_typos(reconstructed_para)
            reconstructed_para = reconstructed_para[0].upper() + reconstructed_para[1:].lower() if len(
                reconstructed_para) > 1 else reconstructed_para.upper()

        # Append last words summary sentence specifically to the end of paragraph 2
        if p_idx == 1 and local_last_words:
            new_sentence = " " + " ".join(local_last_words).capitalize() + "."
            reconstructed_para += new_sentence

        cleaned_paragraphs.append(reconstructed_para)

    return "\n\n".join(cleaned_paragraphs)


# -------------------------------------------------------------------------
# Main Execution Block
# -------------------------------------------------------------------------
if __name__ == "__main__":
    my_messy_data = """homEwork:
  tHis iz your homeWork, copy these Text to variable.

  You NEED TO normalize it fROM letter CASEs point oF View. also, create one MORE senTENCE witH LAST WoRDS of each existING SENtence and add it to the END OF this Paragraph.

  it iZ misspeLLing here. fix“iZ” with correct “is”, but ONLY when it Iz a mistAKE.

  last iz TO calculate nuMber OF Whitespace characteRS in this Tex. caREFULL, not only Spaces, but ALL whitespaces. I got 87."""

    # 1. Profile whitespaces from original raw data
    total_whitespaces = count_whitespaces(my_messy_data)

    # 2. Clean and normalize text using functional pipeline
    final_cleaned_paragraph = normalize_and_clean_text(my_messy_data)

    # 3. Print report and results
    print("--- Data Cleaning & Profiling Report ---")
    print(f"Total Whitespace Characters Counted: {total_whitespaces}")
    print("\n[Cleaned Paragraph Output]:\n")
    print(final_cleaned_paragraph)
    print("\n----------------------------------------")