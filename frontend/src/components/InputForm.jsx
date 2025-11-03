import { useState, useEffect } from "react";
import { Autocomplete, TextField } from "@mui/material";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { SpinLoader  } from "react-loadly";

export default function InputForm({ onAnalyze, loading }) {
  const [topic, setTopic] = useState("");
  const [trending, setTrending] = useState([]);

  // Fetch trending topics once
  useEffect(() => {
    const fetchTrending = async () => {
      try {
        const res = await axios.get("http://localhost:8000/trending");
        setTrending(res.data.trending || []);
      } catch (err) {
        console.error("Error fetching trending topics:", err);
      }
    };
    fetchTrending();
  }, []);

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
          <div className="w-full md:w-1/2">
            <Autocomplete
              freeSolo
              options={trending}
              inputValue={topic}
              onInputChange={(_, newValue) => setTopic(newValue)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Enter a topic (e.g., AI, politics, football)"
                  variant="outlined"
                  fullWidth
                  className="bg-white dark:bg-gray-900 rounded-lg"
                  InputLabelProps={{
                    className: "dark:text-gray-300",
                  }}
                  InputProps={{
                    ...params.InputProps,
                    className:
                      "dark:text-white border-gray-300 dark:border-gray-700 focus:ring-2 focus:ring-blue-500 rounded-lg",
                  }}
                />
              )}
            />
          </div>

          <Button type="submit" disabled={loading}>
            {loading ? <SpinLoader  /> : "Analyze"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
