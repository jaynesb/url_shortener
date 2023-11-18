from urllib.parse import urlparse
import consts
import json

def extract_response_data(response):
    response_payload = json.loads(response.get_data(as_text=True))
    return response_payload[consts.REQUEST_KEY]

# Rip the id from a short URL
# Returns string
def extract_short_id(response):
    return urlparse(extract_response_data(response)).path[1:]

# Check the length of the id on a returned short url
# Should be 7 characters (one preceding '/' and 6 ascii)
# Returns boolean
def verify_id_len(response):
    return len(urlparse(extract_response_data(response)).path) == 7