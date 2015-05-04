# encoding: utf-8

require 'cinch'
require './lib/fb.rb'

class Facebook
    include Cinch::Plugin

    set :help, <<-EOF
!facebook <message>
  Publie <message> sur la page UrLab (urlabbxl).
EOF

    def post_as_urlab msg
        page_token = get_page_token(config[:fb_token], config[:fb_userid], config[:fb_pageid])
        post_to_page(page_token, config[:fb_pageid], msg)
    end

    match /fb\s(.+)/, :method => :postMessage
    def postMessage msg, text
        text.strip!
        if text.empty? 
            msg.reply "Pas grand chose à dire..."
        else
            post_as_urlab(text)
            msg.reply("Lulz on the web !")
        end
    end
end
