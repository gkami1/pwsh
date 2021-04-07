from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from email.message import EmailMessage
import random as rnd, requests, json, os, psycopg2, smtplib
from datetime import datetime

database_url = os.environ['DATABASE_URL']
conn = psycopg2.connect(database_url)
cur = conn.cursor()

app = Flask(__name__)
app.secret_key = 'kamilkrasava'
app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1)
chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def is_human(captcha_response):
    if session.get('debug_mod', 'disabled') == 'enable':
        return True
    payload = {'response': captcha_response, 'secret': os.environ['secret_key']}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']


@app.route('/task5/test/<debug_mod>/')
def enable(debug_mod):
    session['debug_mod'] = debug_mod
    return redirect(url_for('sign_up1'))


@app.route('/task5/sign-up/', methods=['GET', 'POST'])
def sign_up1():
    if request.method == "GET":
        return render_template("sign-up1.html", sitekey=os.environ['site_key'])
    email = request.form['email']
    captcha_response = request.form['g-recaptcha-response']
    if is_human(captcha_response):
        cur.execute(f"SELECT COUNT(*) FROM users WHERE email = '{email}'")
        count = cur.fetchall()[0][0]
        if count > 0:
            return render_template("sign-up1.html", sitekey=os.environ['site_key'], error=True)
        addr = ''.join([rnd.choice(chars) for i in range(8)])
        msg = EmailMessage()
        msg.set_content(f'link: https://sosiskak.herokuapp.com/task5/verification/{addr}')
        msg['Subject'] = 'Activation link'
        msg['From'] = 'no-reply@hwr1.herokuapp.com'
        msg['To'] = email
        with smtplib.SMTP(host='b.li2sites.ru', port=30025) as s:
            s.send_message(msg)
        cur.execute(
            f"INSERT INTO users (email, password, status, secret_code) VALUES ('{email}', '-', 'not_verified', '{addr}')")
        conn.commit()
        return render_template("sign-up1.html", success=True)


@app.route('/task5/verification/<secret>', methods=['GET', 'POST'])
def verification(secret):
    cur.execute(f"SELECT COUNT(*) FROM users WHERE secret_code = '{secret}'")
    count = cur.fetchall()[0][0]
    if count == 0:
        return '<b>Link not found!</b>'
    cur.execute(f"SELECT email FROM users WHERE secret_code = '{secret}'")
    session['email'] = cur.fetchall()[0][0]
    cur.execute(f"UPDATE users SET status = 'verificated'")
    conn.commit()
    return redirect(url_for('sign_up2'))


@app.route('/task5/sign-up2/', methods=['GET', 'POST'])
def sign_up2():
    if session.get('email', None) is None:
        return redirect('sig_up1')
    email = session['email']
    if request.method == 'GET':
        return render_template("sign-up2.html", email=email)
    password1 = request.form['password']
    password2 = request.form['password2']
    if password1 != password2:
        return render_template("sign-up2.html", email=email, error=True)
    hash = generate_password_hash(password1)
    cur.execute(f"UPDATE users SET status = 'registered', password = '{hash}'")
    conn.commit()
    return redirect(url_for('sign_in'))


@app.route('/task5/sign-in/', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'GET':
        return render_template("sign-in.html")
    email = request.form['email']
    password = request.form['password']
    cur.execute(f"SELECT COUNT(*) FROM users WHERE email = '{email}'")
    count = cur.fetchall()[0][0]
    if count == 0:
        return render_template("sign-in.html", error=True)
    cur.execute(f"SELECT password FROM users WHERE email = '{email}'")
    password_hash = cur.fetchall()[0][0]
    if not check_password_hash(password_hash, password):
        return render_template("sign-in.html", error=True)
    time = datetime.now()
    session['email'] = email
    cur.execute(f"INSERT INTO ips (email, ip, time) VALUES ('{email}', '{request.remote_addr}', '{time}')")
    conn.commit()
    session['auth'] = 'logged'
    return redirect(url_for('account'))


@app.route('/task5/sign-out/')
def sign_out():
    session['auth'] = 'not_logged'
    session['email'] = '-'
    return redirect(url_for('sign_in'))


@app.route('/task5/work/', methods=['GET', 'POST'])
def work():
    if session.get('auth', 'not_logged') != 'logged':
        return redirect(url_for('sign_in'))
    email = session['email']
    if request.method == 'POST':
        n = request.form['n']
        time = str(datetime.now())
        cur.execute(
            f"INSERT INTO works (email, n, p, q, status, time_submitted, time_elapsed) VALUES ('{email}', '{n}', '-', '-', 'Queued', '{datetime.now()}', '-')")
        conn.commit()
    cur.execute(f"SELECT time_submitted, n, p, q, status, time_elapsed FROM works WHERE email = '{email}'")
    works = cur.fetchall()
    return render_template('work.html', works=works)


@app.route('/task5/account/')
def account():
    if session.get('auth', 'not_logged') != 'logged':
        return redirect(url_for('sign_in'))
    email = session['email']
    cur.execute(f"SELECT ip, time FROM ips WHERE email = '{email}'")
    ips = cur.fetchall()
    ips.reverse()
    return render_template("account.html", ips=ips)


if __name__ == '__main__':
    app.run()
