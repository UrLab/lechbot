# encoding: utf-8

require 'cinch'
require 'bunny'
require 'time'

class HALBot
    include Cinch::Plugin

    set :help, "Indique ce qui se passe au hackerspace"

    def speakMessage msg
        msgtime = Time.parse msg['time']
        return if Time.now-msgtime > 120
        case msg['trigger']
        when 'door'
            bot.channels.first.send "La porte des escaliers s'ouvre..."
        when 'bell'
            bot.channels.first.send "On sonne à la porte !"
        when 'radiator'
            bot.channels.first.send "Le radiateur est allumé"
        end
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
                if data.key?('trigger') && data.key?('time')
                    speakMessage data
                  end
            end
        rescue Bunny::TCPConnectionFailed, Bunny::AuthenticationFailureError
              bot.debug "Unable to connect to RabbitMQ server. No events for this instance !"
        end
    end
end