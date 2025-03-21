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
    
    print("Initial Tableau:")
    print_tableau(tableau, headers, num_goals, num_constraints)
    
    for i in range(num_goals):
        print(f"\nSolving for Goal {i+1} (Priority {goals[i][2]}):")
        new_tableau = simplex_method(tableau, headers, i)
        if new_tableau is None:
            print("Stopping as further optimization would ruin higher priority goals.")
            break
        tableau = new_tableau
        print_tableau(tableau, headers, num_goals, num_constraints)
    
    print("\nFinal Optimized Tableau:")
    print_tableau(tableau, headers, num_goals, num_constraints)
    print_optimal_solution(tableau, headers, num_vars)

def simplex_method(tableau, headers, goal_index):
    max_iterations = 20
    iterations = 0
    while iterations < max_iterations:
        pivot_col = np.argmax(tableau[goal_index, :-1])
        if tableau[goal_index, pivot_col] <= 0:
            break
        
        if np.all(tableau[:, pivot_col] <= 0):
            print("No valid pivot found. Stopping.")
            return None
        
        ratios = np.where(tableau[:, pivot_col] > 0, tableau[:, -1] / tableau[:, pivot_col], np.inf)
        pivot_row = np.argmin(ratios)
        
        if np.isinf(ratios[pivot_row]):
            print("Unbounded solution detected. Stopping.")
            return None
        
        pivot_element = tableau[pivot_row, pivot_col]
        if pivot_element == 0:
            print("Pivot element is zero. Stopping.")
            return None
        
        print(f"Pivot Column: {headers[pivot_col]}, Pivot Row: {pivot_row + 1}")
        tableau[pivot_row, :] /= pivot_element
        for i in range(len(tableau)):
            if i != pivot_row:
                tableau[i, :] -= tableau[i, pivot_col] * tableau[pivot_row, :]
        
        headers[pivot_col] = headers[pivot_row + len(headers) - len(tableau) - 1]
        
        print("Updated Tableau after Pivot Exchange:")
        print_tableau(tableau, headers, len(headers) - 1 - len(tableau), len(tableau) - len(headers) + 1)
        
        iterations += 1
    
    if iterations >= max_iterations:
        print("Maximum iterations reached. Stopping to prevent infinite loop.")
        return None
    
    return tableau

def print_tableau(tableau, headers, num_goals, num_constraints):
    table_str = "Basic\t" + "\t".join(headers) + "\n"
    for i in range(num_goals):
        table_str += f"Z{i+1}\t" + "\t".join(map(lambda x: f"{x:.2f}", tableau[i])) + "\n"
    for i in range(num_goals):
        table_str += f"d{i+1}_-\t" + "\t".join(map(lambda x: f"{x:.2f}", tableau[num_goals + i])) + "\n"
    for i in range(num_constraints):
        row = 2 * num_goals + i
        if row < len(tableau):
            table_str += f"s{i+1}\t" + "\t".join(map(lambda x: f"{x:.2f}", tableau[row])) + "\n"
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
