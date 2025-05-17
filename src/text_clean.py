import re

def clean_ocr_text(text):
    """
    Cleans the raw OCR text output.
    - Removes extra whitespace.
    - Attempts to fix common OCR errors (can be expanded).
    - Removes lines that are likely OCR noise (e.g., very short lines with junk).
    """
    if not text:
        return ""

    # 1. Normalize whitespace: remove leading/trailing, replace multiple spaces/tabs with single space
    cleaned_text = re.sub(r'[ \t]+', ' ', text).strip()
    # Replace multiple newlines with a single newline
    cleaned_text = re.sub(r'\n\s*\n+', '\n\n', cleaned_text) # Keep paragraph breaks
    cleaned_text = re.sub(r'\n+', '\n', cleaned_text) # Consolidate other newlines


    # 2. Common OCR error corrections (example, expand based on observed errors)
    # corrections = {
    #     r'\b1\b': 'l',  # Replace standalone '1' with 'l' (context dependent)
    #     r'\b0\b': 'O',  # Replace standalone '0' with 'O'
    #     r'ﬁ': 'fi',    # Ligature fi
    #     r'ﬂ': 'fl',    # Ligature fl
    # }
    # for error, correction in corrections.items():
    #     cleaned_text = re.sub(error, correction, cleaned_text)

    # 3. Remove very short lines that are likely noise (e.g. less than 3 alphanumeric chars)
    lines = cleaned_text.split('\n')
    cleaned_lines = [line for line in lines if len(re.findall(r'[a-zA-Z0-9]', line)) >= 3 or not line.strip() == ""]
    cleaned_text = '\n'.join(cleaned_lines)


    # 4. Remove lines consisting only of special characters or very few characters
    # This can be aggressive, adjust as needed.
    # lines = cleaned_text.split('\n')
    # valid_lines = []
    # for line in lines:
    #     # Keep line if it has a reasonable number of alphanumeric characters
    #     if len(re.sub(r'[^a-zA-Z0-9]', '', line)) > 2:
    #         valid_lines.append(line)
    #     # Or if it's an empty line (potential paragraph separator)
    #     elif not line.strip():
    #         valid_lines.append(line)
    # cleaned_text = '\n'.join(valid_lines)


    return cleaned_text.strip()

def structure_text(text):
    """
    Attempts to structure text, e.g., identify bullet points.
    This is a basic example.
    """
    lines = text.split('\n')
    structured_lines = []
    for line in lines:
        stripped_line = line.strip()
        # Basic bullet point detection (-, *, numbers followed by . or ))
        if re.match(r'^[-*\u2022]\s+', stripped_line) or \
           re.match(r'^\d+[\.\)]\s+', stripped_line):
            structured_lines.append("  " + stripped_line) # Indent bullets
        else:
            structured_lines.append(line)
    return '\n'.join(structured_lines)

if __name__ == '__main__':
    sample_ocr_output = """
    This is an exampIe text with some
    errrors like 1 for l and 0 for O.

    There are also extra    spaces.

    - Item one
    * Item two
    1. Third item

    Short junk line: . ,

    Another valid line.
    """
    print("--- Original Text ---")
    print(sample_ocr_output)

    cleaned = clean_ocr_text(sample_ocr_output)
    print("\n--- Cleaned Text ---")
    print(cleaned)

    structured = structure_text(cleaned)
    print("\n--- Structured Text ---")
    print(structured)