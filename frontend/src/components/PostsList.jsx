import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SocialIcon } from "react-social-icons";

export default function PostsList({ results }) {
  const allPosts = [...results.reddit, ...results.mastodon, ...results.youtube];

  // Map source to icon config
  const sourceIcons = {
    reddit: { network: "reddit", bgColor: "#FF4500", fgColor: "white" },
    mastodon: { network: "mastodon", bgColor: "#6364FF", fgColor: "white" },
    youtube: { network: "youtube", bgColor: "#FF0000", fgColor: "white" },
  };

  return (
    <Card className="mt-6 shadow-lg border border-gray-200 dark:border-gray-700">
      <CardHeader>
        <CardTitle>Analyzed Posts</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="max-h-[500px] overflow-y-auto space-y-4">
          {allPosts.map((post, i) => (
            <div
              key={i}
              className="p-4 border border-gray-100 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-800 hover:shadow-lg transition flex flex-col gap-2"
            >
              {/* Post Text */}
              <p className="text-sm text-gray-800 dark:text-gray-200 line-clamp-4">{post.text}</p>

              {/* View Link */}
              {post.url && (
                <a
                  href={post.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:underline"
                >
                  View Post
                </a>
              )}

              {/* Post Details */}
              <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500 dark:text-gray-400 mt-1">
                <span>
                  Emotion: <span className="font-semibold text-indigo-600">{post.top_emotion}</span>
                </span>
                <span>Confidence: {post.top_confidence}</span>
                <span>Likes/Upvotes: {post.likes}</span>
                <span className="flex items-center gap-1">
                  <SocialIcon
                    {...sourceIcons[post.source]}
                    style={{ width: 18, height: 18 }}
                  />
                  <span className="capitalize">{post.source}</span>
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
