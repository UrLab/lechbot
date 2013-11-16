# encoding: utf-8

require 'cinch'
require 'twitter'
require 'nokogiri'

class TwitterBot
	include Cinch::Plugin

	TWITTER_URL = /.*https?:\/\/(mobile\.)?twitter\.com\/[^\/]+\/status\/(\d+)?/

	def url2tweetid url
		$2.to_i if url =~ TWITTER_URL
	end

	match TWITTER_URL, :method => :showTweet, :prefix => //
	def showTweet msg
		debug "Tweet ID: #{url2tweetid msg.message}"
		tweet = Twitter.status(url2tweetid msg)
		msg.reply "@#{tweet.from_user}: «#{tweet.text}»"
	end

	match /twitter\s*(\s!.+)/, :method => :postTweet
	def postTweet msg, text
		Twitter.update(text)
	    msg.reply "Pinky Pinky"
	end

	match /retweet\s+#{TWITTER_URL}/, :method => :reTweet
	def reTweet msg
		begin
			tweet = Twitter.retweet(url2tweetid msg.message)
			msg.reply "Bowel !"
		rescue Twitter::Error::AlreadyRetweeted
			msg.reply "Déjà retweeté"
		rescue Twitter::Error::Unauthorized
			msg.reply "Non-autorisé"
		end
	end
end
