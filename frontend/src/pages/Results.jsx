import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { questionApi, resultApi } from "../api.js";

export default function Results() {
  const [results, setResults] = useState([]);
  const [exams, setExams] = useState([]);

  useEffect(() => {
    resultApi.get("/results").then((r) => setResults(r.data));   // REST -> Result Service
    questionApi.get("/exams").then((r) => setExams(r.data));     // REST -> Question Service
  }, []);

  const title = (id) => exams.find((e) => e.id === id)?.title || `Exam ${id}`;
  return (
    <div className="card">
      <h2>My Results</h2>
      <table>
        <thead><tr><th>Exam</th><th>Score</th><th>Percentage</th><th></th></tr></thead>
        <tbody>
          {results.map((r) => (
            <tr key={r.id}>
              <td>{title(r.exam_id)}</td>
              <td>{r.score} / {r.total_questions}</td>
              <td>{r.percentage}%</td>
              <td><Link to={`/result/${r.id}`}>View</Link></td>
            </tr>
          ))}
        </tbody>
      </table>
      {results.length === 0 && <p>No results yet.</p>}
    </div>
  );
}
