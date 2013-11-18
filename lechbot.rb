# encoding: utf-8

require 'cinch'

require './plugins/status'
require './plugins/motd'
require './plugins/twitter'
require './plugins/janitor'
require './plugins/wikichanges'
require './plugins/HAL'

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
      StatusBot, 
      MotdBot, 
      TwitterBot, 
      JanitorBot,
      WikiChangesBot,
      HALBot
    ]
    @last_motd = nil

    conf.plugins.options[TwitterBot] = {
      consumer_key: TWITTER_CONSUMER_KEY,
      consumer_secret: TWITTER_CONSUMER_SECRET,
      oauth_token: TWITTER_OAUTH_TOKEN,
      oauth_token_secret: TWITTER_OAUTH_SECRET 
    }

    conf.plugins.options[MotdBot] = {
      motd_wiki_url: URLAB_WIKI_MOTDURL,
      username: URLAB_WIKI_USERNAME,
      password: URLAB_WIKI_PASSWORD
    }

    conf.plugins.options[StatusBot] = {
      status_get_url: STATUS_GET_URL,
      status_change_url: STATUS_CHANGE_URL,
      pamela_url: PAMELA_URL
    }

    conf.plugins.options[JanitorBot] = {
      pamela_url: PAMELA_URL
    }

    conf.plugins.options[WikiChangesBot] = {
      wiki_changes_url: WIKI_CHANGES_URL,
      username: URLAB_WIKI_USERNAME
    }

    conf.plugins.options[HALBot] = {
      amq_queue: EVENTS_QUEUE,
      amq_server: AMQ_SERVER
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

lechbot.start
