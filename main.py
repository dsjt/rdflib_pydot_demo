# -*- coding: utf-8 -*-
import sys
import rdflib
from DotWrapper import DotWrapper
import argparse

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def parse_arguments():
    parser = argparse.ArgumentParser(description='RDF と pydotの連携')
    parser.add_argument('-i', '--input', default="tmp.ttl",
                        help="入力ファイル(turtle)")
    parser.add_argument('-o', '--output', default=None,
                        help="出力ファイル(svg)")
    return parser.parse_args()

def main():
    args = parse_arguments()

    # turtleファイルの読み込み
    g = rdflib.Graph().parse(args.input, format="turtle")
    mn = g.namespace_manager

    # pydotグラフの作成
    graph = DotWrapper("my_graph")
    for s, p, o in g:
        graph.add_triple(s, p, o, g)

    if args.output is not None:
        graph.write_svg(args.output)
    else:
        print(graph)

    return

if __name__ == '__main__':
    main()
