import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { questionApi, resultApi, errorText } from "../api.js";

export default function Exam() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [exam, setExam] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});      // { questionId: "A" }
  const [current, setCurrent] = useState(0);
  const [secondsLeft, setSecondsLeft] = useState(null);

  const answersRef = useRef(answers);              // always holds the latest answers
  answersRef.current = answers;
  const submitted = useRef(false);                 // prevents double submit

  useEffect(() => {
    // REST calls: React -> Question Service (exam details + questions WITHOUT correct answers)
    Promise.all([questionApi.get(`/exams/${id}`), questionApi.get(`/questions/${id}`)])
      .then(([e, q]) => { setExam(e.data); setQuestions(q.data); setSecondsLeft(e.data.duration * 60); })
      .catch((err) => alert(errorText(err)));
  }, [id]);

  const submit = useCallback(async () => {
    if (submitted.current) return;
    submitted.current = true;
    try {
      // REST call: React -> POST /results/submit -> Result Service
      const res = await resultApi.post("/results/submit", { exam_id: Number(id), answers: answersRef.current });
      navigate(`/result/${res.data.id}`);
    } catch (err) {
      submitted.current = false;
      alert("Submit failed: " + errorText(err));
    }
  }, [id, navigate]);

  // Countdown timer: runs once per second; at zero the exam is submitted automatically.
  useEffect(() => {
    if (secondsLeft === null) return;
    if (secondsLeft <= 0) { submit(); return; }
    const t = setTimeout(() => setSecondsLeft((s) => s - 1), 1000);
    return () => clearTimeout(t);
  }, [secondsLeft, submit]);

  if (!exam || questions.length === 0) return <p>Loading exam... (or this exam has no questions)</p>;

  const q = questions[current];
  const mm = String(Math.floor(secondsLeft / 60)).padStart(2, "0");
  const ss = String(secondsLeft % 60).padStart(2, "0");
  const options = [["A", q.option_a], ["B", q.option_b], ["C", q.option_c], ["D", q.option_d]];

  return (
    <div className="card">
      <div className="row"><h2>{exam.title}</h2><b className="timer">Time Remaining: {mm}:{ss}</b></div>
      <p>Question {current + 1} of {questions.length}</p>
      <h3>{q.question}</h3>
      {options.map(([letter, text]) => (
        <label key={letter} className={"option" + (answers[q.id] === letter ? " selected" : "")}>
          <input type="radio" name={`q${q.id}`} checked={answers[q.id] === letter}
                 onChange={() => setAnswers({ ...answers, [q.id]: letter })} />
          {text}
        </label>
      ))}
      <div className="row">
        <button disabled={current === 0} onClick={() => setCurrent(current - 1)}>Previous</button>
        <button disabled={current === questions.length - 1} onClick={() => setCurrent(current + 1)}>Next</button>
      </div>
      <div className="nums">
        {questions.map((item, i) => (
          <button key={item.id} onClick={() => setCurrent(i)}
                  className={(i === current ? "cur " : "") + (answers[item.id] ? "done" : "")}>{i + 1}</button>
        ))}
      </div>
      <button className="submit" onClick={submit}>Submit Exam</button>
    </div>
  );
}
