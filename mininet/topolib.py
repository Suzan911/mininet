"Library of potentially useful topologies for Mininet"

from mininet.topo import Topo
from mininet.net import Mininet

# The build() method is expected to do this:
# pylint: disable=arguments-differ

class TreeTopo( Topo ):
    "Topology for a tree network with a given depth and fanout."

    def build( self, depth=1, fanout=2 ):
        # Numbering:  h1..N, s1..M
        self.hostNum = 1
        self.switchNum = 1
        # Build topology
        self.addTree( depth, fanout )

    def addTree( self, depth, fanout ):
        """Add a subtree starting with node n.
           returns: last node added"""
        isSwitch = depth > 0
        if isSwitch:
            node = self.addSwitch( 's%s' % self.switchNum )
            self.switchNum += 1
            for _ in range( fanout ):
                child = self.addTree( depth - 1, fanout )
                self.addLink( node, child )
        else:
            node = self.addHost( 'h%s' % self.hostNum )
            self.hostNum += 1
        return node


def TreeNet( depth=1, fanout=2, **kwargs ):
    "Convenience function for creating tree networks."
    topo = TreeTopo( depth, fanout )
    return Mininet( topo, **kwargs )


class TorusTopo( Topo ):
    """2-D Torus topology
       WARNING: this topology has LOOPS and WILL NOT WORK
       with the default controller or any Ethernet bridge
       without STP turned on! It can be used with STP, e.g.:
       # mn --topo torus,3,3 --switch lxbr,stp=1 --test pingall"""

    def build( self, x, y ):
        if x < 3 or y < 3:
            raise Exception( 'Please use 3x3 or greater for compatibility '
                             'with 2.1' )
        hosts, switches, dpid = {}, {}, 0
        # Create and wire interior
        for i in range( 0, x ):
            for j in range( 0, y ):
                loc = '%dx%d' % ( i + 1, j + 1 )
                # dpid cannot be zero for OVS
                dpid = ( i + 1 ) * 256 + ( j + 1 )
                switch = switches[ i, j ] = self.addSwitch(
                    's' + loc, dpid='%016x' % dpid )
                host = hosts[ i, j ] = self.addHost( 'h' + loc )
                self.addLink( host, switch )
        # Connect switches
        for i in range( 0, x ):
            for j in range( 0, y ):
                sw1 = switches[ i, j ]
                sw2 = switches[ i, ( j + 1 ) % y ]
                sw3 = switches[ ( i + 1 ) % x, j ]
                self.addLink( sw1, sw2 )
                self.addLink( sw1, sw3 )

class LeafSpineTopo ( Topo ):
    """Leaf-Spine topology with a given leaf number, spine number and fanout"""

    def build( self, leaf=2, spine=2, fanout=2):
        self.dpid = 1
        leaf_list, spine_list, hostNum = [], [], 1

        # Build spine switches
        self._addSwitch( spine, spine_list, "spine")
        # Build leaf switches
        self._addSwitch( leaf, leaf_list, "leaf")

        # Link between leaf and spine
        for spine_sw in spine_list:
            for leaf_sw in leaf_list:
                self.addLink(spine_sw, leaf_sw)

        # Link between leaf and host
        for leaf_sw in leaf_list:
            for _ in range( fanout ):
                host = self.addHost( 'h%s' % hostNum)
                self.addLink( leaf_sw, host )
                hostNum += 1

    def _addSwitch( self, number, sw_list, sw_name ):
        for i in range( 0, number ):
            sw_list.append(self.addSwitch( '%s%s' % (sw_name, str(i + 1)), dpid='%016x' % self.dpid ))
            self.dpid += 1

# pylint: enable=arguments-differ
