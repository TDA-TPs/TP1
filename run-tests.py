import os
import sys
import subprocess
import difflib

NOT_THE_SUSPECT = "No es el sospechoso correcto"

def extract_expected_results(file_path):
    """Parse the expected results file into a dictionary mapping filenames to their expected outputs."""
    expected_results = {}
    
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if not line.strip().startswith('//')]
    
    i = 0
    while i < len(lines):
        if not lines[i]:
            i += 1
            continue
        
        filename = lines[i]
        i += 1
        
        result_lines = []
        while i < len(lines) and lines[i]:
            result_lines.append(lines[i])
            i += 1
        
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
    
    diff = list(difflib.ndiff(expected_lines, actual_lines))
    
    significant_diff = [line for line in diff if line.startswith('+ ') or line.startswith('- ') or line.startswith('? ')]
    
    return '\n'.join(significant_diff)

def validate_assignments(actual_result, test_file_path):
    """
    Validate that each suspicious timestamp falls within the range of its assigned transaction.
    Returns a list of validation errors, or an empty list if all assignments are valid.
    """
    if actual_result == NOT_THE_SUSPECT:
        return []
    
    assignments = []
    for line in actual_result.split('\n'):
        if '-->' in line:
            parts = line.split('-->')
            suspicious_timestamp = int(parts[0].strip())
            transaction_parts = parts[1].strip().split('±')
            transaction_time = int(transaction_parts[0].strip())
            transaction_error = int(transaction_parts[1].strip())
            assignments.append((suspicious_timestamp, transaction_time, transaction_error))
    
    validation_errors = []
    for i, (suspicious_timestamp, transaction_time, transaction_error) in enumerate(assignments):
        lower_bound = transaction_time - transaction_error
        upper_bound = transaction_time + transaction_error
        
        if not (lower_bound <= suspicious_timestamp <= upper_bound):
            validation_errors.append(
                f"Invalid assignment: Timestamp {suspicious_timestamp} is outside the range of transaction {transaction_time}±{transaction_error} [{lower_bound}, {upper_bound}]"
            )
    
    return validation_errors

def main():
    if len(sys.argv) != 2:
        print("Usage: python run-tests.py <folder_path>")
        print("Example: python run-tests.py ./examples_catedra")
        print("Remember to have the greedy_algorithm.py file in the same directory and run the test while being in the folder that contains it.")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    greedy_algorithm_path = "./greedy_algorithm.py"
    report_file_path = "test_report.txt"
    validation_report_path = "validation_report.txt"
    
    if not os.path.isdir(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        sys.exit(1)
    
    expected_results_path = os.path.join(folder_path, "resultados-esperados.txt")
    
    if not os.path.isfile(expected_results_path):
        print(f"Error: The expected results file '{expected_results_path}' does not exist.")
        sys.exit(1)
    
    expected_results = extract_expected_results(expected_results_path)
    
    test_files = [
        f for f in os.listdir(folder_path) 
        if f.endswith('.txt') and f != "resultados-esperados.txt"
    ]
    
    discrepancies = []
    validation_issues = []
    
    for test_file in sorted(test_files):
        test_file_path = os.path.join(folder_path, test_file)
        print(f"Testing {test_file}...")
        actual_result = run_test(greedy_algorithm_path, test_file_path)
        
        errors = validate_assignments(actual_result, test_file_path)
        if errors:
            validation_issues.append({
                'test_file': test_file,
                'errors': errors
            })
        
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
    
    with open(validation_report_path, 'w') as f:
        f.write("# Validation Report\n\n")
        
        if not validation_issues:
            f.write("All assignments are valid! All suspicious timestamps fall within their assigned transaction ranges.\n")
        else:
            f.write(f"Found {len(validation_issues)} tests with invalid assignments:\n\n")
            
            for i, issue in enumerate(validation_issues, 1):
                f.write(f"## {i}. Test: {issue['test_file']}\n\n")
                for error in issue['errors']:
                    f.write(f"- {error}\n")
                f.write("\n---\n\n")
    
    print(f"\nTesting complete. Reports generated at:")
    print(f"- Test report: {report_file_path}")
    print(f"- Validation report: {validation_report_path}")
    print(f"Total test files: {len(test_files)}")
    print(f"Discrepancies found: {len(discrepancies)}")
    print(f"Files with invalid assignments: {len(validation_issues)}")
    
    if discrepancies:
        print("Failed tests:")
        for disc in discrepancies:
            print(f"  - {disc['test_file']}")
            
    if validation_issues:
        print("Tests with invalid assignments:")
        for issue in validation_issues:
            print(f"  - {issue['test_file']}")

if __name__ == "__main__":
    main()