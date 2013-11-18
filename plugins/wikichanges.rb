# encoding: utf-8

require 'cinch'
require 'rufus/scheduler'
require 'nokogiri'

class WikiChangesBot
	include Cinch::Plugin

	PERSISTENCE_FILE = ".wiki_last_diff"

	def saveLastDiff diffid
		File.open PERSISTENCE_FILE, 'w' do |file|
			file.puts diffid.to_s
		end
	end

	def getLastDiff
		return 0 unless File.exists? PERSISTENCE_FILE
		return File.read(PERSISTENCE_FILE).to_i
	end

	def scheme
		config[:wiki_changes_url].scheme
	end

	def host
		config[:wiki_changes_url].host
	end

	def each_diff
		page = Nokogiri::HTML open(config[:wiki_changes_url].to_s).read
		page.css('.mw-changeslist-line-not-watched').each do |change|
			link = change.css('a[tabindex]').first
			if link && link.text == 'diff'
				author = change.css('.mw-userlink').first.text
				title = link.attr 'title'
				diff_id = (link.attr('href') =~ /diff=([^&]+)/) ? $1.to_i : 0
				partial_href = link.attr 'href'
				href = URI.parse "#{scheme}://#{host}#{partial_href}"
				yield diff_id, title, href, author
			end
		end
	end

	listen_to :connect, :method => :start
	def start *args
		if ! config[:wiki_changes_url] || config[:wiki_changes_url].empty?
			bot.debug "URL de changements sur le wiki non configurée"
			return
		end

		config[:wiki_changes_url] = URI.parse config[:wiki_changes_url].to_s 

		@scheduler = Rufus::Scheduler.new
		bot.info "Created scheduler for WIKI CHANGES"

		lastDiff = getLastDiff
		@scheduler.every '1m' do 
			bot.info "START FINDING CHANGES ON WIKI"

			changes = 0
			newDiff = lastDiff

			each_diff do |diff_id, title, href, author|
				# Stop if we reach a diff we already know
				break if diff_id <= lastDiff
				bot.channels.first.send "#{author} a modifié #{title} #{href}"
				newDiff = diff_id if diff_id > newDiff
				changes += 1
			end

			saveLastDiff newDiff if newDiff > lastDiff
			lastDiff = newDiff

			bot.info "FOUND #{changes} changes. Goodbye"
		end
	end
end