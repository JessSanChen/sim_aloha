# Jessica Chen
# BMW Lab
# 12/22/2020
from abc import abstractmethod
from random import seed, random
import matplotlib.pyplot as plt
import numpy as np

# seed(1)


class Node:
    def __init__(self, p: float):
        self.p = p
        self.pkt_success = 0
        self.pkt_collide = 0
        self.xmit_attempt = 0
        self.xmit_log = []

    def generate_xmit(self):
        r = random()
        if r < self.p:
            return True
        else:
            return False

    def change_p(self, new_p: float):
        self.p = new_p

    # this method avoids explicit count of pkt_success/collide
    # relies directly on xmit_log array
    def return_result(self):
        # xmit_attempts = sum(x is not None for x in self.xmit_log)
        # xmit_success = self.xmit_log.count(True)
        # xmit_collide = self.xmit_log.count(False)
        xmit_attempts = self.xmit_attempt
        xmit_success = self.pkt_success
        xmit_collide = self.pkt_collide
        return "attempts " + str(xmit_attempts) + " success " + str(xmit_success) + " collide " + str(xmit_collide)


class System:
    def __init__(self, n: int, t: int):
        self.n = n
        self.t = t
        self.sys = self.run_sim()[0]
        self.xmit_attempts = self.run_sim()[1]
        self.success = self.run_sim()[2]
        self.collide = self.run_sim()[3]

    def print_sys(self):
        print(self.sys)

    @abstractmethod
    def create_sys(self):
        pass

    @abstractmethod
    def run_sim(self):
        pass


class FixedPSys(System):
    def __init__(self, n: int, t: int, p: float):
        self.p = p
        super().__init__(n, t)

    def create_sys(self):
        sys = []
        for i in range(self.n):
            sys.append(Node(random()))
        return sys

    # avoids making arrays for each null
    # does not use xmit_log array and instead explicitly counts
    def run_sim(self):
        sys = self.create_sys()
        total_xmit_count = 0
        total_success = 0
        total_collide = 0
        for slot in range(self.t):
            xmit_count = 0
            potential_success = -1
            for node in range(self.n):
                xmit = sys[node].generate_xmit()
                if xmit:
                    xmit_count += 1
                # check if first xmit; keep track
                    if xmit_count == 1:
                        potential_success = node
                    if xmit_count > 1:
                        sys[node].pkt_collide += 1
                        total_collide += 1
            # if collision, first node also collides
            if xmit_count > 1:
                sys[potential_success].pkt_collide += 1
                total_collide += 1
            # if only one transmits, then success
            elif xmit_count == 1:
                sys[potential_success].pkt_success += 1
                total_success += 1
            total_xmit_count += xmit_count
        return [sys, total_xmit_count, total_success, total_collide]


class BinExpBackoff(System):
    def __init__(self, n: int, t: int, p_min, p_max):
        self.p_min = p_min
        self.p_max = p_max
        super().__init__(n, t)

    def create_sys(self):
        sys = []
        for i in range(self.n):
            # initialize with random p values
            sys.append(Node(random()))
        return sys

    # can't avoid using arrays here for sake of graph
    # xmit_log: false = collide, true = success, none = no xmit attempt
    # currently tracks counts parallel (instead of going back through array
    # to sum success/failures. not sure if this is better or worse.

    def run_sim(self):
        sys = self.create_sys()
        total_xmit_count = 0
        total_collide = 0
        total_success = 0
        for slot in range(self.t):
            xmit_count = 0
            potential_success = -1
            for node in range(self.n):
                xmit = sys[node].generate_xmit()
                # transmission attempt
                if xmit:
                    xmit_count += 1
                    # sure of collision
                    if xmit_count > 1:
                        total_collide += 1
                        sys[node].pkt_collide += 1
                        sys[node].p = max([self.p_min, sys[potential_success].p/2])
                        sys[node].xmit_log.append(False)
                    # potential success; first mark
                    elif xmit_count == 1:
                        potential_success = node
                # no transmission attempt
                else:
                    sys[node].xmit_log.append(None)
            # check to see if first xmit was a success or collision
            if xmit_count == 1:
                sys[potential_success].xmit_log.append(True)
                sys[potential_success].pkt_success += 1
                sys[potential_success].p = min([self.p_max, 2*sys[potential_success].p])
                total_success += 1
            elif xmit_count > 1:
                sys[potential_success].xmit_log.append(False)
                sys[potential_success].pkt_collide += 1
                sys[potential_success].p = max([self.p_min, sys[potential_success].p/2])
                total_collide += 1
            total_xmit_count += xmit_count
        return [sys, total_xmit_count, total_success, total_collide]

    # no arrays for each node's xmit log; should run faster
    """
    def run_sim_no_xmitlog(self):
        sys = self.create_sys()
        total_xmit_count = 0
        total_collide = 0
        total_success = 0
        for slot in range(self.t):
            xmit_count = 0
            potential_success = -1
            for node in range(self.n):
                xmit = sys[node].generate_xmit()
                # transmission attempt
                if xmit:
                    sys[node].xmit_attempt += 1
                    xmit_count += 1
                    # sure of collision
                    if xmit_count > 1:
                        total_collide += 1
                        sys[node].pkt_collide += 1
                        sys[node].p = max([self.p_min, sys[potential_success].p/2])
                    # potential success; first mark
                    elif xmit_count == 1:
                        potential_success = node
            # check to see if first xmit was a success or collision
            if xmit_count == 1:
                sys[potential_success].pkt_success += 1
                sys[potential_success].p = min([self.p_max, 2*sys[potential_success].p])
                total_success += 1
            elif xmit_count > 1:
                sys[potential_success].pkt_collide += 1
                sys[potential_success].p = max([self.p_min, sys[potential_success].p/2])
                total_collide += 1
            total_xmit_count += xmit_count
        return [sys, total_xmit_count, total_success, total_collide]
        """


