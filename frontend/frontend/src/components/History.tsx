import React from "react";

const history = [
  {
    id: 1,
    user: "Alice",
    query: "What are your hours?",
    answer: "We are open 9am-5pm, Monday to Friday.",
  },
  {
    id: 2,
    user: "Bob",
    query: "Do you have any openings?",
    answer: "We are currently fully booked.",
  },
];

const History = () => {
  return (
    <div className="p-[20px] w-[80%]">
      <h1 className="text-[32px] font-medium mb-4">Request History</h1>

      <div className="flex flex-col gap-[20px]">
        {history.map((item) => (
          <div
            key={item.id}
            className="relative p-6 bg-white rounded-2xl border border-gray-200 shadow-sm"
          >
            <div className="flex justify-between items-start mb-4">
              <div className="flex flex-col gap-1">
                <p className="text-sm text-gray-500 font-medium">User</p>
                <p className="text-lg font-semibold">{item.user}</p>

                <p className="text-sm text-gray-500 font-medium mt-2">Query</p>
                <p className="text-gray-800">{item.query}</p>

                <p className="text-sm text-gray-500 font-medium mt-2">Answer</p>
                <p className="text-gray-700">{item.answer}</p>
              </div>

              <span className="px-3 py-1 text-sm font-medium rounded-full border bg-gray-100 text-gray-700 border-gray-300">
                COMPLETED
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default History;
