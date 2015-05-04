require "koala"

def get_page_token user_token, userID, pageID
    k = Koala::Facebook::API.new user_token
    k.get_object("/#{userID}/accounts").each do |acc|
        if acc["id"] == pageID
            return acc["access_token"]
        end
    end
    nil
end

def post_to_page token, pageID, message
    k = Koala::Facebook::API.new token
    k.put_connections pageID, "feed", :message => message
end
