import { useState } from "react";
import ReactMarkdown from "react-markdown";

import "./App.css";

export default function App() {
  const [url, setUrl] = useState("");
  const [summary, setSummary] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    // On repart de zéro à chaque nouvelle demande
    setSummary("");
    setError("");
    setLoading(true);

    try {
      const response = await fetch("/api/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (!response.ok) {
        // FastAPI renvoie le message d'erreur dans "detail"
        throw new Error(data.detail || "Une erreur est survenue.");
      }

      setSummary(data.summary);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <h1>Résumeur YouTube</h1>
      <p className="subtitle">
        Colle le lien d'une vidéo et obtiens un résumé en français.
      </p>

      <form onSubmit={handleSubmit} className="form">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://www.youtube.com/watch?v=..."
          required
          disabled={loading}
        />
        <button type="submit" disabled={loading || !url}>
          {loading ? "Résumé en cours…" : "Résumer"}
        </button>
      </form>

      {loading && (
        <p className="hint">
          Cela peut prendre un peu de temps pour les vidéos longues.
        </p>
      )}

      {error && <div className="card error">{error}</div>}

      {summary && (
        <section className="card">
          <h2>Résumé</h2>
          <div className="markdown">
            <ReactMarkdown>{summary}</ReactMarkdown>
          </div>
        </section>
      )}
    </main>
  );
}