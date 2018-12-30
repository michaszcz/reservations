from config import settings
from flask import Flask

app = Flask(__name__)
app.secret_key = settings.SECRET
