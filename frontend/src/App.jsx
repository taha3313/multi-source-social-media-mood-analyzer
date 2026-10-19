import { useState } from "react";
import { api } from "./lib/api";
import InputForm from "./components/InputForm";
import StatsCard from "./components/StatsCard";
import EmotionPieChart from "./components/EmotionPieChart";
import EmotionBarChart from "./components/EmotionBarChart";
import PostsList from "./components/PostsList";
import ThemeToggle from "./components/ThemeToggle";

function App() {
  const [results, setResults] = useState({ reddit: [], mastodon: [], youtube: [], all_posts: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const analyzeTopic = async (topic) => {
    setLoading(true);
    setError("");
    try {
      const res = await api.post("/analyze", { topic });
      setResults(res.data.results);
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed. Please try again shortly.");
    }
    setLoading(false);
  };


  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition">
      <header className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
        <h1 className="text-3xl font-bold text-center mb-8">
          🌐 Multi-Source Social Media Mood Analyzer
        </h1>
        <ThemeToggle />
      </header>

      <InputForm onAnalyze={analyzeTopic} loading={loading} />

      {error && <p role="alert" className="p-4 text-red-600">{error}</p>}

      <StatsCard all_posts={results.all_posts} loading={loading} />
      <EmotionPieChart all_posts={results.all_posts} loading={loading} />
      <EmotionBarChart all_posts={results.all_posts} loading={loading} />
      <PostsList results={results} loading={loading} />
    </div>
  );
}

export default App;
