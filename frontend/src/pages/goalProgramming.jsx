import React, { useState, useEffect } from "react";
import solveLinearProgramming from "../services/getSolution";
import GoalSolution from "../components/GoalSolution";
import GoalSteps from "../components/GoalSteps";

const Constraints = ({
  constraints,
  setConstraints,
  variableTypes,
  setVariableTypes,
  variables,
}) => {
  const addConstraint = () => setConstraints([...constraints, ""]);
  const updateConstraint = (index, value) => {
    const newConstraints = [...constraints];
    newConstraints[index] = value;
    setConstraints(newConstraints);
  };

  const removeConstraint = (index) => {
    const newConstraints = constraints.filter((_, i) => i !== index);
    setConstraints(newConstraints.length > 0 ? newConstraints : [""]);
  };

  return (
    <div className="bg-white shadow-lg rounded-lg p-6 mb-6 transition-all hover:shadow-xl">
      <h2 className="text-2xl font-bold text-indigo-700 mb-4">Constraints</h2>
      <div className="space-y-3">
        {constraints.map((constraint, index) => (
          <div key={index} className="flex items-center gap-2">
            <input
              type="text"
              value={constraint}
              onChange={(e) => updateConstraint(index, e.target.value)}
              placeholder={`Constraint ${index + 1} (e.g., 2x1 + 3x2 <= 10)`}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
            />
            {constraints.length > 1 && (
              <button
                onClick={() => removeConstraint(index)}
                className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50 transition-all"
              >
                ✖
              </button>
            )}
          </div>
        ))}
        <button
          onClick={addConstraint}
          className="mt-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50 transition-all"
        >
          Add Constraint
        </button>
      </div>
    </div>
  );
};

const Goals = ({ goals, setGoals, variables }) => {
  const addGoal = () => setGoals([...goals, ""]);
  const updateGoal = (index, value) => {
    const newGoals = [...goals];
    newGoals[index] = value;
    setGoals(newGoals);
  };

  const removeGoal = (index) => {
    const newGoals = goals.filter((_, i) => i !== index);
    setGoals(newGoals.length > 0 ? newGoals : [""]);
  };

  return (
    <div className="bg-white shadow-lg rounded-lg p-6 mb-6 transition-all hover:shadow-xl">
      <h2 className="text-2xl font-bold text-indigo-700 mb-4">Goals</h2>
      <h3 className="text-md font-bold text-indigo-800 mb-4">
        Enter goals due to their priority
      </h3>
      <div className="space-y-3">
        {goals.map((goal, index) => (
          <div key={index} className="flex items-center gap-2">
            <input
              type="text"
              value={goal}
              onChange={(e) => updateGoal(index, e.target.value)}
              placeholder={`Goal ${index + 1} (e.g., 2x1 + 3x2 <= 10)`}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
            />
            {goals.length > 1 && (
              <button
                onClick={() => removeGoal(index)}
                className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50 transition-all"
              >
                ✖
              </button>
            )}
          </div>
        ))}
        <button
          onClick={addGoal}
          className="mt-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50 transition-all"
        >
          Add Goal
        </button>
      </div>
    </div>
  );
};

const extractCoefficients = (expression, variables) => {
  const regex = /([-+]?\d*\.?\d*)\s*(x\d+)/g;
  let match;
  const coefficients = Array(variables.length).fill(0);

  while ((match = regex.exec(expression)) !== null) {
    let coefficient = match[1];
    const variable = match[2];
    const index = variables.indexOf(variable);

    if (coefficient === "" || coefficient === "+") {
      coefficient = 1;
    } else if (coefficient === "-") {
      coefficient = -1;
    } else {
      coefficient = parseFloat(coefficient);
    }

    if (index !== -1) {
      coefficients[index] = coefficient;
    }
  }
  return coefficients;
};

const extractInequality = (constraint) => {
  const regex = /(<=|>=|=)/;
  const match = constraint.match(regex);
  return match ? match[0] : null;
};

const extractRightHandSide = (constraint) => {
  const parts = constraint.split(/(<=|>=|=)/);
  return parts.length > 1 ? parseFloat(parts[2]) : null;
};

const extractVariables = (expression) => {
  const regex = /(x\d+)/g;
  const variables = new Set();
  let match;
  while ((match = regex.exec(expression)) !== null) {
    variables.add(match[1]);
  }
  return Array.from(variables);
};

