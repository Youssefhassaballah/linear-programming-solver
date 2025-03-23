import numpy as np

class GoalProgramming:
    def __init__(self, goals, constraints, rhs, constraint_types, var_restrictions):
        self.goals = sorted(goals, key=lambda x: x[2], reverse=True)
        self.constraints = np.array(constraints, dtype=float)
        self.rhs = np.array(rhs, dtype=float)
        self.constraint_types = constraint_types
        self.var_restrictions = var_restrictions
        self.steps = []
        self.solution = []
        self.num_vars = len(constraints[0])
        self.num_goals = len(self.goals)
        self.num_constraints = len(constraints)
        self.slack_vars = [f"s{i+1}" for i in range(self.num_constraints)]
        self.deviation_vars_plus = [f"d{i+1}_+" for i in range(self.num_goals)]
        self.deviation_vars_minus = [f"d{i+1}_-" for i in range(self.num_goals)]
        self.total_vars = self.num_vars + self.num_constraints + 2 * self.num_goals
        self.tableau = np.zeros((self.num_goals + self.num_goals + self.num_constraints, self.total_vars + 1))
        self.headers = ([f"x{i+1}" for i in range(self.num_vars)] + self.slack_vars +
                        self.deviation_vars_plus + self.deviation_vars_minus + ["RHS"])
        self.row_headers = ([f"Z{i+1}" for i in range(self.num_goals)] +
                            [f"d{i+1}_-" for i in range(self.num_goals)] + self.slack_vars)
        self._initialize_tableau()
    
    def _initialize_tableau(self):
        for i, goal in enumerate(self.goals):
            coeffs, target, priority = goal
            self.tableau[i, :self.num_vars] = np.array(coeffs) * priority
            self.tableau[i, self.num_vars + self.num_constraints + i] = -priority
            self.tableau[i, self.num_vars + self.num_constraints + self.num_goals + i] = 0
            self.tableau[i, -1] = target
        
        for i, goal in enumerate(self.goals):
            coeffs, target, priority = goal
            row = self.num_goals + i
            self.tableau[row, :self.num_vars] = coeffs
            self.tableau[row, self.num_vars + self.num_constraints + i] = 0
            self.tableau[row, self.num_vars + self.num_constraints + self.num_goals + i] = 1
            self.tableau[row, -1] = target
        
        for i in range(self.num_constraints):
            row = 2 * self.num_goals + i
            self.tableau[row, :self.num_vars] = self.constraints[i]
            self.tableau[row, self.num_vars + i] = 1  # Adding slack variable
            self.tableau[row, -1] = self.rhs[i]
        
        self.steps.append(self.format_tableau())
        
        self.steps.append(self.format_tableau())
    
    def solve(self):
        for i in range(self.num_goals):
            new_tableau, new_row_headers, stop = self.simplex_method(i)
            if stop:
                break
            self.tableau = new_tableau
            self.row_headers = new_row_headers
            self.steps.append(self.format_tableau())
            
            if all(header in self.row_headers for header in self.headers[:self.num_vars]):
                self.extract_solution()
                return
        
        self.extract_solution()
    
    def simplex_method(self, goal_index):
        max_iterations = 1000  
        iterations = 0
        while iterations < max_iterations:
            pivot_col = np.argmax(self.tableau[goal_index, :-1])
            if self.tableau[goal_index, pivot_col] <= 0:
                return self.tableau, self.row_headers, False
            
            valid_rows = np.where((self.tableau[:, pivot_col] > 0) & (~np.char.startswith(self.row_headers, 'Z')))[0]
            if len(valid_rows) == 0:
                return self.tableau, self.row_headers, True
            
            ratios = self.tableau[valid_rows, -1] / self.tableau[valid_rows, pivot_col]
            pivot_row = valid_rows[np.argmin(ratios)]
            
            if np.isinf(ratios[np.argmin(ratios)]):
                return self.tableau, self.row_headers, True
            
            pivot_element = self.tableau[pivot_row, pivot_col]
            if pivot_element == 0:
                return self.tableau, self.row_headers, True
            
            self.tableau[pivot_row, :] /= pivot_element
            for i in range(len(self.tableau)):
                if i != pivot_row:
                    self.tableau[i, :] -= self.tableau[i, pivot_col] * self.tableau[pivot_row, :]
            
            self.row_headers[pivot_row] = self.headers[pivot_col]
            iterations += 1
        
        return self.tableau, self.row_headers, False
    
    def extract_solution(self):
        self.solution = [0.0] * self.num_vars
        for i in range(self.num_vars):
            var_name = f"x{i+1}"
            if var_name in self.row_headers:
                self.solution[i] = float(self.tableau[self.row_headers.index(var_name), -1])
                
    
    def format_tableau(self):
        table_str = "Basic\t" + "\t".join(self.headers) + "\n"
        for i, row_name in enumerate(self.row_headers):
            table_str += f"{row_name}\t" + "\t".join(map(lambda x: f"{x:.2f}", self.tableau[i])) + "\n"
        return table_str
    


def main():
    goals = [([200, 0], 1000, 1), ([100, 400], 1200, 2), ([0, 250], 800, 1)]
    constraints = [[1500, 3000]]
    rhs = [15000]
    constraint_types = ['<=']
    var_restrictions = ['>=0', '>=0']
    gp = GoalProgramming(goals, constraints, rhs, constraint_types, var_restrictions)
    gp.solve()
    print(gp.solution)
    for step in gp.steps:
        print (step)


main()