import { Link, useLocation } from "react-router-dom";

const Sidebar = () => {
  const location = useLocation();

  return (
    <div className="w-64 h-full bg-[#F1F1F1] rounded-[20px] ">
      <img
        src="src/assets/aifrontdesk_logo.jpeg"
        alt=""
        className="w-[100px] h-[100px] rounded-[20px] ml-[20px] mt-[20px]"
      />
      <nav className="ml-2.5 mt-5 space-y-1.5">
        <Link
          to="/"
          className={`block py-2.5 px-4 text-gray-700 rounded-[10px] ${
            location.pathname === "/"
              ? "font-semibold bg-white shadow-sm"
              : "hover:font-semibold hover:bg-white hover:shadow-sm"
          }`}
        >
          Requests
        </Link>
        <Link
          to="/history"
          className={`block py-2.5 px-4 text-gray-700 rounded-[10px] ${
            location.pathname === "/history"
              ? "font-semibold bg-white shadow-sm"
              : "hover:font-semibold hover:bg-white hover:shadow-sm"
          }`}
        >
          History
        </Link>
      </nav>
    </div>
  );
};

export default Sidebar;
