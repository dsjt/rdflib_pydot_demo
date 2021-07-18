# -*- coding: utf-8 -*-
import sys
from collections import defaultdict
import rdflib
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import FOAF , XSD
import pydot
from Mapping import Mapping
import html

import logging
logger = logging.getLogger(__name__)

def nodename(identifier):
    return "node"+str(identifier)

def edgename(identifier):
    return "edge"+str(identifier)

graph_settings = {
    "charset":"UTF-8",
    "labelloc":"b",
    "labeljust":"c",
    "bgcolor":"white",
    "fontcolor":"black",
    "fontsize":18,
    "style":"filled",
    "rankdir":"TB",
    "margin":0.2,
    "splines":"spline",
    "ranksep":1.0,
    "nodesep":0.9,
    "layout":"dot",
    "rankdir":"LR",
}

node_setting_template = {
    "style":"solid\\,filled",
    "fontsize":20,
    "fontcolor":"white",
    "fontname":"HackGen35",
    "fillcolor":"gray70",
    "color":"black",
    "shape": "box",
    "height":1,
    "width":2.0
}

class_settings = node_setting_template.copy()
class_settings["fillcolor"] = "#1f77b4"

instance_settings = node_setting_template.copy()
instance_settings["fillcolor"] = "#2ca02c"

literal_settings = node_setting_template.copy()
literal_settings["fillcolor"] = "#8c564b"

edge_settings = {
    "style":"solid",
    "fontsize":16,
    "fontcolor":"black",
    "fontname":"Hackgen",
    "color":"#ff7f0e",
    "labelfloat":True,
    "labeldistance":2.5,
    "labelangle":70,
    "penwidth":3.0
}

import argparse

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

    # Rdflibオブジェクトとpydot用文字列のマッピング作成
    node_mapping = Mapping(naming=nodename)
    edge_mapping = Mapping(naming=edgename)

    for s, p, o in g:
        sn = node_mapping.register(s)
        on = node_mapping.register(o)
        edge_mapping.register((s, p, o))


    # pydotグラフの作成
    graph = pydot.Dot("my_graph", **graph_settings)

    # pydot graphにnodeを登録する
    # クラスかインスタンスかリテラルかを区別しながら登録する。
    for obj, node in node_mapping.mapping.items():
        if isinstance(obj, URIRef):
            cand = list(g[obj:RDF.type:])
            if len(cand) == 0:  # クラスではなかろうか
                continue
                # graph.add_node(pydot.Node(node, label=obj,
                #                           **class_settings))
            else:               # インスタンスではなかろうか
                graph.add_node(pydot.Node(node, label=html.escape(obj.n3(mn)),
                                          **instance_settings))
        elif isinstance(obj, Literal):
            graph.add_node(pydot.Node(node, label=html.escape(obj.n3(mn)),
                                      **literal_settings))
        else:
            logger.warn(f"unknown object {obj.n3()}, {obj}, {type(obj)}")

    # pydot graphにedgeを登録する
    for (s, p, o), edge in edge_mapping.mapping.items():
        sn = node_mapping(s)
        on = node_mapping(o)
        if graph.get_node(sn) and graph.get_node(on):
            graph.add_edge(pydot.Edge(sn, on,
                                      label=html.escape(f"<{p.n3(mn)}>"),
                                      **edge_settings))

    if args.output is not None:
        graph.write_svg(args.output)
    else:
        print(graph)

    return

if __name__ == '__main__':
    main()
