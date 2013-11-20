# LechBot
cinch-based IRC bot for #urlab on freenode

## Dependencies
 
* Ruby (`ruby` command), Rubygems (`gem` command)
* RabbitMQ (for hackerspace events) (`rabbitmq-server` service)
* Bundler gem (`gem install bundler`)

## Setup
	
	$ bundle install [--without development]
	$ cp config.rb.example config.rb

Then edit config.rb with correct values.

## Running this bot

	$ bundle exec ruby lechbot.rb

You may also need to run the development http server:

	$ bundle exec ruby devserver.rb

