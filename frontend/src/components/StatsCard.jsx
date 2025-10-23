import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SocialIcon } from "react-social-icons";

export default function StatsCard({ all_posts: allposts }) {
  const total = allposts.length;

  // Most common emotion
  const emotionCounts = allposts.reduce((acc, r) => {
    acc[r.top_emotion] = (acc[r.top_emotion] || 0) + 1;
    return acc;
  }, {});
  const topEmotion = Object.entries(emotionCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || "-";

  // Average reactions (likes/upvotes)
  const redditPosts = allposts.filter((post) => post.source === "reddit");
  const mastodonPosts = allposts.filter((post) => post.source === "mastodon");
  const youtubePosts = allposts.filter((post) => post.source === "youtube");

  const avgLikesReddit = redditPosts.length
    ? (redditPosts.reduce((sum, r) => sum + r.likes, 0) / redditPosts.length).toFixed(1)
    : 0;
  const avgLikesMastodon = mastodonPosts.length
    ? (mastodonPosts.reduce((sum, r) => sum + r.likes, 0) / mastodonPosts.length).toFixed(1)
    : 0;
  const avgLikesYouTube = youtubePosts.length
    ? (youtubePosts.reduce((sum, r) => sum + r.likes, 0) / youtubePosts.length).toFixed(1)
    : 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
      {/* Total Posts */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Total Posts Analyzed</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-4xl font-bold text-center text-indigo-600">{total}</p>
        </CardContent>
      </Card>

      {/* Most Common Emotion */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Most Common Emotion</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-semibold text-center text-indigo-600">{topEmotion}</p>
        </CardContent>
      </Card>

      {/* Average Reactions */}
      <Card className="shadow-sm col-span-2 md:col-span-2">
        <CardHeader>
          <CardTitle>Average Reactions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col space-y-2 md:flex-row md:space-x-6 md:space-y-0 justify-center items-center text-center">
            {/* Reddit */}
            <div className="flex items-center gap-2">
              <SocialIcon network="reddit" fgColor="white" bgColor="#FF4500" style={{ width: 28, height: 28 }} />
              <span className="font-semibold">Reddit: {avgLikesReddit}</span>
            </div>

            {/* Mastodon */}
            <div className="flex items-center gap-2">
              <SocialIcon network="mastodon" fgColor="white" bgColor="#6364FF" style={{ width: 28, height: 28 }} />
              <span className="font-semibold">Mastodon: {avgLikesMastodon}</span>
            </div>

            {/* YouTube */}
            <div className="flex items-center gap-2">
              <SocialIcon network="youtube" fgColor="white" bgColor="#FF0000" style={{ width: 28, height: 28 }} />
              <span className="font-semibold">YouTube: {avgLikesYouTube}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}