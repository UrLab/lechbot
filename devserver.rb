# Development Open/Close API endpoint

require 'sinatra'

$status = 'closed'

get '/changestatus' do
  if params.key?('status') && ['open', 'close'].include?(params['status'])
    $status = (params['status'] == 'open') ? 'open' : 'closed'
    return 200, $status
  end
  return 400, "Unknown status"
end

get '/getstatus' do
  return $status
end
