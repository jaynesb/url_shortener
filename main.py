from flask import Flask, request, abort, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from urllib.parse import urlparse
import short_url
import validators

# Set up the default Flask app
# Flask does a significant portion of the REST API legwork for us
# Flask's documentation is here: https://flask.palletsprojects.com/en/3.0.x/
# Could switch to FastAPI if we want a swagger page for ease of use...
app = Flask(__name__)
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app)

# String consts... maybe put these elsewhere
COUNTER_KEY = "url_counter"
DOMAIN = "url-encoder.test"
REQUEST_KEY = "url"

# Global variables weren't a functioning solution. Let's try a cache instead.
# We're going to start the cache at 1, since the cache at 0 makes the first encoded result weird
cache.set(COUNTER_KEY, 1)
# We also need a DOMAIN for our generated URLs

# Set up Flask Limiter for rate limiting (see https://flask-limiter.readthedocs.io/en/stable/)
# This will use in-memory storage
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Something to quickly validate if we've received a valid payload
# Since we want to return json, we might as well expect json
# This could always be expanded later
def handle_request_content(request_obj):
    print(request_obj.content_type)
    if request_obj.content_type != "application/json":
        abort(415)
    request_json = request_obj.get_json(force=True)
    print(request_json)
    # Make sure the payload has a url field
    if not request_json[REQUEST_KEY]:
        abort(422)
    # Validate we're actually receiving a URL here, use validators library
    if not validators.url(request_json[REQUEST_KEY]):
        abort(422)
    return request_json

# This makes an assumption that we're returning an http URL.
# Doesn't matter for this exercise, since we're not redirecting
# to the shortened URL
def make_encoded_url(id):
    encoded_url = "http://{}/{}".format(DOMAIN, id)
    print(encoded_url)
    return encoded_url

def increment_counter():
    current_count = int(cache.get(COUNTER_KEY))
    cache.set(COUNTER_KEY, current_count + 1)

# Encodes a URL
# This should be a POST, since we'll be storing in memory
@app.route("/encode", methods=["POST"])
@limiter.limit("2/second")
def encode():
    request_json = handle_request_content(request)

    # Short_URL encodes an integer and returns an encoded value
    # Make it a minimum of 6 characters, just because that looks nicer
    encoded_id = short_url.encode_url(cache.get(COUNTER_KEY), 6)
    print("Encoded id: " + encoded_id)
    # Store the URL in our store, then increment the counter
    # I considered checking if we've already shortened a URL for the requested, but that
    # feels like it'd be too computationally intensive and ultimately not worth it
    cache.set(cache.get(COUNTER_KEY), request_json[REQUEST_KEY])
    increment_counter()
    return jsonify(make_encoded_url(encoded_id))

# Decodes a URL
# This should be a QUERY, since we expect our URL to be in the request body
# Fun stuff about QUERY, since it's new-ish: 
# https://www.ietf.org/archive/id/draft-ietf-httpbis-safe-method-w-body-02.html
@app.route("/decode", methods=["QUERY"])
@limiter.limit("2/second")
def decode():
    request_json = handle_request_content(request)
    
    # parse the returned URL for our encoded id and decode it
    # the path includes the leading slash, substr that out
    parsed_id = urlparse(request_json[REQUEST_KEY]).path
    # Make sure we're not being provided too long a key
    # Could could possibly do this with regex for a slightly more robust solution?
    if len(parsed_id) > 7:
        abort(400)
    parsed_id = parsed_id[1:]
    print("Id to decode: " + parsed_id)
    decoded_id = short_url.decode_url(parsed_id)
    # We should make sure the id exists in our store as a final sanity check...
    if not cache.has(decoded_id):
        abort(404)
    return jsonify(cache.get(decoded_id))

# make the script run Flask automatically when it starts
if __name__ == "__main__":
    app.run()