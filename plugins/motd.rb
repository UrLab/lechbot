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
        else
            url = URI.parse $1
          
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
            msg.reply "#{m.user} gagne le MotD !"
            @last_motd = Time.now
        end
    end
end