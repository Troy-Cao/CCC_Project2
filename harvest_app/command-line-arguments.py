# Demo for command line arguments

import sys
import getopt
import argparse
from optparse import OptionParser

####################
# Read Arguments
def read_arg1():
    ''' Return the number of arguments '''
    ret = len(sys.argv)

    return ret


def read_arg2():
    ''' Return out all arguments '''
    ret = sys.argv
    tmp = {k: v for k in range(read_arg1()) for v in ret}

    return ret


def read_arg3():
    ''' Return arguments other than the file being run'''
    args = sys.argv[1:]
    return args


#####################
# Parse Arguments:
# 前前后后有三个library吧：optget, optparse, argparse

def parse_arg1():
    '''lib: optget
       usage: test.py -i <inputfile> -o <outputfile>
    '''
    # Mandatory inputs:
    argv = sys.argv[1:]
    inputfile = ''
    outputfile = ''

    try:
        # getopt.getopt(args, shortopts, longopts=[])
        # h -> '-h' -> '--help'
        # i -> '-i' -> '--ifile='
        # o -> '-o' -> '--ofile='
        # : -> Required argument
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        # sys.exot(): The optional arg can be an integer giving the exit status (defaulting to '0'), 
            # or another type of object. This value is NOT actually defined by the module.
            # exit(0) means a clean exit without any errors / problems
            # exit(1) means an exit with some errors / problems
            # exit(2) for command line syntax errors
        sys.exit(2)

    for opt, arg in opts:
        print("Parsed Arguments: ", opt, arg)

        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    print('Input file is: ', inputfile)
    print('Output file is: ', outputfile)
    return


def parse_arg2():
    '''lib: argparse
       usage: test.py -i <inputfile> -o <outputfile>
       https://docs.python.org/3.3/library/argparse.html#argparse.ArgumentParser.parse_args
    '''
    
    parser = argparse.ArgumentParser(description='DESCRIPTION: Process some integers.')

# Later, calling parse_args() will return an object with two attributes, integers and accumulate. 
# - The "integers" attribute will be a list of one or more ints, 
# - The "accumulate" attribute will be either 
#   - the sum() function if "--sum" was specified at the command line, or
#   - the max() function if it was not.

    parser.add_argument('integers', metavar='N', type=int, nargs='+',
                    help='an integer for the accumulator')
    parser.add_argument('--sum', dest='accumulate', action='store_const',
                    const=sum, default=max,
                    help='sum the integers (default: find the max)')

    args = parser.parse_args()
    print(args)
    print(args.integers)
    print(args.accumulate(args.integers))

    return


if __name__ == "__main__":

    # ra1 = read_arg1()
    # print("Number of arguments: ", ra1)

    # ra2 = read_arg2()
    # print("Arguments are: ", ra2)

    # ra3 = read_arg3()
    # print("Real Arguments are: ", ra3)
    
    ######################################
    # print('= '*38)
    # parse_arg1()

    parse_arg2()