# encoding: utf-8

require 'cinch'
require 'mechanize'
require "./models"
require 'nokogiri'
require 'open-uri'
require 'json'
require 'rufus/scheduler'
require 'twitter'
require 'bunny'
require 'time'

require './plugins/status'
require './plugins/motd'
require './plugins/twitter'

begin
  require './config'
rescue Exception
  $stderr.puts "Missing config.rb !"
  exit 1
end

#First channel has authority on topic change, !open/!close/!status
CHANNELS_PROD = ['#urlab']
CHANNELS_DEV  = ['#titoufaitdestests']
CHANNELS = PRODUCTION ? CHANNELS_PROD : CHANNELS_DEV

WIKI_CHANGES_URL = URI.parse "http://wiki.urlab.be/Special:RecentChanges?hideminor=1"

MUSIC_PROVIDERS = [
  'soundcloud.com', 
  'youtube.com', 'www.youtube.com', 'youtu.be'
]

GIT_VERSION = `git log | head -1`.split(' ').pop

lechbot = Cinch::Bot.new do
  Nick = PRODUCTION ? "LechBot" : "DechBot"
  
  configure do |conf|
    conf.server = "irc.freenode.org"
    conf.channels = CHANNELS
    conf.nick = Nick
    conf.realname = Nick
    config.plugins.plugins = [StatusBot, MotdBot, TwitterBot]
    @last_motd = nil

    conf.plugins.options[TwitterBot] = {
      consumer_key: TWITTER_CONSUMER_KEY,
      consumer_secret: TWITTER_CONSUMER_SECRET,
      oauth_token: TWITTER_OAUTH_TOKEN,
      oauth_token_secret: TWITTER_OAUTH_SECRET 
    }

    conf.plugins.options[MotdBot] = {
      motd_wiki_url: URLAB_WIKI_MOTDURL
    }

    conf.plugins.options[StatusBot] = {
      status_get_url: STATUS_GET_URL,
      status_change_url: STATUS_CHANGE_URL,
      pamela_url: PAMELA_URL
    }
  end
    
  #Explain the meaning of Lechbot's life
  on :message, /^\!lechbot$/ do |msg|
    msg.reply "Salut, je suis #{Nick} ! Je tiens la page #{URLAB_WIKI_MOTDURL} à jour."
    msg.reply "Je m'occupe aussi d'ouvrir/fermer UrLab grâce à vos !open et !close."
    msg.reply "Je vous tiens informé des modifications sur le Wiki, et si vous me donnez une URL Twitter, je vous affiche le tweet correspondant."
    msg.reply "Enfin, grâce à mon ami HAL, je vous informe de tout mouvement au space."
    msg.reply "Si je deviens trop encombrant, tuez-moi avec `tg #{Nick}`"
  end
  
  on :message, /^\!version$/ do |msg|
    prefix = PRODUCTION ? "https://github.com/titouanc/lechbot/tree/" : ""
    msg.reply prefix+GIT_VERSION
  end

  #KTFB (Kill This Fuckin' Bot)
  on :message, /^tg #{Nick}/i do |msg|
    event_of_the_day = `egrep -h "$(date +"%m/%d|%b* %d")" /usr/share/calendar/* | cut -f 2`
    bot.quit event_of_the_day.split(/\n/).shuffle.pop
  end

  #Cool stuff
  on :action, /^slaps #{Nick}/ do |msg|
    msg.reply "Oh oui, encoooore !"
  end
end


### CRONs ###
now = Time.now
wed = Time.new now.year, now.month, now.day, 20   #Today 20h
wed += 86400 until wed.wednesday? && wed>Time.now #Next wednesday, 20h

scheduler = Rufus::Scheduler.new
scheduler.every '1w', first_at:wed do
  pamela_data = JSON.parse open("http://pamela.urlab.be/mac.json").read
  people = pamela_data['color'] + pamela_data['grey']
  
  unless people.empty?
    randomly_chosen = people.shuffle.first 
    lechbot.channels.first.send "Salut #{randomly_chosen} ! Tu pourrais vider la poubelle s'il-te-plaît ?"
  end
end

scheduler.every '1m' do 
  puts "START FINDING CHANGES ON WIKI"
  page = Nokogiri::HTML open(WIKI_CHANGES_URL.to_s).read
  difflinks = page.css '#mw-content-text .special a[tabindex]'
  changed = []

  difflinks.each do |link|
    if link.text == "diff"
      href = URI.parse "#{WIKI_CHANGES_URL.scheme}://#{WIKI_CHANGES_URL.host}#{link.attr 'href'}"
      if href.query =~ /diff=(\d+)/ && ! Wikichange.get($1)
        diff_id = $1
        page_name = href.query.gsub /.*title=([^&]+).*/, '\1'
        if page_name != 'MusicOfTheDay'
          changed << Wikichange.create(id:diff_id, url:href, name:page_name)
        end
      end
    end
  end
  
  changed.each do |ch|
    lechbot.channels.first.send ch.to_s
  end
  puts "FOUND #{changed.length} changes. Goodbye"
end
### ###

### Events ###
begin
  amq_conn = Bunny.new AMQ_SERVER
  amq_conn.start
  chan = amq_conn.create_channel
  queue = chan.queue EVENTS_QUEUE
  queue.subscribe do |delivery_info, metadata, payload|
    begin
      data = JSON.parse payload
      if data.key?('trigger') && data.key?('time')
        msgtime = Time.parse data['time']
        if Time.now - msgtime < 120 #Ignore messages older than 2mins
          case data['trigger']
          when 'door'
            lechbot.channels.first.send "La porte des escaliers s'ouvre..."
          when 'bell'
            lechbot.channels.first.send "On sonne à la porte !"
          when 'radiator'
            lechbot.channels.first.send "Le radiateur est allumé"
          end
        end
      end
    rescue
      
    end
  end
rescue Bunny::TCPConnectionFailed
  puts "\033[31mUnable to connect to RabbitMQ server. No events for this instance !\033[0m"
end
### ###

lechbot.start
