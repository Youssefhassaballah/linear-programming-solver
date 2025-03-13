import React, { useState, useEffect } from "react";
import solveLinearProgramming from "./services/getSolution"; 
import StepsTable from "./solutions";

const ObjectiveFunction = ({
  objective,
  setObjective,
  setOptimizationType,
}) => (
  <div className="bg-white shadow-lg rounded-lg p-6 mb-6 transition-all hover:shadow-xl">
    <h2 className="text-2xl font-bold text-indigo-700 mb-4">
      Objective Function
    </h2>
    <div className="flex flex-col md:flex-row gap-4">
      <input
        type="text"
        value={objective}
        onChange={(e) => setObjective(e.target.value)}
        placeholder="Enter objective function (e.g., 3x1 + 2x2)"
        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
      />
      <select
        onChange={(e) => setOptimizationType(e.target.value)}
        className="px-4 py-2 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
      >
        <option value="max">Maximize</option>
        <option value="min">Minimize</option>
      </select>
    </div>
  </div>
);

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

  const updateVariableType = (variable, value) => {
    const newVariableTypes = { ...variableTypes, [variable]: value };
    setVariableTypes(newVariableTypes);
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
      <h2 className="text-2xl font-bold text-indigo-700 mb-4 mt-6">
        Variable Types
      </h2>
      <div className="space-y-3">
        {variables.map((variable) => (
          <div key={variable} className="flex items-center gap-2">
            <span className="font-medium">{variable}</span>
            <select
              value={variableTypes[variable] || "non-negative"}
              onChange={(e) => updateVariableType(variable, e.target.value)}
              className="px-4 py-2 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
            >
              <option value="non-negative">Non-negative</option>
              <option value="unrestricted">Unrestricted</option>
            </select>
          </div>
        ))}
      </div>
    </div>
  );
};

const MethodSelection = ({ setMethod }) => (
  <div className="bg-white shadow-lg rounded-lg p-6 mb-6 transition-all hover:shadow-xl">
    <h2 className="text-2xl font-bold text-indigo-700 mb-4">
      Method Selection
    </h2>
    <select
      onChange={(e) => setMethod(e.target.value)}
      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
    >
      <option value="simplex">Simplex Method</option>
      <option value="big-m">Big M Method</option>
      <option value="two-phase">Two Phase Method</option>
      <option value="goal-programming">Goal Programming Method</option>
    </select>
  </div>
);

const Result = ({ result }) => (
  <div className="bg-white shadow-lg rounded-lg p-6 mb-6 transition-all hover:shadow-xl">
    <h2 className="text-2xl font-bold text-indigo-700 mb-4">Result</h2>
    <pre className="bg-gray-100 p-4 rounded-md overflow-auto">
      {JSON.stringify(result, null, 2)}
    </pre>
  </div>
);

const extractCoefficients = (expression, variables) => {
  const regex = /([-+]?\d*\.?\d*)\s*([a-zA-Z]\d*)/g;
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
  const regex = /([a-zA-Z]\d*)/g;
  const variables = new Set();
  let match;
  while ((match = regex.exec(expression)) !== null) {
    variables.add(match[1]);
  }
  return Array.from(variables);
};

const App = () => {
  const [objective, setObjective] = useState("");
  const [optimizationType, setOptimizationType] = useState("max");
  const [constraints, setConstraints] = useState([""]);
  const [variableTypes, setVariableTypes] = useState({});
  const [method, setMethod] = useState("big-m");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [variables, setVariables] = useState([]);

  useEffect(() => {
    setVariables(extractVariables(objective));
  }, [objective]);



  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);
  
      const objectiveCoefficients = extractCoefficients(objective, variables);
      const parsedConstraints = constraints.map((constraint) => {
        const coefficients = extractCoefficients(
          constraint.split(/(<=|>=|=)/)[0],
          variables
        );
        const inequality = extractInequality(constraint);
        const rhs = extractRightHandSide(constraint);
        return { coefficients, inequality, rhs };
      });
  
      const rhs = parsedConstraints.map((c) => c.rhs);
      const constraintTypes = parsedConstraints.map((c) => c.inequality);
      const constraintCoefficients = parsedConstraints.map((c) => c.coefficients);
      const varRestrictions = variables.map((variable) =>
        variableTypes[variable] === "unrestricted" ? "unrestricted" : ">=0"
      );
  
      if (
        objectiveCoefficients.includes(null) ||
        rhs.includes(null) ||
        constraintTypes.includes(null) ||
        constraintCoefficients.some((coeffs) => coeffs.includes(null)) ||
        varRestrictions.includes(null)
      ) {
        throw new Error("One or more parameters are null.");
      }
  
      const DataToSend = {
        objective: objectiveCoefficients,
        optimization: optimizationType,
        constraints: constraintCoefficients,
        rhs: rhs,
        constraint_types: constraintTypes,
        var_restrictions: varRestrictions,
        method: method,
      };
      console.log(DataToSend)
      const apiResult = await solveLinearProgramming(DataToSend);
      console.log("get")
      setResult(apiResult);
    } catch (error) {

      console.error("Error during submission:", error);
      setError("An error occurred while solving the problem.");
    } finally {
      setLoading(false);
    }
  };
  

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center text-indigo-800 mb-8">
          Linear Programming Calculator
        </h1>

        <ObjectiveFunction
          objective={objective}
          setObjective={setObjective}
          setOptimizationType={setOptimizationType}
        />

        <Constraints
          constraints={constraints}
          setConstraints={setConstraints}
          variableTypes={variableTypes}
          setVariableTypes={setVariableTypes}
          variables={variables}
        />

        <MethodSelection setMethod={setMethod} />

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

        {/* {result && <Result result={result} />} */}
        {result && <StepsTable data={result} />}
      </div>
    </div>
  );
};

export default App;
