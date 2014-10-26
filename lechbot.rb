# encoding: utf-8

require 'cinch'

%w(status motd twitter janitor wikichanges HAL help reminder kanboard techwednesday).each do |plugin|
  require "./plugins/#{plugin}"
end

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

GIT_VERSION = `git log | head -1`.split(' ').pop

lechbot = Cinch::Bot.new do
  STARTED = Time.now
  Nick = PRODUCTION ? "LechBot" : "DechBot"
  
  configure do |conf|
    conf.server = "chat.freenode.org"
    conf.channels = CHANNELS
    conf.nick = Nick
    conf.realname = Nick
    config.plugins.plugins = [
      Status, 
      Motd, 
      Twitteur, 
      Janitor,
      WikiChanges,
      HAL,
      Reminder,
      Kanboarder,
      TechWednesday,
      Cinch::Help
    ]

    conf.plugins.options[Twitteur] = {
      consumer_key: TWITTER_CONSUMER_KEY,
      consumer_secret: TWITTER_CONSUMER_SECRET,
      oauth_token: TWITTER_OAUTH_TOKEN,
      oauth_token_secret: TWITTER_OAUTH_SECRET 
    }

    conf.plugins.options[Motd] = {
      motd_wiki_url: "#{WIKI_URL}/#{WIKI_MOTD}",
      username: WIKI_USERNAME,
      password: WIKI_PASSWORD
    }

    conf.plugins.options[Status] = {
      status_get_url: STATUS_GET_URL,
      status_change_url: STATUS_CHANGE_URL,
      pamela_url: PAMELA_URL
    }

    conf.plugins.options[Janitor] = {
      pamela_url: PAMELA_URL
    }

    conf.plugins.options[WikiChanges] = {
      wiki_changes_url: "#{WIKI_URL}/#{WIKI_CHANGES}",
      username: WIKI_USERNAME
    }

    conf.plugins.options[HAL] = {
      amq_queue: HAL_EVENTS,
      amq_server: HAL_AMQ_BROKER
    }

    conf.plugins.options[Reminder] = {
      events_url: EVENTS_URL,
      kan_user: KAN_USERNAME,
      kan_pass: KAN_PASSWORD,
      kan_board: KAN_BOARD
    }

    conf.plugins.options[Kanboarder] = {
      kan_user: KAN_USERNAME,
      kan_pass: KAN_PASSWORD,
      kan_board: KAN_BOARD
    }

    conf.plugins.options[TechWednesday] = {
      wiki_url: WIKI_URL,
      username: WIKI_USERNAME,
      password: WIKI_PASSWORD
    }
  end
    
  #Explain the meaning of Lechbot's life
  on :message, /^\!lechbot *$/ do |msg|
    msg.reply "Hilight me ! (#{bot.nick}: help). Je réponds aussi en query"
  end
  
  on :message, /^\!version *$/ do |msg|
    prefix = PRODUCTION ? "https://github.com/titouanc/lechbot/tree/" : ""
    msg.reply prefix+GIT_VERSION
  end

  on :message, /^\!uptime *$/ do |msg|
    dt = (Time.now - STARTED).to_i
    days = dt/86400
    dt %= 86400
    hours = dt/24
    dt %= 24
    minutes = dt/60
    seconds = dt%60
    msg.reply "#{days} jours #{hours}h #{minutes}m #{seconds}s"
  end

  #KTFB (Kill This Fuckin' Bot)
  on :message, /^tg #{Nick}/i do |msg|
    event_of_the_day = `egrep -h "$(date +"%m/%d|%b* %d")" /usr/share/calendar/* | cut -f 2`
    bot.quit event_of_the_day.split(/\n/).shuffle.pop
  end

  #Cool stuff
  on :action, /^slaps #{Nick}/ do |msg|
    msg.reply "#{msg.user}: Oh oui, encoooore !"
  end
end

lechbot.start
