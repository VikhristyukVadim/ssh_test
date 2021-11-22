import argparse


def argument_parser():
    """Initialising of arg parser"""
    parser = argparse.ArgumentParser(description='--> launch App', formatter_class=argparse.RawTextHelpFormatter, )

    """Creating parser arguments"""
    # Server parser----------------------------------------------------------------------------------------------------
    parser.add_argument('--ip', help="ip address", required=True)
    parser.add_argument('-p', help="port", required=True)
    parser.add_argument('-password', help="password", required=True)

    args = parser.parse_args()
    return args
