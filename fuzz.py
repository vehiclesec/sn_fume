import sys
import random
import math
sys.path.append('generators')
sys.path.append('helper_functions')
sys.path.append('fume')
sys.path.append('parsers')

import helper_functions.validate_fuzzing_params as vfp
import helper_functions.parse_config_file as pcf
import helper_functions.print_configuration as pc
import helper_functions.crash_logging as cl

import globals as g

import fume.markov_model as mm
import fume.fuzzing_engine as fe
import fume.run_target as rt

def calculate_X1():
    g.X1 = 1 / g.CONSTRUCTION_INTENSITY

def calculate_X2():
    g.X2 = 1 - g.FUZZING_INTENSITY

def calculate_X3():
    g.X3 = 1 - (2 * math.log(1 + g.FUZZING_INTENSITY, 10))

def main():

    try:
        config_f = open(sys.argv[1], 'r')
        config = config_f.readlines()
        pcf.parse_config_file(config)
        config_f.close()
    except FileNotFoundError:
        print("Could not find the supplied file: %s" % sys.argv[1])
        exit(-1)
    except IndexError:
        pass

    if g.user_supplied_X[0] == 0:
        calculate_X1()
    if g.user_supplied_X[1] == 0:
        calculate_X2()
    if g.user_supplied_X[2] == 0:
        calculate_X3()

    vfp.validate_all()

    cl.create_crash_directory()

    pc.print_configuration()

    markov_model = mm.initialize_markov_model()

    rt.run_target()

    fe.run_fuzzing_engine(markov_model)

if __name__ == "__main__":
    main()