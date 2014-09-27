# encoding: utf-8

require 'cinch'
require 'open-uri'
require 'json'

class Status
    include Cinch::Plugin

    set :help, <<-EOF
!status
  Affiche le statut (ouvert/fermé) du hackerspace.
EOF

    match /(open|close)\s*(\d*)/, :method => :changeStatus
    def changeStatus msg, status, delay
        msg.reply "#{msg.user}: Hey ! Maintenant on utilise l'interrupteur :)"
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
            if Time.now < $opentime
                msg.reply "Le hs ouvrira à #{$opentime.strftime('%H:%M')}"
            end
        else
            pamela_data = JSON.parse open(config[:pamela_url]).read
            people = pamela_data['color'].length + pamela_data['grey'].length
            msg.reply "Le hackerspace est ouvert #{since}, et il y a en ce moment #{people} personnes \\o/"
            if Time.now < $closetime
                msg.reply "Le hs fermera à #{$closetime.strftime('%H:%M')}"
            end
        end
    end
end
