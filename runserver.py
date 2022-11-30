#!/usr/bin/env python3

import argparse
from sys import exit, stderr
from app import app

def main():
    """
        Main function that takes input, checks that it is the correct format,
        and passes it to new instance of the class.
        User should input single integer input to command line, or "-h" for help message
    """
    try:
        parser = argparse.ArgumentParser(allow_abbrev=False)
        parser.add_argument('port',
            help='the port at which the server should listen')
        args = parser.parse_args()
    except argparse.ArgumentError:
        print('Argument error, please see help message by using -h.')
        exit(1)

    # formate arguments
    port = args.port

    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

if __name__ == '__main__':
    main()
