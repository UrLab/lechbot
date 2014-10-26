# encoding: utf-8

require 'cinch'
require './lib/mediawiki'

class TechWednesday
    include Cinch::Plugin
    include MediaWiki

    set :help, <<-EOF
!tw
  Affiche l'ordre du jour du prochain Tech Wednesday
!tw <votre point>
  Ajoute <votre point> à l'ordre du jour du prochain TechWednesday
EOF

    match /tw(.*)/, :method => :tw
    def tw msg, point
        point.strip!
        msg.reply "Un instant..."

        next_tw_page = next_tw login(config[:wiki_url], config[:username], config[:password])

        if point.empty?
            msg.reply "#{next_tw_page.title}:"
            next_tw_oj(next_tw_page).each do |point|
                msg.reply " - #{point}"
            end
        else
            next_tw_add_point next_tw_page, point
            msg.reply "Point ajouté à l'ordre du jour du prochain TechWednesday"
        end
    end
end
