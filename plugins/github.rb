# encoding: utf-8

require 'cinch'
require 'open-uri'
require 'json'

class Github
    include Cinch::Plugin

    set :help, <<-EOF
URL Github dans un message
  Affiche quelques infos sur le repo
EOF

    PART = /[\w\d_\.-]+/
    GITHUB_URL = /https?:\/\/github\.com\/(#{PART}\/#{PART})\/?(\s|$)/

    match GITHUB_URL, :method => :showRepo, :prefix => //
    def showRepo msg, repo_id
        url = "https://api.github.com/repos/#{repo_id}"
        begin
            repo = JSON.parse open(url).read
            bot.info "Grab info for #{repo_id}"
            name = "#{repo['name']}"
            if repo['stargazers_count'] > 100
                name = "#{name} (#{repo['stargazers_count']} *)"
            end
            desc = "#{repo['description']}"
            msg.reply "#{name}: #{desc}"
        rescue Exception => err
            bot.error "Unable to fetch #{url} #{err}"
        end
    end
end
