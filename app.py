import requests
from uuid import uuid4
from flask import Flask, render_template, redirect, url_for
from flask import Flask, request
from trending import get_trending
from datetime import datetime, timedelta
import time
import waitress
import unicodedata
import json
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


@app.before_request
def before_request_func():
    logging.info(f"From remote addr: {request.remote_addr} for url: {request.url.split(':')[-1]}")

@app.route('/')
def trending():
    rid = str(uuid4()).split("-")[0]
    logging.info(f"{datetime.utcnow() + timedelta(hours=5, minutes=30)}: {rid} Received new content request.")
    s = time.time()
    info = get_trending()
    e = time.time()
    logging.info(f"{datetime.utcnow() + timedelta(hours=5, minutes=30)}: {rid} Took {e-s} seconds.")
    return render_template('show.html', info=info['data'])
    # return res

if __name__ == "__main__":
    app.debug = False
    port = int(os.environ.get('PORT', 33507))
    waitress.serve(app, port=port)
