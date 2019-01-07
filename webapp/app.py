#!/usr/bin/env python3

from flask import Flask, render_template
import os
from generatetopo import odl_topo_builder
import getip    
from get_stats import odl_stat_collector

app = Flask(__name__)
odlControllerList = getip.findController()

@app.route("/")
def index():
    return render_template('home.html')
    
@app.route("/topology")
def topology():
    parser=odl_topo_builder(odlControllerList[0])
    return render_template('topo.html', topologyInfo=parser.fetchTopology())
    """
    result = generatetopo.run()
    
    if result == 1:
        return render_template('topo-failure.html')
    elif result == 0:
        return render_template('displaytopo.html')
    """

@app.route("/node-stats")
def node_stats():
    o = odl_stat_collector(odlControllerList[0])
    return render_template('nodes.html', nodes = o.run())
    
    
        
@app.route("/controller")
def getControllerIP():
    print(odlControllerList)
    return render_template('settings.html', odlList = odlControllerList)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)

