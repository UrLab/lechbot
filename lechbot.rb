# encoding: utf-8

require 'cinch'
require 'mechanize'
require './models'
require 'nokogiri'
require 'open-uri'
require 'json'
require 'rufus/scheduler'

PRODUCTION = true

#First channel has authority on topic change, !open/!close/!status
CHANNELS_PROD = ['#urlab']
CHANNELS_DEV  = ['#titoufaitdestests']
CHANNELS = PRODUCTION ? CHANNELS_PROD : CHANNELS_DEV

begin
  require './config'
rescue Exception
  $stderr.puts "Missing config.rb !"
  exit 1
end

class Time
  def same_day? other
    day == other.day && month == other.month && year == other.year
  end
end

URLAB_WIKI_MOTDURL  = "http://wiki.urlab.be/#{PRODUCTION ? 'MusicOfTheDay' : 'User:TitouBot'}"

MUSIC_PROVIDERS = [
  'soundcloud.com', 
  'youtube.com', 'www.youtube.com', 'youtu.be'
]

lechbot = Cinch::Bot.new do
  Nick = "LechBot"
  
  configure do |conf|
    conf.server = "irc.freenode.org"
    conf.channels = CHANNELS
    conf.nick = Nick
    conf.realname = Nick
    @last_motd = nil
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
      m.reply "Hey ! You changed topic, but I didn't find any URL in its beginning =/"
    elsif @last_motd && @last_motd.same_day?(Time.now)
      m.reply "The MotD has already changed today"
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
      m.reply "Updated #{URLAB_WIKI_MOTDURL} page with #{url} from #{m.user} !"
      @last_motd = Time.now
    end
  end
  
  #When a link to a known music provider is found, add it to the database
  on :message, /(https?:\/\/(#{MUSIC_PROVIDERS*'|'})\/[^\s]+)/ do |msg, url|
    addMusic url, msg.user.name, msg.channel.name
  end

  #Post Tweet when a Twitter URL pass by
  on :message, /(https?:\/\/twitter\.com\/[^\/]+(\/status\/\d+)?)/ do |msg, url|
      page = Nokogiri::HTML open(url)
      tweet = page.css('.tweet').first
      user = tweet.css('.fullname').first.text
      text = tweet.css('.tweet-text').first.text
      msg.reply "@#{user}: «#{text}»"
  end
  
  #Explain the meaning of Lechbot's life
  on :message, /^\!lechbot/ do |msg|
    msg.reply "Hello, I'm LechBot ! I collect musics links passing on this chan and I can give you a random one with `!music [all]`"
    msg.reply "Known music providers are #{MUSIC_PROVIDERS*', '}."
    msg.reply "I get you tweets if I hear about their URL."
    if msg.channel.name == CHANNELS.first
      msg.reply "I'm also maintaining the MotD page (#{URLAB_WIKI_MOTDURL}), and the space status !"
      msg.reply "Finally, each week I pick someone randomly, and tell him to take out the trash."
    end
    msg.reply "Kill me with `tg #{Nick}`"
  end
  
  #Reply to !status
  on :message, /^\!status/ do |msg|
    if msg.channel == CHANNELS.first
      response = JSON.parse open("http://api.urlab.be/spaceapi/status").read
      since = (response.key? 'since') ? "since #{Time.at(response['since']).strftime('%d/%m/%Y %H:%M')}" : ''
      if response['state'] == "closed"
        msg.reply "The space is closed #{since} /o\\"
      else
        pamela_data = JSON.parse open("http://pamela.urlab.be/mac.json").read
        people = pamela_data['color'].length + pamela_data['grey'].length
        msg.reply "The space is open #{since}, and there are now #{people} people \\o/"
      end
    end
  end

  #!open & !close
  on :message, /^\!(open|close)/ do |msg, status|
    if msg.channel == CHANNELS.first
      baseurl = "http://api.urlab.be/spaceapi/statuschange"
      begin
        response = open("#{baseurl}?status=#{status}")
        if status == "open"
          msg.reply "The space is open ! Let the magic begin :)"
        else
          msg.reply "The space is closed ! Don't forget to put the lights and radiator off !"
        end
      rescue Exception => e
        msg.reply "Unable to access SpaceAPI: #{e} !!! (Did you wait 5min since last status change ?)"
      end
    end
  end

  #Return a random music from the database
  on :message, /^\!music((\s+)all)?/i do |msg|
    act = $1
    queryset = Music.all
    if act != 'all'
      chan = Chan.first name:msg.channel.name
      queryset = queryset.all(chan:chan) unless act
    end
    len = queryset.count
    if len.zero?
      msg.reply "Currently no music !"
    else
      music = queryset[rand len]
      date = music.date.strftime '%d/%m/%Y %Hh'
      msg.reply "#{music.url} proposed by #{music.sender} on #{music.chan.name}"
    end
  end
  
  #KTFB (Kill This Fuckin' Bot)
  on :message, /^tg #{Nick}/i do |msg|
    event_of_the_day = `egrep -h "$(date +"%m/%d|%b* %d")" /usr/share/calendar/* | cut -f 2`
    bot.quit event_of_the_day.split(/\n/).shuffle.pop
  end

  #Cool stuff
  on :action, /^slaps #{Nick}/ do |msg|
    msg.reply "Oh oui, encore."
  end
end


### Trash reminder ###
now = Time.now
wed = Time.new now.year, now.month, now.day, 20   #Today 20h
wed += 86400 until wed.wednesday? && wed>Time.now

scheduler = Rufus::Scheduler.start_new
scheduler.every '1w', first_at:wed do
  pamela_data = JSON.parse open("http://pamela.urlab.be/mac.json").read
  people = pamela_data['color'] + pamela_data['grey']
  
  unless people.empty?
    randomly_chosen = people.shuffle.first 
    lechbot.channels.first.send "Hey #{randomly_chosen} ! Could you PLEAAAASE take out the trash ?"
  end
end
### ###

lechbot.start
