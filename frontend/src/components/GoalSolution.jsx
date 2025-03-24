import React from "react";

const GoalSolution = ({ data }) => {
  console.log("data", data);

  if (!data) {
    console.error("Data is undefined");
    return <div>Error: Data is undefined</div>;
  }

  if (!data.optimal_solution) {
    console.error("Optimal solution is undefined");
    return <div>Error: Optimal solution is undefined</div>;
  }

  return (
    <div className="bg-white shadow-lg rounded-lg p-6 my-6 transition-all hover:shadow-xl">
      <h2 className="text-2xl font-bold text-indigo-700 mb-4">
        Optimal Solution
      </h2>
      <div>
        <table className="w-full border border-gray-300 text-sm">
          <thead className="bg-indigo-500 text-white">
            <tr>
              {data.optimal_solution &&
                data.optimal_solution.map((_, index) => (
                  <th key={index} className="px-3 py-2 border">
                    x{index + 1}
                  </th>
                ))}
            </tr>
          </thead>
          <tbody>
            <tr className="border border-gray-300 odd:bg-gray-50 hover:bg-gray-200">
              {data.optimal_solution &&
                data.optimal_solution.map((value, index) => (
                  <td key={index} className="px-3 py-2 border text-center">
                    {value.toFixed(2)}
                  </td>
                ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default GoalSolution;
