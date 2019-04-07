from mininet.topo import Topo
from mininet.net import Mininet

class MainTopo(Topo):
	"Full mesh and Trees"
	

	def __init__ (self):
		"Create Topology."
		
		# Make topology
		Topo.__init__(self)
		
		# Add Switches
		S1 = self.addSwitch('S1')
		S2 = self.addSwitch('S2')
		S3 = self.addSwitch('S3')
		S4 = self.addSwitch('S4')
		S5 = self.addSwitch('S5')
		S6 = self.addSwitch('S6')
		S7 = self.addSwitch('S7')
		S8 = self.addSwitch('S8')
		
		# Add Hosts
		H1 = self.addHost('H1', mac='00:00:00:00:00:01')
		H2 = self.addHost('H2', mac='00:00:00:00:00:02')
		H3 = self.addHost('H3', mac='00:00:00:00:00:03')
		H4 = self.addHost('H4', mac='00:00:00:00:00:04')
		H5 = self.addHost('H5', mac='00:00:00:00:00:05')
		H6 = self.addHost('H6', mac='00:00:00:00:00:06')
		H7 = self.addHost('H7', mac='00:00:00:00:00:07')
		H8 = self.addHost('H8', mac='00:00:00:00:00:08')
		
		
		# Add Links
		## Switch to Switch Links
		#Ful Mesh Core
		self.addLink(S1, S2)
		self.addLink(S1, S3)
		self.addLink(S1, S4)
		self.addLink(S2, S3)
		self.addLink(S2, S4)
		self.addLink(S3, S4)
		
		
		# Core to PE switches
		self.addLink(S1, S5)
		self.addLink(S2, S6)
		self.addLink(S3, S7)
		self.addLink(S4, S8)
		
		# PE Ring connections
		#self.addLink(S5, S6)
		#self.addLink(S5, S7)
		#self.addLink(S7, S8)
		#self.addLink(S8, S6)
		
		# PE to CE Switches
		self.addLink(S5, H1)
		self.addLink(S5, H2)
		self.addLink(S6, H3)
		self.addLink(S6, H4)
		self.addLink(S7, H5)
		self.addLink(S7, H6)
		self.addLink(S8, H7)
		self.addLink(S8, H8)
		
		
# Allows the file to be imported using `mn --custom <filename> --topo dcharoot`
topos = {
    'dcharoot': MainTopo
	}

