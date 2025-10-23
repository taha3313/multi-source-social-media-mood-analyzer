import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function EmotionBarChart({ all_posts: results }) {
  const emotionStats = {};

  results.forEach((r) => {
    if (!emotionStats[r.top_emotion]) emotionStats[r.top_emotion] = [];
    emotionStats[r.top_emotion].push(r.top_confidence);
  });

  const data = Object.entries(emotionStats).map(([emotion, values]) => {
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
    return { emotion, avg_confidence: Math.round(avg * 100) / 100 };
  });

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle>Average Confidence per Emotion</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <XAxis dataKey="emotion" />
            <YAxis domain={[0, 1]} />
            <Tooltip />
            <Legend />
            <Bar dataKey="avg_confidence" fill="#4F46E5" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
