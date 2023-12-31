import pytest
import validators
from urllib.parse import urlparse
from main import app
import consts
import testhelpers

def test_root_returns_404(client):
    response = client.get("/")
    assert response.status_code == 404

# Make sure encode works, generically
def test_encode_valid_url(client):
    response = client.post("/encode", json={
        "url": "https://www.google.com"
    })
    assert response.status_code == 200
    assert validators.url(testhelpers.extract_response_data(response))
    # We can't determine that the id is "correct", but short_url's tests
    # should cover that, so we just need to make sure we're returning the right format
    assert testhelpers.verify_id_len(response)

# Make sure encode doesn't return the same id for two same urls
def test_encode_already_encoded_url(client):
    response = client.post("/encode", json={
        "url": "https://www.google.com"
    })
    first_id = testhelpers.extract_short_id(response)
    response_two = client.post("/encode", json={
        "url": "https://www.google.com"
    })
    second_id = testhelpers.extract_short_id(response_two)
    assert first_id != second_id

# Make sure encode doesn't return the same id for two different urls
# Not particularly different than the previous test, but still valid
def test_encode_unique_urls(client):
    response = client.post("/encode", json={
        "url": "https://www.google.com"
    })
    first_id = testhelpers.extract_short_id(response)
    response_two = client.post("/encode", json={
        "url": "https://www.bing.com"
    })
    second_id = testhelpers.extract_short_id(response_two)
    assert first_id != second_id

# Test error code for invoking /encode with not a url
def test_encode_not_a_url(client):
    response = client.post("/encode", json={
        "url": "hello there"
    })
    assert response.status_code == 422

# Test error code for invoking /encode with not json
def test_encode_request_with_wrong_content_type(client):
    response = client.post("/encode", data = "hello there")
    assert response.status_code == 415

# Test error code for invoking /encode with no data
def test_encode_request_without_payload(client):
    response = client.post("/encode")
    assert response.status_code == 400

# Make sure decode works in a normal scenario
def test_decode_encoded_url(client):
    original_url = "https://www.google.com"
    encode_response = client.post("/encode", json={
        "url": original_url
    })
    decode_response = client.post("/decode", json={
        "url": encode_response.get_json(force=True)[consts.REQUEST_KEY]
    })
    assert testhelpers.extract_response_data(decode_response) == original_url

# Make up an "encoded" url, make sure we get a 418 on attempted decode
def test_decode_url_with_bad_id(client):
    decode_response = client.post("/decode", json={
        "url": "http://{}/{}".format(consts.DOMAIN, "ms34i2")
    })
    assert decode_response.status_code == 418

# Make up an encoded URL using the skipped id, since it will never be in the cache.
def test_decode_not_encoded_url(client):
    decode_response = client.post("/decode", json={
        "url": "http://{}/{}".format(consts.DOMAIN, "mmmmmm")
    })
    assert decode_response.status_code == 404

# Test status code for attempting to decode not a url
def test_decode_not_a_url(client):
    response = client.post("/decode", json={
        "url": "hello there"
    })
    assert response.status_code == 422

# Make sure decode doesn't work if extra stuff is on the end of the url
def test_decode_url_with_query_params(client):
    encode_response = client.post("/encode", json={
        "url": "https://www.google.com"
    })
    decode_response = client.post("/decode", json={
        "url": encode_response.get_json(force=True)[consts.REQUEST_KEY] + "?someextrastuff"
    })
    assert decode_response.status_code == 400

# Make sure decode doesn't work if extra stuff is on the end of the url
def test_decode_url_with_fragment(client):
    encode_response = client.post("/encode", json={
        "url": "https://www.google.com"
    })
    decode_response = client.post("/decode", json={
        "url": encode_response.get_json(force=True)[consts.REQUEST_KEY] + "#someextrastuff"
    })
    assert decode_response.status_code == 400

# Make sure decode validates a payload
def test_decode_request_without_payload(client):
    response = client.post("/decode")
    assert response.status_code == 400

# Make sure decode expects json, not text
def test_decode_request_with_wrong_content_type(client):
    response = client.post("/decode", data = "hello there")
    assert response.status_code == 415

# make sure the limiter config is working
def test_limiter_returns_429(client):
    encode_response_one = client.post("/encode", json={
        "url": "https://www.google.com"
    })
    encode_response_two = client.post("/encode", json={
        "url": "https://www.bing.com"
    })
    encode_response_three = client.post("/encode", json={
        "url": "https://www.github.com"
    })
    assert encode_response_one.status_code == 200
    assert encode_response_two.status_code == 200
    assert encode_response_three.status_code == 429