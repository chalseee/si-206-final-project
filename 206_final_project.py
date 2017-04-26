import tweepy
import twitter_info
import json
import sqlite3
import omdb
import unittest
from collections import Counter
import time

consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
tweepy_api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

	#create a list of strings of movie titles called 'movies'.
movies = ['vampire in brooklyn', 'queen of katwe', 'the book of eli']
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
		# • imdb_id: IMDB movie ID
		# •	title: movie title
		# •	imdb_rating: IMDB rating
		# •	year_released: year released in theatres 
		# •	studio: production studio
		# •	actors: top-billed actors
class Movie:
	def __init__(self, imdb_id, title, imdb_rating, year_released, studio, actors):
		self.imdb_id = imdb_id
		self.title = title
		self.imdb_rating = imdb_rating
		self.year_released = year_released
		self.studio = studio
		self.actors = actors

	# a. Implement a __str__ method that outputs information about the class in the form of a string of this format:
		#  *movie*, id: *imdb_id*, was made by *studio*, rated *imdb_rating* by IMDB in *year*.
	def __str__(self):
		return '{} was produced by {} in {}. It has a rating of {} on IMDB.'.format((self.title).title(), self.studio, self.year_released, self.imdb_rating)

	# b. Implement a method that outputs a sentence-long string summary of the number of actors and top-billed actors in the move in this format:
		# It contains *number of top actors* major actors - *names of actors*
	def actor_summary(self):
		return ('It contains ' + str(len(self.actors.split(','))) + ' major actors - {}').format(self.actors)

#2. Implement a Tweet class that will hold all of the information for a tweet for later use in the program. 
	# It should contain these member variables:
	# •	movie: associated movie search term (movie title)
	# •	tweet_id: tweet’s ID
	# •	text: the text of the tweet
	# •	user_id: tweet poster’s ID
	# •	retweets: retweets received by tweet
class Tweet:
	def __init__(self, movie, tweet_id, text, user_id, retweets):
		self.movie = movie
		self.tweet_id = tweet_id
		self.text = text
		self.user_id = user_id
		self.retweets = retweets

#3. Implement a User class that will hold all of the information for a user for later use in the program. 
	# It should contain these member variables:
		# •	user_id: user’s ID
		# •	screen_name: user’s screen name
		# •	num_favs: number of item’s a user has ever favorited
		# •	description: user bio (or description)
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
	return [Movie(c['imdbID'], c['Title'].lower(), c['imdbRating'], c['Year'], c['Production'], c['Actors']) for c in CACHE_DICTION['omdb_movies_requests'] if c['Response'] == 'True']

#  2. Define a function called get_user_tweets that gets at least 10 Tweets from a twitter search on a movie term, and uses caching. The function should 
	# 	return a list of dictionaries of the data that was retrieved from Twitter. 
def cache_tweets(movies):
	for m in movies:
		if (m + '_tweets') not in CACHE_DICTION:
			CACHE_DICTION[m + '_tweets'] = (tweepy_api.search(q=m)['statuses'])[:15]
			f = open(CACHE_FNAME, 'w')
			f.write(json.dumps(CACHE_DICTION))
			f.close()

#  3. Define a function called get_tweets that accepts a list of tweet dictionaries and returns a list of Tweet class instances.
def get_tweets(movies):
	all_tweets = []
	for m in movies:
		for c in CACHE_DICTION[m + '_tweets']:
			all_tweets.append(Tweet(m, c['id_str'], c['text'], c['user']['id'], c['retweet_count']))
	return all_tweets

#  4. Define a function called get_neighborhood that accepts a list of tweets dictionaries and returns a list 
	# of User instances composed of every user who was ever mentioned within the list of tweets as well as all users who wrote the original tweets
	# and cache this data in the CACHE_DICTION under the keyword user_neighborhood
