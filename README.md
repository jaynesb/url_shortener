# url_shortener
A URL Shortener wrapped in an API. This was written using Python 3.12, but should be compatible with other 3.x versions of Python.

## Requirements
This python program depends on a number of other python modules to function, especially Flask. To install these, run the following in your terminal:

```
pip install -r requirements.txt
```

Note: if using 

## Running the app
This is a very simple python application. To run it, execute the following in your terminal:

```
python main.py
```
This hosts the application on `localhost` at port `5000`.

To stop the server, simply `Ctrl+C` in the terminal hosting the app.


## Using the app
The API exposes two endpoints:
- `/encode`
- `/decode`

Both endpoints expect the POST http method, and a simple json payload containing a URL. Both endpoints are rate-limited to 2 requests per second.

### Encode
The `/encode` method expects a json payload in the following format.
```
{
    "url": "protocol://some-url.here/maybe/with/extra/stuff?or-not
}
```

The following is a valid example of invoking the `/encode` endpoint using `curl`:
```
curl -X POST http://localhost:5000/encode -H "content-type: application/json" -d '{"url":"https://www.google.com"}'
```
Or with `Powershell`:
```
Invoke-WebRequest -Method POST -URI http://localhost:5000/encode -ContentType 'application/json' -Body '{"url":"https://www.google.com"}' 
```

Shortened URLs are persisted in-memory only. Restarting the application will reset the shortened URLs returned by the `/encode` endpoint.

### Decode
The `/decode` method expects a json payload in the following format.
```
{
    "url": "<a url returned by the /encode endpoint>"
}
```

The following is a valid example of invoking the `/decode` endpoint using `curl`
```
curl -X POST http://localhost:5000/decode -H "content-type: application/json" -d '{"url":"http://url-encoder.test/m867nv"}'
```
Or with `Powershell`:
```
Invoke-WebRequest -Method POST -URI http://localhost:5000/decode -ContentType 'application/json' -Body '{"url":"http://url-encoder.test/m867nv"}' 
```

## Troubleshooting

If `/encode` or `/decode` are invoked incorrectly, they may return various `4xx` error codes. Below is a quick reference for the more likely ones.
| Error Code | Likely Cause                                                                                                        |
| :--------: | ------------------------------------------------------------------------------------------------------------------- |
|   `400`    | This occurs when a payload is not provided to the request, or cannot be processed for some reason.                  |
|   `404`    | This occurs when decoding an id that matches the short_url algorithm, but isn't in the cache.                       |
|   `415`    | This occurs when the payload content type is not JSON.                                                              |
|   `418`    | This occurs when a valid URL is sent to be decoded with an id that doesn't match short_url's algorithm.             |
|   `422`    | This occurs when the JSON payload does not contain a "url" property, or when the "url" property is not a valid URL. |