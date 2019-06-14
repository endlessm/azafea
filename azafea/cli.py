import argparse
from typing import List


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='azafea',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-c', '--config', default='/etc/azafea/config.toml',
                        help='Optional path to a configuration file, if needed')
    parser.add_argument('-p', '--print-config', action='store_true',
                        help='Load the configuration, print it, then exit')

    return parser


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = get_parser()

    return parser.parse_args(args)
