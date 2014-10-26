# encoding: utf-8

require 'cinch'
require './lib/mediawiki'

class Motd
    include Cinch::Plugin
    include MediaWiki

    STATEFILE = 'motd.yml'

    set :help, <<-EOF
!motd <url>
  Change la musique du jour (max 1x par jour calendrier). NB: ceci n'inclut pas le sujet du chan
!topic <texte>
  Change le sujet du chan. NB: ceci n'inclut pas la musique du jour.
EOF

    def withState
        state = false
        fd = nil
        if File.exists? STATEFILE
            fd = File.open STATEFILE, 'r+'
            fd.flock File::LOCK_EX
            state = YAML.load File.read(STATEFILE)
        else
            fd = File.open STATEFILE, 'w'
            fd.flock File::LOCK_EX
        end
        state ||= {
            music: {
                text: "http://www.youtube.com/watch?v=p8oi6M4z_e0",
                changed: Time.at(0)
            }, 
            topic: {
                text: "Brace yourself, LechBot is coming !!!",
                changed: Time.at(0)
            }
        }

        begin
            yield state
            fd.seek 0
            fd.truncate 0
            fd.write YAML.dump(state)
        ensure
            fd.flock File::LOCK_UN
            fd.close
        end
    end

    def makeTopic state, chan
        chan.topic = "#{state[:music][:text]} :: #{state[:topic][:text]}"
    end

    def tell msg, stateKey
        response = "BITE"
        withState do |state|
            values = state[stateKey]
            if values
                author = values.key?(:author) ? values[:author] : "un inconnu"
                date = values.key?(:changed) ? values[:changed].strftime("Le %d/%m/%Y à %H:%M") : "jamais"
                response = "#{date} par #{author}"
            end
        end
        msg.reply response
    end

    listen_to :topic, :method => :remakeTopic
    def remakeTopic msg
        return if msg.user == bot.name
        withState do |state|
            makeTopic state, msg.channel
        end
        msg.reply "#{msg.user}: *JE* m'occupe du MotD !!! (utilise !motd et/ou !topic)"
    end

    match /motd\s*$/, :method => :tellMotd
    def tellMotd msg
       tell msg, :music 
    end

    match /motd\s+(https?:\/\/[^\s]+)/, :method => :changeMotd
    def changeMotd msg, url
        withState do |state|
            if state[:music][:changed].to_date == Time.now.to_date
                msg.reply "La musique du jour a déjà été changée aujourd'hui !"
            elsif ! config[:motd_wiki_url] || config[:motd_wiki_url].empty?
                bot.error "L'URL du MotD manque dans la configuration"
            elsif ! config[:username] || config[:username].empty?
                bot.error "Nom d'utilisateur sur le wiki manquant"
            elsif ! config[:password] || config[:password].empty?
                bot.error "Mot de passe du wiki manquant"
            else
                agent = login config[:motd_wiki_url], config[:username], config[:password]
                updateMotD agent, config[:motd_wiki_url], msg.user, url
                
                state[:music][:changed] = Time.now
                state[:music][:text] = url
                state[:music][:author] = msg.user.name
                makeTopic state, msg.channel

                title = ""
                begin
                    page = Nokogiri::HTML open(url)
                    title = ": " + page.css('title').text
                rescue Exception => e
                    bot.error "MotD title fetch error #{e.to_s} !!!"
                end
                msg.reply "#{msg.user} a changé la musique du jour#{title}"
            end
        end
    end

    match /topic\s+([^\s].*)\s*$/, :method => :changeTopic
    def changeTopic msg, text
        withState do |state|
            state[:topic][:text] = text
            state[:topic][:changed] = Time.now
            state[:topic][:author] = msg.user.name
            makeTopic state, msg.channel
        end
    end

    match /topic\s*$/, :method => :tellTopic
    def tellTopic msg
        tell msg, :topic
    end
end