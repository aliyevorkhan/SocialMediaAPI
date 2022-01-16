from utils import *
from faker import Faker
from config_reader import ConfigReader
import random
import logging


class Bot:
    def __init__(self, number_of_users=10, max_posts_per_user=10, max_likes_per_user=10):
        self.number_of_users = number_of_users
        self.max_posts_per_user = max_posts_per_user
        self.max_likes_per_user = max_likes_per_user
        
        self.fake = Faker()

        self.access_tokens = []
        self.post_ids = []


    def signup_and_login_users(self):
        for i in range(self.number_of_users):
            username = self.fake.user_name()
            password = self.fake.password()
            email = self.fake.email()
            full_name = self.fake.name()

            result_of_signup = signup(username,password,email, full_name)

            if result_of_signup.ok:
                logging.warning("{}. user signed up".format(i+1))
                result_of_login = login(username,password)
                self.access_tokens.append(result_of_login.json()["access_token"])
            
    def create_post_by_user(self):
        for token in self.access_tokens:
            for _ in range(self.max_posts_per_user):
                title = self.fake.address()
                content = self.fake.text()
               
                result_of_post_creation = create_post(title,content,token)
               
                if result_of_post_creation.ok:
                    detail = result_of_post_creation.json()["detail"]
                    post_id = result_of_post_creation.json()["post_id"]
                    
                    logging.warning("{}. Post id: {}".format(detail, post_id))

                    self.post_ids.append(post_id)

    def like_randomly(self):
        for token in self.access_tokens:
            for _ in range(self.max_likes_per_user):
                post_id = random.choice(self.post_ids)
                result_of_post_like = like(post_id, token)

                if result_of_post_like.ok:
                    detail = result_of_post_like.json()["detail"]

                    logging.warning("{}".format(detail))

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

    config = ConfigReader()

    bot = Bot(config.number_of_users, config.max_posts_per_user, config.max_likes_per_user)

    bot.signup_and_login_users()
    bot.create_post_by_user()
    bot.like_randomly()