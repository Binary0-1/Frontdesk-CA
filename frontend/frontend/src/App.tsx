import { Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import RequestsPage from "./pages/RequestsPage";
import HistoryPage from "./pages/HistoryPage";
import "./App.css";

function App() {
  return (
    <main className="p-5 h-screen bg-[#DBDBDB] ">
      <div className="rounded-[20px]  bg-[#F1F1F1] flex h-full">
        <Sidebar />
        <Routes>
          <Route path="/" element={<RequestsPage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </div>
    </main>
  );
}

export default App;
