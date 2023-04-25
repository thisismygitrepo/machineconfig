
activate_ve latest

# read api key from hhere
$ini_file = "$HOME\dotfiles\creds\tokens\openai_api.txt"
$api_key = Get-Content -Path $ini_file
# remove trailing empty space or new line
$api_key = $api_key.Trim()
python -m revChatGPT.V3 --api_key $api_key $args

deactivate
