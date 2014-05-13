# encoding: utf-8

require 'cinch'
require 'rufus/scheduler'
require 'open-uri'
require 'json'
require 'time'

class Reminder
    include Cinch::Plugin

    set :help, "Rappel des events a venir"

    listen_to :connect, :method => :start
    def start *args
        @scheduler = Rufus::Scheduler.new
        bot.info "Created scheduler for JANITOR"

        @scheduler.every '1h', first_at:(Time.now+10) do
            now = Time.now
            payload = JSON.parse open(config[:events_url]).read

            payload['events'].each do |ev|
                name, url, date = ev['name'], ev['url'], Time.parse(ev['date'])
                dt = date-now
                debug "EVENT: DT=#{dt} #{date} #{name} #{url}"

                case dt
                when 7*86400-3600..7*86400
                    bot.channels.first.send "=== Rappel === *#{name}* a lieu dans une semaine #{url}"
                when 3*86400-3600..3*86400
                    bot.channels.first.send "=== Rappel === *#{name}* a lieu dans 3 jours #{url}"
                when 82800..86400
                    bot.channels.first.send "=== Rappel === *#{name}* a lieu demain #{url}"
                when 7200..10800
                    bot.channels.first.send "=== Rappel === *#{name}* a lieu dans moins de 3h ! #{url}"
                end 
            end
        end
    end
end
