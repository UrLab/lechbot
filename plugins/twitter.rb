# encoding: utf-8

require 'cinch'
require 'twitter'
require 'nokogiri'

class TwitterBot
	include Cinch::Plugin

	TWITTER_URL = /.*https?:\/\/(mobile\.)?twitter\.com\/[^\/]+\/status\/(\d+)?/

	listen_to :connect, :method => :configureTwitter
	def configureTwitter msg
		Twitter.configure do |conf|
      		conf.consumer_key = (config[:consumer_key] || raise(ArgumentError, "Missing Twitter consumer key"))
      		conf.consumer_secret = (config[:consumer_secret] || raise(ArgumentError, "Missing Twitter consumer secret"))
      		conf.oauth_token = (config[:oauth_token] || raise(ArgumentError, "Missing Twitter OAuth token"))
      		conf.oauth_token_secret = (config[:oauth_token_secret] || raise(ArgumentError, "Missing Twitter OAuth token secret"))
    	end
    	bot.info "Twitter configured (#{config[:consumer_key]}) !"
	end

	def url2tweetid url
		$2.to_i if url =~ TWITTER_URL
	end

	def protectTwitter msg
		begin
			yield
		rescue Twitter::Error::AlreadyRetweeted
			msg.reply "Déjà retweeté"
		rescue Twitter::Error::Unauthorized, Twitter::Error::Forbidden
			msg.reply "Non-autorisé"
		rescue Twitter::Error::NotFound
			msg.reply "Tweet introuvable..."
		end
	end

	match TWITTER_URL, :method => :showTweet, :prefix => //
	def showTweet msg
		tweet = Twitter.status(url2tweetid msg.message)
		msg.reply "@#{tweet.from_user}: « #{tweet.text} »"
	end

	match /twitter\s(.+)/, :method => :postTweet
	def postTweet msg, text
		text.strip!
		debug text
		if text.empty? 
			msg.reply "Pas grand chose à dire..."
		else
			protectTwitter msg do
				Twitter.update(text)
				msg.reply "Pinky Pinky !"
			end
		end
	end

	match /retweet\s+#{TWITTER_URL}/, :method => :reTweet
	def reTweet msg
		protectTwitter msg do 
			tweet = Twitter.retweet(url2tweetid msg.message)
			msg.reply "Bowel Bowel !"
		end
	end
end
