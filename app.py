from flask import Flask, redirect, url_for, abort, render_template, request
from random import randint
import json
import requests

app = Flask(__name__)


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


@app.route('/')
def menu():
    ans = ['<ul type="disc" id="menu">',
           '<li><a href="/task1/random/">/task1/random/</a></li>',
           '<li><a href="/task1/i_will_not/">/task1/i_will_not/</a></li>',
           '</ul>']
    return "<pre>{}</pre>".format(''.join(ans))


@app.route('/task2/avito/<city>/<category>/<announcement>')
def avito(city, category, announcement):
    letters = list('qwertyuiopasdfghjklzxcvbn m')
    product = announcement.split('_')[:-1]
    ans = list()
    ans.append('<h1>debug info</h1>')
    ans.append('<p>city={} category={} ad={}</p>'.format(city, category, announcement))
    ans.append('<h1>{}</h1>'.format(' '.join([i.capitalize() for i in product])))
    ans.append('<p>{}</p>'.format(product[0][0]))
    return '\n'.join(ans)


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


@app.route('/task2/num2words/<num>')
def num_words(num):
    numbers = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    decimal_numbers = ['twenty', 'thirty', 'forty', 'fifty',
                       'sixty', 'seventy', 'eighty', 'ninety']
    bad_numbers = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen',
                   'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
    ans = dict()
    if num.isdigit():
        num = int(num)
        if num > 999 or num < 0:
            status = 'FAIL'
        else:
            status = 'OK'
    else:
        status = 'FAIL'
    ans['status'] = status
    if status == 'FAIL':
        return json.dumps(ans)
    ans['number'] = num
    ans['isEven'] = False if num % 2 != 0 else True

    words = list()
    if num // 100 > 0:
        words.append(numbers[num // 100])
        words.append('hundred')
    second_num = num // 10 - num // 100 * 10
    if second_num == 1:
        words.append(bad_numbers[num % 10])
    else:
        if second_num != 0:
            words.append(decimal_numbers[second_num - 2])
        if num % 10 != 0:
            words.append(numbers[num % 10])
    ans['words'] = ' '.join(words)
    return json.dumps(ans)


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
