import React from "react";

const Solution = ({ data }) => {
  return (
    <div className="bg-white shadow-lg rounded-lg p-6 mb-6 transition-all hover:shadow-xl">
      <h2 className="text-2xl font-bold text-indigo-700 mb-4">
        Optimal Solution
      </h2>
      <div>
        <table className="w-full border border-gray-300 text-sm">
          <thead className="bg-indigo-500 text-white">
            <tr>
              {data.solution.map((_, index) => (
                <th key={index} className="px-3 py-2 border">
                  x{index + 1}
                </th>
              ))}
              <th className="px-3 py-2 border">z</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border border-gray-300 odd:bg-gray-50 hover:bg-gray-200">
              {data.solution.map((value, index) => (
                <td key={index} className="px-3 py-2 border text-center">
                  {value.toFixed(2)}
                </td>
              ))}
              <td className="px-3 py-2 border text-center">
                {data.optimal_value.toFixed(2)}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Solution;
