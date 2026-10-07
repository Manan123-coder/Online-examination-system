import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { resultApi, errorText } from "../api.js";

export default function Result() {
  const { id } = useParams();
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    // REST call: React -> GET /results/{id} -> Result Service
    resultApi.get(`/results/${id}`).then((r) => setResult(r.data)).catch((e) => setError(errorText(e)));
  }, [id]);

  if (error) return <p className="error">{error}</p>;
  if (!result) return <p>Loading...</p>;
  return (
    <div className="card center">
      <h2>Exam Completed</h2>
      <p className="big">Score: {result.score} / {result.total_questions}</p>
      <p className="big">Percentage: {result.percentage}%</p>
      <p>Correct: {result.score}</p>
      <p>Wrong: {result.total_questions - result.score}</p>
      <button onClick={() => navigate("/dashboard")}>Back to Dashboard</button>
    </div>
  );
}
