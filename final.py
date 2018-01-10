import got
import codecs
from tweepy import *
from nltk.tokenize import word_tokenize
from datetime import datetime


geo = {}
location = {}

def readFile(filename):
	query_list = []
	with open(filename) as f:
		for line in f:
			query_list.append(line.rstrip())
	return query_list

def exportToCsv(filename, tweets):
	outputFile = codecs.open(filename, "w+", "utf-8")
	outputFile.write('username;date;retweets;favorites;text;tokens;geo;location;mentions;hashtags;id;query;permalink;grade')

	for tweet in tweets:
		outputFile.write(('\n%s;%s;%d;%d;"%s";%s;%s;%s;%s;%s;"%s";%s;%s;%s' % (tweet.username, tweet.date.strftime("%Y-%m-%d %H:%M"), tweet.retweets, tweet.favorites, tweet.text, tweet.tokens, tweet.geo, tweet.location, tweet.mentions, tweet.hashtags, tweet.id, tweet.query, tweet.permalink, tweet.grade)))

def initTweepy():
	
	consumer_key="Z3HVUfUQcMuKGJvOd1reDAky9"
	consumer_secret="Tob0xWhFbEUOfHFHEInvuyY9uanHxJLhsM3DGgqUWj8TMFVseu"
	
	access_token="933020656899383296-UT4LiGh0nsmzTYH9uJpRLkwBJFU8Ie8"
	access_token_secret="oaBZymtnE9Mju232evbxdnZETA5zRBD43OgFj0CqrSUhn"

	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)

	return API(auth)

def getGeo(tweepy, id):
	tweet = tweepy.get_status(id)
	if tweet._json:
		if "geo" in tweet._json:
			if tweet._json["geo"] != None:
				return tweet._json["geo"]["coordinates"]
			else:
				return ""
		else:
			return ""
	else:
		return ""

def buildGeoDictionary(statuses):
	for status in statuses:
		json = status._json
		user = status.user
		
		if user.location:
			location.update({status.id_str : user.location})
		if 'geo' in json:
			if json['geo']:
				geo.update({status.id_str : json['geo']['coordinates']})

def getGeoBulk(tweets, tweepy):
	bulk = []
	for tweet in tweets:
		if len(bulk) == 100:
			statuses = tweepy.statuses_lookup(bulk)
			buildGeoDictionary(statuses)
			bulk = []
		bulk.append(tweet.id)

	tweets2 = []
	for tweet in tweets:
		aux = tweet
		if tweet.id in geo:
			aux.geo = geo[tweet.id]

		if tweet.id in location:
			aux.location = location[tweet.id]
		else:
			aux.location = ""
		tweets2.append(aux)

	return tweets2


if __name__ == '__main__':
	tweepy = initTweepy()
	tweetCriteria = got.manager.TweetCriteria()
	
	words = readFile("words.txt")
	dates = readFile("date.txt")
	disruptions = readFile("disruption_grade.csv")

	tweets2 = []
	disr = {}
	for d in disruptions:
		d1 = d.split(' ')
		disr[d1[0]] = d1[3]

	for date in dates:
		print("DATES: " + date)
		dt = date.split(' ')
		tweetCriteria.setSince(dt[0]).setUntil(dt[1])

		for word in words:
			print("WORD: " + word)
			tweetCriteria.setQuerySearch(word)
			tweets = got.manager.TweetManager.getTweets(tweetCriteria)

			for tweet in tweets:
				if tweet.id.isdigit():
					aux = tweet
					# aux.geo = getGeo(tweepy, tweet.id)
					aux.query = word
					aux.text = tweet.text.replace(';', '').replace('\\', '')
					aux.tokens = [ x.encode('utf-8') for x in word_tokenize(aux.text)]
					aux.grade = disr[str(tweet.date.date())]
					tweets2.append(aux)

			print(str(len(tweets2)))

	filtered_tweets = dict((x.id, x) for x in tweets2).values()
	print("BEFORE: " + str(len(tweets2)) + "\nAfter: " + str(len(filtered_tweets)))

	finalTweets = getGeoBulk(filtered_tweets, tweepy)

	exportToCsv("tweets.csv", finalTweets)


		#tweet = got.manager.TweetManager.getTweets(tweetCriteria)[0]

	#print(tweet.username)