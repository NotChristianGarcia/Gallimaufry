from agavepy.actors import get_binary_message
import requests

bin_message = get_binary_message()

imgur_req = requests.post("https://api.imgur.com/3/image", bin_message,
                   headers={'Authorization':'Client-ID 8af4e56496131e0'})

print(imgur_req.json()['data']['link'])