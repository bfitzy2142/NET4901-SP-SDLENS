# NET4901-Senior Project: SDLENS

## Application Overview
SDLens is a monitoring application for OpenFlow based networks which use the OpenDaylight controller. It provides real time information from the OpenFlow switches, as well as an interactive topology of the network.

This entire application was built using the web-framework Flask.

## Installation
The following instructions will discribe how to install and run our web application, **SDLENS** with the OpenDaylight controller.
### Prerequisites
This application makes uses the following services:
- MySql Server
- Nmap
- OpenDaylight Controller
  - The following packages for the controller:
    - odl-restconf
    - odl-l2switch-switch
    - odl-dlux-core
    - odl-dluxapps-nodes
    - odl-dluxapps-topology
    - odl-dluxapps-yangui
    - odl-dluxapps-yangvisualizer
    - odl-dluxapps-yangman
- Python 3
  - python-pip

#### Optional
- Mininet
We have used the Mininet VM to emulate a SDN network.

### Installing
Preface: All commands will assuem a linux operating system.

#### MySql Server
Installing the MySql Server is quite easy, as it can be accomplished with Aptitude.

```
$ apt install mysql-server
$ apt install libmysqlclient-dev
```

#### OpenDaylight
OpenDaylight can be downloaded from the [OpenDaylight](https://www.opendaylight.org/) website. This application has been based off of OpenDaylight version: `0.8.3`

Once OpenDaylight has been extracted, you can start the program with:

```bash
$ karaf-version/bin/./karaf clean
```

When starting the program with the `clean` option, this ensures that any previously installed packages are not inclueded and allows for more continuity at the cost of an extra step. To install the OpenDaylight features which we use, the following command is used:

```
> feature:install odl-restconf odl-l2switch-switch odl-dlux-core odl-dluxapps-nodes odl-dluxapps-topology odl-dluxapps-yangui odl-dluxapps-yangvisualizer odl-dluxapps-yangman
```

#### Mininet (Optional)
If you are using Mininet to emulate a SDN network, you can download the virtual machine from Mininet's website: [Download](https://github.com/mininet/mininet/wiki/Mininet-VM-Images)

Once downloaded and opperational, you can create a new topology with the following command. Note that you will have to specifiy the IP address of the OpenDaylight controller.

```bash
$ sudo mn --controller=remote,ip=`controller IP` --switch ovsk,protocols=OpenFLow13 --topo Topology of your choice
```

A mesh topology is included with this repository called 'basicMesh' under the mininet directory. Copy this file to your Mininet VM and place it within ~/scripts. Create ~/scripts if that directory does not already exist. To create the mesh topology, add your controller's IP address and run the following:

```sh
sudo mn --custom scripts/basicMesh.py --topo dcharoot --controller=remote,ip='controller IP' --switch ovsk,protocols=OpenFlow13
```

Once mininet is running issue the following:

```sh
pingall
```

This will generate traffic throughout the network and allow the contoller to populate the openflow switches with flowrules.

## Authors
- Samuel Robillard - Carleton University, Canada
- Bradley Fitzgerald - Carleton University, Canada
- Josh Nelson - Carleton University, Canada
- Samuel Cook - Carleton University, Canada

![SDLens_Group](https://user-images.githubusercontent.com/44167644/55919797-47097d80-5bc5-11e9-9967-34752b6e1f3d.jpg)
