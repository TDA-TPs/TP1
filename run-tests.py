import os
import sys
import subprocess
import difflib

NOT_THE_SUSPECT = "No es el sospechoso correcto"

def extract_expected_results(file_path):
    """Parse the expected results file into a dictionary mapping filenames to their expected outputs."""
    expected_results = {}
    
    with open(file_path, 'r') as f:
        # Filter out comment lines
        lines = [line.strip() for line in f if not line.strip().startswith('//')]
    
    i = 0
    while i < len(lines):
        # Skip empty lines
        if not lines[i]:
            i += 1
            continue
        
        # This should be a filename
        filename = lines[i]
        i += 1
        
        # Collect all result lines until an empty line or end of file
        result_lines = []
        while i < len(lines) and lines[i]:
            result_lines.append(lines[i])
            i += 1
        
        # Store the expected result for this filename
        expected_results[filename] = '\n'.join(result_lines)
    
    return expected_results

def run_test(greedy_algorithm_path, test_file_path):
    """Run the greedy algorithm on a test file and return the output."""
    try:
        result = subprocess.run(
            ['python3', greedy_algorithm_path, test_file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error running test: {e.stderr}"

def find_differences(expected, actual):
    """Find and highlight the differences between expected and actual results."""
    if expected == actual:
        return None
    
    expected_lines = expected.split('\n')
    actual_lines = actual.split('\n')
    
    # Use difflib to find the differences
    diff = list(difflib.ndiff(expected_lines, actual_lines))
    
    # Filter to show only added, removed, or changed lines
    significant_diff = [line for line in diff if line.startswith('+ ') or line.startswith('- ') or line.startswith('? ')]
    
    return '\n'.join(significant_diff)

def main():
    if len(sys.argv) != 2:
        print("Usage: python run-tests.py <folder_path>")
        print("Example: python run-tests.py ./examples_catedra")
        print("Remember to have the greedy_algorithm.py file in the same directory and run the test while being in the folder that contains it.")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    greedy_algorithm_path = "./greedy_algorithm.py"
    report_file_path = "test_report.txt"
    
    # Check if the folder exists
    if not os.path.isdir(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        sys.exit(1)
    
    # Path to the expected results file
    expected_results_path = os.path.join(folder_path, "resultados-esperados.txt")
    
    # Check if the expected results file exists
    if not os.path.isfile(expected_results_path):
        print(f"Error: The expected results file '{expected_results_path}' does not exist.")
        sys.exit(1)
    
    # Extract expected results
    expected_results = extract_expected_results(expected_results_path)
    
    # Find all test files
    test_files = [
        f for f in os.listdir(folder_path) 
        if f.endswith('.txt') and f != "resultados-esperados.txt"
    ]
    
    # Run tests and compare results
    discrepancies = []
    
    for test_file in sorted(test_files):
        test_file_path = os.path.join(folder_path, test_file)
        print(f"Testing {test_file}...")
        actual_result = run_test(greedy_algorithm_path, test_file_path)
        
        # Special handling for files ending with "-no-es.txt" or "-no-es-bis.txt"
        if test_file.endswith("-no-es.txt") or test_file.endswith("-no-es-bis.txt"):
            if actual_result != NOT_THE_SUSPECT:
                discrepancies.append({
                    'test_file': test_file,
                    'expected': NOT_THE_SUSPECT,
                    'actual': actual_result,
                    'diff': f"Expected '{NOT_THE_SUSPECT}', got a different result"
                })
        elif test_file in expected_results:
            expected_result = expected_results[test_file]
            if expected_result != actual_result:
                diff = find_differences(expected_result, actual_result)
                discrepancies.append({
                    'test_file': test_file,
                    'expected': expected_result,
                    'actual': actual_result,
                    'diff': diff
                })
        else:
            discrepancies.append({
                'test_file': test_file,
                'expected': "No expected result found",
                'actual': actual_result,
                'diff': "No expected result to compare with"
            })
    
    # Generate report
    with open(report_file_path, 'w') as f:
        f.write("# Test Report\n\n")
        
        if not discrepancies:
            f.write("All tests passed! No discrepancies found.\n")
        else:
            f.write(f"Found {len(discrepancies)} discrepancies:\n\n")
            
            for i, discrepancy in enumerate(discrepancies, 1):
                f.write(f"## {i}. Test: {discrepancy['test_file']}\n\n")
                f.write("### Differences:\n")
                f.write(f"```\n{discrepancy['diff']}\n```\n\n")
                f.write("### Expected:\n")
                f.write(f"```\n{discrepancy['expected']}\n```\n\n")
                f.write("### Actual:\n")
                f.write(f"```\n{discrepancy['actual']}\n```\n\n")
                f.write("---\n\n")
    
    print(f"\nTesting complete. Report generated at {report_file_path}")
    print(f"Total test files: {len(test_files)}")
    print(f"Discrepancies found: {len(discrepancies)}")
    if discrepancies:
        print("Failed tests:")
        for disc in discrepancies:
            print(f"  - {disc['test_file']}")

if __name__ == "__main__":
    main()