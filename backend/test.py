import praw

reddit = praw.Reddit(
    client_id="mSn9XrNoY3BQLqkgKLa7hw",
    client_secret=None,
    user_agent="tweetmood-project",
    check_for_async=False
)

for submission in reddit.subreddit("all").search("Trump tariffs", limit=3):
    print(submission.title)