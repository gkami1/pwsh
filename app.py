from random import randint
import Flask
import requests
import inflect
import json

app = Flask(__name__)

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

@app.route('/')
def menu():
    ans = ['<ul type="disc" id="menu">',
           '<li><a href="/task1/random/">/task1/random/</a></li>',
           '<li><a href="/task1/i_will_not/">/task1/i_will_not/</a></li>',
           '</ul>']
    return "<pre>{}</pre>".format(''.join(ans))

@app.route('/task2/avito/<city>/<category>/<ad>/')
def avito(city, category, ad):
    out = """<h1>debug info</h1><p>city={} category={} ad={}</p><h1>{}</h1><p>{}</p>""".format(city, category, ad, category[1], city[1])
    return out

@app.route('/task2/cf/profile/<username>')
def codeforces(username):
    url = 'https://codeforces.com/api/user.info?handles={}'.format(username)
    ans = '<table id="stats" border="1"><tr>{}</tr><tr>{}</tr></table>'
    first = '<td>User</td><td>Rating</td>'
    second = '<td>{}</td><td>{}</td>'
    r = requests.get(url)
    s = r.json()
    if s['status'] != 'OK':
        return 'User not found'
    return ans.format(first, second.format(username, str(s['result'][0]['rating'])))

@app.route('/task2/num2words/<num>/')
def numc(num):
    if int(num) < 0 or int(num) > 999:
        return json.dumps({"status": "FAIL"})
    else:
        p = inflect.engine()
        l = p.number_to_words(int(num))
        if 'and' in l:
            l = ''.join(l.split(' and'))
        if '-' in l:
            l = ' '.join(l.split('-'))
        if int(num) % 2 == 0:
            n = True
        else:
            n = False
        return json.dumps({"status": "OK", "number": int(num), "isEven": n, "words": str(l)})
