import sys
from data           import Data
from request_github import Fetcher
from svg_builder    import SVGBuilder


def main():
    data = Data()

    fetcher = Fetcher(data)
    fetcher.fetch_data()

    builder = SVGBuilder(data)
    builder.create_svg_cards()



if __name__ == '__main__':
    main()
    sys.exit(0)