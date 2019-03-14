/* 
JavaScript functions that are used to preform
API calls to the Flask backend to display useful
information to the user such as packet count, 
interface throughput, host information, etc.
***SDLENS 2019***
*/

/*
Function to call topo-switch-stats API via POST and gather 
switch throughput Information with the help of the
handleThroughput method on API response. 
*/
function throughputInfo(node)
{
    var xhr = new XMLHttpRequest();
    
    if (xhr)
    {
        // open( method, location, isAsynchronous )
        xhr.open("POST", "/topo-switch-stats", true);
        // bind callback function
        xhr.onreadystatechange = function()
        {
          handleThroughput(xhr, node);
        };
        // actually send the Ajax request 
        var post_params = '{ "switch_throughput" : "' + node + '"}';
        xhr.setRequestHeader("Content-type", "application/json");
        xhr.send(post_params); // Send request
    }
}

/*
 Callback function that processes the server response for switch throughput
 and builds an html string with the selected switch's interface throughput information 
 that is presented to the user when they hover over that switch.
 */
function handleThroughput(xhr, node) {
    if (xhr.readyState == 4 && xhr.status == 200)
    {   
        var tp_stats = [];
        var flow_stats = '';

        responseJSON = JSON.parse(xhr.responseText);
        var device = Object.keys(responseJSON);

        // Contains the name of the keys which are interface names or flow-stats
        var keys = Object.keys(responseJSON[device])
        
        var basic_title = 'Node: <b>' + node + '</b>'
                        + '<br>Type: <b>Switch<b></br>';
                        
        var flow_title = '<span style="text-align:center"><br><b>Flow Stats:</b></span>';
        var tp_title = '<span style="text-align:center">Throughput Stats:</span>';
        for (var i = 0; i < keys.length; i++) {
            if (keys[i] != 'flow-stats'){
                var inter =  keys[i];
                var tx_bps = responseJSON[device][keys[i]]['tx_bps'];
                var rx_bps = responseJSON[device][keys[i]]['rx_bps'];
                tp_stats.push('<br>Interface: <b>' + inter + '</b>',
                                '<br><span style="padding-left:2em">Tx: <b>'+ tx_bps + ' bps</b></span></br>',
                                '<span style="padding-left:2em">Rx: <b>'+ rx_bps + ' bps</b></span>');
            }else {
              active_flows = responseJSON[device][keys[i]]['active_flows']
              packets_looked_up = responseJSON[device][keys[i]]['packets_looked_up']
              packets_matched = responseJSON[device][keys[i]]['packets_matched']
              flow_stats = '<br><span style="padding-left:2em">Active Flows: <b>'+ active_flows + '</b></span></br>'
                         + '<span style="padding-left:2em">Packets Looked Up: <b>'+ packets_looked_up + '</b></span></br>'
                         + '<span style="padding-left:2em">Packets Matched: <b>'+ packets_matched + '</b></span></br>'
            }
        }

        var throughput_stats = tp_stats.join("");
        var title = basic_title + flow_title + flow_stats + tp_title + throughput_stats;
        
        network['body']['nodes'][node]['options']['title'] = title;
        
    }
}

/*
Function to call topo-switch-stats API via POST
and gather edge Information with the help of the
handleEdge method on API response. 
*/
function edgeInfo(edge)
{
    var xhr = new XMLHttpRequest();
    
    if (xhr)
    {
        // open( method, location, isAsynchronous )
        xhr.open("POST", "/topo-switch-stats", true);
        // bind callback function
        xhr.onreadystatechange = function()
        {
          handleEdge(xhr);
        };
        // actually send the Ajax request 
        var post_params = '{ "edge" : "' + edge + '"}';
        xhr.setRequestHeader("Content-type", "application/json");
        xhr.send(post_params); // Send request
    }
}

/*
 Callback function that processes the server response for edge stats
 and builds a table with the selected edge's information that is
 presented to the user.
 */
function handleEdge(xhr) {
  if (xhr.readyState == 4 && xhr.status == 200)
  {
      responseJSON = JSON.parse(xhr.responseText);

      var title = new Array();
      title.push(["Source Port", "Destination Port"]);
      
      var table = document.createElement("TABLE");
      table.classList.add("table-bordered");
      table.classList.add("table");
      table.border = "1";
      
      //Get the count of columns.
      var columnCount = 2;

      //Add the header row.
      var row = table.insertRow(-1);
      for (var i = 0; i < columnCount; i++) {
          var headerCell = document.createElement("TH");
          headerCell.innerHTML = title[0][i];
          row.appendChild(headerCell);
      }

      //Add the data rows.
      
          row = table.insertRow(-1);
          for (var j = 0; j < columnCount; j++) {
              var cell = row.insertCell(-1);
              
              var src_port = responseJSON['src_port'];
              var dst_port = responseJSON['dst_port'];

              switch (j) {
                  case 0:
                      cell.innerHTML = src_port;
                      break;
                  case 1:
                      cell.innerHTML = dst_port;
                  }
          }
      
      //add table to infobox div
      document.getElementById('infobox').appendChild(table);
      //move page view to the bottom
      window.scrollTo(0, document.body.scrollHeight);
  }
}

