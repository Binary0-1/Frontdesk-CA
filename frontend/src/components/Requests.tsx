import { useState, useEffect } from "react";
import Request from "./Request";

const Requests = () => {
  const [requests, setRequests] = useState([]);
  const [answers, setAnswers] = useState<{ [key: number]: string }>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPending();
  }, []);

  const fetchPending = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/requests/pending");
      const data = await res.json();
      setRequests(data);
    } catch (err) {
      console.error("Failed to fetch pending requests", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (id: number, value: string) => {
    setAnswers((prev) => ({ ...prev, [id]: value }));
  };

  const handleSubmit = async (id: number) => {
    const answer = answers[id];
    if (!answer) {
      alert("Please enter an answer.");
      return;
    }

    try {
      const res = await fetch(`http://127.0.0.1:8000/requests/${id}/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer }),
      });

      if (!res.ok) throw new Error("Failed to submit answer");

      setRequests((prev) => prev.filter((req) => req.id !== id));
    } catch (err) {
      console.error(err);
      alert("Failed to submit answer");
    }
  };

  return (
    <div className="flex flex-col p-[20px] w-[80%]">
      <h1 className="text-[32px] font-medium mb-4">Pending Requests</h1>

      {loading && (
        <div className="flex flex-wrap gap-[20px]">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="w-[300px] h-[180px] bg-gray-200 animate-pulse rounded-lg"
            />
          ))}
        </div>
      )}

      {!loading && (
        <div className="w-full flex items-start gap-x-[20px]">
          <div className="gap-[20px] flex flex-wrap items-start w-full">
            {requests.map((request) => (
              <Request
                key={request.id}
                request={request}
                answers={answers}
                handleAnswerChange={handleAnswerChange}
                handleSubmit={handleSubmit}
              />
            ))}

            {requests.length === 0 && (
              <p className="text-gray-500 text-lg">No pending requests 🎉</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Requests;
