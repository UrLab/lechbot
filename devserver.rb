# Development Open/Close API endpoint

require 'sinatra'
require 'json'

$status = 'closed'
$lastchange = Time.now

get '/changestatus' do
  if params.key?('status') && ['open', 'close'].include?(params['status'])
  	$lastchange = Time.now
    $status = (params['status'] == 'open') ? 'open' : 'closed'
    return {'state' => $status, 'since' => $lastchange.to_i}.to_json
  end
  return 400, "Unknown status"
end

get '/getstatus' do
  return {'state' => $status, 'since' => $lastchange.to_i}.to_json
end