const GoalProgrammingPage = () => {
  const [constraints, setConstraints] = useState([""]);
  const [variableTypes, setVariableTypes] = useState({});
  const [result, setResult] = useState({
    optimal_solution: [5.0, 2.5],
    steps: [
      "     x0      x1      S0+   S1+   S2+   S0-   S1-   S2-   S3   RHS\nZ0   0.0     0.0     0.0   0.0   0.0   -1.0  0.0   0.0   0.0  0.0\nZ1   0.0     0.0     0.0   0.0   0.0   0.0   -1.0  0.0   0.0  0.0\nZ2   0.0     0.0     0.0   0.0   0.0   0.0   0.0   -1.0  0.0  0.0\nS0-  200.0   0.0     -1.0  0.0   0.0   1.0   0.0   0.0   0.0  1000.0\nS1-  100.0   400.0   0.0   -1.0  0.0   0.0   1.0   0.0   0.0  1200.0\nS2-  0.0     250.0   0.0   0.0   -1.0  0.0   0.0   1.0   0.0  800.0\nS3   1500.0  3000.0  0.0   0.0   0.0   0.0   0.0   0.0   1.0  15000.0",
      "     x0   x1      S0+     S1+   S2+   S0-    S1-  S2-  S3   RHS\nZ0   0.0  0.0     0.0     0.0   0.0   -1.0   0.0  0.0  0.0  0.0\nZ1   0.0  400.0   0.5     -1.0  0.0   -0.5   0.0  0.0  0.0  700.0\nZ2   0.0  250.0   0.0     0.0   -1.0  0.0    0.0  0.0  0.0  800.0\nx0   1.0  0.0     -0.005  0.0   0.0   0.005  0.0  0.0  0.0  5.0\nS1-  0.0  400.0   0.5     -1.0  0.0   -0.5   1.0  0.0  0.0  700.0\nS2-  0.0  250.0   0.0     0.0   -1.0  0.0    0.0  1.0  0.0  800.0\nS3   0.0  3000.0  7.5     0.0   0.0   -7.5   0.0  0.0  1.0  7500.0",
      "     x0   x1   S0+      S1+      S2+   S0-       S1-     S2-  S3   RHS\nZ0   0.0  0.0  0.0      0.0      0.0   -1.0      0.0     0.0  0.0  0.0\nZ1   0.0  0.0  0.0      0.0      0.0   0.0       -1.0    0.0  0.0  0.0\nZ2   0.0  0.0  -0.3125  0.625    -1.0  0.3125    -0.625  0.0  0.0  362.5\nx0   1.0  0.0  -0.005   0.0      0.0   0.005     0.0     0.0  0.0  5.0\nx1   0.0  1.0  0.00125  -0.0025  0.0   -0.00125  0.0025  0.0  0.0  1.75\nS2-  0.0  0.0  -0.3125  0.625    -1.0  0.3125    -0.625  1.0  0.0  362.5\nS3   0.0  0.0  3.75     7.5      0.0   -3.75     -7.5    0.0  1.0  2250.0",
      "     x0   x1   S0+     S1+  S2+   S0-      S1-   S2-  S3            RHS\nZ0   0.0  0.0  0.0     0.0  0.0   -1.0     0.0   0.0  0.0                    0.0\nZ1   0.0  0.0  0.0     0.0  0.0   0.0      -1.0  0.0  0.0                    0.0\nZ2   0.0  0.0  -0.625  0.0  -1.0  0.625    0.0   0.0  -0.08333333333333333   175.0\nx0   1.0  0.0  -0.005  0.0  0.0   0.005    0.0   0.0  0.0                    5.0\nx1   0.0  1.0  0.0025  0.0  0.0   -0.0025  0.0   0.0  0.0003333333333333333  2.5\nS2-  0.0  0.0  -0.625  0.0  -1.0  0.625    0.0   1.0  -0.08333333333333333   175.0\nS1+  0.0  0.0  0.5     1.0  0.0   -0.5     -1.0  0.0  0.13333333333333333    300.0",
    ],
  });
  // "'optimal_solution': [5.0, 2.5],'steps': ['     x0      x1      S0+   S1+   S2+   S0-   S1-   S2-   S3   RHS\nZ0   0.0     0.0     0.0   0.0   0.0   -1.0  0.0   0.0   0.0  0.0\nZ1   0.0     0.0     0.0   0.0   0.0   0.0   -1.0  0.0   0.0  0.0\nZ2   0.0     0.0     0.0   0.0   0.0   0.0   0.0   -1.0  0.0  0.0\nS0-  200.0   0.0     -1.0  0.0   0.0   1.0   0.0   0.0   0.0  1000.0\nS1-  100.0   400.0   0.0   -1.0  0.0   0.0   1.0   0.0   0.0  1200.0\nS2-  0.0     250.0   0.0   0.0   -1.0  0.0   0.0   1.0   0.0  800.0\nS3   1500.0  3000.0  0.0   0.0   0.0   0.0   0.0   0.0   1.0  15000.0', '     x0   x1      S0+     S1+   S2+   S0-    S1-  S2-  S3   RHS\nZ0   0.0  0.0     0.0     0.0   0.0   -1.0   0.0  0.0  0.0  0.0\nZ1   0.0  400.0   0.5     -1.0  0.0   -0.5   0.0  0.0  0.0  700.0\nZ2   0.0  250.0   0.0     0.0   -1.0  0.0    0.0  0.0  0.0  800.0\nx0   1.0  0.0     -0.005  0.0   0.0   0.005  0.0  0.0  0.0  5.0\nS1-  0.0  400.0   0.5     -1.0  0.0   -0.5   1.0  0.0  0.0  700.0\nS2-  0.0  250.0   0.0     0.0   -1.0  0.0    0.0  1.0  0.0  800.0\nS3   0.0  3000.0  7.5     0.0   0.0   -7.5   0.0  0.0  1.0  7500.0', '     x0   x1   S0+      S1+      S2+   S0-       S1-     S2-  S3   RHS\nZ0   0.0  0.0  0.0      0.0      0.0   -1.0      0.0     0.0  0.0  0.0\nZ1   0.0  0.0  0.0      0.0      0.0   0.0       -1.0    0.0  0.0  0.0\nZ2   0.0  0.0  -0.3125  0.625    -1.0  0.3125    -0.625  0.0  0.0  362.5\nx0   1.0  0.0  -0.005   0.0      0.0   0.005     0.0     0.0  0.0  5.0\nx1   0.0  1.0  0.00125  -0.0025  0.0   -0.00125  0.0025  0.0  0.0  1.75\nS2-  0.0  0.0  -0.3125  0.625    -1.0  0.3125    -0.625  1.0  0.0  362.5\nS3   0.0  0.0  3.75     7.5      0.0   -3.75     -7.5    0.0  1.0  2250.0', '     x0   x1   S0+     S1+  S2+   S0-      S1-   S2-  S3            RHS\nZ0   0.0  0.0  0.0     0.0  0.0   -1.0     0.0   0.0  0.0                    0.0\nZ1   0.0  0.0  0.0     0.0  0.0   0.0      -1.0  0.0  0.0                    0.0\nZ2   0.0  0.0  -0.625  0.0  -1.0  0.625    0.0   0.0  -0.08333333333333333   175.0\nx0   1.0  0.0  -0.005  0.0  0.0   0.005    0.0   0.0  0.0                    5.0\nx1   0.0  1.0  0.0025  0.0  0.0   -0.0025  0.0   0.0  0.0003333333333333333  2.5\nS2-  0.0  0.0  -0.625  0.0  -1.0  0.625    0.0   1.0  -0.08333333333333333   175.0\nS1+  0.0  0.0  0.5     1.0  0.0   -0.5     -1.0  0.0  0.13333333333333333    300.0']"
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [variables, setVariables] = useState([]);
  const [goals, setGoals] = useState([""]); // Initialize with one goal

  useEffect(() => {
    const allConstraints = [...constraints, ...goals];
    setVariables(extractVariables(allConstraints.join(" ")));
  }, [constraints, goals]);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);

      const parsedConstraints = constraints.map((constraint) => {
        const coefficients = extractCoefficients(
          constraint.split(/(<=|>=|=)/)[0],
          variables
        );
        const inequality = extractInequality(constraint);
        const rhs = extractRightHandSide(constraint);
        return { coefficients, inequality, rhs };
      });

      const parsedGoals = goals.map((goal) => {
        const coefficients = extractCoefficients(
          goal.split(/(<=|>=|=)/)[0],
          variables
        );
        const inequality = extractInequality(goal);
        const rhs = extractRightHandSide(goal);
        return { coefficients, inequality, rhs };
      });

      const rhs = parsedConstraints.map((c) => c.rhs);
      const constraintTypes = parsedConstraints.map((c) => c.inequality);
      const constraintCoefficients = parsedConstraints.map(
        (c) => c.coefficients
      );
      const varRestrictions = variables.map((variable) =>
        variableTypes[variable] === "unrestricted" ? "unrestricted" : ">=0"
      );

      const goalCoefficients = parsedGoals.map((g) => g.coefficients);
      const goalValues = parsedGoals.map((g) => g.rhs);
      const goalDirections = parsedGoals.map((g) => g.inequality);

      if (
        rhs.includes(null) ||
        constraintTypes.includes(null) ||
        constraintCoefficients.some((coeffs) => coeffs.includes(null)) ||
        varRestrictions.includes(null) ||
        goalCoefficients.some((coeffs) => coeffs.includes(null)) ||
        goalValues.includes(null) ||
        goalDirections.includes(null)
      ) {
        throw new Error("One or more parameters are null.");
      }

      const DataToSend = {
        method: "goal",
        constraints_coeffs: constraintCoefficients,
        constraints_values: rhs,
        goals_coeffs: goalCoefficients,
        goals_values: goalValues,
        goals_directions: goalDirections,
      };
      console.log(DataToSend);
      const apiResult = await solveLinearProgramming(DataToSend);
      console.log("get");
      setResult(apiResult);
    } catch (error) {
      console.error("Error during submission:", error);
      setError("An error occurred while solving the problem.");
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center text-indigo-800 mb-4">
          Goal Programming Calculator
        </h1>

        <Constraints
          constraints={constraints}
          setConstraints={setConstraints}
          variableTypes={variableTypes}
          setVariableTypes={setVariableTypes}
          variables={variables}
        />
        <Goals goals={goals} setGoals={setGoals} variables={variables} />
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6">
            <strong className="font-bold">Error!</strong>
            <span className="block sm:inline"> {error}</span>
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className={`w-full py-3 rounded-md transition-all ${
            loading
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white"
          } focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50`}
        >
          {loading ? "Processing..." : "Solve"}
        </button>

        {result && <GoalSolution data={result} />}
        {result && <GoalSteps data={result} />}
      </div>
    </div>
  );
};

export default GoalProgrammingPage;
