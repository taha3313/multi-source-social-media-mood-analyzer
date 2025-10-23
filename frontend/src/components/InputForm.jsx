import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";

export default function InputForm({ onAnalyze, loading }) {
  const [topic, setTopic] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (topic.trim() === "") return;
    onAnalyze(topic);
  };

  return (
    <Card className="p-4 mb-6 shadow-md">
      <CardContent>
        <form
          onSubmit={handleSubmit}
          className="flex flex-col md:flex-row gap-4 justify-center items-center"
        >
          <Input
            placeholder="Enter a topic (e.g., AI, politics, football)"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="w-full md:w-1/2"
          />
          <Button type="submit" disabled={loading}>
            {loading ? "Analyzing..." : "Analyze"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
