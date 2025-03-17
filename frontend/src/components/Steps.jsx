import React from "react";

const Steps = ({ data }) => {
  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h2 className="text-2xl font-bold text-indigo-700 mb-4">Steps</h2>
      <div className="space-y-8 max-w-4xl mx-auto">
        {data.steps.map((step, index) => {
          const rows = step.split("\n").filter((row) => row.trim() !== "");
          const header = rows[0].split("\t");
          const bodyRows = rows.slice(1).map((row) => row.split("\t"));

          return (
            <div
              key={index}
              className="bg-white shadow-md rounded-lg p-4 overflow-x-auto"
            >
              <h3 className="text-lg font-semibold mb-2 text-gray-700">
                Step {index + 1}
              </h3>
              <table className="w-full border border-gray-300 text-sm">
                <thead className="bg-indigo-500 text-white">
                  <tr>
                    {header.map((cell, i) => (
                      <th key={i} className="px-3 py-2 border">
                        {cell}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {bodyRows.map((row, i) => (
                    <tr
                      key={i}
                      className="border border-gray-300 odd:bg-gray-50 hover:bg-gray-200"
                    >
                      {row.map((cell, j) => (
                        <td key={j} className="px-3 py-2 border text-center">
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Steps;