def get_neighborhood(movies):
	if 'user_neighborhood' not in CACHE_DICTION:
		CACHE_DICTION['user_neighborhood'] = []
		for m in movies:
			for u in CACHE_DICTION[m + '_tweets']:
				user = tweepy_api.get_user(u['user']['id'])
				CACHE_DICTION['user_neighborhood'].append(user) #duplicates??
				
				for m in u['entities']['user_mentions']:
					neighbor = tweepy_api.get_user(m['screen_name'])
					CACHE_DICTION['user_neighborhood'].append(neighbor)		
		f = open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()
	return [User(c['id_str'], c['screen_name'], c['favourites_count'], c['description']) for c in CACHE_DICTION['user_neighborhood']]





#PART 2: DATABASE QUERIES
# Using the functions you created in Part 2 of the project, use the 'movies' list of strings and the tweepy_keyword to create your tables.
# Then, using each class you created, input the class instances into the three tables.
conn = sqlite3.connect('206_final_project_database.db')
cur = conn.cursor()

	#1. Create Movies table and commit its data to the database
statement = 'CREATE TABLE IF NOT EXISTS Movies (imdb_id TEXT PRIMARY KEY, title TEXT, imdb_rating INTEGER, year_released INTEGER, studio TEXT, actors TEXT)'
cur.execute(statement)
movie_results = request_movies(movies)
for m in movie_results:
	statement = 'INSERT OR IGNORE INTO Movies Values (?,?,?,?,?,?)'
	data = (m.imdb_id, m.title, m.imdb_rating, m.year_released, m.studio, m.actors)
	cur.execute(statement, data)

	#2. Create Tweets table and commit its data to the database
statement = 'CREATE TABLE IF NOT EXISTS Tweets (tweet_id TEXT PRIMARY KEY, movie TEXT, text TEXT, user_id TEXT, retweets INTEGER)'
cur.execute(statement)
cache_tweets(movies)
tweets = get_tweets(movies)
for t in tweets:
	statement = 'INSERT OR IGNORE INTO Tweets Values (?,?,?,?,?)'
	data = (t.tweet_id, t.movie, t.text, t.user_id, t.retweets)
	cur.execute(statement, data)

	#3. Create Users table and commit its data to the database
statement = 'CREATE TABLE IF NOT EXISTS Users (user_id TEXT PRIMARY KEY, screen_name TEXT, num_favs INTEGER, description TEXT)'
cur.execute(statement)
neighborhood = get_neighborhood(movies)
for n in neighborhood:
	statement = 'INSERT OR IGNORE INTO Users Values (?,?,?,?)'
	data = (n.user_id, n.screen_name, n.num_favs, n.description)
	cur.execute(statement, data)

conn.commit()

#MAKE QUERIES TO THE DATABASE and save them in different variables.
	# 1.Select movie with the highest rating. Save this in a variable called highest_rated_movie
statement = 'SELECT title FROM Movies WHERE imdb_rating = (SELECT max(imdb_rating) FROM Movies)'
cur.execute(statement)
highest_rated_movie = cur.fetchall()[0][0]

	# 2. Select the retweets, title, and text attributes for the tweet with the most retweets. Save it in a variable called most_retweeted.
cur.execute('SELECT DISTINCT retweets, title, text FROM Movies INNER JOIN Tweets ON Tweets.movie=Movies.title AND retweets > 10')
	#a. Sort these results by number of retweets highest to lowest
most_retweeted = sorted(set(cur.fetchall()), key=lambda tup: -tup[0])

	# 3. Select all the Users whose screen names are less than 10 characters long. Save this in a value called user_info. 
cur.execute('SELECT screen_name, num_favs FROM Users WHERE LENGTH(screen_name) < 10')
user_info = cur.fetchall()
	#a. Save the screen names and favorities in screen_names and number_favs, respectively.
screen_names, number_faves = zip(*user_info)
	#b. Save the average number of favorites for users in a variable called average_favs
c = Counter(list(number_faves))
average_favs = sum(c.elements()) / len(number_faves)
	#c. Save the usernames of all users whose screen_names are less than 7 characters long in a variable called less_than_seven
