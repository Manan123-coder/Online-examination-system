import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { studentApi, errorText } from "../api.js";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const login = async () => {
    try {
      // REST call: React -> POST /students/login -> Student Service
      const res = await studentApi.post("/students/login", { email, password });
      // JWT: store the token so later requests can send it
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("studentId", res.data.student_id);
      localStorage.setItem("name", res.data.name);
      navigate("/dashboard");
    } catch (err) {
      setError(errorText(err));
    }
  };

  return (
    <div className="card auth">
      <h2>Login</h2>
      <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
      {error && <p className="error">{error}</p>}
      <button onClick={login}>Login</button>
      <p>Don't have an account? <Link to="/register">Register</Link></p>
    </div>
  );
}
