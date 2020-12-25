from flask import Flask, redirect, url_for, abort, render_template, request
from random import randint
import json
import requests

app = Flask(__name__)


@app.route('/task3/cf/profile/<handle>/page/<page_number>/')
def profiles(handle, page_number):
    try:
        ans = list()
        url = 'https://codeforces.com/api/user.status?handle={}&from=1&count=100'
        r = requests.get(url.format(handle))
        result = r.json()['result']
        p = list()
        for i in result:
            p.append((str(i['creationTimeSeconds']), i['problem']['name'], i['verdict']))
            if len(p) == 25:
                ans.append(p.copy())
                p.clear()
        if len(p) != 0:
            ans.append(p.copy())
        if len(ans) < int(page_number) or int(page_number) <= 0:
            abort(404)
        links = list()
        links.append(("Previous", "/task3/cf/profile/{}/page/{}/".format(handle, int(page_number) - 1)))
        for i in range(len(ans)):
            links.append((i + 1, "/task3/cf/profile/{}/page/{}/".format(handle, str(i + 1))))
        links.append(("Next", "/task3/cf/profile/{}/page/{}/".format(handle, int(page_number) + 1)))
        pagination = render_template("kek.html", links=links, current_page=int(page_number), rows=ans[int(page_number) - 1], count_of_pages=len(ans))
        return pagination
    except:
        return "<h1>НЕТУ</h1>"


@app.route('/task3/cf/profile/<handle>/')
def redir(handle):
    return redirect(url_for('kek', handle=handle, page_number="1"))


@app.route('/task3/cf/top/')
def top():
    data = request.args.copy()
    url = 'https://codeforces.com/api/user.info?handles={}'
    names = data['handles']
    ans = list()
    try:
        orderby = data['orderby']
    except:
        orderby = "handle"
    for i in names.split('|'):
        handle = str(requests.get(url.format(i)).json()['result'][0]["handle"])
        ans.append(['/task3/cf/profile/{}/'.format(handle), handle, str(requests.get(url.format(i)).json()['result'][0]["rating"])])
    y, reverse = (-2, False) if orderby == "handle" else (-1, True)
    values = sorted(ans, key=lambda x: x[y], reverse=reverse)
    return render_template("Tables.html", values=values)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("nf.html"), 404

app.run()
