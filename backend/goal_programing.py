import numpy as np
from tabulate import tabulate


class SimplexSolver:


    def __init__(self, coefficients, constraints, objective_coeffs, unrestricted_vars, is_maximization=True):

        self.is_maximization = 1 if is_maximization else -1
        self.num_constraints = len(coefficients)
        self.num_variables = len(coefficients[0])
        self.coefficients = np.array(coefficients, dtype=float)
        self.constraints = np.array(constraints, dtype=float)
        self.objective_coeffs = np.array(objective_coeffs, dtype=float) * -1
        self.unrestricted_vars = np.array(unrestricted_vars, dtype=float)
        self.num_unrestricted = int(np.sum(self.unrestricted_vars == 1))
        self.num_artificial = 0
        self.objective_value = 0
        self.basic_vars = [i + self.num_variables for i in range(self.num_constraints)]
        self.tableau_steps = []
        self.current_tableau = []
        self.variable_names = []
        self.unrestricted_indices = []

    def add_slack_variables(self):
        """Add slack variables to the coefficient matrix and objective function."""
        identity = np.eye(self.num_constraints)
        self.coefficients = np.hstack((self.coefficients, identity))
        self.objective_coeffs = np.append(self.objective_coeffs, np.zeros(self.num_constraints))

    def handle_unrestricted_variables(self):
        """Handle unrestricted variables by representing them as the difference of two non-negative variables."""
        if self.num_unrestricted > 0:
            for i in range(len(self.unrestricted_vars)):
                if self.unrestricted_vars[i] == 1:
                    # For each unrestricted variable, add its negative counterpart
                    negative_coeff = np.array(self.coefficients[:, i]) * -1
                    self.coefficients = np.hstack((self.coefficients, negative_coeff.reshape(-1, 1)))
                    self.objective_coeffs = np.append(self.objective_coeffs, self.objective_coeffs[i] * -1)
                    self.basic_vars.append(self.num_variables + self.num_constraints + i)

        # Track indices of unrestricted variables
        self.unrestricted_indices = [j for j in range(len(self.unrestricted_vars)) if self.unrestricted_vars[j] == 1]

    def solve(self):
        """
        Solve the linear programming problem using the Simplex method.

        Returns:
            tuple: (solution_vector, objective_value, status_message)
        """
        optimal = False
        self.record_tableau_step()

        while not optimal:
            # Find the entering variable (pivot column)
            if self.is_maximization == 1:
                pivot_col = np.argmin(self.objective_coeffs)
            else:
                pivot_col = np.argmax(self.objective_coeffs)

            # Check for unbounded solution
            if np.all(self.coefficients[:, pivot_col] <= 0):
                return None, None, "Unbounded solution"

            # Calculate ratios for minimum ratio test
            ratios = np.zeros(self.num_constraints)
            for i in range(self.num_constraints):
                if self.coefficients[i, pivot_col] > 0:
                    ratios[i] = self.constraints[i] / self.coefficients[i, pivot_col]
                else:
                    ratios[i] = np.inf

            # Find the leaving variable (pivot row)
            pivot_row = np.argmin(ratios)

            # Pivot operation
            pivot_element = self.coefficients[pivot_row, pivot_col]
            self.coefficients[pivot_row] /= pivot_element
            self.constraints[pivot_row] /= pivot_element

            # Update other rows
            for i in range(self.num_constraints):
                if i != pivot_row:
                    factor = self.coefficients[i, pivot_col]
                    self.coefficients[i] -= factor * self.coefficients[pivot_row]
                    self.constraints[i] -= factor * self.constraints[pivot_row]

            # Update objective row
            factor = self.objective_coeffs[pivot_col]
            self.objective_coeffs -= factor * self.coefficients[pivot_row]
            self.objective_value -= factor * self.constraints[pivot_row]

            # Update basic variables
            self.basic_vars[pivot_row] = pivot_col

            # Check for optimality
            if self.is_maximization == 1:
                optimal = np.all(self.objective_coeffs >= 0)
            else:
                optimal = np.all(self.objective_coeffs <= 0)

            self.record_tableau_step()

        # Prepare solution vector
        solution = np.zeros(self.num_variables + self.num_unrestricted)
        for i in range(self.num_constraints):
            if self.basic_vars[i] < self.num_variables:
                solution[self.basic_vars[i]] = self.constraints[i]
            elif self.basic_vars[i] >= self.num_variables + self.num_constraints:
                solution[self.basic_vars[i] - self.num_constraints] = self.constraints[i]

        return solution, self.objective_value, "Optimal solution found"

    def setup_variable_names(self):
        """Set up names for variables in the tableau for display purposes."""
        self.variable_names = [f'x{i}' for i in range(self.num_variables)]
        self.variable_names.insert(0, '')  # Empty cell for row labels

        # Add slack variable names
        for i in range(self.num_constraints):
            self.variable_names.append(f'S{i}')

        # Add unrestricted variable names
        for i in range(self.num_unrestricted):
            self.variable_names.append(f"x{self.unrestricted_indices[i]}'")

        # Add artificial variable names
        for i in range(self.num_artificial):
            self.variable_names.append(f'a{i}')

        # Add RHS column label
        self.variable_names.append('RHS')

    def record_tableau_step(self):
        """Record the current state of the tableau for display."""
        self.current_tableau = []

        # Set up variable names if not done yet
        if not self.variable_names:
            self.setup_variable_names()

        # Add header row with variable names
        self.current_tableau.append(self.variable_names)

        # Add objective function row
        z_row = ['Z']
        for coeff in self.objective_coeffs:
            z_row.append(coeff)
        z_row.append(self.objective_value)
        self.current_tableau.append(z_row)

        # Add constraint rows
        for i in range(len(self.coefficients)):
            row = self.coefficients[i].tolist()
            row.insert(0, self.variable_names[self.basic_vars[i] + 1])  # Add basic variable label
            row.append(self.constraints[i])  # Add RHS value
            self.current_tableau.append(row)

        # Format the tableau using tabulate and add to steps
        self.tableau_steps.append( tabulate(self.current_tableau, tablefmt="plain",  floatfmt=".3f")) 


