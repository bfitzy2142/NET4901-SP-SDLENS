#!/usr/bin/env python3
# TODO: Organize imports properly
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from requests import get
from gen_topo import generate_topology
from get_stats import Odl_Stat_Collector
from deviceInfo import odl_switch_info
from forms import RegisterForm, GraphForm
from user_db import create_user_db
from gen_graphs import sql_graph_info
from topo_db import Topo_DB_Interactions
from get_flows import Odl_Flow_Collector
from flow_summary_graphs import pull_flow_graphs
from l2_flow_tracer import L2FlowTracer
from authenticator import Authenticator
from json import dumps

# TODO: Find PEP8 way of importing modules

import json

auth = Authenticator()


app = Flask(__name__)
# aux = Webapp_Auxiliary()
# odlControllerList = aux.device_scan()
# controllerIP = odlControllerList[0]
odl_user = auth.working_creds['controller']['username']
odl_password = auth.working_creds['controller']['password']
controllerIP = auth.working_creds['controller']['controller-ip']


app.secret_key = auth.working_creds['application']['secret_key']
app.config['MYSQL_HOST'] = auth.working_creds['database']['MYSQL_HOST']
app.config['MYSQL_USER'] = auth.working_creds['database']['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = auth.working_creds['database']['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = auth.working_creds['database']['MYSQL_DB']
app.config['MYSQL_CURSORCLASS'] = auth.working_creds['database']['CURSORCLASS']

# Init Mysql
mysql = MySQL(app)

# Get SQL Auth & Creds
yaml_db_creds = auth.working_creds['database']
sql_creds = {"user": yaml_db_creds['MYSQL_USER'],
             "password": yaml_db_creds['MYSQL_PASSWORD'],
             "host": yaml_db_creds['MYSQL_HOST']
            }
db = auth.working_creds['database']['MYSQL_DB']
flow_tracer = L2FlowTracer(**sql_creds, db=db)
topo = generate_topology(**sql_creds, db=db)
topo_db = Topo_DB_Interactions(**sql_creds, db=db)


# TODO: CLEAN UP CODE

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


@app.route('/l2_trace_flow/<string:source_ip>/<string:dest_ip>', methods=['GET'])
def rest_trace_flows(source_ip, dest_ip):
    flow_trace_results = flow_tracer.trace_flows(source_ip, dest_ip)
    return jsonify(flow_trace_results)

@app.route('/stp_topo')
def get_stp_topo():
    return jsonify(topo_db.build_stp_topology())


@app.route("/topology")
@is_logged_in
def topology():
    topologyInfo = topo.fetch_topology()
    return render_template('topo.html', topologyInfo=topologyInfo)


@app.route("/node-stats")
@is_logged_in
def node_stats():
    o = Odl_Stat_Collector(controllerIP)
    return render_template('nodes.html', nodes=o.run())


@app.route("/flow-stats")
@is_logged_in
def flow_stats():
    switch_list = get_switches()
    flow_dict = {}
    for switch in switch_list:
        o = Odl_Flow_Collector(controllerIP, switch)
        flow_dict[switch] = o.run()
    return render_template('flows.html', flow_dict=flow_dict)
    # print(flow_dict)


@app.route("/device-info")
@is_logged_in
def device_info():
    o = odl_switch_info(controllerIP, odl_user, odl_password)
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
        topo_db = Topo_DB_Interactions(**sql_creds, db=db)
        # Get counters for switch
        raw_json = request.get_json()
        key = ''.join(raw_json.keys())

        if (key == 'switch'):
            switch = raw_json['switch']
            counters = topo_db.switch_query(switch)
            return jsonify(counters)
        elif (key == 'edge'):
            edge = raw_json['edge']
            edgeinfo = topo_db.edge_query(edge)
            return jsonify(edgeinfo)
        elif (key == 'host'):
            host = raw_json['host']
            hostinfo = topo_db.host_query(host)
            return jsonify(hostinfo)
        elif (key == 'switch_throughput'):
            switch = raw_json['switch_throughput']
            return jsonify(topo_db.calculate_throughput(switch))

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
    render_kwargs = {}
    switch = switch_name
    render_kwargs["sw"] = switch
    # Get port counters using stat_collector
    pc = Odl_Stat_Collector(controllerIP)
    stats = pc.run()
    node_pc = stats[switch]  # Only use this node's counters
    render_kwargs["node_pc"] = node_pc
    # Get flow stats
    flow_collector = Odl_Flow_Collector(controllerIP, switch)
    flows = flow_collector.run()
    render_kwargs["flows"] = flows
    # Get port graph stats
    interface_graphs = {}
    time = '6'
    interfaces = switch_int_query(switch)
    switch_num = switch.replace("openflow:", "")
    for interface in interfaces:
        int_num = interface.replace(f"{switch}:", "")
        graph_object = sql_graph_info(switch_num, int_num, time)
        data = graph_object.db_pull(switch_num, int_num, time)
        interface_graphs[interface] = data
    render_kwargs["int_graphs"] = interface_graphs
    # Get flow summary stats
    flow_s_graphs = pull_flow_graphs(switch_num, time)
    render_kwargs["flow_s_graph"] = flow_s_graphs

    return render_template("switch_stats.html", **render_kwargs)


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


def get_switches():
    """Returns a list of switches stored in the DB."""
    cur = mysql.connection.cursor()
    # Repetitive code, move to sql tooling
    switch_list = []
    cur.execute("SELECT Node FROM nodes WHERE Type='switch';")
    switch_tuples = cur.fetchall()
    # print(switch_tuples)
    for switch in switch_tuples:
        # print(switch['Node'])
        switch_list.append(switch['Node'])
    cur.close()
    return(switch_list)


def get_switch_interfaces():
    """Returns a dictionary of switches w/ a list of interfaces
    from the DB."""
    switch_dict = {}
    switch_list = get_switches()
    for switch in switch_list:
        switch_dict[switch] = switch_int_query(switch)
    return switch_dict


def switch_int_query(switch):
    """Helper function that returns the list of interfaces for a
    given switch from the DB."""
    interface_list = []
    switch = switch.replace(':', '')
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT Interface FROM {switch}_interfaces;")
    interface_tuples = cursor.fetchall()
    for interface in interface_tuples:
        interface_list.append(interface['Interface'])
    return interface_list

@app.template_filter('tojson_pretty')
def to_pretty_json(value):
    return dumps(value, sort_keys=True, indent=4, separators=(',', ': '))

@app.route('/github')
def github():
    return redirect("https://github.com/sambo19/NET4901-SP")


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out')
    return redirect(url_for('login'))


if __name__ == "__main__":
    create_user_db()
    app.run(debug=True)
