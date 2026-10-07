import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { questionApi, resultApi } from "../api.js";

export default function Dashboard() {
  const [exams, setExams] = useState([]);
  const [results, setResults] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    // REST call: React -> GET /exams -> Question Service
    questionApi.get("/exams").then((r) => setExams(r.data));
    // REST call: React -> GET /results -> Result Service (needs JWT)
    resultApi.get("/results").then((r) => setResults(r.data)).catch(() => {
      localStorage.clear(); navigate("/login");   // token expired
    });
  }, [navigate]);

  const title = (id) => exams.find((e) => e.id === id)?.title || `Exam ${id}`;

  return (
    <>
      <h2>Welcome, {localStorage.getItem("name")}</h2>
      <h3>Available Exams</h3>
      {exams.map((e) => (
        <div className="card row" key={e.id}>
          <div><b>{e.title}</b><br />{e.question_count} Questions · {e.duration} Minutes</div>
          <button onClick={() => navigate(`/exam/${e.id}`)}>Start Exam</button>
        </div>
      ))}
      <h3>Previous Results</h3>
      {results.length === 0 && <p>No results yet.</p>}
      {results.slice(0, 5).map((r) => (
        <div className="card row" key={r.id}>
          <span>{title(r.exam_id)}</span>
          <span>{r.score} / {r.total_questions} ({r.percentage}%)</span>
          <Link to={`/result/${r.id}`}>View</Link>
        </div>
      ))}
    </>
  );
}
