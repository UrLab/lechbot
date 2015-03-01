# encoding: utf-8

require 'mechanize'
require 'time'

class Kanboard
    Months = [
        "janvier", "février", "mars", "avril", "mai", "juin",
        "juillet", "août", "septembre", "octobre", "novembre", "décembre"
    ]

    def initialize username, password, server="http://kanboard.urlab.be/"
        @server = server
        @agent = Mechanize.new do |mech|
            mech.follow_meta_refresh = true
        end

        page = @agent.get "#{@server}?controller=user&action=login"
        form = page.forms[0]
        form.username = username
        form.password = password
        form.submit
    end

    def boards
        page = @agent.get "?controller=project"
        boards = page.links.delete_if do |link| 
            not link.href =~ /project_id/ or link.text =~ /^\d/
        end
        return boards.inject({}) do |res, link|
            res[link.text.strip] = link.href.gsub(/.*project_id=(\d+).*/, '\1').to_i
            res
        end
    end

    def get_board board_id
        board_id = boards[board_id] if board_id.kind_of? String
        @agent.get "#{@server}?controller=board&action=show&project_id=#{board_id}"
    end
    private :get_board

    def add_card board, title, due_date=nil
        link = get_board(board).search('th')[0].search('a')[0]
        url = link['href'].gsub('&amp;', '&')
        form = @agent.get(url).forms[0]
        form['title'] = title
        form['date_due'] = due_date.strftime "%d/%m/%Y" if due_date
        form.submit.uri
    end

    def parseDate datestr
        if datestr =~ /(\d{1,2}) (#{Months*"|"}) (\d{4})/
            day = $1.to_i
            month = 1 + Months.index($2)
            year = $3.to_i
            Time.mktime(year, month, day, 20)
        end
    end

    def [] board=1
        get_board(board).search('.task-board').map do |task|
            date = task.search('.task-board-date')
            {
                name:  task.search('.task-board-title').text.strip, 
                url:   @server+task.search('a')[0].attributes['href'].to_s,
                date:  parseDate(date.text),
                owner: task.search('.task-board-user').text.strip
            }
        end
    end
end
