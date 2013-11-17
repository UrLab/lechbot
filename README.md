# LechBot
cinch-based IRC bot for #urlab on freenode

## Dependencies
 
* Ruby
* RabbitMQ (for hackerspace events)

## Setup

	$ bundle install [--without development]
	$ cp config.rb.example config.rb

Then edit config.rb with correct values.

## Running this bot

	$ bundle exec ruby lechbot.rb

You may also need to run the development http server:

	$ bundle exec ruby devserver.rb

