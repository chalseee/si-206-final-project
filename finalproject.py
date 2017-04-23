import tweepy
import twitter_info
import json
import sqlite3
import omdb
import itertools
import unittest
import collections

consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
tweepy_api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

	#create a list of strings of movie titles called 'movies'.
movies = ['candyman', 'vampire in brooklyn', "the preacher's son", 'sister code', 'november rule', 'boy bye', 'hurricane bianca', 'a weekend for the family', 'queen of katwe', 'the book of eli', 'i am not your negro', 'black november', 'the sin seer', 'go tell it on the mountain', 'vampire academy', 'selma', 'keanu', 'son of ingagi', 'blacula', 'dreamgirls','get out', 'boomerang', 'hidden figures', 'the wiz', 'black dynamite', 'white chicks', 'akeelah and the bee', 'glory', 'a raisin in the sun']
	#create a string of a keyword named 'tweepy_keyword' to use to gather Twitter data to use for later.
tweepy_keyword = '@sirdancealot56'





#PART 0: SETUP

	# Create your caching setup to cache data later on.
CACHE_FNAME = "206_final_project_cache.json"
try:
	cache_file = open(CACHE_FNAME,'r')
	cache_contents = cache_file.read()
	cache_file.close()
	CACHE_DICTION = json.loads(cache_contents)
except:
	CACHE_DICTION = {}

#Implement 3 classes:
# 1. Implement a Movie class that will hold all of the information for a movie from omdb for later use in the program. 
	# It should contain these member variables:
	# - imdb movie id -- this column in the PRIMARY KEY
	# - movie title
	# - advisory rating (string -- 'PG', 'R', 'PG-13', etc.)
	# - year released (integer of a year)
	# - studio (the production studio that made the movie, which is a string)
class Movie:
	def __init__(self, imdb_id, title, advisory_rating, year_released, studio):
		self.imdb_id = imdb_id
		self.title = title
		self.advisory_rating = advisory_rating
		self.year_released = year_released
		self.studio = studio

	# a. Implement a __str__ method that outputs information about the class in the form of a string of this format:
		#  *movie*, id: *imdb_id*, was made by *studio*, rated *advisory_rataing* by IMDB in *year*.
	def __str__(self):
		return '{}, id: {}, was made by {}, rated {} by IMDB in {}'.format(self.title, self.imdb_id, self.studio, self.advisory_rating, self.year_released)

	# b. Implement a method that ???  TBD

#2. Implement a Tweet class that will hold all of the information for a tweet for later use in the program. 
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

#3. Implement a User class that will hold all of the information for a user for later use in the program. 
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




#PART 1: METHODS

#  1. Define a function called request_movies that accepts a list of strings containing movie titles and returns a list of Movie class instances
	# and cache this data in the CACHE_DICTION under the key 'omdb_movies_requests'
def request_movies(movies):
	if 'omdb_movies_requests' not in CACHE_DICTION:
		CACHE_DICTION['omdb_movies_requests'] = [json.loads(omdb.request(t=m).text) for m in movies]
		f = open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()
	return [Movie(c['imdbID'], c['Title'], c['Rated'], c['Year'], c['Production']) for c in CACHE_DICTION['omdb_movies_requests'] if c['Response'] == 'True']

#  2. Define a function called get_user_tweets that gets at least 20 Tweets from a 
	# 	specific Twitter user's timeline, and uses caching. The function should 
	# 	return a Python object representing the data that was retrieved from Twitter. 
def get_user_tweets(user_handle):
	if user_handle not in CACHE_DICTION:
		CACHE_DICTION[user_handle] = tweepy_api.user_timeline(id = user_handle, include_rts = True, count = 50)

		f = open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()
	return CACHE_DICTION[user_handle]

#  3. Define a function called get_tweets that accepts a list of tweet dictionaries and returns a list of Tweet class instances
def get_tweets(user_tweets):
	return [Tweet(t['id_str'], t['text'], t['user']['id'], t['user']['created_at'], t['retweet_count']) for t in user_tweets]

#  4. Define a function called get_neighborhood that accepts a list of tweets and returns a list 
	# of user instances composed of every user who was ever mentioned within the list of tweets as well as all users who wrote the original tweets
	# and cache this data in the CACHE_DICTION under the keyword *search term*_user_neighborhood
def get_neighborhood(user_tweets):
	if (tweepy_keyword + 'user_neighborhood') not in CACHE_DICTION:
		CACHE_DICTION[tweepy_keyword + '_user_neighborhood'] = []
		for u in user_tweets:
			user = tweepy_api.get_user(u['user']['id'])
			CACHE_DICTION[tweepy_keyword + '_user_neighborhood'].append(user) #duplicates??
			for m in u['entities']['user_mentions']:
				neighbor = tweepy_api.get_user(m['screen_name'])
				CACHE_DICTION[tweepy_keyword + '_user_neighborhood'].append(neighbor)		
		f = open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()
	return [User(c['id_str'], c['screen_name'], c['favourites_count'], c['description']) for c in CACHE_DICTION[tweepy_keyword + '_user_neighborhood']]




