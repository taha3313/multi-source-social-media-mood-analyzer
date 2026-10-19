from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from mastodon import Mastodon
from bs4 import BeautifulSoup
import praw
import asyncio
import os
import math
import time
import threading
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import httpx

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

app = FastAPI(title="Multi-Source Social Media Mood Analyzer")

# -----------------------------
# CORS
# -----------------------------
origins = [origin.strip() for origin in os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Models
# -----------------------------
class TopicRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=200, pattern=r"\S")
    limit: int = Field(default=20, ge=3, le=200)

# -----------------------------
# Device Setup
# -----------------------------
use_gpu = int(os.getenv("USE_GPU", "0"))
device_str = "cuda" if use_gpu else "cpu"

# -----------------------------
# AI Models
# -----------------------------
embedding_model = None
emotion_classifier = None
util = None
model_lock = threading.Lock()
analysis_lock = asyncio.Lock()


def load_models():
    """Load once, on demand, so probes do not download models or require credentials."""
    global embedding_model, emotion_classifier, util
    with model_lock:
        if embedding_model is not None and emotion_classifier is not None:
            return
        from sentence_transformers import SentenceTransformer, util as similarity_util
        from transformers import pipeline
        import torch

        torch.set_num_threads(int(os.getenv("INFERENCE_THREADS", "2")))
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device=device_str)
        emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None, truncation=True, device=0 if use_gpu else -1,
        )
        util = similarity_util


# -----------------------------
# Reddit Setup
# -----------------------------
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT", "mood-analyzer/1.0"),
    timeout=20,
    check_for_async=False,
) if os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET") else None

# -----------------------------
# Mastodon Setup
# -----------------------------
mastodon = Mastodon(
    access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
    api_base_url=os.getenv("MASTODON_BASE_URL", "https://mastodon.social"),
    request_timeout=20,
) if os.getenv("MASTODON_ACCESS_TOKEN") else None

# -----------------------------
# YouTube Setup (HTTPX)
# -----------------------------
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_COMMENT_URL = "https://www.googleapis.com/youtube/v3/commentThreads"

# -----------------------------
# Utilities
# -----------------------------
def clean_html(raw_html: str) -> str:
    return BeautifulSoup(raw_html, "html.parser").get_text()

def expand_topic_semantically(topic: str, max_terms: int = 6):
    variants = [
        topic,
        f"{topic} news",
        f"{topic} trends",
        f"{topic} discussion",
        f"{topic} impact",
        f"{topic} analysis",
        f"{topic} opinions",
    ]
    return variants[:max_terms]

# -----------------------------
# Fetching functions
# -----------------------------
def fetch_reddit_posts(topic: str, limit: int = 100):
    posts = []
    if reddit is None:
        return posts
    try:
        for submission in reddit.subreddit("all").search(
            topic,
            limit=limit,
            sort="relevance",
            time_filter="day",
        ):
            text = (submission.title or "") + " " + (submission.selftext or "")
            if text.strip():
                posts.append({
                    "text": text,
                    "likes": submission.score,
                    "source": "reddit",
                    "url": f"https://reddit.com{submission.permalink}"
                })
    except Exception as e:
        print("Reddit fetch error:", type(e).__name__)
    return posts

def fetch_mastodon_posts(topic: str, limit: int = 50):
    posts = []
    if mastodon is None:
        return posts
    try:
        results = mastodon.timeline_hashtag(topic, limit=limit)
        for status in results:
            created_at = status["created_at"]
            if datetime.now(timezone.utc) - created_at > timedelta(days=1):
                continue
            posts.append({
                "text": clean_html(status["content"]),
                "likes": status.get("favourites_count", 0),
                "source": "mastodon",
                "url": status.get("url", "")
            })
        if not posts:
            print(f"No Mastodon posts found for #{topic} in the last 24h.")
    except Exception as e:
        print("Mastodon fetch error:", type(e).__name__)
    return posts