/*
Function to call topo-switch-stats API via POST and gather 
switch interface counter Information with the help of the
handleThroughput method on API response. 
*/
function switchStats(node)
{
    var xhr = new XMLHttpRequest();
    
    if (xhr)
    {
        // open( method, location, isAsynchronous )
        xhr.open("POST", "/topo-switch-stats", true);
        // bind callback function
        xhr.onreadystatechange = function()
        {
            buildTable(xhr);
        };
        // actually send the Ajax request 
        //Limitation: Switch names must include openflow atm.
        var post_params = '{ "switch" : "openflow' + node.slice(9) + '"}';
        xhr.setRequestHeader("Content-type", "application/json");
        xhr.send(post_params); // Send request
    }
}

/*
 Callback function that processes the server response for switch stats
 and builds a table with the selected switch's interface information that is
 presented to the user.
 */
function buildTable(xhr)
{
    if (xhr.readyState == 4 && xhr.status == 200)
    {
        responseJSON = JSON.parse(xhr.responseText);
        
        
        var title = new Array();
        title.push(["Interface", "Tx Packets", "Rx Packets", "Tx Errors", 
                                "Rx Errors", "Tx Drops", "Rx Drops"]);
        
        //Create a HTML Table element.
        var table = document.createElement("TABLE");
        table.classList.add("table-bordered");
        table.classList.add("table");
        table.border = "1";
    
        //Get the count of columns.
        var columnCount = 7;
    
        //Add the header row.
        var row = table.insertRow(-1);
        for (var i = 0; i < columnCount; i++) {
            var headerCell = document.createElement("TH");
            headerCell.innerHTML = title[0][i];
            row.appendChild(headerCell);
        }
    
        //Add the data rows.
        for (var i = 0; i < responseJSON.length; i++) {
            row = table.insertRow(-1);
            for (var j = 0; j < columnCount; j++) {
                var cell = row.insertCell(-1);
                if (j == 0){
                var interface = Object.keys(responseJSON[i]);
                var counters = responseJSON[i][interface];
                }

                switch (j) {
                    case 0:
                        cell.innerHTML = interface;
                        break;
                    case 1:
                        cell.innerHTML = counters['Tx_packs'];
                        break;
                    case 2:
                        cell.innerHTML = counters["Rx_pckts"];
                        break;
                    case 3:
                        cell.innerHTML = counters["Tx_errs"];
                        break;
                    case 4:
                        cell.innerHTML = counters["Rx_errs"];
                        break;
                    case 5:
                        cell.innerHTML = counters["Tx_drops"]; 
                        break;
                    case 6:
                        cell.innerHTML = counters["Rx_drops"];
                         
                    }
            }
        }
        //add table to infobox div
        document.getElementById('infobox').appendChild(table);
        //move page view to the bottom
        window.scrollTo(0, document.body.scrollHeight);
    }
}

/*
Function to call topo-switch-stats API via POST and gather 
basic host Information with the help of the
handleThroughput method on API response. 
*/
function hostStats(node)
{
    var xhr = new XMLHttpRequest();
    
    if (xhr)
    {
        // open( method, location, isAsynchronous )
        xhr.open("POST", "/topo-switch-stats", true);
        // bind callback function
        xhr.onreadystatechange = function()
        {
            handleHost(xhr);
        };
        // actually send the Ajax request 
        var post_params = '{ "host" : "' + node + '"}';
        xhr.setRequestHeader("Content-type", "application/json");
        xhr.send(post_params); // Send request
    }
}

/*
 Callback function that processes the server response for host information
 and builds a table with the selected host's mac address, first appearence 
 and latest appearence on the network.
 */
function handleHost(xhr) {
    if (xhr.readyState == 4 && xhr.status == 200) {
        responseJSON = JSON.parse(xhr.responseText);
        var title = new Array();
        title.push(["MAC Address", "First Appearence", "Latest Interaction"]);
        
        var table = document.createElement("TABLE");
        table.classList.add("table-bordered");
        table.classList.add("table");
        table.border = "1";
        
        //Get the count of columns.
        var columnCount = 3;

        //Add the header row.
        var row = table.insertRow(-1);
        for (var i = 0; i < columnCount; i++) {
            var headerCell = document.createElement("TH");
            headerCell.innerHTML = title[0][i];
            row.appendChild(headerCell);
        }

        //Add the data rows.
        
            row = table.insertRow(-1);
            for (var j = 0; j < columnCount; j++) {
                var cell = row.insertCell(-1);
            
                var ip = responseJSON['ip'];
                var first_seen = responseJSON['first_seen'];
                var last_seen = responseJSON['last_seen'];
                var mac = responseJSON['mac']

                switch (j) {
                    case 0:
                        cell.innerHTML = mac;
                        break;
                    case 1: 
                        cell.innerHTML = first_seen;
                        break;
                    case 2:
                        cell.innerHTML = last_seen;
                }

            }
        
        document.getElementById('titlebar').innerHTML = '<h2><b>Host: '+ ip +'</b></h2>';
        //add table to infobox div
        document.getElementById('infobox').appendChild(table);
        //move page view to the bottom
        window.scrollTo(0, document.body.scrollHeight);
        
    }
}