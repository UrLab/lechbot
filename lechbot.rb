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

class Time
  def same_day? other
    day == other.day && month == other.month && year == other.year
  end
end

URLAB_WIKI_MOTDURL  = "http://wiki.urlab.be/#{PRODUCTION ? 'MusicOfTheDay' : 'User:TitouBot'}"
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
    @last_motd = nil

    Twitter.configure do |config|
      config.consumer_key = TWITTER_CONSUMER_KEY
      config.consumer_secret = TWITTER_CONSUMER_SECRET
      config.oauth_token = TWITTER_OAUTH_TOKEN
      config.oauth_token_secret = TWITTER_OAUTH_SECRET
    end
  end
  
  helpers do
    def addMusic url, senderName, chanName
      chan = Chan.first name:chanName
      chan = Chan.create name:chanName unless chan
      Music.create url:url, sender:senderName, chan:chan
    end
  end
  
  #Track topic change on primary channel
  on :topic do |m|
    return unless m.channel.name == CHANNELS.first
    
    if not m.message =~ /^\s*(https?:\/\/[^\s]+)/
      #Say that we didn't find any url
      m.reply "Hey, tu viens de changer le MotD, mais il n'y avait pas d'URL au début =/"
    elsif @last_motd && @last_motd.same_day?(Time.now)
      m.reply "Le MotD a déjà été changé aujourd'hui !"
    else
      url = URI.parse $1
      if MUSIC_PROVIDERS.include? url.host
        addMusic url, m.user.name, m.channel.name
      end
      
      #Build a new browser
      agent = Mechanize.new do |ag|
        ag.follow_meta_refresh = true
      end
      
      #Go to homepage
      wiki_URI = URI.parse URLAB_WIKI_MOTDURL
      homepage = agent.get "http://#{wiki_URI.host}/"
      loginpage = agent.click homepage.link_with(:text => /log in/i)
      loggedhome = loginpage.form_with(:name => 'userlogin'){|form|
        form.wpName  = URLAB_WIKI_USERNAME
        form.wpPassword = URLAB_WIKI_PASSWORD
      }.submit
      
      #We're now logged in
      
      mypage = agent.get URLAB_WIKI_MOTDURL
      editpage = agent.click mypage.link_with(:text => /edit/i)
      #We have the edit page
      donepage = editpage.form_with(:name => 'editform'){|form|
        pubtime = Time.now.strftime "%d/%m/%Y a %H:%M"
        #Adding an entry (new music)
        form.wpTextbox1 = form.wpTextbox1 + "\n*#{m.user} #{url} (#{pubtime})"
      }.submit
      
      #Say something on the chan
      m.reply "Page #{URLAB_WIKI_MOTDURL} mise à jour avec #{url} de #{m.user} !"
      @last_motd = Time.now
    end
  end
  
  #Post Tweet when a Twitter URL pass by
  on :message,/(https?:\/\/(mobile\.)?twitter\.com\/[^\/]+(\/status\/\d+)?)/ do |msg, url|
      page = Nokogiri::HTML open(url.gsub(/:\/\/mobile\./, '://'))
      tweet = page.css('.tweet').first
      user = tweet.css('.fullname').first.text
      text = tweet.css('.tweet-text').first.text
      msg.reply "@#{user}: «#{text}»"
  end
  
  #Explain the meaning of Lechbot's life
  on :message, /^\!lechbot$/ do |msg|
    msg.reply "Salut, je suis #{Nick} ! Je tiens la page #{URLAB_WIKI_MOTDURL} à jour."
    msg.reply "Je m'occupe aussi d'ouvrir/fermer UrLab grâce à vos !open et !close."
    msg.reply "Je vous tiens informé des modifications sur le Wiki, et si vous me donnez une URL Twitter, je vous affiche le tweet correspondant."
    msg.reply "Enfin, grâce à mon ami HAL, je vous informe de tout mouvement au space."
    msg.reply "Si je deviens trop encombrant, tuez-moi avec `tg #{Nick}`"
  end
  
  #Reply to !status
  on :message, /^\!status/ do |msg|
    if msg.channel == CHANNELS.first
      response = JSON.parse open("http://api.urlab.be/spaceapi/status").read
      since = (response.key? 'since') ? "depuis #{Time.at(response['since']).strftime('%d/%m/%Y %H:%M')}" : ''
      if response['state'] == "closed"
        msg.reply "Le hackerspace est fermé #{since} /o\\"
      else
        pamela_data = JSON.parse open("http://pamela.urlab.be/mac.json").read
        people = pamela_data['color'].length + pamela_data['grey'].length
        msg.reply "Le hackerspace est ouvert #{since}, et il y a en ce moment #{people} personnes \\o/"
      end
    end
  end

  on :message, /^\!version$/ do |msg|
    prefix = PRODUCTION ? "https://github.com/titouanc/lechbot/commit/" : ""
    msg.reply prefix+GIT_VERSION
  end

  #!open & !close
  on :message, /^\!(open|close)/ do |msg, status|
    if msg.channel == CHANNELS.first
      baseurl = PRODUCTION ? "http://api.urlab.be/spaceapi/statuschange" : ""
      begin
        response = open("#{baseurl}?status=#{status}")
        if status == "open"
          msg.reply "Le hackerspace est ouvert. PONEYZ EVERYWHERE <3"
        else
          msg.reply "Le hackerspace est fermé. N'oubliez pas d'éteindre les lumières et le radiateur !"
        end
      rescue Exception => e
        suffix = "(As-tu attendu 5min depuis le dernier changement de statut ?)"
        msg.reply "Erreur d'accès à SpaceAPI: #{e} !!! #{suffix if PRODUCTION}"
      end
    end
  end

  #KTFB (Kill This Fuckin' Bot)
  on :message, /^tg #{Nick}/i do |msg|
    event_of_the_day = `egrep -h "$(date +"%m/%d|%b* %d")" /usr/share/calendar/* | cut -f 2`
    bot.quit event_of_the_day.split(/\n/).shuffle.pop
  end

  #Twitter
  on :message, /^\!twitter (.*)/ do |msg, tweet|
    Twitter.update(tweet)
    msg.reply "Pinky Pinky"
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
### ###

lechbot.start
