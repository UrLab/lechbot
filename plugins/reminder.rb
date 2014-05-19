# encoding: utf-8

require 'cinch'
require 'rufus/scheduler'
require 'open-uri'
require 'json'
require 'time'
require './lib/kanboard'

class Reminder
    include Cinch::Plugin

    DTRANGES = {
        (7*86400-3600)..(7*86400) => "dans une semaine",
        (3*86400-3600)..(3*86400) => "dans 3 jours",
        82800..86400 => "demain",
        7200..10800 => "dans moins de 3h"
    }

    set :help, "Rappel des events a venir"

    def each_event &block
        payload = nil
        begin
            payload = JSON.parse open(config[:events_url]).read
        rescue Exception => err
            debug "Error when fetching events: #{err.class} #{err}"
        end
        if payload
            payload['events'].each &block
        end
    end

    def remind name, url, date, dt_prefix="a lieu"
        dt = date-Time.now
        debug "EVENT: DT=#{dt} #{date} #{name} #{url}"

        DTRANGES.each do |dtrange, dtname|
            if dtrange.include? dt
                bot.channels.first.send "=== Rappel === #{name} #{dt_prefix} #{dtname} #{url}"
                break
            end
        end
    end

    listen_to :connect, :method => :start
    def start *args
        @scheduler = Rufus::Scheduler.new
        bot.info "Created scheduler for JANITOR"

        @scheduler.every '1h', first_at:(Time.now+10) do
            each_event do |ev|
                name, url, date = ev['name'], ev['url'], Time.parse(ev['date'])
                remind name, url, date
            end

            kan = Kanboard.new(config[:kan_user], config[:kan_pass])
            kan[config[:kan_board]].each do |task|
                name, date, url = task[:name], task[:date], task[:url]
                if date
                    remind name, url, date, "est à faire pour"
                end
            end
        end
    end
end
