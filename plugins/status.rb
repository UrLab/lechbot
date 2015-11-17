# encoding: utf-8

require 'cinch'
require 'open-uri'
require 'json'
require 'net/http'

class Status
    include Cinch::Plugin

    set :help, <<-EOF
!status
  Affiche le statut (ouvert/fermé) du hackerspace.
EOF

    match /(open|close).*/, :method => :changeStatus
    def changeStatus msg, status
        msg.reply "#{msg.user}: Hey ! Maintenant on utilise l'interrupteur :)"
    end

    match /sudo \!(open|close).*/, :prefix => '', :method => :forceChangeStatus
    def forceChangeStatus msg, status
        if ! config[:status_change_url] || config[:status_change_url].empty?
            msg.reply "URL de changement de statut non configurée"
            return
        end
        uri = URI(config[:status_change_url])
        is_open = (status == 'open') ? '1' : '0'
        Net::HTTP.post_form(uri, 'secret' => config[:status_change_secret], 'open' => is_open)
        if status == "open"
            msg.reply "Le hackerspace est ouvert. Dites bonjour à HAL de ma part !"
        else
            msg.reply "Le hackerspace est fermé ! A l'occaze, demandez à HAL s'il va bien"
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
        state = response['state']
        since = (state.key? 'lastchange') ? "depuis le #{Time.at(state['lastchange']).strftime('%d/%m/%Y %H:%M')}" : ''

        unless state['open']
            msg.reply "Le hackerspace est fermé #{since} /o\\"
        else
            people = response['sensors']['people_now_present'][0]['value']
            msg.reply "Le hackerspace est ouvert #{since}, et il y a en ce moment #{people} personnes \\o/"
        end
    end
end
