import tweepy
import twitter_info
import json
import sqlite3
import omdb
import itertools

#Tweepy set-up
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
tweepy_api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

movies = ['candyman', 'vampires in brooklyn', 'get out', 'boomerang']
tweepy_keyword = 'fanbros'

#PART ZERO - SETUP

#Cache set-up directions
CACHE_FNAME = "finalproject.json"
try:
	cache_file = open(CACHE_FNAME,'r')
	cache_contents = cache_file.read()
	cache_file.close()
	CACHE_DICTION = json.loads(cache_contents)
except:
	CACHE_DICTION = {}

#Class set-up directions
class Movie:
	def __init__(self, title, advisory_rating, year_released, studio):
		self.title = title
		self.advisory_rating = advisory_rating
		self.year_released = year_released
		self.studio = studio

class Tweet:
	def __init__(self, tweet_id, text, user_id, retweets):
		self.tweet_id = tweet_id
		self.text = text
		self.user_id = user_id
		self.retweets = retweets

class User:
	def __init__(self, user_id, screen_name, num_favs, description):
		self.user_id = user_id
		self.screen_name = screen_name
		self.num_favs = num_favs
		self.description = description

#PART 1: CREATE METHODS

# Some parts of the code should already be filled in when you turn this in:
# - At least 1 function which gets and caches data from 1 of your data sources, and an invocation of each of those functions to show that they work 
# - Tests at the end of your file that accord with those instructions (will test that you completed those instructions correctly!)
# - Code that creates a database file and tables as your project plan explains, such that your program can be run over and over again without error and without duplicate rows in your tables.
# - At least enough code to load data into 1 of your dtabase tables (this should accord with your instructions/tests)

def get_user_tweets(user_handle):
	if user_handle in CACHE_DICTION:
		results = CACHE_DICTION[user_handle]
	else:
		results = tweepy_api.user_timeline(id = user_handle, count = 20)
		CACHE_DICTION[user_handle] = results

		f = open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()
	return results

def get_tweets(user_tweets):
	city = []
	for u in user_tweets:
		city.append(Tweet(t['id_str'], t['text'], t['user']['id'], t['user']['created_at'], t['retweet_count']))
	return city

 def request_movies(movies):
 	omdb_movies = []
 	for m in movies:
 		request = omdb.request(s = m, plot = short)
 		omdb_movies.append(request)
 	return omdb_movies

def get_neighborhood(user_tweets):
	neighborhood = []
	for u in user_tweets:
		for m in u['entities']['user_mentions']:
			user = tweepy_api.get_user(m['screen_name'])
			neighborhood.append(User(user['id_str'], user['screen_name'], user['favourites_count'], user['description']))
	return neighborhood

#PART 3: DATABASE QUERIES
#Using the functions you created in Part 2 of the project, use the omdb_movies list of strings and the tweepy_keyword to create your tables.
conn = sqlite3.connect('finalproject.db')
cur = conn.cursor()

	#1. Create Movies table and commit it to the database

	#2. Create Tweets table and commit it to the database

	#3. Create Users table and commit it to the database


#PART 4: .CSV

conn.close()

#PART 5: TEST SUITE
class Tests(unittest.TestCase):
	def test_request_movies_one(self):
		#test that request_movies() returns a list.
	def test_request_movies_two(self):
		#test that request_movies() returns a list of movie objects.
	def test_movies_one(self):
		#test that my movies table has four columns
	def test_tweets(self):
		#test that the tweets table has five columns
	def test_neighborhood(self):
		#test that get_neighborhood() returns a list of user objects
	def test_select(self): 
		#test thatthe tweets selected were posted from 10am to 12pm
	def test_join(self):
		#test that the selected screen names and user ids are the same.
	def test_movie_dicts(self):
		#test that you can initialize a Movie instance with a dictionary.
if __name__ == "__main__":
	unittest.main(verbosity=2)