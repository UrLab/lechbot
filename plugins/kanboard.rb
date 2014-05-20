# encoding: utf-8

require 'cinch'
require './lib/kanboard'

class Kanboarder
    include Cinch::Plugin

    set :help, <<-EOF
!kanboard <texte>
  Cree une nouvelle tache sur la board principale de kanboard. Si la chaine :dd/mm ou :dd/mm/yyyy est trouvée, donne cette échéance à la carte. 
  Exemple: !kanboard Tuer le monde :21/12/2012
EOF

    match /kanboard\s+([^\s].*)/, :method => :post_to_kanboard
    def post_to_kanboard msg, content
        date = nil
        content.gsub! /\s:(\d\d)\/(\d\d)\/(\d{4})/ do
            date = Time.mktime $3.to_i, $2.to_i, $1.to_i
            ''
        end
        content.gsub! /:(\d\d)\/(\d\d)/ do
            date = Time.mktime Time.now.year, $2.to_i, $1.to_i
            ''
        end

        kan = Kanboard.new config[:kan_user], config[:kan_pass]
        url = kan.add_card config[:kan_board], content.strip, date
        msg.reply url
    end
end
