import { useState } from "react";
import axios from "axios";
import InputForm from "./components/InputForm";
import StatsCard from "./components/StatsCard";
import EmotionPieChart from "./components/EmotionPieChart";
import EmotionBarChart from "./components/EmotionBarChart";
import PostsList from "./components/PostsList";
import ThemeToggle from "./components/ThemeToggle";

function App() {
  const [results, setResults] = useState({ reddit: [], mastodon: [], all_posts: [] });
  const [loading, setLoading] = useState(false);

  const analyzeTopic = async (topic) => {
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/analyze", { topic });
      setResults(res.data.results);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const hasResults = results.reddit.length + results.mastodon.length > 0;

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition">
      <header className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
        <h1 className="text-3xl font-bold text-center mb-8">
          🌐 Multi-Source Social Media Mood Analyzer
        </h1>
        <ThemeToggle />
      </header>

      <InputForm onAnalyze={analyzeTopic} loading={loading} />

      {hasResults && (
        <>
          <StatsCard all_posts={results.all_posts} />
          <EmotionPieChart all_posts={results.all_posts} />
          <EmotionBarChart all_posts={results.all_posts} />
          <PostsList results={results} />
        </>
      )}
    </div>
  );
}

export default App;
