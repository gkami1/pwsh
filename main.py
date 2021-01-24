from flask import Flask, render_template, request, redirect, url_for
import requests
import json
import random as rnd
from random import getrandbits, shuffle
import string

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
        pagination = render_template("profiles.html", links=links, current_page=int(page_number), rows=ans[int(page_number) - 1], count_of_pages=len(ans))
        return pagination
    except:
        return "<h1>НЕТУ</h1>"
    
@app.route('/task3/cf/profile/<handle>/')
def cf(handle):
    return redirect(url_for('profiles', handle=handle, page_number=1))


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
    return render_template("table.html", values=values)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("not_found.html"), 404

app = Flask(__name__)

s = rnd.choice(string.ascii_letters) + rnd.choice(string.ascii_letters)

value_ = {
    "token": "4UffYATBFJOqTiy9aJDnajwBa5XrSTfy",
    "secret": "sufgsfsugfssef3432424242423424242",
    "command": "set",
    "key": "",
    "value": ""
}
data_set = value_

key_ = {
    "token": "4UffYATBFJOqTiy9aJDnajwBa5XrSTfy",
    "secret": "sufgsfsugfssef3432424242423424242",
    "command": "get",
    "key": ""
}
data_get = key_

games_info = {}


@app.route("/task4/santa/create", methods=["GET", "POST"])
def screate():
    if request.method == "POST":
        create_form = request.form
        game_name = str(create_form["name_of_game"])
        game_code = str(getrandbits(64)) + game_name
        game_code_secret = str(getrandbits(64))
        link_for_player = "/task4/santa/play/{link}".format(link=game_code)
        link_for_organizers = "/task4/santa/toss/{link}/{secret}".format(link=game_code, secret=game_code_secret)
        information = {"name": game_name, "code": game_code, "secret": game_code_secret, "play": link_for_player,
                "organize": link_for_organizers, "active": "True", "players": []}
        data_set["key"] = game_code
        data_set["value"] = json.dumps(information)
        requests.post("https://arsenwisheshappy2021.herokuapp.com/query", data=data_set)
        return render_template("screate_post.html", form=create_form, player_link=link_for_player,
                               organizer_link=link_for_organizers)
    else:
        return render_template('screate_form.html')


@app.route("/task4/santa/play/<link>", methods=["GET", "POST"])
def play(link):
    if request.method == "GET":
        link_after_post = '/task4/santa/play/{link}'.format(link=link)
        data_get["key"] = link
        r_get = requests.post("https://arsenwisheshappy2021.herokuapp.com/query", data=data_get)
        game_info = json.loads(r_get.text)
        if game_info["active"] == "False":
            error = True
        else:
            error = False
        return render_template("begintoplay.html", error_start=error, link_after_post=link_after_post)
    elif request.method == "POST" and request.form["name"].strip() == '':
        link_after_post = '/task4/santa/play/{link}'.format(link=link)
        return render_template("begintoplay.html", error_name=True, link_after_post=link_after_post)
    elif request.method == "POST":
        player_form = request.form
        player_name = str(player_form["name"])
        data_get["key"] = link
        r_get = requests.post("https://arsenwisheshappy2021.herokuapp.com/query", data=data_get)
        game_info = json.loads(r_get.text)
        game_info["players"].append(player_name)
        data_set["key"] = link
        data_set["value"] = json.dumps(game_info)
        requests.post("https://arsenwisheshappy2021.herokuapp.com/query", data=data_set)
        return render_template("play_success.html", name=player_name)


@app.route("/task4/santa/toss/<link>/<secret>", methods=["GET", "POST"])
def secreet(link, secret):
    if request.method == "POST":
        data_get["key"] = link
        r_get = requests.post("https://arsenwisheshappy2021.herokuapp.com/query", data=data_get)
        game_info = json.loads(r_get.text)
        players_list = game_info["players"]
        shuffle(players_list)
        pairs = {}
        pairs[players_list[0]] = players_list[-1]
        for i in range(1, len(players_list) // 2):
            pairs[players_list[i]] = players_list[-i - 1]
        game_info["active"] = "False"
        data_set["key"] = link
        data_set["value"] = json.dumps(game_info)
        requests.post("https://arsenwisheshappy2021.herokuapp.com/query", data=data_set)
        list_of_keys = list(pairs.keys())
        return render_template("toss_finished.html", pairs=pairs, list_of_keys=list_of_keys)
    elif request.method == "GET":
        data_get["key"] = link
        r_get = requests.post("https://arsenwisheshappy2021.herokuapp.com/query", data=data_get)
        game_info = json.loads(r_get.text)
        if game_info["active"] == "False":
            error_f = True
        else:
            error_f = False
        players_list = game_info["players"]
        if len(players_list) == 0 or len(players_list) % 2 == 1:
            error_q = True
        else:
            error_q = False
        link_2 = "/task4/santa/toss/{link}/{secret}".format(link=link, secret=secret)
        return render_template("toss_started.html", error_q=error_q, error_f=error_f, players_list=players_list,
                               link_2=link_2)
