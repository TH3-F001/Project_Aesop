import praw
from common.content_helper import Helper


class Reddit:
    def __init__(self, cred_path):
        cred_info = Helper.load_json(cred_path)

        # Setup the client with all necessary credentials
        self.client = praw.Reddit(
            client_id=cred_info["client_id"],
            client_secret=cred_info["client_secret"],
            user_agent=cred_info["user_agent"]
        )

        self.username = cred_info["username"]

    def build_post_dict(self, submission):
        # Builds a dictionary with relevant post details
        return {
            "title": submission.title,
            "author": submission.author,
            "content": submission.selftext,
            "comments": submission.comments,
            "upvotes": submission.ups,
            "downvotes": submission.downs,
            "upvote_ratio": submission.upvote_ratio,
            "likes": submission.likes,
            "subreddit": submission.subreddit,
            "url": submission.url
        }

    def get_posts(self, subreddit, num=5, sort='hot'):
        # Generic method to fetch posts based on sort type
        subreddit = subreddit.replace("r/", "")  # normalize subreddit name
        result = {}
        submissions = getattr(self.client.subreddit(subreddit), sort)(limit=num)
        for submission in submissions:
            result[submission.id] = self.build_post_dict(submission)
        return result

    def get_top_posts(self, subreddit, num=5):  # highest net upvotes
        return self.get_posts(subreddit, num, sort='top')

    def get_hot_posts(self, subreddit, num=5):  # trending at the moment
        return self.get_posts(subreddit, num, sort='hot')

    def get_controversial_posts(self, subreddit, num=5):    # high upvotes and downvoites
        return self.get_posts(subreddit, num, sort='controversial')

    def get_gilded_posts(self, subreddit, num=5):   # has recieved awards
        return self.get_posts(subreddit, num, sort='gilded')

    def get_new_posts(self, subreddit, num=5):  # most recent posts
        return self.get_posts(subreddit, num, sort='new')

    def get_rising_posts(self, subreddit, num=5):   # posts beginning to gain traction
        return self.get_posts(subreddit, num, sort="rising")

    def get_random_rising_posts(self, subreddit, num=5):    # the above, but in random order
        return self.get_posts(subreddit, num, sort='random_rising')

    def search_subreddit(self, subreddit, search_query, num=5):     # search a specific string
        subreddit = subreddit.replace("r/", "")
        result = {}
        for submission in self.client.subreddit(subreddit).search(search_query, sort='relevance', syntax='lucene', time_filter='all', limit=num):
            result[submission.id] = self.build_post_dict(submission)
        return result