users_less_than_seven = list(filter(lambda x: len(x) < 7, screen_names))

	#4. Select all the Tweets and Users
cur.execute('SELECT * FROM Tweets')
tweets = cur.fetchall()
cur.execute('SELECT * FROM Users')
users = cur.fetchall()
	#a. Save the title, text and retweets in a list of tuples. Call this distinct_tweets.
distinct_tweets = [(d[1].title(), str(d[2].encode('utf-8')), d[4]) for d in tweets]
	#b. Save the screen names, favorites and description in a list of tuples. Call this distinct_users.
distinct_users = [(d[1], str(d[2]), str(d[3].encode('utf-8'))) for d in users]

#close the database connection
conn.close()

#PART 3: .TXT OUTPUT
#Create an output file (.txt) containing the following information about the tables in the database:
# Highest Rated movies
# Most Retweeted Tweet About a Movie
	# Number of times that it was retweeted
# Screen names of users who’s screen names have less than 7 characters
	# The average favorites of these users
#Movie Summary
	#__str__() and movie_summary() methods are output for each movie
#Tweets Summary
	# For each distinct tweet (by primary key) in the database, print the output of the text as
	# well as its number of retweets.
	#For each distinct user (by user id) in the database, print the output of the screen name,
	#number of favorites and Twitter bio.

f = open('206_final_project_output.txt', 'w')
p = ['FINAL PROJECT SI 206 - OMDB & TWEEPY MASHUP - {}\n'.format(time.strftime('%m/%d/%Y'))]
p.append('\n\n\n----- Some Stats About the Database -----\n\nHighest Rated Movie - ' + highest_rated_movie.title() + '\n') 
p.append('\nMost Retweeted Tweet about a Movie - ' + most_retweeted[0][1].title() + ' - Retweeted ' + str(most_retweeted[0][0]) + ' times.\n"' + str(most_retweeted[0][2]) + '"')
p.append(str(len(users_less_than_seven)) + '\n\nTwitter screen names that are less than 7 characters:\n')
for idx, u in enumerate(users_less_than_seven):
	p.append(str(idx + 1) + ' - ' + u + '\n')
p.append("\nThese user's average number of favorites - " + str(average_favs) + '\n               -----')

p.append('\n\n\n\n----- Database Contents: MOVIES, TWEETS, USERS -----\n\nMovies Table Summary: \nThere are ' + str(len(movie_results)) + ' movies in the database. \n')
for idx, m in enumerate(movie_results):
	p.append(str(idx + 1) + ' - ' + m.__str__() + '\n\t' + m.actor_summary() + '\n')

p.append('\n\nTweets Table Summary: \nThere are ' + str(len(distinct_tweets)) + ' tweets in the database.')
for idx, d in enumerate(distinct_tweets):
	if (idx%15 == 0):
		p.append('\n<--- ' + d[0] + ' Tweets ---> \n')
	p.append(str(idx + 1) + ' -' + d[1][1:] + '\n\tRetweets: ' + str(d[2]) + '\n')

p.append('\n\n\nUsers Table Summary: \nThere are ' + str(len(distinct_users)) + ' users in the database. \n')
for idx, d in enumerate(distinct_users):
	p.append(str(idx + 1) + ' - ' + d[0] + ' - ' + d[1] + ' favorites \n\tBio: ' + d[2][1:] + '\n')

for temp in p:
	f.write(temp)
f.close()

# PART 4: TEST SUITE
# Create 2 testcases per function and/or class defined.