#PART 2: DATABASE QUERIES
# Using the functions you created in Part 2 of the project, use the 'movies' list of strings and the tweepy_keyword to create your tables.
# Then, using each class you created, input the class instances into the three tables.
conn = sqlite3.connect('finalproject.db')
cur = conn.cursor()

	#1. Create Movies table and commit its data to the database
statement = 'CREATE TABLE IF NOT EXISTS Movies (imdb_id TEXT PRIMARY KEY, title TEXT, advisory_rating TEXT, year_released INTEGER, studio TEXT)'
cur.execute(statement)
user_tweets = get_user_tweets(tweepy_keyword)
results = request_movies(movies)

for r in results:
	statement = 'INSERT OR IGNORE INTO Movies Values (?,?,?,?,?)'
	data = (r.imdb_id, r.title, r.advisory_rating, r.year_released, r.studio)
	cur.execute(statement, data)

	#2. Create Tweets table and commit its data to the database
statement = 'CREATE TABLE IF NOT EXISTS Tweets (tweet_id TEXT PRIMARY KEY, text TEXT, user_id TEXT, time_posted TIMESTAMP, retweets INTEGER)'
cur.execute(statement)
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

#MAKE QUERIES TO THE DATABASE and save them in different variables.
	# 1.Select the user that has the most favorites. Save this in a variable called max_user_favs
statement = 'SELECT * FROM Users WHERE num_favs = (SELECT max(num_favs) FROM Users)'
cur.execute(statement)
max_user_favs = cur.fetchone()

	# 2. Use an inner join 

	# 3. Select all advisory ratings and studios for the movies.
		# Find the most common advisory rating and save it in most_common_rating
		# In the case of a tie, go with the rating that comes first alphabetically
statement = 'SELECT advisory_rating FROM Movies'
cur.execute(statement)
movies_info = [c[0] for c in cur.fetchall()]
counter = collections.Counter(movies_info)
most_common_rating = sorted(counter.most_common(1))[0][0]

#close the database connection
conn.close()




#PART 3: .TXT OUTPUT
#Create an output file (.txt) containing the Users, Tweets, and Movies tables.
#The file should also contain a number of statistics:
	# - average imdb movie rating
	# - most commonly occuring movie rating ('R', 'PG', etc.)
	# - average movie release date
	# - user with the highest number of favorites
	# - tweet with the highest number of retweets




# #PART 4: TEST SUITE
# #Create 8 tests cases for your code above.
# class Tests(unittest.TestCase):
# 	def test_request_movies_one(self):
# 		#test that request_movies() returns a list.
# 		test_movies_one = request_movies(['candyman', 'candyman', 'x'])
# 		self.assertEqual(type(test_movies_one), type([]))
	
# 	def test_request_movies_two(self):
# 		#test that request_movies() returns a list of movie objects.
# 		test_movie_one = request_movies(['candyman', 'candyman', 'x'])
# 		self.assertEqual(type(test_movie_one[0]), type(Movie('d', 7, '2007', 'sf')))

# 	def test_get_tweets(self):
# 		#test that get_tweets() returns a list of tweets objects.
# 		t = get_tweets(get_user_tweets('@sirdancealot56'))
# 		self.assertEqual(type(t[0]), type(Tweet('2323', '3434', '2332', '2332', '3434')))
	
# 	def test_movies(self):
# 		#test that my movies table has five columns
# 		conn = sqlite3.connect('finalproject.db')
# 		cur = conn.cursor()
# 		cur.execute('SELECT * FROM Movies')
# 		result = cur.fetchall()
# 		self.assertTrue(len(result[1]) == 5)
# 		conn.close()
	
# 	def test_tweets(self):
# 		#test that the tweets table has five columns
# 		conn = sqlite3.connect('finalproject.db')
# 		cur = conn.cursor()
# 		cur.execute('SELECT * FROM Tweets')
# 		result = cur.fetchall()
# 		self.assertTrue(len(result[1]) == 5)
# 		conn.close()

# 	def test_users(self):
# 		#test that the users table has four columns
# 		conn = sqlite3.connect('finalproject.db')
# 		cur = conn.cursor()
# 		cur.execute('SELECT * FROM Users')
# 		result = cur.fetchall()
# 		self.assertTrue(len(result[1]) == 4)
# 		conn.close()

# 	def test_movie_dicts(self):
# 		#test that there are are at least 2 distinct movies in the Movies table
# 		conn = sqlite3.connect('finalproject.db')
# 		cur = conn.cursor()
# 		cur.execute('SELECT * FROM Movies')
# 		result = cur.fetchall()
# 		self.assertTrue(len(result) >= 2)
# 		conn.close()

# 	def test_get_user_tweets(self):
# 		fstr = open('finalproject.json', 'r').read()
# 		self.assertTrue('@sirdancealot56' in fstr)

# if __name__ == "__main__":
# 	unittest.main(verbosity=2)



