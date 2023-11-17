from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Set up the default Flask app
# Flask does a significant portion of the REST API legwork for us
# Flask's documentation is here: https://flask.palletsprojects.com/en/3.0.x/
app = Flask(__name__)

# Set up Flask Limiter for rate limiting (see https://flask-limiter.readthedocs.io/en/stable/)
# This will use in-memory storage
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Encodes a URL
# This should be a POST, since we'll be storing in memory
@app.route("/encode", methods=["POST"])
@limiter.limit("2/second")
def encode():
    return "foo"

# Decodes a URL
# This should be a QUERY, since we expect our URL to be in the request body
# Fun stuff about QUERY, since it's new-ish: 
# https://www.ietf.org/archive/id/draft-ietf-httpbis-safe-method-w-body-02.html
@app.route("/decode", methods=["QUERY"])
@limiter.limit("2/second")
def decode():
    return "bar"

if __name__ == "__main__":
    app.run()