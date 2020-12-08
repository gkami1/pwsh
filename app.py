from flask import Flask
from random import randint
import requests


app = Flask(__name__)

@app.route('/')
@app.route('/haba/')
def hello_world():

    s = ["Hello, Haba!",
        "Hello, Arsen!",
        "Hello, Karim!"]

    out = "<pre>{}</pre>".format("\n".join(s))
    return out


@app.route('/task1/random/')
def rand():
    return "Haba's mark is {}".format(str(randint(1, 5)))

@app.route('/task1/i_will_not/')
def i_will_not():
ans = ['<ul type="disc" id="blackboard">']
for i in range(100):
ans.append('<li>I will not waste time</li>')
ans.append('</ul>')
return "<pre>{}</pre>".format(''.join(ans))