class PreemptiveGoalProgramming:
    """
    A class to solve preemptive goal programming problems.
    """

    def __init__(self, goal_coeffs, goal_values, constraint_coeffs, constraint_values,
                unrestricted_vars, goal_directions):
        """
        Initialize the PreemptiveGoalProgramming solver.

        Args:
            goal_coeffs: Coefficient matrix for goals
            goal_values: Right-hand side values for goals
            constraint_coeffs: Coefficient matrix for constraints
            constraint_values: Right-hand side values for constraints
            unrestricted_vars: Binary vector indicating unrestricted variables
            goal_directions: Direction of each goal ('>=', '<=', or '==')
        """
        self.goal_coeffs = np.array(goal_coeffs, dtype=float)
        self.goal_values = np.array(goal_values, dtype=float)
        self.constraint_coeffs = np.array(constraint_coeffs, dtype=float)
        self.constraint_values = np.array(constraint_values, dtype=float)
        self.unrestricted_vars = np.array(unrestricted_vars, dtype=float)
        self.goal_directions = np.array(goal_directions, dtype=str)

        self.num_goals = len(goal_coeffs)
        self.num_constraints = len(constraint_coeffs)
        self.num_variables = len(constraint_coeffs[0])
        self.basic_vars = [i + self.num_variables + self.num_goals for i in
                           range(self.num_constraints + self.num_goals)]
        self.num_unrestricted = int(np.sum(self.unrestricted_vars == 1))
        self.tableau_steps = []
        self.unrestricted_indices = []

    def create_initial_tableau(self):
        """Create the initial tableau for preemptive goal programming."""
        # Initialize tableau with zeros
        total_rows = self.num_constraints + self.num_goals
        total_cols = self.num_variables + 2 * self.num_goals + self.num_constraints
        self.tableau = np.zeros((total_rows, total_cols), dtype=float)
        self.tableau_rhs = np.zeros(total_rows, dtype=float)

        # Fill in goal constraints
        for i in range(self.num_goals):
            self.tableau[i, :self.num_variables] = self.goal_coeffs[i]
            self.tableau[i, i + self.num_variables] = -1  # Negative deviation
            self.tableau[i, i + self.num_variables + self.num_goals] = 1  # Positive deviation
            self.tableau_rhs[i] = self.goal_values[i]

        # Fill in structural constraints
        for i in range(self.num_constraints):
            self.tableau[i + self.num_goals, :self.num_variables] = self.constraint_coeffs[i]
            self.tableau[i + self.num_goals, i + self.num_variables + 2 * self.num_goals] = 1  # Slack variable
            self.tableau_rhs[i + self.num_goals] = self.constraint_values[i]

    def setup_goal_objective_functions(self):
        """Set up objective functions for each goal priority level."""
        # Initialize objective function matrix
        total_cols = self.num_variables + 2 * self.num_goals + self.num_constraints + self.num_unrestricted
        self.goal_objectives = np.zeros((self.num_goals, total_cols))
        self.goal_objective_rhs = np.zeros(self.num_goals)

        # Set up objectives based on goal directions
        for i in range(self.num_goals):
            if self.goal_directions[i] == '>=':
                # For >= goals, minimize negative deviation
                self.goal_objectives[i][i + self.num_variables + self.num_goals] = -1
            elif self.goal_directions[i] == '<=':
                # For <= goals, minimize positive deviation
                self.goal_objectives[i][i + self.num_variables] = -1
            else:  # '=='
                # For == goals, minimize both deviations
                self.goal_objectives[i][i + self.num_variables] = -1
                self.goal_objectives[i][i + self.num_variables + self.num_goals] = -1

    def handle_unrestricted_variables(self):
        """Handle unrestricted variables."""
        if self.num_unrestricted > 0:
            for i in range(len(self.unrestricted_vars)):
                if self.unrestricted_vars[i] == 1:
                    # For each unrestricted variable, add its negative counterpart
                    negative_coeff = np.array(self.tableau[:, i]) * -1
                    self.tableau = np.hstack((self.tableau, negative_coeff.reshape(-1, 1)))
                    self.basic_vars.append(self.num_variables + self.num_constraints + 2 * self.num_goals + i)

        # Track indices of unrestricted variables
        self.unrestricted_indices = [j for j in range(len(self.unrestricted_vars)) if self.unrestricted_vars[j] == 1]

    def setup_variable_names(self):
        """Set up names for variables in the tableau for display purposes."""
        self.variable_names = [f'x{i}' for i in range(self.num_variables)]
        self.variable_names.insert(0, '')  # Empty cell for row labels

        # Add positive deviation variable names
        for i in range(self.num_goals):
            self.variable_names.append(f'S{i}+')

        # Add negative deviation variable names
        for i in range(self.num_goals):
            self.variable_names.append(f'S{i}-')

        # Add slack variable names
        for i in range(self.num_constraints):
            self.variable_names.append(f'S{i + self.num_goals}')

        # Add unrestricted variable names
        for i in range(self.num_unrestricted):
            self.variable_names.append(f"x{self.unrestricted_indices[i]}'")

        # Add RHS column label
        self.variable_names.append('RHS')

    def record_tableau_step(self):
        """Record the current state of the tableau for display."""
        current_tableau = []

        # Add header row with variable names
        current_tableau.append(self.variable_names)

        # Add objective function rows for each goal
        for j in range(self.num_goals):
            z_row = [f"Z{j}"]
            for i in range(len(self.goal_objectives[0])):
                z_row.append(self.goal_objectives[j, i])
            z_row.append(self.goal_objective_rhs[j])
            current_tableau.append(z_row)

        # Add constraint rows
        for i in range(len(self.tableau)):
            row = self.tableau[i].tolist()
            row.insert(0, self.variable_names[self.basic_vars[i] + 1])  # Add basic variable label
            row.append(self.tableau_rhs[i])  # Add RHS value
            current_tableau.append(row)

        # Format the tableau using tabulate and add to steps
        self.tableau_steps.append (tabulate(current_tableau, tablefmt="plain", floatfmt=".3f")) 

    def solve(self):
        """Solve the preemptive goal programming problem."""
        tolerance = 1e-9
        self.record_tableau_step()

        # Update objectives with tableau values
        for i in range(self.num_goals):
            self.goal_objectives[i] += self.tableau[i]
            self.goal_objective_rhs[i] += self.tableau_rhs[i]

        # Process each goal by priority
        for i in range(self.num_goals):
            # Find columns with positive coefficients in the current objective
            candidate_cols = []
            for j in range(len(self.goal_objectives[i])):
                if self.goal_objectives[i, j] > tolerance:
                    candidate_cols.append(j)
                else:
                    candidate_cols.append(-1)

            # Sort columns by coefficient value (descending)
            sorted_cols = sorted(candidate_cols, key=lambda x: self.goal_objectives[i, x], reverse=True)
            sorted_cols = [x for x in sorted_cols if x != -1]

            # Perform pivoting operations until objective is optimized
            while sorted_cols:
                pivot_col = sorted_cols[0]
                valid_pivot = True

                # Check if pivot maintains feasibility for higher priority goals
                for j in range(i):
                    if self.goal_objectives[j, pivot_col] < 0:
                        valid_pivot = False
                        break

                if not valid_pivot:
                    sorted_cols.pop(0)
                    continue

                # Find pivot row using minimum ratio test
                ratios = np.zeros(self.num_constraints + self.num_goals)
                for j in range(self.num_constraints + self.num_goals):
                    if self.tableau[j, pivot_col] > 0:
                        ratios[j] = self.tableau_rhs[j] / self.tableau[j, pivot_col]
                    else:
                        ratios[j] = np.inf

                pivot_row = np.argmin(ratios)
                pivot_element = self.tableau[pivot_row, pivot_col]

                # Perform pivot operation
                self.tableau[pivot_row] /= pivot_element
                self.tableau_rhs[pivot_row] /= pivot_element

                # Update objective rows
                for j in range(self.num_goals):
                    factor = self.goal_objectives[j, pivot_col]
                    self.goal_objectives[j] -= factor * self.tableau[pivot_row]
                    self.goal_objective_rhs[j] -= factor * self.tableau_rhs[pivot_row]

                    # Clean up small values
                    for k in range(len(self.goal_objectives[i])):
                        if abs(self.goal_objectives[j, k]) < tolerance:
                            self.goal_objectives[j, k] = 0

                # Update constraint rows
                for j in range(self.num_constraints + self.num_goals):
                    if j != pivot_row:
                        factor = self.tableau[j, pivot_col]
                        self.tableau[j] -= factor * self.tableau[pivot_row]
                        self.tableau_rhs[j] -= factor * self.tableau_rhs[pivot_row]

                        # Clean up small values
                        for k in range(len(self.tableau[j])):
                            if abs(self.tableau[j, k]) < tolerance:
                                self.tableau[j, k] = 0.0

                # Update basic variables
                self.basic_vars[pivot_row] = pivot_col

                # Check if current objective is optimized
                if np.all(self.goal_objectives[i] <= tolerance):
                    break
                else:
                    # Recalculate candidate columns
                    candidate_cols = []
                    for j in range(len(self.goal_objectives[i])):
                        if self.goal_objectives[i, j] > tolerance:
                            candidate_cols.append(j)
                        else:
                            candidate_cols.append(-1)
                    sorted_cols = sorted(candidate_cols, key=lambda x: self.goal_objectives[i, x], reverse=True)
                    sorted_cols = [x for x in sorted_cols if x != -1]

            # Record tableau after optimizing this goal
            self.record_tableau_step()

        # Prepare solution vector
        solution = np.zeros(self.num_variables)
        for i in range(self.num_constraints + self.num_goals):
            if self.basic_vars[i] < self.num_variables:
                solution[self.basic_vars[i]] = self.tableau_rhs[i]
            elif self.basic_vars[i] >= self.num_variables + self.num_constraints + 2 * self.num_goals:
                idx = self.basic_vars[i] - self.num_constraints - 2 * self.num_goals
                solution[idx] = self.tableau_rhs[i]

        return solution


def main():
    """Example problem demonstrating the use of PreemptiveGoalProgramming."""
    goal_coeffs = np.array([
        [200, 0],
        [100, 400],
        [0, 250]
    ])
    goal_values = [1000, 1200, 800]
    constraint_coeffs = [[1500, 3000]]
    constraint_values = [15000]
    goal_directions = ['>=', '>=', '>=']
    unrestricted_vars = [0, 0]
    # Create and solve the model
    solver = PreemptiveGoalProgramming(
        goal_coeffs, goal_values, constraint_coeffs, constraint_values,
        unrestricted_vars, goal_directions
    )

    # Set up and solve the model
    solver.create_initial_tableau()
    solver.setup_goal_objective_functions()
    solver.handle_unrestricted_variables()
    solver.setup_variable_names()

    # Solve and get the solution
    solution = solver.solve()


    print("\nTableau Steps:")

    for step in solver.tableau_steps:
        print(step)
    print("\nFinal RHS:")
    print(solver.tableau_rhs)
    print("\nOptimal Solution:")
    print(solution)


main()