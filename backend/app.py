from flask import Flask, request, jsonify
from flask_cors import CORS 
from linear_programing_solver import LinearProgrammingSolver
from goal_programing import PreemptiveGoalProgramming

import numpy as np

app = Flask(__name__)
CORS(app)


@app.route('/solve', methods=['GET','POST'])
def solve():
    data = request.json
    if data['method']=='goal':
            goal_coeffs = np.array(data['goals_coeffs'])
            goal_values = data['goals_values']
            constraint_coeffs = data['constraints_coeffs']
            constraint_values = data['constraints_values']
            goal_directions = data['goals_directions']
            unrestricted_vars = []
            for val in data['goals_coeffs'][0]:
                unrestricted_vars.append(0)
            solver = PreemptiveGoalProgramming(
                goal_coeffs, goal_values, constraint_coeffs, constraint_values,
                unrestricted_vars, goal_directions
            )
            solver.create_initial_tableau()
            solver.setup_goal_objective_functions()
            solver.handle_unrestricted_variables()
            solver.setup_variable_names()
            solution = solver.solve()
            k = {"optimal_solution": solution.tolist(), 
                "steps":solver.tableau_steps
            }
            return jsonify(k)
    else:
        print(request.json)
        objective = data['objective'] 
        constraints = data['constraints']
        rhs = data['rhs']
        constraint_types = data['constraint_types']
        var_restrictions = data['var_restrictions']
        method = data['method']
        solver = LinearProgrammingSolver(objective, constraints, rhs, constraint_types, var_restrictions, method=method)
        solution = solver.solve()
        return jsonify(solution)



if __name__ == '__main__':
    app.run(debug=True)
