from flask import Flask, request, abort, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from urllib.parse import urlparse
import short_url
import validators

# Set up the default Flask app
# Flask does a significant portion of the REST API legwork for us
# Flask's documentation is here: https://flask.palletsprojects.com/en/3.0.x/
# Could switch to FastAPI if we want a swagger page for ease of use...
app = Flask(__name__)

# Set up global variables. Simple array to store our encoded URLs, and a counter.
# A more robust solution would use a database instead of a simple array
url_store = []
url_counter = 0
# We also need a domain for our generated URLs
domain = "url-encoder"

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
    if request_obj.content_type != "application/json":
        abort(422)
    request_json = request_obj.get_json(force=True)
    # Make sure the payload has a url field
    if not request_json["url"]:
        abort(422)
    # Validate we're actually receiving a URL here, use validators library
    if not validators.url(request_json["url"]):
        abort(422)
    return request_json

# This makes an assumption that we're returning an http URL.
# Doesn't matter for this exercise, since we're not redirecting
# to the shortened URL
def make_encoded_url(id):
    return "http://{}/{}".format(domain, short_url.encode_url(id))

# Encodes a URL
# This should be a POST, since we'll be storing in memory
@app.route("/encode", methods=["POST"])
@limiter.limit("2/second")
def encode():
    request_json = handle_request_content(request)

    # Short_URL encodes an integer and returns an encoded value
    # Make it a minimum of 6 characters, just because that looks nicer
    encoded_id = short_url.encode(url_counter, min_length=6)

    # Store the URL in our store, then increment the counter
    url_store[url_counter] = request_json["url"]
    url_counter += 1
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
    
    parsed_id = urlparse(request_json["url"]).path

    decoded_id = short_url.decode(parsed_id)
    # We should make sure the id exists in our store as a final sanity check...
    if not 0 <= decoded_id < len(url_store):
        abort(404)
    return jsonify(url_store[decoded_id])

# make the script run Flask automatically when it starts
if __name__ == "__main__":
    app.run()