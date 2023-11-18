from urllib.parse import urlparse
import consts

# Rip the id from a short URL
# Returns string
def extract_short_id(response):
    return urlparse(response.get_json()[consts.REQUEST_KEY]).path[1:]

# Check the length of the id on a returned short url
# Should be 7 characters (one preceding '/' and 6 ascii)
# Returns boolean
def verify_id_len(response):
    return len(urlparse(response.get_json()[consts.REQUEST_KEY]).path) == 7