# if the system doesn't know fail/success of xmit until n nodes later
class DelayedAck(System):
    def __init__(self, n: int, t: int, p_min, p_max, delay):
        self.p_min = p_min
        self.p_max = p_max
        self.delay = delay
        super().__init__(n, t)

    def create_sys(self):
        sys = []
        for i in range(self.n):
            # initialize with random p values
            sys.append(Node(random()))
        return sys

    def run_sim(self):
        sys = self.create_sys()
        total_xmit_count = 0
        total_collide = 0
        total_success = 0
        for slot in range(self.t):
            xmit_count = 0
            potential_success = -1
            for node in range(self.n):
                xmit = sys[node].generate_xmit()
                # transmission attempt
                if xmit:
                    xmit_count += 1
                    # sure of collision
                    if xmit_count > 1:
                        total_collide += 1
                        sys[node].pkt_collide += 1
                        sys[node].xmit_log.append(False)
                    # potential success; first mark
                    elif xmit_count == 1:
                        potential_success = node
                # no transmission attempt
                else:
                    sys[node].xmit_log.append(None)
                # only alter p starting from delay
                if slot >= self.delay:
                    print(slot)
                    print(self.delay)
                    print(node)
                    if sys[node].xmit_log[slot-self.delay]:
                        sys[node].p = max([self.p_min, sys[node].p/2])
                    elif sys[node].xmit_log[slot-self.delay] is False:
                        sys[node].p = max([self.p_min, sys[node].p/2])
            # check to see if first xmit was a success or collision
            if xmit_count == 1:
                sys[potential_success].xmit_log.append(True)
                sys[potential_success].pkt_success += 1
                sys[potential_success].p = min([self.p_max, 2*sys[potential_success].p])
                total_success += 1
            elif xmit_count > 1:
                sys[potential_success].xmit_log.append(False)
                sys[potential_success].pkt_collide += 1
                sys[potential_success].p = max([self.p_min, sys[potential_success].p/2])
                total_collide += 1
            total_xmit_count += xmit_count
        return [sys, total_xmit_count, total_success, total_collide]

    def run_d_sim(self):
        util_arr = []
        delay_values = [i for i in range(self.t)]
        for delay in delay_values:
            test = DelayedAck(self.n, self.t, self.p_min, self.p_max, delay).run_sim()
            util = calc_util(test)
            util_arr.append(util)
        plt.plot(delay_values, util_arr, '-o')
        plt.xlabel("Delay of ACK (time slots)")
        plt.ylabel("Utilization")
        plt.savefig('sim_delayedack_testd.png')
        return util_arr


# it's probably poor design to have to input total and max throughput
# change design so can simply feed in system object? (either BinExpBackoff or sys)
# keep consistent input as with calc_fair()
# must modify either BinExpBackoff or sys object to have these attributes
def calc_util(system):
    return system.success/system.t


