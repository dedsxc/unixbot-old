#!/usr/bin/python3
import time, praw, os, requests, configparser, sys

sys.path.append('..')
from PIL import Image
from libs.logger import logGenerator
from libs.directory import Directory
from libs.twitter import Twitter


class UnixpornBot:
    def __init__(self):
        self.cwd_path           = os.getcwd()
        self.log_file           = os.path.join(self.cwd_path, 'log', 'unixbot.log')
        self.log_directory      = os.path.join(self.cwd_path, 'log')
        self.img_directory      = os.path.join(self.cwd_path, 'img')
        self.cache              = os.path.join(self.cwd_path, 'cache.txt')
        if not os.path.exists(self.cache):
            open(self.cache , 'w')
        self.config_file        = os.path.join(self.cwd_path, '..', 'config.ini')
        self.config             = configparser.ConfigParser()
        Directory.exist(self.log_directory)
        Directory.exist(self.img_directory)
        Directory.erase_file(self.log_file)
        self.logger             = logGenerator(self.log_file)
        self.delay_btw_tweet    = 600
        

    def _connect(self):
        self.config.read(self.config_file)
        # Twitter Authentication
        self.conn = Twitter(consumer_key        = self.config['Twitter']['CONSUMER_KEY'],
                            consumer_secret     = self.config['Twitter']['CONSUMER_SECRET'],
                            access_token        = self.config['Twitter']['ACCESS_TOKEN'],
                            access_token_secret = self.config['Twitter']['ACCESS_TOKEN_SECRET'])
        self.api = self.conn.twitter_connect()
        if self.api.verify_credentials():
            self.logger.info(" OK Authentication to twitter")
        else:
            self.logger.error("[-] Error during authentication")
            exit(0)
        # Reddit Authentication
        self.reddit = praw.Reddit(
            user_agent      = self.config['Reddit']['USERNAME'],
            client_id       = self.config['Reddit']['CLIENT_ID'],
            client_secret   = self.config['Reddit']['CLIENT_SECRET'],
            username        = self.config['Reddit']['USERNAME'],
            password        = self.config['Reddit']['PASSWORD'],
            reddit_url      = self.config['Reddit']['URI']
        )
        self.logger.info('[+] Connected to {}'.format(self.reddit.user.me()))

    def _tweet(self, m_id, m_title, m_link, m_path_img):
        l_status = '📥 - ' + m_title + '  || Credit: ' + m_link
        self.api.update_with_media(filename=m_path_img, status=l_status)
        self.logger.info(" _tweetted successfully")
        self._log_tweet(m_id)
        os.remove(m_path_img)

    def _gather_info(self):
        while 1:
            # Get last post from Reddit r/unixporn
            subreddit = self.reddit.subreddit('unixporn').new(limit=1)
            submission = next(subreddit)
            id_reddit = submission.id
            title_reddit = submission.title
            short_link = submission.shortlink
            url_img = submission.url
            img_to_big = 0
            if not self._already_get(id_reddit):
                self.logger.info('[+] New post title: {}'.format(title_reddit))
                # Download img if exist
                if 'png' in url_img or 'jpeg' in url_img or 'jpg' in url_img:
                    if 'png' in url_img:
                        path_img = 'img/' + id_reddit + '.png'
                        self.logger.info("png: {}".format(url_img))
                    if 'jpeg' in url_img:
                        path_img = 'img/' + id_reddit + '.jpeg'
                        self.logger.info("jpeg: {}".format(url_img))
                    if 'jpg' in url_img:
                        path_img = 'img/' + id_reddit + '.jpg'
                        self.logger.info("jpg: {}".format(url_img))
                    with open(path_img, 'wb') as f:
                        f.write(requests.get(url_img).content)

                    # reduce img size if > 3072Ko
                    if os.path.getsize(path_img) > 3072000:
                        img = Image.open(path_img)
                        img.save(path_img, optimize=True, quality=85)
                        if os.path.getsize(path_img) > 3072000:
                            self.logger.warning('[-] File too big: {}o'.format(os.path.getsize(path_img)))
                            os.remove(path_img)
                            self._log_tweet(id_reddit)
                            img_to_big = 1

                    # ... and _tweet it
                    if img_to_big == 0:
                        self._tweet(id_reddit, title_reddit, short_link, path_img)

                else:
                    self.logger.info("[-] no pic: {}".format(url_img))
                    self.logger.info("[-] url post: {}".format(short_link))
            time.sleep(self.delay_btw_tweet)

    def _already_get(self, m_post_id):
        found = False
        with open(self.cache, 'r') as f:
            for line in f:
                if m_post_id in line:
                    found = True
                    break
        return found

    def _log_tweet(self, m_post_id):
        with open(self.cache, 'a') as f:
            f.write(str(m_post_id) + '\n')

    def process(self):
        self._connect()
        self._gather_info()


# Main Program
def main():
    bot = UnixpornBot()
    bot.process()

if __name__ == '__main__':
    main()
