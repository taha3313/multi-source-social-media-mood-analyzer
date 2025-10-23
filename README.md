# Multi-Source Social Media Mood Analyzer — FastAPI + React

A **social media sentiment and emotion analysis** web application built with:

* **FastAPI** backend
* **React 18 + Vite + Tailwind 4 + ShadCN UI** frontend
* **Hugging Face Transformers** for emotion classification
* **Sentence Transformers** for semantic similarity

The app fetches posts from **Reddit, Mastodon, and YouTube** related to a searched topic, analyzes emotions, and displays interactive visualizations.

🌐 **Live Demo:** *(coming soon)*

---

## 🛠 Features

* Fetches **Reddit, Mastodon, and YouTube comments/posts**
* **Emotion analysis** using `j-hartmann/emotion-english-distilroberta-base`
* **Semantic similarity** between posts and searched topic
* Visualizations:

  * Emotion distribution (**pie chart**, weighted by reactions)
  * Average confidence per emotion (**bar chart**)
  * Detailed posts list with emotion, confidence, likes/upvotes, and source
* **Dark/light mode** support
* CORS enabled for seamless frontend-backend communication

---

## 📁 Project Structure

```
multi-source-mood-analyzer/
├─ backend/
│  ├─ app.py                # FastAPI backend
│  ├─ requirements.txt      # Python dependencies
│  └─ .env                  # API keys and credentials
├─ frontend/
│  ├─ src/
│  │  ├─ components/
│  │  │  ├─ InputForm.jsx
│  │  │  ├─ StatsCard.jsx
│  │  │  ├─ EmotionPieChart.jsx
│  │  │  ├─ EmotionBarChart.jsx
│  │  │  ├─ PostsList.jsx
│  │  │  └─ ThemeToggle.jsx
│  │  └─ App.jsx
│  ├─ package.json
│  └─ vite.config.js        # Vite + Tailwind configuration
└─ README.md
```

---

## ⚡ Backend Setup (FastAPI)

### 1. Create a virtual environment

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
# OR source venv/bin/activate # Linux / macOS
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt**:

```
fastapi==0.115.2
uvicorn==0.23.2
transformers==4.44.2
torch==2.1.0
numpy==1.26.4
pydantic==2.6.0
python-dotenv==1.0.0
praw==7.8.1
Mastodon.py==2.1.4
requests==2.31.0
tokenizers==0.19.1
langdetect==1.0.9
sentencepiece==0.2.0
sacremoses==0.1.1
certifi
sentence-transformers
scikit-learn
httpx
google-api-python-client
```

### 3. Configure environment variables

Create a `.env` file with your API keys:

```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
MASTODON_ACCESS_TOKEN=your_token
MASTODON_BASE_URL=https://mastodon.social
YOUTUBE_API_KEY=your_youtube_key
USE_GPU=0
```

### 4. Run the backend

```bash
uvicorn app:app --reload
```

* Runs at `http://127.0.0.1:8000`
* `/analyze` endpoint accepts POST requests with `{"topic": "AI"}`

---

## ⚡ Frontend Setup (React 18 + Vite + Tailwind 4)

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Run development server

```bash
npm run dev
```

* Runs at `http://localhost:5173`
* Enter a topic to fetch and analyze social media posts

### 3. Notes

* Component-based frontend:

  * `InputForm.jsx` → Topic input and analyze button
  * `StatsCard.jsx` → Summary statistics with icons
  * `EmotionPieChart.jsx` → Weighted emotion distribution
  * `EmotionBarChart.jsx` → Average confidence per emotion
  * `PostsList.jsx` → Scrollable post list with emotions
* Tailwind 4 + ShadCN UI for styling
* Dark/light mode supported via `ThemeToggle.jsx`

---

## 🔹 API Endpoints

### POST `/analyze`

* Input JSON:

```json
{
  "topic": "Artificial Intelligence",
  "limit": 20
}
```

* Response JSON includes:

```json
{
  "topic": "Artificial Intelligence",
  "related_terms": ["AI", "AI news", "AI trends", "..."],
  "total_posts_analyzed": 120,
  "emotion_summary": {"joy": 0.42, "anger": 0.18, "sadness": 0.12, "..."},
  "reaction_stats": {"total_likes": 1023, "avg_likes": 8.53},
  "results": {
    "reddit": [...],
    "mastodon": [...],
    "youtube": [...],
    "all_posts": [...]
  },
  "processing_time": 4.23
}
```

---

## ⚠️ Notes

* Some YouTube comments may reflect **video content rather than topic sentiment**
* Backend supports **thousands of posts** with asynchronous fetching
* Use a valid **Mastodon account token** and **YouTube API key**

---

## 📚 References

* [FastAPI](https://fastapi.tiangolo.com/)
* [React 18](https://reactjs.org/)
* [Vite](https://vitejs.dev/)
* [Tailwind 4](https://tailwindcss.com/)
* [Hugging Face Transformers](https://huggingface.co/transformers/)
* [Sentence Transformers](https://www.sbert.net/)
* [Reddit API (PRAW)](https://praw.readthedocs.io/)
* [Mastodon.py](https://mastodonpy.readthedocs.io/)
* [YouTube Data API](https://developers.google.com/youtube/v3)
