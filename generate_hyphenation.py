import argparse
import random
import string
import sys

def generate_utf8_characters(count, marker):
    """Generate a list of random UTF-8 characters."""
    # Generate a pool of valid characters
    valid_chars = []
    for code_point in range(32, 0xD7FF + 1):
        char = chr(code_point)
        if char not in string.whitespace and char != marker and char not in string.punctuation:
            valid_chars.append(char)

    # Randomly sample from the valid character pool
    return random.sample(valid_chars, count)

def generate_word(characters, min_length, max_length, marker):
    """Generate a word with random length and hyphenation."""
    length = random.randint(min_length, max_length)
    word = ''.join(random.choice(characters) for _ in range(length))

    # Add hyphenation markers at random positions
    if length > 2:  # Only hyphenate words longer than 2 characters
        num_hyphens = random.randint(0, length // 2)  # Up to 1/3 of word length
        positions = sorted(random.sample(range(1, length), num_hyphens), reverse=True)
        for pos in positions:
            word = word[:pos] + marker + word[pos:]

    return word

def validate_parameters(chars, lines, min_length, max_length):
    """Validate input parameters."""
    if chars <= 0:
        raise ValueError("Number of characters must be positive")
    if lines <= 0:
        raise ValueError("Number of lines must be positive")
    if min_length <= 0:
        raise ValueError("Minimum word length must be positive")
    if max_length < min_length:
        raise ValueError("Maximum length cannot be less than minimum length")
    if len(marker) != 1:
        raise ValueError("Hyphenation marker must be a single character")

def main():
    parser = argparse.ArgumentParser(description='Generate hyphenation dictionary')
    parser.add_argument('--chars', '-c', type=int, default=255,
                       help='Number of distinct UTF-8 characters (default: 255)')
    parser.add_argument('--lines', '-l', type=int, default=1000,
                       help='Number of lines to generate (default: 1000)')
    parser.add_argument('--min-length', '-m', type=int, default=3,
                       help='Minimum word length (default: 3)')
    parser.add_argument('--max-length', '-M', type=int, default=8,
                       help='Maximum word length (default: 8)')
    parser.add_argument('--marker', '-k', type=str, default='-',
                       help='Hyphenation marker character (default: "-")')
    parser.add_argument('--output', '-o', type=str, default='generated.wlhamb',
                       help='Output file name (default: generated.wlhamb)')
    parser.add_argument('--seed', '-s', type=int, default=None,
                       help='Random seed for reproducible results (default: None)')

    args = parser.parse_args()

    # Set random seed for reproducibility
    if args.seed is not None:
        random.seed(args.seed)

    global marker
    marker = args.marker

    try:
        validate_parameters(args.chars, args.lines, args.min_length, args.max_length)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Generate characters
    characters = generate_utf8_characters(args.chars, marker)

    # Generate words
    with open(args.output, 'w', encoding='utf-8') as f:
        for _ in range(args.lines):
            word = generate_word(characters, args.min_length, args.max_length, marker)
            f.write(word + '\n')

    print(f"Successfully generated {args.lines} words to {args.output}")
    print(f"Using {args.chars} distinct UTF-8 characters")
    print(f"Word lengths: {args.min_length}-{args.max_length}")
    print(f"Hyphenation marker: '{marker}'")

if __name__ == '__main__':
    main()