import os
import imp
import sys
import argparse

from pargec.c_generator import generate


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('protocol_file', help='path of the proto.py')
    parser.add_argument('output_header')
    parser.add_argument('output_source')
    parser.add_argument('basename', help='name prefix')
    parser.add_argument('-p', "--python", help='generate python wrapper')
    args = parser.parse_args()

    generate(args.protocol_file, args.output_header, args.output_source,
             args.python, args.basename)