def calc_fair(system):
    n = len(system.sys)
    throughput_sum = 0
    variance = 0
    for node in range(n):
        throughput_sum += system.sys[node].pkt_success
        variance += pow(system.sys[node].pkt_success, 2)
    return pow(throughput_sum, 2)/(n*variance)


# run simulation of function of p
def run_p_sim(sys_type: str, n, t):
    util_arr = []
    p_values = [i/100 for i in range(1, 100)]
    for p in range(len(p_values)):
        # if sys_type == "fixed_p":
        test = FixedPSys(n, t, p_values[p]).run_sim()
        success_count = test[2]
        util = success_count/t
        util_arr.append(util)
    plt.plot(p_values, util_arr, '-o')
    plt.xlabel("p-values")
    plt.ylabel("Utilization")
    plt.savefig('sim_fixedp_testp.png')
    return util_arr


def run_n_sim(sys_type: str, t, max_n):
    util_arr = []
    fair_arr = []
    n_values = [n for n in range(1, max_n)]
    for n in n_values:
        if sys_type == "fixedpsys":
            test = FixedPSys(n, t, random())
        elif sys_type == "binexpbackoff":
            test = BinExpBackoff(n, t, 0, 1)
        util_arr.append(calc_util(test))
        fair_arr.append(calc_fair(test))
    plt.plot(n_values, util_arr, '-o', label="Utilization")
    plt.plot(n_values, fair_arr, '-o', label="Fairness")
    plt.xlabel("Number of Nodes")
    plt.legend()
    plt.savefig('binexp_util_fair.png')
    return util_arr


# run a system of t slots and n nodes for many trials
def run_trials(system_type, nodes, timeslots, trials):
    all_xmit_attempts = 0
    all_success = 0
    all_collide = 0
    for exp in range(trials):
        seed(exp)
        if system_type == "binexpbackoff":
            test = BinExpBackoff(nodes, timeslots, 0.05, 1)
        elif system_type == "fixedpsys":
            test = FixedPSys(nodes, timeslots, random())
        all_xmit_attempts += test.xmit_attempts
        all_success += test.success
        all_collide += test.collide
        print("Total transmissions: " + str(test.xmit_attempts))
        print("Total success: " + str(test.success))
        print("Total collisions: " + str(test.collide))
        for node in range(len(test.sys)):
            print("Node " + str(node) + ": " + test.sys[node].return_result())
        print("Utilization: " + str(calc_util(test)))
        print("Fairness: " + str(calc_fair(test)))
        # print(system[0].xmit_log)
    print("all xmit attempts: " + str(all_xmit_attempts))
    print("all success: " + str(all_success))
    print("all collide: " + str(all_collide))


def make_node_graph(system):
    # node_graph, util = plt.subplots()
    nodes = []
    slots = []
    result = []
    for n in range(len(system.sys)):
        for t in range(len(system.sys[n].xmit_log)):
            if system.sys[n].xmit_log[t] is not None:
                nodes.append(n)
                slots.append(t)
                result.append(system.sys[n].xmit_log[t])
    label_color = ['r' if i is True else 'b' for i in result]
    # plt.scatter(
    #     slots[result], nodes[result], 'bo',
    #     slots[~result], nodes[~result], 'ro'
    # )
    fig, (ax1, ax2) = plt.subplots(2, figsize=(10, 12))
    # fig.suptitle('Stacked subplots')
    # node-by-node collision and success
    # ax1.figure(figsize=(12, 8))
    ax1.legend(['Success', 'Collision'])
    ax1.set_xlabel("Time Slot")
    ax1.set_ylabel("Node")
    ax1.scatter(slots, nodes, color=label_color)
    # utilization bar graph
    n = [node for node in range(len(system.sys))]
    util = [node.pkt_success/system.t for node in system.sys]
    ax2.set_xlabel("Node")
    ax2.set_ylabel("Utilization")
    # ax2.figure(figsize=(12, 8))
    ax2.bar(n, util)
    fig.savefig('binexp_node_0.05-0.8.png')


if __name__ == "__main__":
    # run_p_sim("fixed_p", 10, 10000)
    # run_trials("binexpbackoff", 6, 10000, 100)
    # run_n_sim("binexpbackoff", 10000, 100)
    seed(0)
    test = DelayedAck(6, 10000, 0, 1, 10)
    test.run_d_sim()



