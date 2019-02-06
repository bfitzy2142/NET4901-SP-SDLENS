# NET4901-SP
SDLens is a monitoring application for OpenFlow based networks which use the OpenDaylight controller. It proviedes real time information from the OpenFlow switches, as well as an interactive topology of the network.

This entire application was built using the web-framework Flask.

## Getting Started
The following instructions will discribe how to install and run our web application, **SDlens** with the OpenDaylight controller.
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
> apt install mysql-server

#### OpenDaylight
OpenDaylight can be downloaded from the [OpenDaylight](https://www.opendaylight.org/) website. This application has been based off of Opendaylight `0.8.3`

Once OpenDaylight has been extracted, you can start the program with:
> karaf-`version`/bin/./karaf clean

When starting the program with the `clean` option, this ensures that any previously installed packages are not inclueded and allows for more continuity at the cost of an extra step. To install the OpenDaylight features which we use, the following command is used:
> feature:install odl-restconf odl-l2switch-switch odl-dlux-core odl-dluxapps-nodes odl-dluxapps-topology odl-dluxapps-yangui odl-dluxapps-yangvisualizer odl-dluxapps-yangman

#### Mininet (Optional)
If you are using Mininet to emulate a SDN network, you can download the virtual machine from Mininet's website: [Download](https://github.com/mininet/mininet/wiki/Mininet-VM-Images)

Once downloaded and opperational, you can create a new topology with the following command. Note that you will have to specifiy the IP address of the OpenDaylight controller.
> sudo mn --controller=remote,ip=`controller IP` --switch ovsk,protocols=OpenFLow13 --topo `Topology of your choice`
This command can be altered to make the required topology, but the remote controller portion of the command must remain.

#### SDLens
With all of the services now running, we can start the monitoring application.
1. In the directory where the application is located make sure that you have all of the neccicary requirements. This can be accomplished with the following command, and the use of the `requirements.txt`
> pip3 install -r "requirements.txt"
2. The application is now ready to start, and to do so, use the following command from the `webapp` directory:
> ./app.py
This will launch the application, you will need to specifiy a Controller IP in the `SECTION` section so that the application knows where to request information from.
3. The application should now be fully opperational.

## Operation
OPPERATION SECTION - Once the application is closer to being finished and graphs have been added I will add this section to talk about how to use the application.

## Authors
- Samuel Robillard - Carleton University, Canada
- Bradly Fitzgerald - Carleton University, Canada
- Josh Nelson - Carleton University, Canada
- Samuel Cook - Carleton University, Canada