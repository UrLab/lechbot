# encoding: utf-8

require 'cinch'

require './plugins/status'
require './plugins/motd'
require './plugins/twitter'
require './plugins/janitor'
require './plugins/wikichanges'
require './plugins/HAL'
require './plugins/help'

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
  Nick = PRODUCTION ? "LechBot" : "DechBot"
  
  configure do |conf|
    conf.server = "irc.freenode.org"
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
      Cinch::Help
    ]

    conf.plugins.options[Twitteur] = {
      consumer_key: TWITTER_CONSUMER_KEY,
      consumer_secret: TWITTER_CONSUMER_SECRET,
      oauth_token: TWITTER_OAUTH_TOKEN,
      oauth_token_secret: TWITTER_OAUTH_SECRET 
    }

    conf.plugins.options[Motd] = {
      motd_wiki_url: URLAB_WIKI_MOTDURL,
      username: URLAB_WIKI_USERNAME,
      password: URLAB_WIKI_PASSWORD
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
      wiki_changes_url: WIKI_CHANGES_URL,
      username: URLAB_WIKI_USERNAME
    }

    conf.plugins.options[HAL] = {
      amq_queue: EVENTS_QUEUE,
      amq_server: AMQ_SERVER
    }
  end
    
  #Explain the meaning of Lechbot's life
  on :message, /^\!lechbot$/ do |msg|
    msg.reply "Essaye peut-être de me demander de l'aide... (#{bot.nick}: help)"
    msg.reply "(Je réponds aussi en query)"
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

lechbot.start
