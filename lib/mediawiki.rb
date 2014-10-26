require 'mechanize'

module MediaWiki
    def login wiki_url, user, pass
        #Build a new browser
        agent = Mechanize.new do |ag|
            ag.follow_meta_refresh = true
        end
      
        #Go to homepage
        wiki_URI = URI.parse wiki_url.to_s
        homepage = agent.get "http://#{wiki_URI.host}/"
        loginpage = agent.click homepage.link_with(:text => /log in/i)
        loggedhome = loginpage.form_with(:name => 'userlogin'){|form|
            form.wpName  = user
            form.wpPassword = pass
        }.submit
        return agent
    end

    def updateMotD agent, wiki_url, author, music_url
        mypage = agent.get wiki_url

        editpage = agent.click mypage.link_with(:text => /edit/i)
        #We have the edit page
        donepage = editpage.form_with(:name => 'editform'){|form|
            pubtime = Time.now.strftime "%d/%m/%Y a %H:%M"
            form.wpTextbox1 += "\n*#{author} #{music_url} (#{pubtime})"
        }.submit
    end

    def find_tw_date page
        page.search(".wikitable").search("tr").each do |tr|
            th = tr.search("th")
            next if th.length.zero?

            if th.first.text.strip == "Date"
                td = tr.search("td")
                next if td.length.zero?
                return Time.parse td.text
            end
        end
        return nil
    end

    def next_tw agent
        this_year = Time.now.year.to_s

        page = agent.get "/index.php?title=Special:SearchByProperty&offset=0&limit=500&property=Tags&value=techwednesday"
        all_tw = page.links.to_a.delete_if{|link|
            text = link.text
            ! (text.start_with?("Evenement:Techwednesday") && text.end_with?(this_year))
        }.sort{|a, b|
            a_num = a.text.split.last
            b_num = b.text.split.last
            if a_num.length < b_num.length
                a_num = "0" + a_num
            elsif b_num.length < a_num.length
                b_num = "0" + b_num
            end
            a_num <=> b_num
        }.each do |event_link|
            page = agent.get event_link.href
            date = find_tw_date page
            return page if date && date >= Time.now
        end
        return nil
    end

    def next_tw_oj next_tw_page
        oj = next_tw_page.search("#OJ").first.parent.next_sibling
        oj = oj.next_sibling while oj.name != 'ul'
        oj.search("li").map{|e| e.text.strip}
    end

    def next_tw_add_point next_tw_page, point
        edit_link = next_tw_page.search("#OJ").first.parent.search("a").first
        edit_page = next_tw_page.mech.get edit_link.attr('href')
        donepage = edit_page.form_with(:name => 'editform'){|form|
            form.wpTextbox1 = form.wpTextbox1.strip
            form.wpTextbox1 += "\n* #{point}"
            form.checkbox_with(:name => 'wpMinoredit').check
        }.submit
    end
end