class Tests(unittest.TestCase):
#Function Test Cases
	def test_request_movies_one(self):
		#test that request_movies() returns a list.
		test_movies_one = request_movies(['candyman', 'candyman', 'x'])
		self.assertEqual(type(test_movies_one), type([]))
	
	def test_request_movies_two(self):
		#test that request_movies() returns a list of movie objects.
		test_movie_one = request_movies(['candyman', 'candyman', 'x'])
		self.assertEqual(type(test_movie_one[0]), type(Movie('d', 'f' , 6.9 , 'sf', ' j', 'ok')))

	def test_cache_tweets_one(self):
		#test that a movie's tweet dictionary isn't blank, cache_tweets() has written info there
		self.assertTrue(len(CACHE_DICTION[movies[0] + '_tweets']) != 0)

	def test_cache_tweets_two(self):
		#test that the cache stores movie tweets
		fstr = open('206_final_project_cache.json', 'r').read()
		self.assertTrue((movies[0] + '_tweets') in fstr)

	def test_get_tweets_one(self):
		#test that get_tweets returns a list.
		test_users = get_tweets(['queen of katwe', 'the book of eli'])
		self.assertEqual(type(test_users), type([]))

	def test_get_tweets_two(self):
		#test that get_tweets() returns a list of tweets objects.
		t = get_tweets(['queen of katwe'])
		self.assertEqual(type(t[0]), type(Tweet('2323', '3434', '2332', '2332', 3434)))

	def test_get_neighborhood_one(self):
		#test that get_neighborhood() returns a list
		n = get_neighborhood(CACHE_DICTION[movies[2] + '_tweets'])
		self.assertEqual(type(n), type([]))

	def test_get_neighborhood_two(self):
		#test that get_neighborhood() returns a list of user objects
		n = get_neighborhood(CACHE_DICTION[movies[1] + '_tweets'])
		self.assertEqual(type(n[0]), type(User('u', 's', 3, 'r')))

#Class Tests:
	def test_movie_class_one(self):
		#test that a movie class __str__() method works
		m = Movie('12', 'hurricane bianca', 4.3, 2017, 'Paramont', 'some actors, d')
		self.assertEqual(m.__str__(), 'Hurricane Bianca was produced by Paramont in 2017. It has a rating of 4.3 on IMDB.')

	def test_movie_class_two(self):
		#test that variable 'title' is correct
		m = Movie('12', 'hurricane bianca', 4.3, 2017, 'Paramont', 'some actors, d')
		self.assertEqual(m.title, 'hurricane bianca')
	
	def test_tweet_class_one(self):
		#test that variable 'retweets' is an integer
		t = Tweet('cool', '3423', 'okay?', '32432', 45)
		self.assertTrue((type(t.retweets) == int))

	def test_tweet_class_two(self):
		#test that variable 'text' is correct
		t = Tweet('cool', '3423', 'okay?', '32432', 45)
		self.assertEqual(t.text, 'okay?')

	def test_user_class_one(self):
		#test that variable num_favs is an integer
		u = User('438973', 'katwe', 45, 'nope')
		self.assertTrue((type(u.num_favs) == int))

	def test_user_class_two(self):
		#test that variable 'screen_name' is correct
		u = User('438973', 'katwe', 45, 'nope')
		self.assertEqual(u.screen_name, 'katwe')

#OTHER DB Tests:
	def test_movies(self):
		#test that my movies table has five columns
		conn = sqlite3.connect('206_final_project_database.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies')
		result = cur.fetchall()
		self.assertTrue(len(result[1]) == 6)
		conn.close()
	
	def test_tweets(self):
		#test that the tweets table has five columns
		conn = sqlite3.connect('206_final_project_database.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets')
		result = cur.fetchall()
		self.assertTrue(len(result[1]) == 5)
		conn.close()

	def test_users(self):
		#test that the users table has four columns
		conn = sqlite3.connect('206_final_project_database.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users')
		result = cur.fetchall()
		self.assertTrue(len(result[1]) == 4)
		conn.close()

	def test_movie_dicts(self):
		#test that there are are at least 2 distinct movies in the Movies table
		conn = sqlite3.connect('206_final_project_database.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies')
		result = cur.fetchall()
		self.assertTrue(len(result) >= 2)
		conn.close()

if __name__ == "__main__":
	unittest.main(verbosity=2)