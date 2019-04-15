# SDLENS Owner's Manual

The following are the main pages of the SDLENS Monitoring Webapp:

- Topology Page

- Switch Overview Page

- Graphs Page

- Switch Counters Page

- Flow Statistics Page

- Switch Hardware Page

- Github Repository Page


## The Topology Page


![Topology](https://user-images.githubusercontent.com/44167644/55676798-08648200-58aa-11e9-9fe1-49c08f2576e4.png)

**The topology page is designed to allow users to easily peek into their SDN to quickly gather telemetry on all their network elements.**
**There are two areas of interest which display statistics on the topology page:**

- **Topology View panel**

- **Information panel**


##### i. Topology View panel
![topology_box](https://user-images.githubusercontent.com/44167644/55676880-778ea600-58ab-11e9-8df9-de74e0acc644.png)
From this view you can see what your working topology looks like.

##### ii. Information panel
![information_panel](https://user-images.githubusercontent.com/44167644/55676912-f2f05780-58ab-11e9-964b-d176eadeef95.png)
This area is filled with information on statistics gathering events.

### Topology Page Features

#### 1. Throughput and Basic Flow Information

Within the topology area, you can hover over devices or click devices to obtain more information about them.
Hovering over nodes or links will display information about that device. For example, hovering over a switch shows throughput statistics and realtime flow information.
![throughput_info](https://user-images.githubusercontent.com/44167644/55677729-0f47c080-58bb-11e9-9a8a-57c360b96fb8.png)

#### 2. Switch and Host Information


![switch_clicked](https://user-images.githubusercontent.com/44167644/55677780-0c999b00-58bc-11e9-8700-aa1aa0eb8283.png)
**Clicking on a switch will provide information such as switch port counters, errors, stp state, port status, etc.**

![host_clicked](https://user-images.githubusercontent.com/44167644/55677791-2cc95a00-58bc-11e9-9742-78357f77c695.png)
**Clicking on a host will display a timestamp of when that joined the network and the latest interaction with the network it has had.**
#### 3. Flow Tracer Feature
**The flow tracer feature allows users to visualize the path used for two host elements to communicate with one another.**
![flow_tracer_panel](https://user-images.githubusercontent.com/44167644/55676887-a6a51780-58ab-11e9-8d62-0fb3efc0ddab.png)

Within this tab, you select the source host and destination host. Then press trace. The topology view panel will display the path taken from the source host to destination host.
![flow_trace_topo](https://user-images.githubusercontent.com/44167644/55676985-97bf6480-58ad-11e9-86f5-42efd3a7ea94.png)

The information panel displays information of the switches traversed and the flow rule used along with information on that particular flow.

![flow_info_panel](https://user-images.githubusercontent.com/44167644/55677000-07355400-58ae-11e9-9611-f237d9ccefe6.png)

#### 4. STP and RESET
![Additional_options_panel](https://user-images.githubusercontent.com/44167644/55676896-c89e9a00-58ab-11e9-84b4-1f1795d73ca1.png)

If you would like to see the current Spanning Tree Topology then this is possible by clicking the STP Topology button.

![stp_topology](https://user-images.githubusercontent.com/44167644/55678297-4c18b500-58c5-11e9-9601-51dde1ca253c.png)

The information panel displays a legend:
![stp_legend](https://user-images.githubusercontent.com/44167644/55678331-c47f7600-58c5-11e9-8346-540e6ec8b91f.png)

The reset button allows you to clear the topology page.

## Switch Overview Page

This page is not visable from the navbar but can be reached via the multiple hyperlinks displayed on numerous pages. For example, when a node is cliked on the topology page, the hyperlink is the name of the switch above the port counter table.

Below is the switch overview page. Port counters are displayed by default. You can also view that switch's flow tables, a graph showing the flow count history, and graphs partaining to interface utalization. This information under the interface usage tab is the same as what can be found on the graphs page and will be shown in more detail under the "Graphs" section.
![switch_overview](https://user-images.githubusercontent.com/44167644/55678534-83896080-58c9-11e9-8132-ea55c7a0585d.png)

## Graphs Page
The graphs page provides statistics of a particular switch's interface. You must first select a switch, and then the particular interface of interest. From there you can select how far in the past you wish to view statitics for. 

Graphs can report data for the following durations:
- 30 minutes
- 1 hour
- 2 hours
- 6 hours
- 1 day
- All Time

The following graphs are available:
- Received Packets Forwarded
- Transmitted Packets 
- Received Drops
- Transmit Drops

The following figure shows the result of statistics from openflow:1's interface 3 as an example:
![graphs_view](https://user-images.githubusercontent.com/44167644/55678728-8174d100-58cc-11e9-8bc0-cd1a6cb6e312.png)

## Switch Counters Page
The switch counters page is one of the first pages we created for the SDLENS webapp. It simply displays port counters for each switch within the topology. Each switch name is also a hyperlink to reach the switch overview page.  

## Flow Statistics Page
The flow statistic page provides the flow rules and addtional information existing on each switch. Each switch name is also a hyperlink to reach the switch overview page.

Below what the flow page looks like for the first rule on openflow:1:
![flow_stats](https://user-images.githubusercontent.com/44167644/55678796-b170a400-58cd-11e9-8591-a8f5a49649f5.png)

## Switch Hardware Page
The switch hardware page provides additional information on switch interfaces. Below is an example for openflow:1:
![hardware_page](https://user-images.githubusercontent.com/44167644/55678821-1cba7600-58ce-11e9-90b8-0619e5d03de2.png)
