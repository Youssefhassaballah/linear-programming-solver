from flask import Flask, request, jsonify
from flask_cors import CORS 
from linear_programing_solver import LinearProgrammingSolver
import numpy as np


app = Flask(__name__)
CORS(app)




@app.route('/solve', methods=['GET','POST'])
def solve():
    data = request.json
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
