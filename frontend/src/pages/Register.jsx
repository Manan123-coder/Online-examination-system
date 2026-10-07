import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { studentApi, errorText } from "../api.js";

export default function Register() {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const change = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const register = async () => {
    try {
      // REST call: React -> POST /students/register -> Student Service
      await studentApi.post("/students/register", form);
      navigate("/login");
    } catch (err) {
      setError(errorText(err));
    }
  };

  return (
    <div className="card auth">
      <h2>Register</h2>
      <input name="name" placeholder="Name" onChange={change} />
      <input name="email" placeholder="Email" onChange={change} />
      <input name="password" type="password" placeholder="Password (min 6 characters)" onChange={change} />
      {error && <p className="error">{error}</p>}
      <button onClick={register}>Register</button>
      <p>Already have an account? <Link to="/login">Login</Link></p>
    </div>
  );
}
