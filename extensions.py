from flask import (
    Flask,
    Blueprint,
    session,
    redirect,
    request,
    render_template,
    url_for
)
import os


app = Flask(__name__)