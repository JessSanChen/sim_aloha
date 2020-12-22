# Jessica Chen
# BMW Lab
# 12/22/2020

from random import seed, random

seed(1)


class Node:
    def __init__(self, p: float):
        self.p = p
        self.pkt_success = 0
        self.pkt_collide = 0

    def generate_xmit(self):
        r = random()
        if r < self.p:
            return True
        else:
            return False


class System:
    def __init__(self, n: int, t: int):
        self.n = n
        self.t = t
        # allow different sys definitions to make code adaptable
        self.sys = self.create_fixed_p_sys()

    def create_fixed_p_sys(self):
        sys = []
        for i in range(self.n):
            sys.append(Node(1/self.n))
        return sys

    # def create_var_p_sys(self):

    def print_sys(self):
        print(self.sys)

    def run_sim(self):
        total_xmit_count = 0
        total_success = 0
        total_collide = 0
        for slot in range(self.t):
            xmit_count = 0
            potential_success = -1
            for node in range(self.n):
                xmit = self.sys[node].generate_xmit()
                if xmit:
                    xmit_count += 1
                # check if first xmit; keep track
                    if xmit_count == 1:
                        potential_success = node
                    if xmit_count > 1:
                        self.sys[node].pkt_collide += 1
                        total_collide += 1
            # if collision, first node also collides
            if xmit_count > 1:
                self.sys[potential_success].pkt_collide += 1
                total_collide += 1
            # if only one transmits, then success
            elif xmit_count == 1:
                self.sys[potential_success].pkt_success += 1
                total_success += 1
            total_xmit_count += xmit_count
        return [self.sys, total_xmit_count, total_success, total_collide]




if __name__ == "__main__":
    test = System(10, 10000)
    print("Total transmission count: " + str(test.run_sim()[1]))
    print("Total success count: " + str(test.run_sim()[2]))
    print("Total collision count: " + str(test.run_sim()[3]))


