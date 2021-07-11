import tweepy

class Twitter:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.consumer_key           = consumer_key
        self.consumer_secret        = consumer_secret
        self.access_token           = access_token
        self.access_token_secret    = access_token_secret

    def _twitter_auth(self):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        return auth

    def twitter_connect(self):
        api = tweepy.API(self._twitter_auth())
        return api
