import globals as g
import helper_functions.print_verbosity as pv

def print_configuration():
    pv.normal_print("----------------------------------------------")
    pv.normal_print("-------- Fuzzing Engine Configuration --------")
    pv.normal_print("TARGET_ADDR: %s" % g.TARGET_ADDR)
    pv.normal_print("TARGET_PORT: %s" % g.TARGET_PORT)
    pv.normal_print("X1: %s" % g.X1)
    pv.normal_print("X2: %s" % g.X2)
    pv.normal_print("X3: %s" % g.X3)

    if g.VERBOSITY == 1:
        return
    pv.verbose_print("CHOOSE_MUTATION: %s" % g.CHOOSE_MUTATION)
    pv.verbose_print("PACKET_SELECTION_UNIFORM_DISTRIBUTION: %s" % g.PACKET_SELECTION_UNIFORM_DISTRIBUTION)
    pv.verbose_print("FUZZING_STATE_UNIFORM_DISTRIBUTION: %s" % g.FUZZING_STATE_UNIFORM_DISTRIBUTION)
    pv.verbose_print("FUZZING INTENSITY: %s" % g.FUZZING_INTENSITY)
    pv.verbose_print("CONSTRUCTION_INTENSITY: %s" % g.CONSTRUCTION_INTENSITY)
    pv.verbose_print("b: %s" % g.b)
    pv.verbose_print("c1: %s" % g.c[0])
    pv.verbose_print("c2: %s" % g.c[1])
    pv.verbose_print("c3: %s" % g.c[2])
    pv.verbose_print("c4: %s" % g.c[3])

    pv.verbose_print("d1: %s" % g.d[0])
    pv.verbose_print("d2: %s" % g.d[1])
    pv.verbose_print("d3: %s" % g.d[2])
    pv.verbose_print("d4: %s" % g.d[3])
    pv.normal_print("----------------------------------------------")