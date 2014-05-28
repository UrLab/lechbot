# encoding: utf-8

require 'cinch'
require 'mechanize'

module MediaWiki
    def login wiki_url, user, pass
        #Build a new browser
        agent = Mechanize.new do |ag|
            ag.follow_meta_refresh = true
        end
      
        #Go to homepage
        wiki_URI = URI.parse wiki_url.to_s
        homepage = agent.get "http://#{wiki_URI.host}/"
        loginpage = agent.click homepage.link_with(:text => /log in/i)
        loggedhome = loginpage.form_with(:name => 'userlogin'){|form|
            form.wpName  = user
            form.wpPassword = pass
        }.submit
        return agent
    end

    def updateMotD agent, wiki_url, author, music_url
        mypage = agent.get wiki_url

        editpage = agent.click mypage.link_with(:text => /edit/i)
        #We have the edit page
        donepage = editpage.form_with(:name => 'editform'){|form|
            pubtime = Time.now.strftime "%d/%m/%Y a %H:%M"
            form.wpTextbox1 += "\n*#{author} #{music_url} (#{pubtime})"
        }.submit
    end
end

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
        state = {}
        fd = nil
        if File.exists? STATEFILE
            fd = File.open STATEFILE, 'r+'
            fd.flock File::LOCK_EX
            state = YAML.load File.read(STATEFILE)
            fd.seek 0
            fd.truncate 0
        else
            state = {
                music: {
                    text: "http://www.youtube.com/watch?v=p8oi6M4z_e0",
                    changed: Time.at(0)
                }, 
                topic: {
                    text: "Brace yourself, LechBot is coming !!!",
                    changed: Time.at(0)
                }
            }
            fd = File.open STATEFILE, 'w'
            fd.flock File::LOCK_EX
        end
        yield state
        fd.write YAML.dump(state)
        fd.flock File::LOCK_UN
        fd.close
    end

    def makeTopic state, chan
        chan.topic = "#{state[:music][:text]} :: #{state[:topic][:text]}"
    end

    listen_to :topic, :method => :remakeTopic
    def remakeTopic msg
        return if msg.user == bot.name
        withState do |state|
            makeTopic state, msg.channel
        end
        msg.reply "#{msg.user}: *JE* m'occupe du MotD !!! (utilise !motd et/ou !topic)"
    end

    match /motd\s*(https?:\/\/[^\s]+)/, :method => :changeMotd
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
                makeTopic state, msg.channel

                title = ""
                begin
                    page = Nokogiri::HTML open(url)
                    title = ": " + page.css('title').text
                rescue Exception => e
                    bot.error "MotD title fetch error #{e.to_s} !!!"
                end
                msg.reply "#{msg.user} a changé la musique du jour #{title}"
            end
        end
    end

    match /topic/, :method => :changeTopic
    def changeTopic msg
        newtopic = msg.message.gsub(/\!topic\s*/, '').strip
        if newtopic.empty?
            msg.reply "Topic vide, je ne cautionne certainement pas !"
        else
            withState do |state|
                state[:topic][:text] = newtopic
                state[:topic][:changed] = Time.now
                makeTopic state, msg.channel
            end
        end
    end
end