import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const COLORS = ["#6366F1", "#F59E0B", "#EF4444", "#10B981", "#8B5CF6", "#3B82F6", "#A78BFA"];

export default function EmotionPieChart({ all_posts: results }) {
  // Aggregate data and include "Other" slice
  let data = Object.entries(
    results.reduce((acc, r) => {
      acc[r.top_emotion] = (acc[r.top_emotion] || 0) + (r.likes + 1); // weighted by likes
      return acc;
    }, {})
  ).map(([name, value]) => ({ name, value }));

  // Compute total and threshold for "Other"
  const total = data.reduce((sum, d) => sum + d.value, 0);
  const threshold = total * 0.05; // 5% threshold
  let mainSlices = [];
  let otherValue = 0;
  data.forEach((d) => {
    if (d.value < threshold) otherValue += d.value;
    else mainSlices.push(d);
  });
  if (otherValue > 0) mainSlices.push({ name: "Other", value: otherValue });
  data = mainSlices;

  // Custom label
  const renderLabel = ({ cx, cy, midAngle, outerRadius, percent, index }) => {
    const RADIAN = Math.PI / 180;
    const radius = outerRadius + 20;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);
    const slice = data[index];
    return (
      <text
        x={x}
        y={y}
        fill="#333"
        textAnchor={x > cx ? "start" : "end"}
        dominantBaseline="central"
        fontSize={12}
      >
        {`${slice.name}: ${slice.value} (${(percent * 100).toFixed(0)}%)`}
      </text>
    );
  };

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle>Emotion Distribution (Weighted by Reactions)</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              outerRadius={100}
              label={renderLabel}
              labelLine
              isAnimationActive
            >
              {data.map((_, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => value.toFixed(0)} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
