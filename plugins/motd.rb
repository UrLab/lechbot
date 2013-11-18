# encoding: utf-8

require 'mechanize'

class Time
    def same_day? other
        day == other.day && month == other.month && year == other.year
    end
end


class MotdBot
    include Cinch::Plugin

    listen_to :topic, :method => :changeMotd
    def changeMotd msg
        if not msg.message =~ /^\s*(https?:\/\/[^\s]+)/
            msg.reply "Pas d'url, pas de MotD d°-°b"
        elsif @last_motd && @last_motd.same_day?(Time.now)
            msg.reply "Le MotD a déjà été changé aujourd'hui !"
        elsif ! config[:motd_wiki_url] || config[:motd_wiki_url].empty?
            msg.reply "L'URL du MotD manque dans la configuration"
        elsif ! config[:username] || config[:username].empty?
            msg.reply "Nom d'utilisateur sur le wiki manquant"
        elsif ! config[:password] || config[:password].empty?
            msg.reply "Mot de passe du wiki manquant"
        else
            url = URI.parse $1
          
            #Build a new browser
            agent = Mechanize.new do |ag|
                ag.follow_meta_refresh = true
            end
          
            #Go to homepage
            wiki_URI = URI.parse config[:motd_wiki_url]
            homepage = agent.get "http://#{wiki_URI.host}/"
            loginpage = agent.click homepage.link_with(:text => /log in/i)
            loggedhome = loginpage.form_with(:name => 'userlogin'){|form|
                form.wpName  = config[:username],
                form.wpPassword = config[:password]
            }.submit
          
            #We're now logged in
          
            mypage = agent.get config[:motd_wiki_url]
            editpage = agent.click mypage.link_with(:text => /edit/i)
            #We have the edit page
            donepage = editpage.form_with(:name => 'editform'){|form|
                pubtime = Time.now.strftime "%d/%m/%Y a %H:%M"
                #Adding an entry (new music)
                form.wpTextbox1 = form.wpTextbox1 + "\n*#{msg.user} #{url} (#{pubtime})"
            }.submit
          
            #Say something on the chan
            msg.reply "#{msg.user} gagne le MotD !"
            @last_motd = Time.now
        end
    end
end