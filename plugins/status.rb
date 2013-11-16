# encoding: utf-8

require 'open-uri'
require 'json'
class StatusBot
    include Cinch::Plugin

    PAMELA_URL = "http://pamela.urlab.be/mac.json"
    GET_STATUS_URL = "http://api.urlab.be/spaceapi/status"
    CHANGE_STATUS_URL = "" #"http://api.urlab.be/spaceapi/statuschange"

    match /(open|close)/, :method => :changeStatus
    def changeStatus msg, status
        begin
            response = open("#{CHANGE_STATUS_URL}?status=#{status}")
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

    match /status/, :method => :status
    def status msg
        response = JSON.parse open(GET_STATUS_URL).read
        since = (response.key? 'since') ? "depuis le #{Time.at(response['since']).strftime('%d/%m/%Y %H:%M')}" : ''
        if response['state'] == "closed"
            msg.reply "Le hackerspace est fermé #{since} /o\\"
        else
            pamela_data = JSON.parse open(PAMELA_URL).read
            people = pamela_data['color'].length + pamela_data['grey'].length
            msg.reply "Le hackerspace est ouvert #{since}, et il y a en ce moment #{people} personnes \\o/"
        end
    end
end
