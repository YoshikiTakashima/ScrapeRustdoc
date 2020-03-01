import requests

# getText: fetches text from the URL
#     Input:  url  = URL of target
#     Output: text = text at that URL
# 
# May return empty string if error occurs
def fetch(url):
    page = requests.get(url)
    ret = ""

    if page.status_code < 300:
        ret = page.text
    
    return ret
