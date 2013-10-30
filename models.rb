require 'data_mapper'

DataMapper.setup(:default, "sqlite3://#{File.dirname __FILE__}/lechbot.sqlite3")

class Chan
  include DataMapper::Resource
  
  property :id, Serial
  property :name, String
end

class Music
  include DataMapper::Resource
  
  property :id, Serial
  property :url, URI
  property :sender, String
  property :date, DateTime
  
  belongs_to :chan
  
  before :save do |music|
    music.date = DateTime.now
  end

  def soundcloud?
    url.host == 'soundcloud.com'
  end
  
  def youtube?
    url.host == 'youtube.com' || url == 'youtu.be'
  end
end

class Wikichange
  include DataMapper::Resource
  
  property :id, Serial
  property :url, URI
  property :name, String
  
  def to_s
    "Page #{name} changed #{url.to_s}"
  end
end

DataMapper.finalize
DataMapper.auto_upgrade!
