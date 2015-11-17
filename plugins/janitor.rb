# encoding: utf-8

require 'cinch'
require 'rufus/scheduler'
require 'open-uri'
require 'json'

class Janitor
    MNESIA = ".janitor_last_chosen"
    include Cinch::Plugin

    set :help, "Tous les mercredis, si le hackerspace est ouvert, deux volontaires sont désignés pour sortir la poubelle"

    def notification name
        amq_conn = Bunny.new config[:amq_server]
        amq_conn.start
        chan = amq_conn.create_channel
        queue = chan.queue config[:amq_queue]
        queue.publish({
            'name' => name, 
            'time' => Time.now.strftime("%Y-%m-%d %H:%M:%S")
        }.to_json)
        chan.close
        amq_conn.close
    end

    match /poke\s*$/, :method => :poke_hackerspace
    def poke_hackerspace msg
       notification "poke"
       msg.reply "Coucou HAL (de la part de #{msg.user}) !!!"
    end

    listen_to :connect, :method => :start
    def start *args
        now = Time.now
        wed = Time.new now.year, now.month, now.day, 20   #Today 20h
        wed += 86400 until wed.wednesday? && wed>Time.now #Next wednesday, 20h

        @scheduler = Rufus::Scheduler.new
        bot.info "Created scheduler for JANITOR"

        @scheduler.every '1w', first_at:wed do
            pamela_data = JSON.parse open(config[:pamela_url]).read
            people = pamela_data['users'].map{|e| e['username']} + pamela_data['unknown_mac']
            unless people.empty?
                ineligible = []
                begin
                    ineligible = JSON.parse File.read(MNESIA)
                rescue
                end

                choosable = people - ineligible
                choosable = people if choosable.length < 2

                randomly_chosen = choosable.shuffle[0...2] 
                notification "trash"
                bot.channels.first.send "Salut #{randomly_chosen*' & '} ! Vous pourriez vider la poubelle s'il-vous-plaît ?"
                File.open(MNESIA, "w") do |f|
                    f.puts randomly_chosen.to_json
                end
            end
        end
    end
end
