import { useState } from "react";

interface RequestItem {
  id: number;
  user: string;
  query: string;
  requestedAt: Date;
  status: "pending" | "fulfilled" | "rejected";
}

interface RequestProps {
  request: RequestItem;
  answers: { [key: number]: string };
  handleAnswerChange: (id: number, value: string) => void;
  handleSubmit: (id: number) => void;
}

const statusStyles = {
  pending: "bg-yellow-100 text-yellow-700 border-yellow-300",
  fulfilled: "bg-green-100 text-green-700 border-green-300",
  rejected: "bg-red-100 text-red-700 border-red-300",
};

const Request: React.FC<RequestProps> = ({
  request,
  answers,
  handleAnswerChange,
  handleSubmit,
}) => {
  const [showTextArea, setShowTextArea] = useState(false);
  const toggleTextArea = () => setShowTextArea((prev) => !prev);

  return (
    <div className="relative p-6 bg-white rounded-2xl border border-gray-200 shadow-sm">
      <div className="flex justify-between items-start mb-4">
        <div className="flex flex-col gap-1">
          <p className="text-sm text-gray-500 font-medium">User</p>
          <p className="text-lg font-semibold">{request.user}</p>

          <p className="text-sm text-gray-500 font-medium mt-2">Query</p>
          <p className="text-gray-800">{request.query}</p>

          <p className="text-sm text-gray-500 font-medium mt-2">Requested At</p>
          <p className="text-gray-700">
            {new Intl.DateTimeFormat("en-US", {
              year: "numeric",
              month: "long",
              day: "2-digit",
            }).format(request.requestedAt)}
          </p>
        </div>

        {request.status && (
          <span
            className={`px-3 py-1 text-sm font-medium rounded-full border ${
              statusStyles[request.status]
            }`}
          >
            {request.status.toUpperCase()}
          </span>
        )}
      </div>

      {/* Small + button in bottom-right */}
      {!showTextArea && request.status === "pending" && (
        <button
          onClick={toggleTextArea}
          title="Add Answer"
          className="absolute bottom-4 right-4 group cursor-pointer outline-none hover:rotate-90 transition-transform duration-300"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="28"
            height="28"
            viewBox="0 0 24 24"
            className="stroke-gray-400 fill-none group-hover:fill-gray-800 transition-all"
          >
            <path
              d="M12 22A10 10 0 1 0 12 2a10 10 0 0 0 0 20Z"
              strokeWidth="1.5"
            ></path>
            <path d="M8 12h8" strokeWidth="1.5"></path>
            <path d="M12 16V8" strokeWidth="1.5"></path>
          </svg>
        </button>
      )}

      {/* Fixed height container for textarea so card height doesn't change */}
      <div className="mt-4 h-40">
        {showTextArea && request.status === "pending" && (
          <div className="h-full flex flex-col">
            <label className="text-sm text-gray-600 font-medium">
              Your Answer
            </label>

            <textarea
              className="w-full p-3 border rounded-xl mt-1 flex-1 resize-none focus:ring-2 focus:ring-blue-400"
              placeholder="Type your response..."
              value={answers[request.id] || ""}
              onChange={(e) => handleAnswerChange(request.id, e.target.value)}
            />

            <button
              className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
              onClick={() => handleSubmit(request.id)}
              disabled={!answers[request.id]}
            >
              Submit Answer
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Request;
