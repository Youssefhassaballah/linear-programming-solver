import numpy as np

class LinearProgrammingSolver:
    def __init__(self, objective, constraints, rhs, constraint_types, var_restrictions, method="simplex", type="max"):
        self.objective = np.array(objective, dtype=float)
        self.constraints = np.array(constraints, dtype=float)
        self.rhs = np.array(rhs, dtype=float)
        self.constraint_types = constraint_types
        self.var_restrictions = var_restrictions
        self.method = method.lower()
        self.big_m = 1e2 
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
        # Create a copy of the tableau
        modified_tableau = tableau.copy()
        # Multiply first row by -1
        if(self.type == "min"):
            modified_tableau[0] = [x if np.isclose(x, 0, atol=1e-10) else -x for x in modified_tableau[0]]
        # Format and store the modified tableau
        formatted_table = self.format_tableau(modified_tableau, headers)
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
                return {
                    "solution": None,
                    "optimal_value": None,
                    "error": "Unbounded solution",
                    "steps": self.steps}
            
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
        num_vars = len(self.objective)
        num_constraints = len(self.constraints)
        surplus_vars = []
        artificial_vars = []
        for i, c_type in enumerate(self.constraint_types):
            if c_type == '=':  
                artificial_vars.append(i)
            elif c_type == '>=' or c_type == '<=':  
                surplus_vars.append(i)  
                artificial_vars.append(i)
        num_surplus = len(surplus_vars)
        num_artificial = len(artificial_vars)
        total_vars = num_vars + num_surplus + num_artificial
        tableau = np.zeros((num_constraints + 1, total_vars + 1))
        tableau[1:, :num_vars] = self.constraints
        tableau[1:, -1] = self.rhs
        surplus_start = num_vars
        artificial_start = num_vars + num_surplus

        for i, row in enumerate(surplus_vars):
            if self.constraint_types[row] == '<=':
                tableau[row + 1, surplus_start + i] = 1
            else:
                tableau[row + 1, surplus_start + i] = -1
        for i, row in enumerate(artificial_vars):
            tableau[row + 1, artificial_start + i] = 1  
        
        for i, row in enumerate(artificial_vars):
            tableau[0, artificial_start + i] = self.big_m  
        tableau[0, :num_vars] = -self.objective
        headers = (
            [f"x{i+1}" for i in range(num_vars)] + 
            [f"s{i+1}" for i in range(num_surplus)] + 
            [f"A{i+1}" for i in range(num_artificial)] + 
            ["RHS"]
        )
        self.basic_vars = [f"A{i+1}" for i in range(num_artificial)]
        
        self.log_step(tableau, headers)
        for i, row in enumerate(artificial_vars):
            tableau[0, :artificial_start] -= self.big_m * tableau[row + 1, :artificial_start]
            tableau[0, artificial_start + i] = 0
        for i in tableau[1:,-1]:
            tableau[0,-1] -= i*self.big_m
        
        self.log_step(tableau, headers)
        while np.any(tableau[0, :-1] < 0):  
            pivot_col = np.argmin(tableau[0, :-1])  
            column_entries = tableau[1:, pivot_col]  
            valid_rows = column_entries > 0  
            if not np.any(valid_rows):  
                return {
                    "solution": None,
                    "optimal_value": None,
                    "error": "Unbounded solution",
                    "steps": self.steps
                }
            ratios = np.where(valid_rows, tableau[1:, -1] / column_entries, np.inf)
            if np.all(ratios == np.inf):  
                return {
                    "solution": None,
                    "optimal_value": None,
                    "error": "Unbounded solution",
                    "steps": self.steps
                }
            pivot_row = np.argmin(ratios) + 1  
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
        optimal_value=0
        for i in range(num_vars):
            optimal_value += self.objective[i]*solution[i]

        if self.type == "min":
            optimal_value = -optimal_value
        return {"solution": solution, "optimal_value":  optimal_value, "steps": self.steps}




    def two_phase_method(self):
        num_vars = len(self.objective)
        num_constraints = len(self.constraints)
        surplus_vars = []
        artificial_vars = []

        for i, c_type in enumerate(self.constraint_types):
            if c_type == '=':
                artificial_vars.append(i)
            elif c_type == '>='or c_type == '<=' :
                surplus_vars.append(i)
                artificial_vars.append(i)

        num_surplus = len(surplus_vars)
        num_artificial = len(artificial_vars)
        total_vars = num_vars + num_surplus + num_artificial

        tableau = np.zeros((num_constraints + 1, total_vars + 1))

        tableau[1:, :num_vars] = self.constraints
        tableau[1:, -1] = self.rhs

        surplus_start = num_vars
        artificial_start = num_vars + num_surplus

        for i, row in enumerate(surplus_vars):
            if self.constraint_types[row] == '<=':
                tableau[row + 1, surplus_start + i] = 1
            else:
                tableau[row + 1, surplus_start + i] = -1 

        for i, row in enumerate(artificial_vars):
            tableau[row + 1, artificial_start + i] = 1  

        for i, row in enumerate(artificial_vars):
            tableau[0, artificial_start + i] = 1  

        headers = (
            [f"x{i+1}" for i in range(num_vars)] + 
            [f"s{i+1}" for i in range(num_surplus)] + 
            [f"A{i+1}" for i in range(num_artificial)] + 
            ["RHS"]
        )

        self.basic_vars = [f"A{i+1}" for i in range(num_artificial)]

        self.log_step(tableau, headers)

        for i, row in enumerate(artificial_vars):
            tableau[0, :] -= tableau[row + 1, :]

        self.log_step(tableau, headers)

        while np.any(tableau[0, :-1] < 0):
            pivot_col = np.argmin(tableau[0, :-1])
            column_entries = tableau[1:, pivot_col]
            valid_rows = column_entries > 0  

            if not np.any(valid_rows):  
                return {
                    "solution": None,
                "optimal_value": None,
                "error": "Unbounded solution",
                "steps": self.steps
            }

            ratios = np.where(valid_rows, tableau[1:, -1] / column_entries, np.inf)
            pivot_row = np.argmin(ratios) + 1  

            tableau[pivot_row, :] /= tableau[pivot_row, pivot_col]

            for i in range(len(tableau)):
                if i != pivot_row:
                    tableau[i, :] -= tableau[i, pivot_col] * tableau[pivot_row, :]

            self.basic_vars[pivot_row - 1] = headers[pivot_col]

            self.log_step(tableau, headers)

        if not np.isclose(tableau[0, -1], 0):
            return {
            "solution": None,
            "optimal_value": None,
            "error": "Infeasible solution",
            "steps": self.steps
        }

        tableau = np.delete(tableau, artificial_start + np.arange(num_artificial), axis=1)
        headers = headers[:artificial_start] + ["RHS"]

        tableau[0, :num_vars] = -self.objective
        self.log_step(tableau, headers)

        while np.any(tableau[0, :-1] < 0):
            pivot_col = np.argmin(tableau[0, :-1])
            column_entries = tableau[1:, pivot_col]
            valid_rows = column_entries > 0  

            if not np.any(valid_rows):  
                return {
                "solution": None,
                "optimal_value": None,
                "error": "Unbounded solution",
                "steps": self.steps
            }

            ratios = np.where(valid_rows, tableau[1:, -1] / column_entries, np.inf)
            pivot_row = np.argmin(ratios) + 1  

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
        optimal_value = tableau[0, -1] 
        return {"solution": solution, "optimal_value": optimal_value, "steps": self.steps}




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

    # objective = [1, 2, 1]  
    # constraints = [[1, 1, 1], [2, -5, 1]]
    # rhs = [7, 10]
    # constraint_types = ['=', '>=']
    # var_restrictions = ['>=0', '>=0', '>=0']
    
    # solver = LinearProgrammingSolver(objective, constraints, rhs, constraint_types, var_restrictions, method="big-m", type="min")
    # solution = solver.solve()
=======

    objective = [1, 2, 1]  
    constraints = [[1, 1, 1], [2, -5, 1]]
    rhs = [7, 10]
    constraint_types = ['=', '>=']
    var_restrictions = ['>=0', '>=0', '>=0']
    
    # solver = LinearProgrammingSolver(objective, constraints, rhs, constraint_types, var_restrictions, method="big-m", type="min")
    # solution = solver.solve()
    
    
    solver = LinearProgrammingSolver(objective, constraints, rhs, constraint_types, var_restrictions, method="two-phase")
    solution = solver.solve()


    #solver = LinearProgrammingSolver(objective, constraints, rhs, constraint_types, var_restrictions, method="simplex", type="min")
    #solution = solver.solve()
    
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