import got
import codecs
from tweepy import *

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
	outputFile.write('username;date;retweets;favorites;text;geo;mentions;hashtags;id;query;permalink')

	for tweet in tweets:
		outputFile.write(('\n%s;%s;%d;%d;"%s";%s;%s;%s;"%s";%s;%s' % (tweet.username, tweet.date.strftime("%Y-%m-%d %H:%M"), tweet.retweets, tweet.favorites, tweet.text, tweet.geo, tweet.mentions, tweet.hashtags, tweet.id, tweet.query, tweet.permalink)))

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
			print("LOCATION:" + user.location)
			location.update({status.id : user.location})
		if 'geo' in json:
			if json['geo']:
				print("GEO:" + json["geo"]["coordinates"])
				geo.update({status.id : json['geo']['coordinates']})

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
	words = readFile("words.txt")
	#print(words)

	tweetCriteria = got.manager.TweetCriteria()
	tweetCriteria.setSince("2017-12-07").setUntil("2017-12-08")

	tweets2 = []
	for word in words:
		print("WORD: " + word)
		tweetCriteria.setQuerySearch(word)
		tweets = got.manager.TweetManager.getTweets(tweetCriteria)

		for tweet in tweets:
			if tweet.id.isdigit():
				aux = tweet
				# aux.geo = getGeo(tweepy, tweet.id)
				aux.query = word
				tweets2.append(aux)

		print(str(len(tweets2)))

	finalTweets = getGeoBulk(tweets2, tweepy)

	exportToCsv("tweets.csv", finalTweets)


		#tweet = got.manager.TweetManager.getTweets(tweetCriteria)[0]

	#print(tweet.username)