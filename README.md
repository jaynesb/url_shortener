# url_shortener
A URL Shortener wrapped in an API. This was written using Python 3.12, but should be compatible with other 3.x versions of Python.

## Requirements
This python program depends on a number of other python modules to function, especially Flask. To install these, run the following in your terminal:
```bash
pip install -r requirements.txt
```

curl -X POST http://localhost:5000/encode -H "content-type: application/json" -d '{"url":"https://www.google.com"}'
curl -X POST http://localhost:5000/decode -H "content-type: application/json" -d '{"url":"<insert URL from encode command>"}'