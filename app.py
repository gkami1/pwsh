from random import randint
from flask import Flask, render_template, request, abort, redirect, url_for
import requests
import json

proxies = {
    "http": "http://192.168.2.1:3128",
    "https": "http://192.168.2.1:3128"
}

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
    out = """<h1>debug info</h1><p>city={} category={} ad={}</p><h1>{}</h1><p>{}</p>""".format(city, category, ad,
                                                                                               category[1], city[1])
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


@app.route('/task3/cf/profile/<handle>/page/<page_number>/')
def cfsingle(handle, page_number):
    try:
        ans = list()
        url = 'https://codeforces.com/api/user.status?handle={}&from=1&count=100'
        r = requests.get(url.format(handle), proxies=proxies)
        result = r.json()['result']
        k = list()
        for i in result:
            k.append((str(i['creationTimeSeconds']), i['problem']['name'], i['verdict']))
            if len(k) == 25:
                ans.append(k.copy())
                k.clear()
        if len(k) != 0:
            ans.append(k.copy())
        if len(ans) < int(page_number) or int(page_number) <= 0:
            abort(404)
        links = list()
        links.append(("Previous", "/task3/cf/profile/{}/page/{}/".format(handle, int(page_number) - 1)))
        for i in range(len(ans)):
            links.append((i + 1, "/task3/cf/profile/{}/page/{}/".format(handle, str(i + 1))))
        links.append(("Next", "/task3/cf/profile/{}/page/{}/".format(handle, int(page_number) + 1)))
        pagination = render_template("kek.html", links=links, current_page=int(page_number),
                                     rows=ans[int(page_number) - 1], count_of_pages=len(ans))
        return pagination
    except:
        return "<h1>НЕТ</h1>"


@app.route('/task3/cf/profile/<handle>/')
def redir(handle):
    return redirect(url_for('kek.html', handle=handle, page_number="1"))



@app.route('/task3/cf/top/')
def sftop():
    data = request.args.copy()
    url = 'https://codeforces.com/api/user.info?handles={}'
    names = data['handles']
    ans = list()
    try:
        с = data['orderby']
    except:
        с = "handle"
    for i in names.split('|'):
        handle = str(requests.get(url.format(i), proxies=proxies).json()['result'][0]["handle"])
        ans.append(['/task3/cf/profile/{}/'.format(handle), handle,
                    str(requests.get(url.format(i)).json()['result'][0]["rating"])])
    y, reverse = (-2, False) if с == "handle" else (-1, True)
    values = sorted(ans, key=lambda x: x[y], reverse=reverse)
    return render_template("Tables.html", values=values)


@app.errorhandler(404)
def page_not_found():
    return render_template("404.html")


app.run()
