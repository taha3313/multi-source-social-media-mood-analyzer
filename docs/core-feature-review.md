# Core feature review

This review is based on the checked-in implementation, not a live credentialed collection or model-quality benchmark. Infrastructure changes do not establish reliable product results.

## Recommended direction

Make this a topic monitoring and comparison tool for a defined user, such as a small team tracking reactions to a product launch. A useful question is: “What changed in the discussion about our product this week, on which sources, and which posts explain it?” The current one-off emotion charts cannot answer that yet.

## Priority 1: Make every result auditable

- Return source status separately: success with zero matches, missing credentials, denied access, quota exhaustion, timeout and provider error. The current collectors print errors and return empty lists, so missing data looks like absent discussion.
- Preserve stable post IDs, timestamps, retrieval time, query and model revision. Show links and counts by source, including excluded posts and reasons. YouTube currently selects recently published videos, not necessarily recently published comments; harmonize the actual post time window.
- Provide one shared aggregation contract. The API weights emotions using confidence × log(reactions + 2), while the pie chart uses reactions + 1 and the summary card counts posts. The same sample can therefore tell three different stories. Default to an unweighted post distribution with optional clearly named engagement weighting. Clamp negative Reddit scores in the pie chart too; API logarithms are now guarded, but raw scores remain signed.
- Show sample size, coverage and collection limitations. Reddit votes, Mastodon favourites and YouTube likes are different measures. Neither classifier confidence nor engagement weighting is statistical confidence about public opinion.

## Priority 2: Improve relevance before adding sources

- Replace fixed “news/trends/discussion/impact/analysis” suffixes with explicit query controls and user-confirmed aliases. The existing function name suggests semantic expansion, but it only adds fixed strings.
- Apply a calibrated relevance policy to all sources. Currently only YouTube is filtered by semantic similarity; Reddit and Mastodon receive scores later but are not filtered. Use a human-reviewed dataset containing ambiguous names, unrelated comments and multiword topics.
- Fix Mastodon topic search: arbitrary multiword phrases passed to `timeline_hashtag` are not a general topic search, and one instance does not represent the whole network. Make instance scope visible and distinguish hashtags from phrase search.
- Detect language and initially restrict analysis to supported English content. Add French/Arabic only with an evaluated multilingual model and per-language evidence. The present English classifier should not silently label arbitrary languages.
- Separate emotion expressed in a post from sentiment toward the target. An angry post may criticize a competitor or quote someone else. Add target-aware positive/negative/neutral stance with supporting excerpts, while retaining emotion as secondary context.

## Priority 3: Make the product useful over time

- Add explicit time windows, saved topics and snapshots. Show daily/weekly changes with source-balanced counts, discussion volume, and representative posts. Store provenance with each snapshot so changes in collectors/models do not look like audience shifts.
- Cluster recurring themes and let users inspect supporting posts. Prefer a small, traceable set of themes to an unsupported generated summary. Add comparisons between products, releases or time windows after the sampling policy is stable.
- Make API and UI display limits agree. `limit // 3` currently truncates each source independently, loses the remainder and does not fill slots from sources that have more data. Let users choose sources and see the complete analyzed count alongside the displayed count.
- Add a labelled evaluation set for relevance, language, target stance and emotions. Report per-source/per-language errors, especially sarcasm, quotations and mixed emotions. Model scores alone are not quality evidence.

## Priority 4: Control cost and latency

Six search variants currently fan out to 18 collectors and up to 18 YouTube video searches plus comment requests. Similarity is encoded comment by comment and the entire result set is encoded again. `limit` does not reduce that work.

Start with bounded per-source budgets, batched embeddings, duplicate removal by stable ID and canonical URL, short-lived query caching and retries only for transient failures. Add cancellation and provider-specific quota reporting. Move long analyses into a job with progress and cancellation when synchronous latency is measured to be too high; a queue is not needed merely to imitate another project.

Before enabling unattended public use, add request throttling and a total analysis deadline. The current per-process concurrency guard limits inference overlap, but timed-out worker threads may continue calling providers. Verify real peak RAM and quota consumption before choosing hosting.

## Suggested first milestone

Ship one trustworthy English topic comparison: chosen sources and time window, explicit source status, consistent counts/weights, filtered relevant posts, and a small human-reviewed evaluation set. Add saved history next. This produces a stronger portfolio demonstration than increasing the number of charts or sources.
