import math
import numpy
import lab5_wnet
import matplotlib.pyplot as p

# Stuff about each packet in the simulator, to keep track of start and end
# times, identity of sender, whether collision happened or not.
class Packet:
    def __init__(self,starttime,sender,receiver=None,ptime=1):
        self.start = starttime
        self.sender = sender
        self.receiver = receiver
        self.ptime = ptime  # size of packet in time slots
        self.end = -1		# will get initialized later when xmitting
        if receiver == None:
            self.coll_flag = lab5_wnet.NO_COLLISION

#
# Various performance statistics that we want to maintain and possibly plot.
# Attach one of these objects to each node, and also to the entire network.
#
class Stats:
    def __init__(self,simtime):
        self.reset(simtime)

    def reset(self,simtime):
        self.simtime = simtime	# total simulation time
        self.attempts = 0	# number of attempts by network or node
        self.success = 0	# number that succeeded
        self.collisions = 0	# number that failed (collided)
        self.latency = 0     # average latency; most useful for a node
        self.backoffs = 0    # number of backoffs; generally useful at a node
        self.pending = 0     # only makes much sense at a node
        self.numbackoffs = 0	# number of backoffs at node
        # downlink stats for a node
        self.downrecd = 0       # number of packets received on downlink to node
        self.downq = 0          # current length of downlink queue to a node
        self.plist = []

    # _print() is a bit hacky.  we have one kind of Stats object that
    # we attach to both the network and each node.  The info we want printed
    # depends on whether we're printing it from the network or a node.  When
    # it's a node, the "type" is the node ID, otherwise, it's 'net'
    def _print(self,time,ptime,type):
        if time == 0: u = 0
        else: u = (1.0*self.success*ptime)/time
        if type == 'net':
    #	    print "Time %d attempts %d success %d coll %d util %.2f downloaded %d" % (time,self.attempts,self.success,self.collisions,u,self.downrecd)
            print("Time %d attempts %d success %d util %.2f" % (time,self.attempts,self.success,u))
        else:
    #	    print "  Node %d attempts %d success %d coll %d lat %d backoffs %d downrecd %d" % (int(type), self.attempts, self.success, self.collisions, self.latency, self.numbackoffs, self.downrecd)
    #	    print "  Node %d attempts %d success %d coll %d lat %d" % (int(type), self.attempts, self.success, self.collisions, self.latency)
            print("  Node %d attempts %d success %d coll %d" % (int(type), self.attempts, self.success, self.collisions))

##########################################################################
# Plot scatter plot of successful transmissions and collisions.
# Plot bar graph of per-node throughput (# successful transmissions
##########################################################################
def plot_data(wnet):
    succ = []
    x = []
    y = []
    xcoll = []
    ycoll = []
    for node in wnet.nlist:
        succ.append(node.stats.success)
        y = y + [node.get_id()] * len(node.sent)
        x = x + node.sent
        ycoll = ycoll + [node.get_id()] * len(node.coll)
        xcoll = xcoll + node.coll
    p.subplots_adjust(hspace = 0.1)
    p.subplot(2,1,1)
    p.ylabel('Node (blue=success; red=collision)')
    p.xlabel('Time sent')
    if x != [] and y != []:
        p.scatter(x, y, c='b')
    if xcoll != [] and ycoll != []:
        ycoll = numpy.array(ycoll)
        p.scatter(xcoll, ycoll-0.4, c='r')

    p.subplot(2,1,2)
    ind = numpy.arange(len(wnet.nlist))
    width = 0.35
    p.bar(ind, succ, width, color = 'g')
    p.ylabel('# successful receptions')
    p.xlabel('Node #')
    p.show()