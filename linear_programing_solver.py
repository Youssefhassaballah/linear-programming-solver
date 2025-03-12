import numpy as np

class LinearProgrammingSolver:
    def __init__(self, objective, constraints, rhs, constraint_types, var_restrictions, method="simplex", type="max"):
        self.objective = np.array(objective, dtype=float)
        self.constraints = np.array(constraints, dtype=float)
        self.rhs = np.array(rhs, dtype=float)
        self.constraint_types = constraint_types
        self.var_restrictions = var_restrictions
        self.method = method.lower()
        self.steps = []
        self.basic_vars = [f"s{i+1}" for i in range(len(self.constraints))]  
        self.type = type.lower()
        if self.type == "min":
            self.objective = -self.objective
        

    def solve(self):
        if self.method == "simplex":
            return self.simplex_method()
        elif self.method == "big-m":
            return self.big_m_method()
        elif self.method == "two-phase":
            return self.two_phase_method()
        elif self.method == "goal-programming":
            return self.goal_programming()
        else:
            raise ValueError("Invalid method selected")



    def log_step(self, tableau, headers):
        formatted_table = self.format_tableau(tableau, headers)
        self.steps.append(formatted_table)



    def format_tableau(self, tableau, headers):
        table_str = "Basic\t" + "\t".join(headers) + "\n"
        for i, row in enumerate(tableau):
            basic_var = "Z" if i == 0 else self.basic_vars[i-1]
            table_str += basic_var + "\t" + "\t".join(map(lambda x: f"{x:.2f}", row)) + "\n"
        return table_str



    def simplex_method(self):
        num_vars = len(self.objective)
        num_constraints = len(self.constraints)
        
        tableau = np.zeros((num_constraints + 1, num_vars + num_constraints + 1))
        
        tableau[1:, :num_vars] = self.constraints
        tableau[1:, num_vars:num_vars+num_constraints] = np.eye(num_constraints)
        tableau[1:, -1] = self.rhs
        tableau[0, :num_vars] = -self.objective
        
        headers = [f"x{i+1}" for i in range(num_vars)] + [f"s{i+1}" for i in range(num_constraints)] + ["RHS"]
        
        self.log_step(tableau, headers)
        

        while np.any(tableau[0, :-1] < 0):
            pivot_col = np.argmin(tableau[0, :-1])
            ratios = tableau[1:, -1] / tableau[1:, pivot_col]
            valid_ratios = [ratios[i] if tableau[i + 1, pivot_col] > 0 else np.inf for i in range(len(ratios))]
            pivot_row = np.argmin(valid_ratios) + 1
            
            # error
            if tableau[pivot_row, pivot_col] <= 0:
                return "Unbounded solution"
            
            tableau[pivot_row, :] /= tableau[pivot_row, pivot_col]
            
            for i in range(len(tableau)):
                if i != pivot_row:
                    tableau[i, :] -= tableau[i, pivot_col] * tableau[pivot_row, :]
            

            self.basic_vars[pivot_row - 1] = headers[pivot_col]
            
            self.log_step(tableau, headers)

        solution = np.zeros(num_vars)
        for i in range(num_vars):
            col = tableau[1:, i]
            if np.sum(col == 1) == 1 and np.sum(col == 0) == len(col) - 1:
                row_index = np.where(col == 1)[0][0] + 1
                solution[i] = tableau[row_index, -1]

        if self.type == "min":
            optimal_value = -tableau[0, -1]
        else:
            optimal_value = tableau[0, -1]
        
        
        return {"solution": solution, "optimal_value": optimal_value, "steps": self.steps}
    


    def big_m_method(self):
        return "Big-M method solution coming soon"



    def two_phase_method(self):
        return "Two-Phase method solution coming soon"



    def goal_programming(self):
        return "Goal Programming solution coming soon"



# Example usage
def main():
    objective = [5, -4, 6, -8]  # min
    constraints = [[1, 2, 2, 4], [2, -1, 1, 2], [4, -2, 1, -1]]
    rhs = [40, 8, 10]
    constraint_types = ['<=', '<=', '<=']
    var_restrictions = ['>=0', '>=0', '>=0']
    


    # objective = [3, 5]  # max
    # constraints = [[1, 2], [1, -1]]
    # rhs = [6, 1]
    # constraint_types = ['<=', '>=']
    # var_restrictions = ['>=0', '>=0']



    solver = LinearProgrammingSolver(objective, constraints, rhs, constraint_types, var_restrictions, method="simplex", type="min")
    solution = solver.solve()
    
    print("Optimal Solution:", solution["solution"])
    print("Optimal Value:", solution["optimal_value"])
    print("Steps:")
    for step in solution["steps"]:
        print(step)
        print("------------------")


main()

# x1 + 2x2 + 2x3 + 4x4 ≤ 40
# 2x1 − x2 + x3 + 2x4 ≤ 8
# 4x1 − 2x2 + x3 − x4 ≤ 10
# x1, x2, x3, x4 ≥ 0
# Solve for the objective function: Minimize z = 5x1 − 4x2 + 6x3 − 8x4