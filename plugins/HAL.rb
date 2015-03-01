# encoding: utf-8

require 'cinch'
require 'bunny'
require 'time'

class HAL
    include Cinch::Plugin

    set :help, "Indique ce qui se passe au hackerspace"

    TRIGGERS_TEXTS = {
        'door_stairs' => "Quelqu'un est de passage",
        'bell' => "On sonne à la porte !",
        'heater_on' => "Le radiateur est allumé",
        'heater_off' => "Le radiateur est éteint",
        'hs_open' => "Le hackerspace est ouvert ! RAINBOWZ NSA PONEYZ EVERYWHERE \\o/",
        'hs_close' => "Le hackerspace est fermé ! N'oubliez pas d'éteindre les lumières et le radiateur.",
        'passage' => "Il y a quelqu'un à l'intéreur"
    }

    TRIGGERS_RATELIMIT = {
        'passage' => 3600,
    }

    TRIGGER_LAST = {}

    def speakMessage msg
        msgtime = Time.parse msg['time']

        #Drop messages older than 2 mins
        if Time.now-msgtime > 120 || ! TRIGGERS_TEXTS.key?(msg['name'])
            bot.info "Drop message #{msg}"
            return
        end

        trig = msg['name']
        limit = TRIGGERS_RATELIMIT[trig]
        last = TRIGGER_LAST[trig]
        return if limit && last && Time.now - last < limit
        bot.channels.first.send TRIGGERS_TEXTS[msg['name']]
        TRIGGER_LAST[trig] = Time.now
    end

    listen_to :connect, :method => :start
    def start *args
        begin
            amq_conn = Bunny.new config[:amq_server]
            amq_conn.start
            bot.info "Got connection to AMQ server"

            chan = amq_conn.create_channel
            queue = chan.queue config[:amq_queue]
            bot.info "Got queue #{config[:amq_queue]}"

            queue.subscribe do |delivery_info, metadata, payload|
                data = JSON.parse payload
                if data.key?('name') && data.key?('time')
                    speakMessage data
                end
            end
        rescue Bunny::TCPConnectionFailed, Bunny::AuthenticationFailureError
              bot.debug "Unable to connect to RabbitMQ server. No events for this instance !"
        end
    end
end