def split_into_segments(text):
    segments = text.split(".")  # Splitting by period followed by a space
    return [segment.strip() for segment in segments if segment]

# Tokenize the segment
def tokenize(segment):
    tokens = segment.split()  # Simple space-based tokenization
    return tokens