# Emotion models, local LLMs and source options

Research snapshot: 2026-10-19. Provider access rules and model cards can change. This compares options for this repository; it is not a measured benchmark of our data.

## Recommendation

Use a small, multi-label emotion model to score every post. Start with an ONNX CPU pilot of [`Zeolit/lettuce-thymos-26m-v1`](https://huggingface.co/Zeolit/lettuce-thymos-26m-v1): 26.5M parameters, 28 MB quantized ONNX, 28 independent GoEmotions scores, and Apache-2.0. It supports English, French and Arabic among 22 languages. Use its per-label thresholds; fixed 0.5 is specifically discouraged by the model card. Its reported GoEmotions English macro-F1 is 0.527; its 22-language result is 0.446 on machine-translated test texts, so this is a candidate to evaluate, not a quality guarantee. On BRIGHTER, the model reports Arabic dialect variation and weaker Arabic results. Build a native English, French, Tunisian Arabic and MSA test set before advertising those languages.

Keep the emotion model deterministic and post-level. Return the leading emotions, scores above calibrated thresholds, language, model/version and a visible “uncertain” result. A multi-label output can show mixed reactions (for example, admiration and concern) instead of forcing every post into one dominant label. Per-post model scores are not calibrated probabilities about a population. Roll up results with the same aggregation rule in API and charts, and expose counts and source coverage.

Do not add a second classifier just to have “multiple models.” First compare the current classifier and the small ONNX model on the same hand-labeled posts. A second model is useful if it answers a distinct question, such as target stance (positive/negative/neutral toward the named company) or emotion-summary quality. Measure disagreement and show uncertainty rather than silently averaging incompatible scores.

## Classifier candidates

| Candidate | Use | Size and languages from model card | Fit here |
| --- | --- | --- | --- |
| [`Zeolit/lettuce-thymos-26m-v1`](https://huggingface.co/Zeolit/lettuce-thymos-26m-v1) | 28-label GoEmotions, multi-label | 26.5M parameters; 28 MB quantized ONNX; 22 languages including English, French, Arabic and Persian; Apache-2.0 | Best first CPU/low-memory experiment. Explicit thresholds and CPU ONNX example. Arabic dialect/domain performance still needs local evaluation. |
| [`Horizon-Labs/multilingual-emotions-small`](https://huggingface.co/Horizon-Labs/multilingual-emotions-small) | 28-label GoEmotions, multi-label | 141M parameters; Apache-2.0; 35 languages; 268 MB quantized ONNX | Strong comparison candidate. The card reports better average scores than the 26M model on its benchmark, but it is much larger. Try only if the tiny model misses important distinctions. |
| [`Horizon-Labs/multilingual-emotions-base`](https://huggingface.co/Horizon-Labs/multilingual-emotions-base) | Same 28 labels, multi-label | 308M parameters; Apache-2.0; 35 languages; 641 MB quantized ONNX | Accuracy comparison, not a free-instance choice. Quantized model file alone is larger than Render's free 512 MB RAM. |
| [`SamLowe/roberta-base-go_emotions`](https://huggingface.co/SamLowe/roberta-base-go_emotions) | 28-label English baseline | 125M parameters; English; model card reports MIT | Useful English benchmark. Not the multilingual option. |
| Current `j-hartmann/emotion-english-distilroberta-base` | Seven single-label English categories | 82M parameters according to Horizon's comparison; English | Keep as the baseline during evaluation. The comparison lists no license; check the model's own current terms before redistributing weights or making a public product depend on them. It gives one top emotion in this app, while the API already returns scores that the UI does not surface. |

These model-card scores use different datasets and protocols; compare candidates on the same held-out sample and labels before choosing. GoEmotions annotations are English Reddit comments. They do not establish performance on YouTube, Mastodon, Bluesky, political topics, sarcasm, Tunisian dialect or the overall mood of a population. See the [small-model evaluation and limitations](https://huggingface.co/Zeolit/lettuce-thymos-26m-v1#evaluation) and the [Horizon comparison](https://huggingface.co/Horizon-Labs/multilingual-emotions-small#evaluation).

A small emotion encoder is not a generative LLM. That is a useful distinction: it scores each post cheaply and predictably; a local LLM can write a readable description of a batch but may overstate patterns or invent causes.

## Local light LLM option

[`Qwen3-0.6B`](https://huggingface.co/Qwen/Qwen3-0.6B) is Apache-2.0 and is available locally through Ollama, llama.cpp, LM Studio and other runtimes. Ollama lists its Q4_K_M download at about 523 MB. That is the weight file, before runtime memory, prompt context, tokenizer, application and the emotion model. It exceeds this Render plan's 512 MB RAM on weights alone, so do not bundle it with the backend there. On a developer laptop or a separately provisioned machine it is reasonable to try as an optional summary writer. Qwen3's language coverage includes French and Tunisian Arabic, but that is not proof of reliable emotion interpretation in those dialects.

Recommended role: feed a small, fixed JSON object of aggregate emotion counts, source counts, time comparisons and a handful of user-visible post IDs with their measured labels. Ask the LLM to describe only those supplied values, return valid JSON, and attach evidence post IDs to every observation. If it cannot support a claim, it must omit it. Do not ask it to independently assign emotion labels to all posts, infer demographics or claim “public opinion.” Provide a deterministic summary when the local LLM is disabled or slow.

Run it locally behind a narrow adapter (for example, an optional Ollama URL), never download its weights on API startup, and do not make product results depend on a user machine being available. A production self-hosted LLM service needs measured RAM, concurrency and latency headroom; it is a separate deployment resource. Start with one tiny model, a 300-token output cap and at most a few sampled evidence posts. Compare generated text with an expert-reviewed set before release.

The classifiers already provide a more defensible detailed emotion overview than an LLM prompt: surface multi-label scores, top two or three labels, mixed-emotion rate, source/language slices and trend changes. Add target-aware stance separately; “angry text” does not necessarily mean anger at the searched topic.

## Public and low-cost source candidates

“Free to call” does not mean a complete firehose, stable SLA, unrestricted commercial use or permission to bypass access controls. Keep per-source status, query scope, collection time, limits, duplicates and errors visible. Do not scrape logged-in pages or rotate identities to evade platform restrictions.

| Source | Access path | What it adds | Limits and fit |
| --- | --- | --- | --- |
| Reddit | Existing PRAW OAuth app | Large topic communities and comments | Existing collector is a good source when credentials/access are valid. Reddit's Data API requires registration and compliance; the current terms restrict use of user content for training ML without rightsholder permission, and access can be limited or paid for use outside permitted scope. This app performs inference, not fine-tuning; still minimize retention and respect removal/attribution terms. |
| YouTube | Existing Data API v3 key | Comments around videos, with engagement | Official API gives 100 `search.list` calls per day by default and a separate 10,000-unit daily pool for other calls. This app expands a topic into six terms by default: that is six video-search calls plus up to 18 comment calls for three videos each per analysis. Search quota therefore caps it around 16 analyses/day before other use. Search fewer, deduplicate terms/videos, cache results and report quota errors. |
| Mastodon / Fediverse | Existing instance API | Public hashtag conversations | Public hashtag timeline is a public endpoint on an instance, but only returns posts containing that hashtag and the selected instance/federation view. One instance is not the whole Fediverse. Search statuses is server-dependent and generally needs authentication; public hashtag timeline is the safer default. Current code treats arbitrary phrases as hashtags, so this adapter needs correction. |
| Bluesky | `app.bsky.feed.searchPosts` via public AppView | Public short posts, replies and repost metadata | Bluesky documents unauthenticated public `app.bsky.*` GETs at `https://public.api.bsky.app`. Strong next general social source. A direct search probe from this environment returned HTTP 403, so verify from Render and implement clear source-unavailable status before relying on it. Don't depend on a scraped mirror or the live firehose for a first version. |
| Lemmy | Instance `GET /api/v4/search` on Lemmy 1.0+ / current API schema | Federated forum posts and comments | Public reads can work without a user account, but search is instance-scoped and federated coverage depends on that instance. Add only when the user can choose/see the instance; normalize post and comment separately. |
| Hacker News | [Algolia HN Search API](https://hn.algolia.com/api) | Tech-startup, developer and product-launch discussions | Search stories and comments without an API key. Good high-value niche source for tech projects, poor proxy for broad public mood. It is a third-party search service over HN, so cache and handle outages. |
| Stack Exchange | Official Stack Exchange API | Domain-specific questions, answers and comments | Useful for developer/product feedback, not a general social sample. Anonymous quota is shared by IP (default 10,000/day with an app key); respect `backoff`, cache identical queries and show Stack Exchange's CC BY-SA attribution when displaying content. |
| RSS / Atom feeds | Publisher-provided feeds | News articles and publisher-chosen comments where available | Simple, keyless and cheap, but coverage is opt-in and not a social conversation sample. Keep “news coverage” separate from user-post sentiment. |
| GDELT DOC API | Open news-index search | Broad news article/event context | Useful for “what is media covering?” and topic timelines, not direct public emotions. Present as news coverage/context rather than another social network. |

The most useful first expansion is Bluesky plus Hacker News for a technology-oriented product, while retaining Reddit, YouTube and Mastodon as separately reported sources. Add Lemmy or Stack Exchange when the product's user and topic area justify their instance/community scope. RSS/GDELT belong in a distinct news panel. A larger source count does not make the sample representative: each source captures a different population, ranking system and participation pattern.

Avoid unofficial Instagram, TikTok, X or LinkedIn scrapers as the foundation of a product. Access can break, permissions and terms can change, and scraping often yields incomparable or incomplete samples. If those networks are essential, use a currently supported official access route and make its availability an explicit product requirement.

## Architecture that can run locally and on a small host

1. Define a shared post contract: platform, stable post ID, URL, created-at time, text, reply/repost flag, public engagement counts, language, retrieval time and collection query. Deduplicate by platform ID before text similarity.
2. Give each source a small adapter with a timeout, result budget, provider backoff, cursor support, cached responses and explicit statuses such as `ok`, `no_matches`, `not_configured`, `rate_limited` and `unavailable`.
3. Separate collection budgets by source. A single user's topic should not launch six YouTube searches and eighteen comment requests every time they click. Start with one normalized query per source, explicit time range, modest result caps and cache.
4. Replace the current PyTorch emotion pipeline with the 26M ONNX candidate only after parity evaluation. The app also loads Sentence Transformers for semantic similarity; replacing just the emotion classifier will not remove all model memory. Profile the complete process and cold model download, with the same thread/worker limits as Render. Keep ONNX files cached locally; Render free disk is ephemeral.
5. Store model/version and source status with each result. Expose multi-label emotion details in cards and charts; never combine engagement counts across platforms as if they measured the same thing.
6. Add the local LLM summary behind an opt-in interface. It consumes aggregates and evidence IDs; provider/model failure should not block collection or invalidate the deterministic dashboard.

## Evaluation before declaring it a real product

Make a small, manually reviewed benchmark from the exact languages, query types and source mix the product targets. Include irrelevant search matches, negation, sarcasm, quotes/reposts, slang, code-switching, MSA/Tunisian Arabic and French. Measure relevance precision, per-label precision/recall/F1, abstention, latency, peak resident memory and source yield separately. Keep model output, human label and adjudication history so updates are comparable.

For source quality, report per-platform counts, time coverage, error/empty states, and the share removed as duplicates or irrelevant. Do not aggregate emotion into a single “world mood” score until sampling and weighting are explained and validated. Show the posts that support each trend.
