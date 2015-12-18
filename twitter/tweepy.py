import itertools
import tweepy
from twitter.models import TwitterUser
from twitter.models import TwitterList
from twitter.models import Tweet

class TwitterTweepy:
    """
    Access to twitter API with Tweepy library
    """
    consumer_key = "Vuh03kAwNIJm7Nb769szVgLOC"
    consumer_secret = "KB8JUp6wGqt3S4E3QvhiDM2KQeITPTyq3imYBrIl7nyahSNWOh"
    access_token = "297349951-BnxwnjhigMxTDB0wdRqQNL5EBma6ROpduvPJxYBS"
    access_token_secret = "mt2TyQzOOu6g6uGxbhuFIhh5Y0nkNW01txxdTtHrsEE2E"

    def __init__(self):
        self.api = self.authenticate()

    def authenticate(self):
        """
        Authenticate with Twitter API
        :return Twitter API wrapper object
        """
        try:
            auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            # Twitter API wrapper, with options to automatically wait for the rate limit
            return tweepy.API(auth, wait_on_rate_limit='true', wait_on_rate_limit_notify='true')
        except tweepy.TweepError:
            print("Error in authentication")

    def user_exists(self, screenName):
        """
        Check whether a name is a valid twitter username or not
        :param screenName: name to check
        :return: true if valid username, false if invalid username
        """
        try:
            user_to_check = self.api.get_user(screenName)
            print(user_to_check.screen_name + ", " + screenName)
            if user_to_check.screen_name.lower() == screenName.lower():
                return True
        except tweepy.TweepError:
            print("Tweepy: Error in user_exists")

        return False

    def profile_information_search(self, names, friends=False, followers=False, max_followers={},
                                   list_memberships=False, list_subscriptions=False):
        """ :Start Profile Information Search
            :param names: comma separated list of EGO names entered by user
            :param friends: boolean Friends lookup yes or no
            :param followers: boolean Followers lookup yes or no
            :param max_followers: maximum number of followers a EGO-name can have
            :param list_memberships: get the lists a user is a member of yes or no
            :param list_subscriptions: get the lists a users is subscribed on yes or no (also owned lists)
        """
        # https://dev.twitter.com/rest/reference/get/users/lookup
        # get names from list, remove empty (otherwise error)
        names_list = names.split(',')
        print('friends {} followers {} max followers {} listmemberships {} listsubscriptions {}'
              .format(friends, followers, max_followers, list_memberships, list_subscriptions))
        # list of ego_users as TwitterUser-objects
        list_ego_users = list()
        # convert names entered to twitter users objects and store
        for name in names_list:
            # string cannot not be empty
            if name:
                try:
                    user = self.api.get_user(name)
                    twitter_user = TwitterUser(user_id=user.id, name=user.name, screen_name=user.screen_name,
                                               friends_count=user.friends_count, followers_count=user.followers_count)
                    if user.followers_count > max_followers:
                        # exclude EGO-user if it has to many followers
                        print("{} has too many followers".format(name))
                        twitter_user.max_followers_exceeded = True
                        names_list.remove(name)
                    twitter_user.save()
                    # used for getting the id in list memberships and list subscriptions
                    list_ego_users.append(twitter_user)
                except tweepy.TweepError:
                    print("Error in profile_information_search: error get username EGO-user")
        # Collect friends of ego-users
        if friends:
            print("Collect friends")
            # iterate over all ego names the user has entered
            for name in names_list:
                # check first if name is not empty
                if name:
                    print("Friend ids of {}".format(name))
                    ids = list()
                    # get user ids of friends of user
                    for friend_id in tweepy.Cursor(self.api.friends_ids, screen_name=name).items():
                        # add ids to list of ids
                        ids.append(friend_id)
                    # get user objects from friend-ids and store in database
                    for page in self._paginate(ids, 100):
                        self._saveusers(page)

        # Collect followers of ego users
        if followers:
            print("Collect followers")
            for name in names_list:
                # check first if name is not empty
                if name:
                    print("Follower ids of {}".format(name))
                    ids = list()
                    # get user ids of followers of user
                    for follower_id in tweepy.Cursor(self.api.followers_ids, screen_name=name).items():
                        ids.append(follower_id)
                    # get user objects from follower-ids and store in database
                    for page in self._paginate(ids, 100):
                        self._saveusers(page)

        # Collect lists the ego users are members of
        if list_memberships:
            print("Collect list memberships")
            for name in names_list:
                if name:
                    # check first if list is not empty
                    ego_user = self._get_user(name, list_ego_users)
                    print(name, list_ego_users)
                    for twitter_list in tweepy.Cursor(self.api.lists_memberships, screen_name=name).items():
                        # for a many to many relationship, the object has to be saved first,
                        # then the relationship can be added
                        twitterlist = TwitterList(list_id=twitter_list.id, list_name=twitter_list.name,
                                                  list_full_name=twitter_list.full_name)
                        twitterlist.save()
                        twitterlist.user_membership.add(ego_user)



        # Collect lists the ego user subscribes to
        if list_subscriptions:
            print("Collect list subscriptions")
            for name in names_list:
                if name:
                    # check first if list is not empty
                    ego_user = self._get_user(name, list_ego_users)
                    print(name, list_ego_users)
                    for twitter_list in tweepy.Cursor(self.api.lists_subscriptions, screen_name=name).items():
                        twitterlist = TwitterList(list_id=twitter_list.id, list_name=twitter_list.name,
                                                  list_full_name=twitter_list.full_name)
                        twitterlist.save()
                        twitterlist.user_subscription.add(ego_user)

    def _saveusers(self, ids):
        """
        converts a hundred ids of users to objects and saves them
        :param ids: max 100
        """
        users = self.api.lookup_users(user_ids=ids)
        for user in users:
            twitter_user = TwitterUser(user_id=user.id, name=user.name, screen_name=user.screen_name,
                                       friends_count=user.friends_count,
                                       followers_count=user.followers_count)
            twitter_user.save()

    def _paginate(self, iterable, page_size):
        """
        iterates over an iterable in <page size> pieces
        code from http://stackoverflow.com/questions/14265082/query-regarding-pagination-in-
        tweepy-get-followers-of-a-particular-twitter-use
        http://stackoverflow.com/questions/3744451/is-this-how-you-paginate-or-is-there-a-better-algorithm/3744531#3744531
        :param iterable: the iterable to iterate over
        :param page_size: the max page size returned
        :return: generator
        """
        while True:
            # https://docs.python.org/3.5/library/itertools.html
            # itertools.tee(iterable, n=2) Return n independent iterators from a single iterable
            # tee returns two copies of the iterable
            i1, i2 = itertools.tee(iterable)
            # start of iterable is shifted page_size times / first -> page size items placed in page
            iterable, page = (itertools.islice(i1, page_size, None), list(itertools.islice(i2, page_size)))
            if len(page) == 0:
                break
            yield page

    def _get_user(self, name, list_users):
        """
        returns the user with the username from the given list
        :param name: name of the user
        :param list_users: the list of users
        :return: TwitterUser object with the name
        """
        for user in list_users:
            print("get user method {} {}".format(name, user.screen_name))
            if user.screen_name.lower() == name.lower():
                return user


class TweetsByNameStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        text_of_tweet = ""
        hashtags = ""
        urls = ""
        mentions = ""
        delimiter = ";"
        is_retweet = False
        # check is the tweet is a retweet
        # if it is, add is_retweet = True and get the text from the original tweet (normal text is truncated)
        if hasattr(status, 'retweeted_status'):
            text_of_tweet = status.retweeted_status.text
            is_retweet = True
        else:
            text_of_tweet = status.text
        # get mentions, urls & hashtags
        if hasattr(status, 'entities'):
            for url in status.entities.expanded_url:
                urls += url + delimiter
            for hashtag in status.entities.hashtags:
                hashtags += hashtag + delimiter
            for mention in status.entities.user_mentions:
                mentions += mention + delimiter
        tweet = Tweet(tweet_id=status.id_str,
                      tweeter_id=status.user.id, tweeter_name=status.user.screen_name,tweet_text=text_of_tweet,
                      tweet_date=status.created_at, is_retweet=is_retweet,
                      mentions=mentions, hashtags=hashtags, hyperlinks=urls)
        tweet.save()