def fetch_youtube_comments_for_topic(topic: str, max_videos: int = 3, max_comments: int = 50, min_similarity: float = 0.3):
    posts = []
    if not YOUTUBE_API_KEY:
        return posts
    try:
        with httpx.Client(timeout=30.0) as client:
            # Search videos
            params = {
                "part": "snippet",
                "q": topic,
                "type": "video",
                "order": "relevance",
                "publishedAfter": (datetime.utcnow() - timedelta(days=1)).isoformat("T") + "Z",
                "maxResults": max_videos,
                "key": YOUTUBE_API_KEY,
            }
            r = client.get(YOUTUBE_SEARCH_URL, params=params)
            r.raise_for_status()
            items = r.json().get("items", [])
            video_ids = [item["id"]["videoId"] for item in items]

            topic_vec = embedding_model.encode(topic, convert_to_tensor=True, show_progress_bar=False)

            # Fetch comments for each video
            for vid in video_ids:
                params_c = {
                    "part": "snippet",
                    "videoId": vid,
                    "maxResults": min(max_comments, 100),
                    "textFormat": "plainText",
                    "key": YOUTUBE_API_KEY,
                }
                rc = client.get(YOUTUBE_COMMENT_URL, params=params_c)
                rc.raise_for_status()
                for item in rc.json().get("items", []):
                    snippet = item["snippet"]["topLevelComment"]["snippet"]
                    text = snippet["textDisplay"]
                    sim = util.cos_sim(
                        embedding_model.encode(text, convert_to_tensor=True),
                        topic_vec
                    ).item()
                    if sim >= min_similarity:
                        posts.append({
                            "text": text,
                            "likes": snippet.get("likeCount", 0),
                            "source": "youtube",
                            "url": f"https://www.youtube.com/watch?v={vid}&lc={item['id']}",
                            "similarity": round(sim, 3)
                        })
    except Exception as e:
        print("YouTube fetch error:", type(e).__name__)
    return posts

# -----------------------------
# Timeout wrapper
# -----------------------------
async def fetch_with_timeout(func, *args, timeout=30):
    try:
        return await asyncio.wait_for(asyncio.to_thread(func, *args), timeout)
    except asyncio.TimeoutError:
        print(f"⚠️ Timeout fetching {func.__name__}")
        return []

# -----------------------------
# Async fetch wrapper
# -----------------------------
async def fetch_all_sources(topics):
    tasks = []
    for term in topics:
        tasks += [
            fetch_with_timeout(fetch_reddit_posts, term),
            fetch_with_timeout(fetch_mastodon_posts, term, timeout=30),
            fetch_with_timeout(fetch_youtube_comments_for_topic, term, 3, 50, 0.3, timeout=60),
        ]
    results = await asyncio.gather(*tasks)
    return [p for group in results for p in group]

# -----------------------------
# Deduplicate and sample
# -----------------------------
def deduplicate_and_sample(all_posts, max_posts=200):
    unique = {}
    for p in all_posts:
        t = p["text"].strip()
        if len(t) > 30 and t not in unique:
            unique[t] = p
    posts = list(unique.values())
    posts_sorted = sorted(posts, key=lambda x: x["likes"] + len(x["text"]) / 100, reverse=True)
    return posts_sorted[:max_posts]

# -----------------------------
# Batched emotion analysis
# -----------------------------
async def analyze_posts_batch(posts, batch_size=32):
    texts = [p["text"][:512] for p in posts]
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_scores = await asyncio.to_thread(emotion_classifier, batch)
        for p, scores in zip(posts[i:i+batch_size], batch_scores):
            scores.sort(key=lambda x: x["score"], reverse=True)
            p["top_emotion"] = scores[0]["label"]
            p["top_confidence"] = round(scores[0]["score"], 3)
            p["all_scores"] = {s["label"]: round(s["score"], 3) for s in scores}
            results.append(p)
    return results

# -----------------------------
# Main API
# -----------------------------
@app.post("/analyze")
async def analyze_topic(req: TopicRequest):
    if not any((reddit, mastodon, YOUTUBE_API_KEY)):
        raise HTTPException(status_code=503, detail="No social sources configured. Add API credentials on the server.")
    if analysis_lock.locked():
        raise HTTPException(status_code=503, detail="Another analysis is running. Try again shortly.")
    async with analysis_lock:
        await asyncio.to_thread(load_models)
        return await run_analysis(req)


