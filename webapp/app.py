#!/usr/bin/env python3
# TODO: Organize imports properly
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

# Deprecated in favour of gen_topo
# from generatetopo import odl_topo_builder

from gen_topo import generate_topology
from get_stats import Odl_Stat_Collector
from deviceInfo import odl_switch_info
from auxiliary import Webapp_Auxiliary
from forms import RegisterForm, GraphForm
from user_db import create_user_db
from gen_graphs import sql_graph_info
from topo_db import Topo_DB_Interactions
from get_flows import Odl_Flow_Collector

from authenticator import Authenticator
# TODO: Find PEP8 way of importing modules

import json

auth = Authenticator()


app = Flask(__name__)
# aux = Webapp_Auxiliary()
# odlControllerList = aux.device_scan()
# controllerIP = odlControllerList[0]
controllerIP = auth.working_creds['controller']['controller-ip']


app.secret_key = auth.working_creds['application']['secret_key']
app.config['MYSQL_HOST'] = auth.working_creds['database']['MYSQL_HOST']
app.config['MYSQL_USER'] = auth.working_creds['database']['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = auth.working_creds['database']['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = auth.working_creds['database']['MYSQL_DB']
app.config['MYSQL_CURSORCLASS'] = auth.working_creds['database']['CURSORCLASS']

# Init Mysql
mysql = MySQL(app)

# TODO: CLEAN UP CODE, MAKE INIT SCRIPT

@app.route("/")
def index():
    if 'logged_in' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route("/dashboard")
@is_logged_in
def dashboard():
    return render_template('home.html')


@app.route("/topology")
@is_logged_in
def topology():
    # Get SQL Auth & Creds
    yaml_db_creds = auth.working_creds['database']
    sql_creds = {"user": yaml_db_creds['MYSQL_USER'],
                 "password": yaml_db_creds['MYSQL_PASSWORD'],
                 "host": yaml_db_creds['MYSQL_HOST']
                 }
    db = auth.working_creds['database']['MYSQL_DB']

    parser = generate_topology(**sql_creds, db=db)
    return render_template('topo.html', topologyInfo=parser.fetch_topology())


@app.route("/node-stats")
@is_logged_in
def node_stats():
    o = Odl_Stat_Collector(controllerIP)
    return render_template('nodes.html', nodes=o.run())


@app.route("/flow-stats")
@is_logged_in
def flow_stats():
    cur = mysql.connection.cursor()
    # Repetitive code, move to sql tooling
    switch_list = []
    cur.execute("SELECT Node FROM nodes WHERE Type='switch';")
    switch_tuples = cur.fetchall()
    print(switch_tuples)
    for switch in switch_tuples:
        print(switch['Node'])
        switch_list.append(switch['Node'])
    cur.close()
    flow_dict = {}
    for switch in switch_list:
        o = Odl_Flow_Collector(controllerIP, switch)
        flow_dict[switch] = o.run()
    return render_template('flows.html', flow_dict=flow_dict)
    # print(flow_dict)


@app.route("/device-info")
@is_logged_in
def device_info():
    o = odl_switch_info(controllerIP)
    return render_template('deviceInfo.html', nodes=o.run())


@app.route("/controller")
@is_logged_in
def getControllerIP():
    # print(odlControllerList)
    return render_template('settings.html', odlIP=controllerIP)


@app.route("/topo-switch-stats", methods=['GET', 'POST'])
@is_logged_in
def getSwitchCounters():

    if (request.method == 'POST'):
        # Get SQL Auth & Creds
        yaml_db_creds = auth.working_creds['database']
        sql_creds = {"user": yaml_db_creds['MYSQL_USER'],
                        "password": yaml_db_creds['MYSQL_PASSWORD'],
                        "host": yaml_db_creds['MYSQL_HOST']}
        db = auth.working_creds['database']['MYSQL_DB']

        # Get counters for switch
        obj = Topo_DB_Interactions(**sql_creds, db=db)
        raw_json = request.get_json()
        key = ''.join(raw_json.keys())

        if (key == 'switch'):
            switch = raw_json['switch']
            counters = obj.switch_query(switch)
            return jsonify(counters)
        elif (key == 'edge'):
            edge = raw_json['edge']
            edgeinfo = obj.edge_query(edge)
            return jsonify(edgeinfo)
        elif (key == 'host'):
            host = raw_json['host']
            hostinfo = obj.host_query(host)
            return jsonify(hostinfo)
        elif (key == 'switch_throughput'):
            switch = raw_json['switch_throughput']
            return jsonify(obj.calculate_throughput(switch))

@app.route("/graphs", methods=['GET', 'POST'])
@is_logged_in
def graphs():
    graph_input = GraphForm(request.form)
    if request.method == 'POST' and graph_input.validate():
        node = graph_input.node.data
        interface = graph_input.interface.data
        time = graph_input.time.data

        graph_object = sql_graph_info(node, interface, time)
        data = graph_object.db_pull(node, interface, time)

        return render_template("graphs.html", form=graph_input, data=data)
    return render_template("graphs.html", form=graph_input)


@app.route("/switch/<string:switch_name>", methods=['GET'])
@is_logged_in
def switch_stats(switch_name):
    switch = switch_name
    # Get port counters using stat_collector
    pc = Odl_Stat_Collector(controllerIP)
    stats = pc.run()
    # Get flow stats
    node_pc = stats[switch]  # Only use this node's counters
    flow_collector = Odl_Flow_Collector(controllerIP, switch)
    flows = flow_collector.run()
    return render_template("switch_stats.html", sw=switch, node_pc=node_pc, flows=flows)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        submit_user(form)
        flash('You are now registered and can login', 'success')
        redirect(url_for('index'))

    return render_template('register.html', form=form)


def submit_user(form):
    """Helper function to submit user registration to the Database."""
    name = form.name.data
    email = form.email.data
    username = form.username.data
    password = sha256_crypt.encrypt(str(form.password.data))
    # TODO: Move into sql tooling object
    cur = mysql.connection.cursor()
    query = ("INSERT INTO users(name, email, username, password) " +
             f"VALUES('{name}', '{email}', '{username}', '{password}')")
    cur.execute(query)
    mysql.connection.commit()
    cur.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        # TODO: Use SQL tooling object once made.
        cur = mysql.connection.cursor()
        # Get user by username
        result = cur.execute(
            f"SELECT * FROM users WHERE username = '{username}'")

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in', 'sucess')
                return redirect(url_for('dashboard'))
            else:
                error = 'invalid login'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out')
    return redirect(url_for('login'))


if __name__ == "__main__":
    create_user_db()
    app.run(debug=True)
