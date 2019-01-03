import requests
import re
import os
import getip

# OpenDayLight RESTCONF API parser for topology information

odlList=getip.findController()
controllerIP=odlList[0]


odl_topo_url = 'http://'+ controllerIP +':8181/restconf/operational/network-topology:network-topology'

#Probably want to find better way to use creds. I.E (not in clear text in this python script)  
odl_username = 'admin'
odl_password = 'admin'

#List to store the devices in the topology
deviceList = []
#List to store the edges (links) between nodes
connectionList = []


def fetchTopology():
    # fetch state of topology from ODL REST API.
    response = requests.get(odl_topo_url, auth=(odl_username, odl_password))
    # Find information about nodes in retrieved JSON file.

    for nodes in response.json()['network-topology']['topology']:
        if re.match(r"^flow:[0-9]+$", nodes['topology-id']):
            
            # Walk through all node information.
            node_info = nodes['node']
            # Look for MAC and IP addresses in node information.
            
            for node in node_info:
                deviceList.append(node['node-id'])
                

    # get links between switches

    for links in response.json()['network-topology']['topology'][2]['link']:
       # if re.match(r"openflow:", links['link-id'][]):
        connection = {"src": links['source']['source-node'],
                      "dst": links['destination']['dest-node']}
        connectionList.append(connection)

        # remove redundant connections
        for x in range(len(connectionList)):
            for y in range(x+1, len(connectionList)):
                if (connectionList[x]['src'] == connectionList[y]['dst'] and connectionList[x]['dst'] == connectionList[y]['src']):
                    connectionList.remove(connectionList[y])
 

"""
The generateTopoHtml method generates an HTML file containing the javascript code to display the current Opendaylight topology.
"""
def generateTopoHtml():
    
    #Get the start and end of the html file
    f = open("./templates/topology-template.html", "r")
    #i = 0
    html_doc_static1 = ''
    html_doc_static2 = ''
    html_doc_static3 = ''
    
    for i,line in enumerate(f):
        if i < 35:
            html_doc_static1 += line
        elif i > 35 and i < 47:
            html_doc_static2 += line
        elif i > 47:
            html_doc_static3 += line
    f.close()

    #Build javascript dicts to represent dynamic topology information

    #The following is an example of the Javascript will create
      """
     var nodes = new vis.DataSet([
            {id: 1, label: 'Node 1'},
            {id: 2, label: 'Node 2'},
            {id: 3, label: 'Node 3'},
            {id: 4, label: 'Node 4'},
            {id: 5, label: 'Node 5'}
        ]);
    
        var edges = new vis.DataSet([
            {from: 1, to: 3},
            {from: 1, to: 2},
            {from: 2, to: 4},
            {from: 2, to: 5}
        ]);
    """
    dictDataSet = '\n        var nodes = new vis.DataSet([\n'
    for x in range(len(deviceList)):

        if x < len(deviceList)-1:
            dictDataSet += '            {id: \'' + \
                deviceList[x]+'\', label: \'' + deviceList[x]+'\'},\n'

        else:
            dictDataSet += '            {id: \'' + \
                deviceList[x]+'\', label: \'' + \
                deviceList[x]+'\'}\n        ]);\n'

    dictDataSet += '\n        var edges = new vis.DataSet([\n'
    for x in range(len(connectionList)):
        

        if x != len(connectionList)-1:
            dictDataSet += '            {from: \'' + \
                connectionList[x]['src'] + '\', to: \'' + \
                connectionList[x]['dst'] + '\'},\n'
        else:
            dictDataSet += '            {from: \'' + connectionList[x]['src'] + \
                '\', to: \'' + connectionList[x]['dst'] + '\'}\n        ]);\n'

    #Create HTML file with newly generated Javascript
    html_doc_ControllerIP='     <h1>Topology for: '+ controllerIP +'</h1>\n'
    html_doc = html_doc_static1 + html_doc_ControllerIP + html_doc_static2 + dictDataSet + html_doc_static3


    f = open("./templates/displaytopo.html", "w")
    f.write(html_doc)
    f.close()
    
def run():
    connectionList.clear()
    deviceList.clear()
    try:
        fetchTopology()
        generateTopoHtml()
        return 0 #no failure reported
    except:
        return 1 #failure to report

