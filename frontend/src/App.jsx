import { Link, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Exam from "./pages/Exam.jsx";
import Result from "./pages/Result.jsx";
import Results from "./pages/Results.jsx";

// Protected route: if there is no JWT token saved, send the user to /login.
function Protected({ children }) {
  const navigate = useNavigate();
  if (!localStorage.getItem("token")) return <Navigate to="/login" replace />;
  const logout = () => { localStorage.clear(); navigate("/login"); };
  return (
    <>
      <nav className="nav">
        <b>Online Exam Platform</b>
        <span>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/results">My Results</Link>
          <a href="#logout" onClick={logout}>Logout</a>
        </span>
      </nav>
      <div className="container">{children}</div>
    </>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/dashboard" element={<Protected><Dashboard /></Protected>} />
      <Route path="/exam/:id" element={<Protected><Exam /></Protected>} />
      <Route path="/result/:id" element={<Protected><Result /></Protected>} />
      <Route path="/results" element={<Protected><Results /></Protected>} />
    </Routes>
  );
}
