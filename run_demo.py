# Import the main orchestration class from the package
from phonetic_match.matcher import PhoneticMatcher

def run_tests():
    """
    Executes a series of predefined test cases to verify the matcher's performance.
    """
    # Instantiate the matcher which loads the processing and encoding engines
    matcher = PhoneticMatcher()
    
    # List of tuples containing (Target Name, Reference Name) to test various edge cases:
    # 1. Spelling variants (Muhammad/Mohd)
    # 2. Initials (John Doe/J Doe)
    # 3. Expansion of initials (JK Rowling/Joanne Kathleen Rowling)
    # 4. Spacing differences (Abu Bakar/Abubakar)
    test_cases = [
        ("Muhammad", "Mohd"),
        ("John Doe", "J Doe"),
        ("JK Rowling", "Joanne Kathleen Rowling"),
        ("Abu Bakar", "Abubakar"),
    ]
    
    # Print diagnostic header
    print("Running Verification Tests...")
    print("-" * 40)
    
    # Iterate through each test case
    for target, reference in test_cases:
        # Perform the match with debug=True to see the internal trace of segment matches
        result = matcher.match(target, reference, debug=True)
        # Output the final calculated similarity percentage
        print(f"Result: {result['F1']}%")
        # Visual separator for readability
        print("-" * 40)

# Standard Python entry point boilerplate
if __name__ == "__main__":
    # Execute the test suite
    run_tests()

