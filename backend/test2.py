import numpy as np

def goal_programming(goals, constraints, rhs, constraint_types, var_restrictions):
    constraints = np.array(constraints, dtype=float)
    rhs = np.array(rhs, dtype=float)
    goals = sorted(goals, key=lambda x: x[2], reverse=True)
    num_vars = len(constraints[0])
    num_goals = len(goals)
    num_constraints = len(constraints)
    slack_vars = [f"s{i+1}" for i in range(num_constraints)]
    deviation_vars_plus = [f"d{i+1}_+" for i in range(num_goals)]
    deviation_vars_minus = [f"d{i+1}_-" for i in range(num_goals)]
    total_vars = num_vars + num_constraints + 2 * num_goals
    tableau = np.zeros((num_goals + num_goals + num_constraints, total_vars + 1))
    
    for i, goal in enumerate(goals):
        coeffs, target, priority = goal
        tableau[i, :num_vars] = np.array(coeffs) * priority
        tableau[i, num_vars + num_constraints + i] = -priority
        tableau[i, num_vars + num_constraints + num_goals + i] = 0
        tableau[i, -1] = target
    
    for i, goal in enumerate(goals):
        coeffs, target, priority = goal
        row = num_goals + i
        tableau[row, :num_vars] = coeffs
        tableau[row, num_vars + num_constraints + i] = 0
        tableau[row, num_vars + num_constraints + num_goals + i] = 1
        tableau[row, -1] = target
    
    for i in range(num_constraints):
        row = 2 * num_goals + i
        tableau[row, :num_vars] = constraints[i]
        tableau[row, num_vars + i] = 1
        tableau[row, -1] = rhs[i]
    
    headers = (
        [f"x{i+1}" for i in range(num_vars)] +
        slack_vars +
        deviation_vars_plus +
        deviation_vars_minus +
        ["RHS"]
    )
    row_headers = (
        [f"Z{i+1}" for i in range(num_goals)] +
        [f"d{i+1}_-" for i in range(num_goals)] +
        slack_vars
    )
    
    print("Initial Tableau:")
    print_tableau(tableau, headers, row_headers)
    
    for i in range(num_goals):
        print(f"\nSolving for Goal {i+1} (Priority {goals[i][2]}):")
        new_tableau, new_row_headers = simplex_method(tableau, headers, row_headers, i, num_goals)
        if new_tableau is None:
            print("Stopping as further optimization would ruin higher priority goals.")
            break
        tableau = new_tableau
        row_headers = new_row_headers
        print_tableau(tableau, headers, row_headers)
    
    print("\nFinal Optimized Tableau:")
    print_tableau(tableau, headers, row_headers)
    print_optimal_solution(tableau, headers, num_vars)

def simplex_method(tableau, headers, row_headers, goal_index, num_goals):
    max_iterations = 1000  
    iterations = 0
    while iterations < max_iterations:
        pivot_col = np.argmax(tableau[goal_index, :-1])
        if tableau[goal_index, pivot_col] <= 0:
            break
        
        valid_rows = np.where((tableau[:, pivot_col] > 0) & (~np.char.startswith(row_headers, 'Z')))[0]
        if len(valid_rows) == 0:
            print("No valid pivot found. Stopping.")
            return None, row_headers
        
        ratios = tableau[valid_rows, -1] / tableau[valid_rows, pivot_col]
        pivot_row = valid_rows[np.argmin(ratios)]
        
        if np.isinf(ratios[np.argmin(ratios)]):
            print("Unbounded solution detected. Stopping.")
            return None, row_headers
        
        pivot_element = tableau[pivot_row, pivot_col]
        if pivot_element == 0:
            print("Pivot element is zero. Stopping.")
            return None, row_headers
        
        print(f"Pivot Column: {headers[pivot_col]}, Pivot Row: {row_headers[pivot_row]}")
        tableau[pivot_row, :] /= pivot_element
        for i in range(len(tableau)):
            if i != pivot_row:
                tableau[i, :] -= tableau[i, pivot_col] * tableau[pivot_row, :]
        
        row_headers[pivot_row] = headers[pivot_col]
        
        print("Updated Tableau after Pivot Exchange:")
        print_tableau(tableau, headers, row_headers)
        
        iterations += 1
    
    if iterations >= max_iterations:
        print("Maximum iterations reached. Stopping to prevent infinite loop.")
        return None, row_headers
    
    return tableau, row_headers

def print_tableau(tableau, headers, row_headers):
    table_str = "Basic\t" + "\t".join(headers) + "\n"
    for i, row_name in enumerate(row_headers):
        table_str += f"{row_name}\t" + "\t".join(map(lambda x: f"{x:.2f}", tableau[i])) + "\n"
    print(table_str)

def print_optimal_solution(tableau, headers, num_vars):
    print("\nOptimal Solution:")
    for i in range(num_vars):
        print(f"{headers[i]} = {tableau[-1, i]:.2f}")

def main():
    goals = [
        ([200, 0], 1000, 1),
        ([100, 400], 1200, 2),
        ([0, 250], 800, 1)
    ]
    constraints = [
        [1500, 3000]
    ]
    rhs = [15000]
    constraint_types = ['<=']
    var_restrictions = ['>=0', '>=0']
    goal_programming(goals, constraints, rhs, constraint_types, var_restrictions)

main()