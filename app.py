#-*- coding: utf-8 -*-
"""
Dan web
"""

import os
import json

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

here = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    """
    Dan website index page."""
    return render_template("index.html")
    

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 1:
        host = sys.argv[1]
    else:
        host = "127.0.0.1"
    PORT = 8000
    app.debug = True
    app.run(port=PORT, host=host)
