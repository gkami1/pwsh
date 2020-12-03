from flask import Flask
app = Flask(__name__)

@app.route('/')
@app.route('/haba')
def hello_world():

    s = ["Hello, Haba!",
        "Hello, Arsen!",
        "Hello, Karim!"]

    out = "<pre>{}</pre>".format("\n".join(s))
    return out
