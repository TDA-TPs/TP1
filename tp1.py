import heapq
import sys

NOT_THE_SUSPECT = "No es el sospechoso correcto"

def tie_break_candidates(transactions_candidates):
    '''
    Given a list of transactions candidates, it returns the one with the smallest finish time

    Args:
        - transactions_candidates: list of tuples (transaction, index).
    E.g. [((1, 2, 3, (2, 1)), 0), ((2, 3, 4, (2, 1)), 1), ...]

    Returns:
        - The transaction with the smallest finish time and its index.
    E.g. ((1, 2, 3, (2, 1)), 0)
    '''
    first_to_finish = transactions_candidates[0][0][2]
    first_to_finish_transaction = transactions_candidates[0]
    for i in range(len(transactions_candidates)):
        actual_transaction_finish_time = transactions_candidates[i][0][2]
        if actual_transaction_finish_time < first_to_finish:
            first_to_finish = actual_transaction_finish_time
            first_to_finish_transaction = transactions_candidates[i]
    return first_to_finish_transaction[0][3], first_to_finish_transaction[1]

                      
def suspicious_transaction_is_in_range(suspicious_transaction, transaction_candidate):
    if transaction_candidate[0] <= suspicious_transaction and transaction_candidate[2] >= suspicious_transaction:
        return True
    return False


def check_suspicius_transactions(n, transactions_with_error, suspicious_transactions):
    res = []

    # O(n)
    transactions_with_error = [(t[0] - t[1] if t[0] - t[1] > 0 else 0, t[0], t[0] + t[1], t) for t in transactions_with_error]  # (ti - ei, ti, ti + ei, t)
    
    # Sort transactions by start time (ti - ei)
    # O(n log n)
    transactions_with_error.sort(key=lambda x: x[0])

    # O(n)
    for i in range(n):
        actual_suspicious_transaction = suspicious_transactions[i]
        # print("Actual suspicious transaction: ", actual_suspicious_transaction)
        transactions_candidates = []
        # O(n)
        for i in range(len(transactions_with_error)):
            actual_transaction = transactions_with_error[i]
            if suspicious_transaction_is_in_range(actual_suspicious_transaction, actual_transaction):
                transactions_candidates.append((actual_transaction, i))

        if not transactions_candidates:
            return NOT_THE_SUSPECT
        # print("Transactions candidates: ", transactions_candidates)
        # O(n)
        final_candidate, index = tie_break_candidates(transactions_candidates)
        res.append((actual_suspicious_transaction, final_candidate))
        # print("Final candidate: ", final_candidate)
        # O(n)
        transactions_with_error = [t for i, t in enumerate(transactions_with_error) if i != index]
    return res


def read_and_process_file(file_path):
    """
    Reads input from a file and processes transactions
    
    Format:
    - First line: n (number of transactions)
    - Next n lines: timestamp,error for transactions_with_error
    - Next n lines: suspicious transaction timestamps
    
    Note: Lines starting with # are treated as comments and skipped
    """
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines() if not line.strip().startswith('#')]
        
        n = int(lines[0])
        
        transactions_with_error = []
        for i in range(1, n+1):
            timestamp, error = lines[i].split(',')
            transactions_with_error.append([int(timestamp), int(error)])
        
        suspicious_transactions = []
        for i in range(n+1, 2*n+1):
            suspicious_transactions.append(int(lines[i]))
        
        # print(f"Processing {n} transactions...")
        # print(f"Transactions with error: {transactions_with_error}")
        # print(f"Suspicious transactions: {suspicious_transactions}")
        
        result = check_suspicius_transactions(n, transactions_with_error, suspicious_transactions)
        return result
    
def format_result(result):
    if result == NOT_THE_SUSPECT:
        return NOT_THE_SUSPECT
    
    formatted_lines = []
    for suspicious_timestamp, transaction in result:
        timestamp, error = transaction
        formatted_lines.append(f"{suspicious_timestamp} --> {timestamp} ± {error}")
    
    return "\n".join(formatted_lines)

if __name__ == "__main__":

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        result = read_and_process_file(file_path)
        formatted_result = format_result(result)
        print(formatted_result)
    else:
        print("Please provide a file path as an argument")
        print("Example: python3 tp1.py route/to/file.txt")

"""
The algorithm is greedy because it follows this approach:
For each suspicious transaction it:
Picks the candidate transaction whose start time (ti - ei) is the smallest of all, that is, the first available transaction.
Then, if the suspicious transaction is in the range of the candidate transaction, it is added to the list of candidates. If it is not, the candidate is re-pushed to the heap (and it does not check for further candidates because we decided to use a heap of minimum start time).
Finally, it tie breaks the candidates by choosing the one has the smallest finish time (ti + ei), adds it to the result list and re-pushies the remaining candidates back to the heap.
By choosing the local optimal solution (the first available transaction) we reach the global optimal solution.
"""

"""
Time complexity:
O(n) + O(n log n) + (O(n) * ( O(n) + O(n) + O(n) )) = O(n) + (O(n) * (O(n))) - O(n) + O(n^2) = O(n^2) 
"""
