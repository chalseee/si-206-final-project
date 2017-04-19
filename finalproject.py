import tweepy
import twitter_info
import json
import sqlite3
import omdb
import itertools

#Tweepy set-up:
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
tweepy_api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

#create a list of strings of movie titles called 'movies'. the list should be 20 movies long.
movies = ['candyman', 'candyman', 'vampire in brooklyn', "the preacher's son", 'sister code', 'november rule', 'boy bye', 'hurricane bianca', 'a weekend for the family', 'queen of katwe', 'the book of eli', 'i am not your negro', 'black november', 'the sin seer', 'go tell it on the mountain', 'vampire academy', 'selma', 'keanu', 'son of ingagi', 'blacula', 'dreamgirls','get out', 'boomerang', 'hidden figures', 'the wiz', 'black dynamite', 'white chicks', 'akeelah and the bee', 'glory', 'a raisin in the sun']
#create a string of a keyword named 'tweepy_keyword'
tweepy_keyword = '@SirDancealot56'

#PART ZERO - SETUP

# Put your caching setup here:
CACHE_FNAME = "finalproject.json"
try:
	cache_file = open(CACHE_FNAME,'r')
	cache_contents = cache_file.read()
	cache_file.close()
	CACHE_DICTION = json.loads(cache_contents)
except:
	CACHE_DICTION = {}

#Implement 3 classes:

#Implement a Movie class that will hold all of the information for a movie from omdb for later use in the program. 
# It should contain these member variables:
# - movie title -- this column is the PRIMARY KEY
# - advisory rating (string -- 'PG', 'R', 'PG-13', etc.)
# - year released (integer of a year)
# - studio (the production studio that made the movie, which is a string)
class Movie:
	def __init__(self, title, advisory_rating, year_released, studio):
		self.title = title
		self.advisory_rating = advisory_rating
		self.year_released = year_released
		self.studio = studio

#Implement a Tweet class that will hold all of the information for a tweet for later use in the program. 
# It should contain these member variables:
# - tweet_id (containing the string id belonging to the Tweet itself) -- this column should be the PRIMARY KEY of this table
# - text (containing the text of the Tweet)
# - user_id (an ID string, referencing the Users table)
# - time_posted (the time at which the tweet was created)
# - retweets
class Tweet:
	def __init__(self, tweet_id, text, user_id, time_posted, retweets):
		self.tweet_id = tweet_id
		self.text = text
		self.user_id = user_id
		self.time_posted = time_posted
		self.retweets = retweets

#Implement a User class that will hold all of the information for a user for later use in the program. 
# It should contain these member variables:
# - user_id (containing the string id belonging to the user, from twitter data -- note the id_str attribute) -- this column should be the PRIMARY KEY of this table
# - screen_name (containing the screen name of the user on Twitter)
# - num_favs (containing the number of tweets that user has favorited)
# - description (text containing the description of that user on Twitter
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
		results = tweepy_api.user_timeline(user_handle)
		CACHE_DICTION[user_handle] = results

		f = open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()
	return results

def get_tweets(user_tweets):
	city = []
	for t in user_tweets:
		city.append(Tweet(t['id_str'], t['text'], t['user']['id'], t['user']['created_at'], t['retweet_count']))
	return city

def request_movies(movies):
 	omdb_movies = []
 	for m in movies:
 		request = json.loads(omdb.request(t = m).text)
 		if (request['Response'] == 'True'):
 			omdb_movies.append(Movie(request['Title'], request['Year'], request['Rated'], request['Production']))
 	return omdb_movies

#write a function gets accepts a list of tweets created with the get_tweets function and uses it to create another list. This list will be filled with the usernames of evert
def get_neighborhood(user_tweets):
	neighborhood = []
	for u in user_tweets:
		user = tweepy_api.get_user(u['user']['id'])
		neighborhood.append(User(user['id_str'], user['screen_name'], user['favourites_count'], user['description']))
		for m in u['entities']['user_mentions']:
			neighbor = tweepy_api.get_user(m['screen_name'])
			neighborhood.append(User(neighbor['id_str'], neighbor['screen_name'], neighbor['favourites_count'], neighbor['description']))
	return neighborhood

#PART 3: DATABASE QUERIES
#Using the functions you created in Part 2 of the project, use the 'movies' list of strings and the tweepy_keyword to create your tables.
#Then, using each class you created, input the class instances into the three tables.
conn = sqlite3.connect('finalproject.db')
cur = conn.cursor()

	#1. Create Movies table and commit its data to the database
statement = 'CREATE TABLE IF NOT EXISTS Movies (title TEXT PRIMARY KEY, advisory_rating TEXT, year_released INTEGER, studio TEXT)'
cur.execute(statement)
user_tweets = get_user_tweets(tweepy_keyword)
results = request_movies(movies)

for r in results:
	statement = 'INSERT OR IGNORE INTO Movies Values (?,?,?,?)'
	data = (r.title, r.advisory_rating, r.year_released, r.studio)
	cur.execute(statement, data)

	#2. Create Tweets table and commit its data to the database
statement = 'CREATE TABLE IF NOT EXISTS Tweets (tweet_id TEXT PRIMARY KEY, text TEXT, user_id TEXT, time_posted TIMESTAMP, retweets INTEGER)'
cur.execute(statement) #haven't done this one yet
tweets = get_tweets(user_tweets)
for t in tweets:
	statement = 'INSERT OR IGNORE INTO Tweets Values (?,?,?,?,?)'
	data = (t.tweet_id, t.text, t.user_id, t.time_posted, t.retweets)
	cur.execute(statement, data)

	#3. Create Users table and commit its data to the database
statement = 'CREATE TABLE IF NOT EXISTS Users (user_id TEXT PRIMARY KEY, screen_name TEXT, num_favs INTEGER, description TEXT)'
cur.execute(statement)
neighborhood = get_neighborhood(user_tweets)
for n in neighborhood:
	statement = 'INSERT OR IGNORE INTO Users Values (?,?,?,?)'
	data = (n.user_id, n.screen_name, n.num_favs, n.description)
	cur.execute(statement, data)
conn.commit()

# MAKE TWO QUERIES TO THE DATABASE and save them in different variables.
	# 1.Select all tweets that a were posted from 10 am to 12pm.

	#2.Join User screen names with Tweet user ids to see which of them match up.

#close the database connection
conn.close()


#PART 4: .CSV


# PART 5: TEST SUITE
# class Tests(unittest.TestCase):
# 	def test_request_movies_one(self):
# 		#test that request_movies() returns a list.
# 	def test_request_movies_two(self):
# 		#test that request_movies() returns a list of movie objects.
# 	def test_movies_one(self):
# 		#test that my movies table has four columns
# 	def test_tweets(self):
# 		#test that the tweets table has five columns
# 	def test_neighborhood(self):
# 		#test that get_neighborhood() returns a list of user objects
# 	def test_select(self): 
# 		#test thatthe tweets selected were posted from 10am to 12pm
# 	def test_join(self):
# 		#test that the selected screen names and user ids are the same.
# 	def test_movie_dicts(self):
# 		#test that you can initialize a Movie instance with a dictionary.
# if __name__ == "__main__":
# 	unittest.main(verbosity=2)