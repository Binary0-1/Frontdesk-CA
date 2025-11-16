import { useEffect, useState } from "react";

const History = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/requests/resolved");
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.error("Failed to fetch history", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-[20px] w-[80%]">
      <h1 className="text-[32px] font-medium mb-4">Request History</h1>

      {loading && (
        <div className="flex flex-col gap-[20px]">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="w-full h-[150px] bg-gray-200 animate-pulse rounded-xl"
            />
          ))}
        </div>
      )}

      {!loading && (
        <div className="flex flex-col gap-[20px]">
          {history.map((item: any) => (
            <div
              key={item.id}
              className="relative p-6 bg-white rounded-2xl border border-gray-200 shadow-sm"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex flex-col gap-1">
                  <p className="text-sm text-gray-500 font-medium">User</p>
                  <p className="text-lg font-semibold">{item.customer_id}</p>

                  <p className="text-sm text-gray-500 font-medium mt-2">
                    Query
                  </p>
                  <p className="text-gray-800">{item.question}</p>

                  <p className="text-sm text-gray-500 font-medium mt-2">
                    Answer
                  </p>
                  <p className="text-gray-700">{item.supervisor_answer}</p>

                  <p className="text-sm text-gray-400 mt-2">
                    Resolved at: {new Date(item.answered_at).toLocaleString()}
                  </p>
                </div>

                <span className="px-3 py-1 text-sm font-medium rounded-full border bg-green-100 text-green-700 border-green-300">
                  COMPLETED
                </span>
              </div>
            </div>
          ))}

          {history.length === 0 && (
            <p className="text-gray-500 text-lg">No history yet.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default History;
