import numpy as np

class LinearProgrammingSolver:
    def __init__(self, objective, constraints, rhs, constraint_types, var_restrictions, method="simplex", type="max"):
        self.method = method.lower()
        self.type = type.lower()
        self.big_m = 1e6
        self.steps = []
        
        self.original_var_count = len(objective)
        self.unrestricted_vars = []
        self.process_unrestricted_vars(objective, constraints, var_restrictions)
        
        self.objective = np.array(self.transformed_objective, dtype=float)
        self.constraints = np.array(self.transformed_constraints, dtype=float)
        self.rhs = np.array(rhs, dtype=float)
        self.constraint_types = constraint_types
        
        self.basic_vars = [f"s{i+1}" for i in range(len(self.constraints))]
        
        if self.type == "min":
            self.objective = -self.objective

    def process_unrestricted_vars(self, objective, constraints, var_restrictions):
        self.transformed_objective = []
        self.transformed_constraints = []
        
        for i, res in enumerate(var_restrictions):
            if res == "unrestricted":
                self.unrestricted_vars.append(i)
                self.transformed_objective.extend([objective[i], -objective[i]])
            else:
                self.transformed_objective.append(objective[i])
        
        for row in constraints:
            new_row = []
            for i, val in enumerate(row):
                if i in self.unrestricted_vars:
                    new_row.extend([val, -val])
                else:
                    new_row.append(val)
            self.transformed_constraints.append(new_row)
    
    def solve(self):
        if self.method == "simplex":
            return self.simplex_method()
        elif self.method == "big-m":
            return self.big_m_method()
        elif self.method == "two-phase":
            return self.two_phase_method()
        else:
            raise ValueError("Invalid method selected")

    def simplex_method(self):
        tableau = self.initialize_tableau()
        while not self.is_optimal(tableau):
            pivot_col = self.select_pivot_column(tableau)
            pivot_row = self.select_pivot_row(tableau, pivot_col)
            tableau = self.perform_pivot(tableau, pivot_row, pivot_col)
        return self.extract_solution(tableau)

    def initialize_tableau(self):
        tableau = np.hstack((self.constraints, np.eye(len(self.constraints)), self.rhs.reshape(-1, 1)))
        obj_row = np.hstack((-self.objective, np.zeros(len(self.constraints) + 1)))
        return np.vstack((tableau, obj_row))
    
    def is_optimal(self, tableau):
        return np.all(tableau[-1, :-1] >= 0)
    
    def select_pivot_column(self, tableau):
        return np.argmin(tableau[-1, :-1])
    
    def select_pivot_row(self, tableau, pivot_col):
        ratios = tableau[:-1, -1] / tableau[:-1, pivot_col]
        valid_ratios = np.where(tableau[:-1, pivot_col] > 0, ratios, np.inf)
        return np.argmin(valid_ratios)
    
    def perform_pivot(self, tableau, pivot_row, pivot_col):
        tableau[pivot_row] /= tableau[pivot_row, pivot_col]
        for i in range(len(tableau)):
            if i != pivot_row:
                tableau[i] -= tableau[i, pivot_col] * tableau[pivot_row]
        return tableau
    
    def extract_solution(self, tableau):
        solution = np.zeros(len(self.objective))
        for i in range(len(self.constraints)):
            if np.sum(tableau[i, :-1] == 1) == 1 and np.sum(tableau[i, :-1] != 0) == 1:
                col = np.where(tableau[i, :-1] == 1)[0][0]
                solution[col] = tableau[i, -1]
        return {"solution": solution, "optimal_value": tableau[-1, -1], "steps": self.steps}


def main():
    objective = [5, -4, 6, -8]  # Minimize
    constraints = [[1, 2, 2, 4], [2, -1, 1, 2], [4, -2, 1, -1]]
    rhs = [40, 8, 10]
    constraint_types = ['<=', '<=', '<=']
    var_restrictions = ['>=0', 'unrestricted', '>=0', '>=0']  # x2 is unrestricted
    
    solver = LinearProgrammingSolver(objective, constraints, rhs, constraint_types, var_restrictions, method="simplex")
    solution = solver.solve()
    
    print("Optimal Solution:", solution["solution"])
    print("Optimal Value:", solution["optimal_value"])
    print("Steps:")
    for step in solution["steps"]:
        print(step)
        print("------------------")

main()
