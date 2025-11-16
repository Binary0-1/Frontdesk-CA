import { useState, useEffect } from "react";
import Request from "./Request";

const initialRequests = [
  {
    id: 1,
    user: "John Doe",
    query: "I need help with my account.",
    requestedAt: new Date(Date.now() - 1000 * 60 * 5),
    status: "pending"
  },
  {
    id: 2,
    user: "Jane Smith",
    query: "I have a billing question.",
    requestedAt: new Date(Date.now() - 1000 * 60 * 30),
    status: "pending"
  },
];

const Requests = () => {
  const [requests, setRequests] = useState(initialRequests);
  const [answers, setAnswers] = useState<{ [key: number]: string }>({});

  const handleAnswerChange = (id: number, value: string) => {
    setAnswers((prev) => ({ ...prev, [id]: value }));
  };

  const handleSubmit = async (id: number) => {
    const answer = answers[id];
    if (!answer) {
      alert("Please enter an answer.");
      return;
    }

    console.log(`Submitting answer for request ${id}: ${answer}`);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    console.log("Answer submitted successfully!");

    setRequests((prev) => prev.filter((req) => req.id !== id));
  };

  return (
    <div className="flex flex-col p-[20px] w-[80%] ">
      <h1 className="text-[32px] font-medium mb-4">Pending Requests</h1>
      <div className="w-full flex items-start gap-x-[20px]">
        <div className="gap-[20px] flex flex-wrap items-start w-full ">
          {requests.map((request) => (
            <Request
              request={request}
              answers={answers}
              handleAnswerChange={handleAnswerChange}
              handleSubmit={handleSubmit}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Requests;
