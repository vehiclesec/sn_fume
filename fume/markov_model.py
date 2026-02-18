import globals as g
import random

class Node():
    def __init__(self, name):
        self.name = name
        self.next = []
        self.next_prob = []

class Markov_Model():
    def __init__(self):
        self.state_s0 = Node('S0')
        self.state_s1 = Node("S1")
        self.state_s2 = Node('S2')
        self.state_sf = Node('Sf')
        self.state_inject = Node('INJECT')
        self.state_delete = Node('DELETE')
        self.state_mutate = Node('MUTATE')
        self.state_bof = Node('BOF')
        self.state_nonbof = Node('NONBOF')
        self.state_send = Node('SEND')
        self.state_response_log = Node('RESPONSE_LOG')
        self.state_connect = Node("CONNECT")        
        self.state_disconnect = Node("DISCONNECT")
        self.state_publish = Node("PUBLISH")
        self.state_register = Node("REGISTER")

        self.current_state = self.state_s0

        self.model_type = 'mutation'

    def next_state(self):
        if self.current_state.name == 'Sf':
            return 

        self.current_state = random.choices(
            self.current_state.next, 
            weights=self.current_state.next_prob)[0]

        print('Next state chosen: %s' % self.current_state.name)

def initialize_markov_model():
    mm = Markov_Model()

    mm.state_s0.next = [mm.state_connect]
    mm.state_s0.next_prob = [1]

    mm.state_response_log.next = [mm.state_s2]
    mm.state_response_log.next_prob = [1]

    mm.state_s1.next = [
        mm.state_connect, 
        mm.state_publish, 
        mm.state_disconnect,
        mm.state_register,

        mm.state_sf]

    for ci in g.c:
        mm.state_s1.next_prob.append(ci - (ci * g.X1))
    mm.state_s1.next_prob.append(g.X1)

    mm.state_connect.next = [mm.state_s2]
    mm.state_connect.next_prob = [1]

    mm.state_disconnect.next = [mm.state_s2]
    mm.state_disconnect.next_prob = [1]

    mm.state_publish.next = [mm.state_s2]
    mm.state_publish.next_prob = [1]

    mm.state_register.next = [mm.state_s2]
    mm.state_register.next_prob = [1]

    mm.state_s2.next = [
        mm.state_inject,
        mm.state_delete,
        mm.state_mutate,
        mm.state_send
    ]
    mm.state_s2.next_prob = [g.d[0], g.d[1], g.d[2], g.X2]

    mm.state_inject.next = [mm.state_bof, mm.state_nonbof]
    mm.state_inject.next_prob = [g.d[3], 1 - g.d[3]]

    mm.state_delete.next = [mm.state_s2]
    mm.state_delete.next_prob = [1]

    mm.state_mutate.next = [mm.state_s2]
    mm.state_mutate.next_prob = [1]

    mm.state_bof.next = [mm.state_s2]
    mm.state_bof.next_prob = [1]

    mm.state_nonbof.next = [mm.state_s2]
    mm.state_nonbof.next_prob = [1]

    mm.state_send.next = [mm.state_s2, mm.state_s1]
    mm.state_send.next_prob = [1 - g.X3, g.X3]

    return mm