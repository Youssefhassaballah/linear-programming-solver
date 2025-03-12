import React from "react";

const data = {
  optimal_value: 7.571428571428571,
  solution: [6.428571428571429, 0.5714285714285714, 0.0],
  steps: [
    "Basic\tx1\tx2\tx3\ts1\tA1\tA2\tRHS\nZ\t0.00\t0.00\t0.00\t0.00\t1.00\t1.00\t0.00\nA1\t1.00\t1.00\t1.00\t0.00\t1.00\t0.00\t7.00\nA2\t2.00\t-5.00\t1.00\t-1.00\t0.00\t1.00\t10.00\n",
    "Basic\tx1\tx2\tx3\ts1\tA1\tA2\tRHS\nZ\t-3.00\t4.00\t-2.00\t1.00\t0.00\t0.00\t-17.00\nA1\t1.00\t1.00\t1.00\t0.00\t1.00\t0.00\t7.00\nA2\t2.00\t-5.00\t1.00\t-1.00\t0.00\t1.00\t10.00\n",
    "Basic\tx1\tx2\tx3\ts1\tA1\tA2\tRHS\nZ\t0.00\t-3.50\t-0.50\t-0.50\t0.00\t1.50\t-2.00\nA1\t0.00\t3.50\t0.50\t0.50\t1.00\t-0.50\t2.00\nx1\t1.00\t-2.50\t0.50\t-0.50\t0.00\t0.50\t5.00\n",
    "Basic\tx1\tx2\tx3\ts1\tA1\tA2\tRHS\nZ\t0.00\t0.00\t0.00\t0.00\t1.00\t1.00\t0.00\nx2\t0.00\t1.00\t0.14\t0.14\t0.29\t-0.14\t0.57\nx1\t1.00\t0.00\t0.86\t-0.14\t0.71\t0.14\t6.43\n",
    "Basic\tx1\tx2\tx3\ts1\tRHS\nZ\t-1.00\t-2.00\t-1.00\t0.00\t0.00\nx2\t0.00\t1.00\t0.14\t0.14\t0.57\nx1\t1.00\t0.00\t0.86\t-0.14\t6.43\n",
    "Basic\tx1\tx2\tx3\ts1\tRHS\nZ\t-1.00\t0.00\t-0.71\t0.29\t1.14\nx2\t0.00\t1.00\t0.14\t0.14\t0.57\nx1\t1.00\t0.00\t0.86\t-0.14\t6.43\n",
    "Basic\tx1\tx2\tx3\ts1\tRHS\nZ\t0.00\t0.00\t0.14\t0.14\t7.57\nx2\t0.00\t1.00\t0.14\t0.14\t0.57\nx1\t1.00\t0.00\t0.86\t-0.14\t6.43\n",
  ],
};

const StepsTable = () => {
  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold text-center mb-6 text-gray-800">
        Linear Programming Steps
      </h1>
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
                <thead className="bg-blue-500 text-white">
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

export default StepsTable;