async def run_analysis(req: TopicRequest):
    start_time = time.time()

    search_terms = expand_topic_semantically(req.topic)
    all_posts = await fetch_all_sources(search_terms)
    posts = deduplicate_and_sample(all_posts, max_posts=200)

    if not posts:
        raise HTTPException(status_code=404, detail="No posts found for topic.")

    analyzed = await analyze_posts_batch(posts, batch_size=32)

    topic_vec = await asyncio.to_thread(embedding_model.encode, req.topic, convert_to_tensor=True, show_progress_bar=False)
    post_vecs = await asyncio.to_thread(embedding_model.encode, [p["text"] for p in analyzed], convert_to_tensor=True, show_progress_bar=False)
    sims = util.cos_sim(post_vecs, topic_vec).reshape(-1).cpu().numpy()

    for post, sim in zip(analyzed, sims):
        post["similarity"] = round(float(post.get("similarity", sim)), 3)
        post["score_weighted"] = round(
            post["top_confidence"] * (1 + math.log(max(0, post["likes"]) + 2)) * (0.5 + float(post["similarity"])),
            3,
        )

    top_posts_sorted = sorted(analyzed, key=lambda x: x["score_weighted"], reverse=True)
    top_reddit = [p for p in top_posts_sorted if p["source"] == "reddit"][:req.limit // 3]
    top_mastodon = [p for p in top_posts_sorted if p["source"] == "mastodon"][:req.limit // 3]
    top_youtube = [p for p in top_posts_sorted if p["source"] == "youtube"][:req.limit // 3]

    emotion_weights = {}
    for p in analyzed:
        e = p["top_emotion"]
        weight = p["top_confidence"] * math.log(max(0, p["likes"]) + 2)
        emotion_weights[e] = emotion_weights.get(e, 0) + weight

    total_weight = sum(emotion_weights.values()) or 1
    emotion_summary = {k: round(v / total_weight, 3) for k, v in emotion_weights.items()}

    total_likes = sum(p["likes"] for p in analyzed)
    avg_likes = round(total_likes / len(analyzed), 2) if analyzed else 0

    elapsed = round(time.time() - start_time, 2)
    print(f"✅ Done in {elapsed}s | Analyzed {len(analyzed)} posts")

    return {
        "topic": req.topic,
        "related_terms": search_terms,
        "total_posts_analyzed": len(analyzed),
        "emotion_summary": emotion_summary,
        "reaction_stats": {
            "total_likes": total_likes,
            "avg_likes": avg_likes,
        },
        "results": {
            "reddit": top_reddit,
            "mastodon": top_mastodon,
            "youtube": top_youtube,
            "all_posts": analyzed,
        },
        "processing_time": elapsed,
    }

# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
async def health():
    return {
        "status": "OK",
        "models_loaded": embedding_model is not None and emotion_classifier is not None,
        "configured_sources": [name for name, enabled in (
            ("reddit", reddit is not None), ("mastodon", mastodon is not None),
            ("youtube", bool(YOUTUBE_API_KEY)),
        ) if enabled],
    }


# -----------------------------
# Trending Topics Endpoint
# -----------------------------
@app.get("/trending")
def get_trending_topics(limit: int = Query(default=10, ge=1, le=50)):
    trending_topics = set()

    # --- Reddit Trending (hot posts titles) ---
    try:
        for submission in (reddit.subreddit("all").hot(limit=limit * 3) if reddit else []):
            title = submission.title.strip()
            if len(title.split()) <= 6:  # simple heuristic: short topics
                trending_topics.add(title)
    except Exception as e:
        print("Reddit trending error:", type(e).__name__)

    # --- YouTube Trending (optional if quota allows) ---
    try:
        if not YOUTUBE_API_KEY:
            return {"trending": sorted(trending_topics)[:limit]}
        with httpx.Client(timeout=10.0) as client:
            params = {
                "part": "snippet",
                "chart": "mostPopular",
                "regionCode": "US",
                "maxResults": limit,
                "key": YOUTUBE_API_KEY,
            }
            r = client.get("https://www.googleapis.com/youtube/v3/videos", params=params)
            r.raise_for_status()
            for item in r.json().get("items", []):
                trending_topics.add(item["snippet"]["title"])
    except Exception as e:
        print("YouTube trending error:", type(e).__name__)

    # --- Return combined & cleaned list ---
    topics_cleaned = list(trending_topics)
    topics_cleaned = [t[:80] for t in topics_cleaned]  # truncate long ones
    return {"trending": topics_cleaned[:limit]}
