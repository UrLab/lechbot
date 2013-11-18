# encoding: utf-8

require 'cinch'
require 'rufus/scheduler'
require 'open-uri'
require 'json'

class JanitorBot
	include Cinch::Plugin

	listen_to :connect, :method => :start

	def start *args
		now = Time.now
		wed = Time.new now.year, now.month, now.day, 20   #Today 20h
		wed += 86400 until wed.wednesday? && wed>Time.now #Next wednesday, 20h

		@scheduler = Rufus::Scheduler.new
		bot.debug "Created scheduler"

		@scheduler.every '1w', first_at:wed do
			pamela_data = JSON.parse open(config[:pamela_url]).read
			people = pamela_data['color'] + pamela_data['grey']
			unless people.empty?
				randomly_chosen = people.shuffle.first 
				bot.channels.first.send "Salut #{randomly_chosen} ! Tu pourrais vider la poubelle s'il-te-plaît ?"
			end
		end
	end
end
