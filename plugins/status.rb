# encoding: utf-8

require 'open-uri'
require 'json'

class StatusBot
    include Cinch::Plugin

    $opentime = 0
    $closetime = 0
    match /(open|close)\s*(\d*)/, :method => :changeStatus
    def changeStatus msg, status, delay
        if ! config[:status_change_url] || config[:status_change_url].empty?
            msg.reply "URL de changement de statut non configurée"
            return
        end
        begin
            if delay.empty?
                response = open("#{config[:status_change_url]}?status=#{status}")
                if status == "open"
                    msg.reply "Le hackerspace est ouvert. PONEYZ EVERYWHERE <3"
                else
                    msg.reply "Le hackerspace est fermé. N'oubliez pas d'éteindre les lumières et le radiateur !"
                end
            else
                if status == "open"
                    $opentime = Time.now + 60*delay.to_i
                    msg.reply "Le hs ouvrira dans #{delay} minutes, à #{$opentime.strftime('%H:%M')}"
                elsif status == "close"
                    $closetime = Time.now + 60*delay.to_i
                    msg.reply "Le hs fermera dans #{delay} minutes, à #{$closetime.strftime('%H:%M')}"
                end
            end

        rescue Exception => e
            suffix = "(As-tu attendu 5min depuis le dernier changement de statut ?)"
            msg.reply "Erreur d'accès à SpaceAPI: #{e} !!! #{suffix if PRODUCTION}"
        end
    end

    match /status/, :method => :status
    def status msg
        if ! config[:status_get_url] || config[:status_get_url].empty?
            msg.reply "URL de récupération de statut non configurée"
            return
        end
        if ! config[:pamela_url] || config[:pamela_url].empty?
            msg.reply "URL Pamela non configurée"
            return
        end
        response = JSON.parse open(config[:status_get_url]).read
        since = (response.key? 'since') ? "depuis le #{Time.at(response['since']).strftime('%d/%m/%Y %H:%M')}" : ''
        if response['state'] == "closed"
            msg.reply "Le hackerspace est fermé #{since} /o\\"
            if (Time.now <=> $opentime) == -1
                msg.reply "Le hs ouvrira à #{($opentime).strftime('%H:%M')}"
            end
        else
            pamela_data = JSON.parse open(config[:pamela_url]).read
            people = pamela_data['color'].length + pamela_data['grey'].length
            msg.reply "Le hackerspace est ouvert #{since}, et il y a en ce moment #{people} personnes \\o/"
            if (Time.now <=> $closetime) == -1
                msg.reply "Le hs fermera à #{($closetime).strftime('%H:%M')}"
            end
        end
    end
end
