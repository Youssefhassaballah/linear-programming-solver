import numpy as np
from tabulate import tabulate

class GoalSolver:
    def __init__(self, c, A, b, goals, priority, constraint_types, variable_restrictions, problem_type='min'):
        self.c = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)
        self.goals = np.array(goals, dtype=float)
        self.priority = np.array(priority, dtype=float)
        self.constraint_types = constraint_types
        self.variable_restrictions = variable_restrictions
        self.problem_type = problem_type
        self.num_vars = len(c)
        self.num_constraints = len(b)
        self.num_goals = len(goals)
        self.tableau = None
        self.basis = None
        self.optimal_solution = None
        self.optimal_value = None
        self.status = None
        self.headers = None
        self.tableau_rows = None
        self.steps = []

    def initialize_tableau(self):
        num_slack =0
        num_deviation =0
        for i in range(self.num_constraints):
         if self.constraint_types[i] == '<=' :
            num_slack += 1
         elif self.constraint_types[i] == '>=' :
            num_deviation +=1

        total_vars = self.num_vars + 2*num_deviation + num_slack
        self.tableau = np.zeros((self.num_constraints + self.num_goals , total_vars + 1)) 

        slack_index = self.num_vars 
        deviation_index = self.num_vars + num_slack

        for i in range(self.num_constraints):
            if self.constraint_types[i] == '<=':
                self.tableau[i, :self.num_vars] = self.A[i]  
                self.tableau[i, slack_index] = 1  # Slack variable
                slack_index += 1
            elif self.constraint_types[i] == '>=':
                self.tableau[i, :self.num_vars] = self.A[i]  
                self.tableau[i, deviation_index] = 1  # d-
                self.tableau[i, deviation_index + self.num_goals] = -1  # d+
                deviation_index += 1

            self.tableau[i, -1] = self.b[i]    

        for i in range(self.num_goals): 
            goal_row = self.num_constraints + i
            self.tableau[goal_row, self.num_vars + num_slack + i ] =-self.priority[i]

        self.basis = list(range(self.num_vars, total_vars))  

    def format_tableau_as_string(self):
        formatted_string = "\t".join(self.headers) + "\n"
        for row in self.tableau_rows:
            formatted_string += "\t".join(map(str, row)) + "\n"
        return formatted_string
    
    def display_tableau(self):
        self.headers = ['Basic'] + [f'x{i + 1}' for i in range(self.num_vars)]

        slack_count = sum(1 for t in self.constraint_types if t == '<=')
        deviation_count = sum(2 if t in ('>=') else 0 for t in self.constraint_types)

        self.headers += [f's{i + 1}' for i in range(slack_count)]
        for i in range (deviation_count//2):
           self.headers += [f'd-{i + 1}']
        for i in range (deviation_count//2):
           self.headers += [f'd+{i + 1}']   
        self.headers.append('RHS')

        self.tableau_rows = []
        for i in range(self.num_constraints):
            if self.basis[i] < self.num_vars:
                basic_var = f'x{self.basis[i] + 1}'  # Decision variable
            elif self.basis[i] < self.num_vars + slack_count:
                basic_var = f's{self.basis[i] - self.num_vars + 1}'  # Slack variable
            else:
                deviation_index = self.basis[i] - self.num_vars - slack_count
                if deviation_index < self.num_goals:  # First two deviation variables are d1- and d2-
                    basic_var = f'd{deviation_index + 1}-'  # d1-, d2-
                else:
                    if deviation_index % 2 == 0:
                        basic_var = f'd{(deviation_index // 2) + 1}+'  # Positive deviation
                    else:
                        basic_var = f'd{(deviation_index // 2) + 1}-'
                    

        # Add the row to the tableau
            row = [basic_var] + list(self.tableau[i, :])
            self.tableau_rows.append(row)

        for i in range(self.num_goals):
            row = [f'Z{i + 1}'] + list(self.tableau[self.num_constraints + i, :])
            self.tableau_rows.append(row)

        self.steps.append(self.format_tableau_as_string())

    def make_consistent(self):  
        for i in range (self.num_goals) :
            goal_row = self.num_constraints + i
            self.tableau[goal_row,] = self.tableau[goal_row,] + self.priority[i]*self.tableau[goal_row-self.num_goals]

    def solve_priority(self, priority_level,index, display_steps=False):
        iteration = 0
        while True:
            if display_steps:
                self.display_tableau()
            
            if all(self.tableau[self.num_constraints+index, :-1] >= 0):
                self.status = 'optimal'
                break
            
            entering_var = np.argmin(self.tableau[self.num_constraints+index, :-1])
            
            if all(self.tableau[:-1, entering_var] <= 0):
                self.status = 'unbounded'
                break
            
            ratios = []
            for i in range(self.num_constraints):
                if self.tableau[i, entering_var] > 0:
                    ratios.append(self.tableau[i, -1] / self.tableau[i, entering_var])
                else:
                    ratios.append(np.inf)
            leaving_var = np.argmin(ratios)
            
            pivot_element = self.tableau[leaving_var, entering_var]
            self.tableau[leaving_var, :] /= pivot_element
            for i in range(self.num_constraints + 1):
                if i != leaving_var:
                    self.tableau[i, :] -= self.tableau[i, entering_var] * self.tableau[leaving_var, :]
            
            self.basis[leaving_var] = entering_var
            iteration += 1

    def solve(self, display_steps=False):
        self.initialize_tableau()
        self.make_consistent()
        priority_map = {priority: index for index, priority in enumerate(self.priority)}
        sorted_priorities = sorted(priority_map.items(), key=lambda item: item[0], reverse=True)
        for priority ,index in sorted_priorities:
         self.solve_priority(priority,index, display_steps)
        
        self.optimal_solution = np.zeros(self.num_vars)
        for i in range(self.num_constraints):
            if self.basis[i] < self.num_vars:
                self.optimal_solution[self.basis[i]] = self.tableau[i, -1]
        self.optimal_value = self.tableau[-1, -1]
    def get_results(self):
        
        return {
            'optimal_solution': self.optimal_solution,
            'optimal_value': self.optimal_value,
            'status': self.status,
            'steps': self.steps
        }




def main():
    c = [5, -4]
    A = [
        [1.5,3],  
        [200,0],  
        [100,400],
        [0,250]  
    ]
    b = [15, 1000, 1200 ,800]  
    goals = [30, 15,100]  
    priority = [1, 2 ,1]  
    constraint_types = ['<=','>=', '>=', '>=']
    variable_restrictions = ['non-negative', 'non-negative']

    solver = GoalSolver(c, A, b, goals, priority, constraint_types, variable_restrictions)
    solver.solve(display_steps=True)
    results = solver.get_results()
    print("\nOptimal Solution:", results['optimal_solution'])
    print("Optimal Value:", results['optimal_value'])
    print("Status:", results['status'])
    for step in results['steps']:
        print(step)
    

main()