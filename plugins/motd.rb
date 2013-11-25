# encoding: utf-8

require 'cinch'
require 'mechanize'

class Time
    def same_day? other
        day == other.day && month == other.month && year == other.year
    end
end


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

class MotdBot
    include Cinch::Plugin
    include MediaWiki

    listen_to :topic, :method => :changeMotd
    def changeMotd msg
        if not msg.message =~ /^\s*(https?:\/\/[^\s]+)/
            msg.reply "Pas d'url, pas de MotD d°-°b"
        elsif @last_motd && @last_motd.same_day?(Time.now)
            msg.reply "Le MotD a déjà été changé aujourd'hui !"
        elsif ! config[:motd_wiki_url] || config[:motd_wiki_url].empty?
            bot.error "L'URL du MotD manque dans la configuration"
        elsif ! config[:username] || config[:username].empty?
            bot.error "Nom d'utilisateur sur le wiki manquant"
        elsif ! config[:password] || config[:password].empty?
            bot.error "Mot de passe du wiki manquant"
        else    
            url = URI.parse $1
            agent = login config[:motd_wiki_url], config[:username], config[:password]
            updateMotD agent, config[:motd_wiki_url], msg.user, url
            #Say something on the chan
            msg.reply "#{msg.user} gagne le MotD !"
            @last_motd = Time.now
        end
    end
end