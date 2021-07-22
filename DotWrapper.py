# -*- coding: utf-8 -*-
from pydot import Node, Dot, Edge
import rdflib
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import FOAF , XSD
from Mapping import Mapping

import logging
logger = logging.getLogger(__name__)

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
    "ratio":"compress",
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
    "width":3,
    "margin":"0\\, 1"
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

def encode_label(s):
    """
    pydot.Nodeのラベルに指定する際に必要なエスケープを加える
    """
    if s.startswith("<") and s.endswith(">"):
        return s
    else:
        return s.replace(":", "\\:")

class DotWrapper(Dot):
    """pydot.Dotのラッパーである。
    add_node, add_edgeの際、rdflibオブジェクトの文字列表現は、URIになる場合があ
    り、変数名としてふさわしくない。rdflibのオブジェクトを指定した際、自動的に変
    数名を割り当てる。
    """
    def __init__(self, name, graph_settings=graph_settings):
        self.name = name
        self.node_mapping = Mapping(naming=DotWrapper.nodename)
        super().__init__(name, **graph_settings)
        pass

    @classmethod
    def nodename(cls, identifier):
        return "node"+str(identifier)

    def add_triple(self, rdf_sub, rdf_pred, rdf_obj, graph):
        self.add_node(rdf_sub, graph)
        self.add_node(rdf_obj, graph)
        self.add_edge(rdf_sub, rdf_pred, rdf_obj, graph)
        pass

    def add_node(self, rdf_obj, graph):
        """
        rdflibオブジェクトを元に、pydotグラフにノードを追加する。
        """
        ret = None
        obj_name = self.node_mapping(rdf_obj)
        s_add_node = super().add_node
        label = encode_label(rdf_obj.n3(graph.namespace_manager))
        if isinstance(rdf_obj, URIRef):
            if list(graph[rdf_obj:RDF.type:]):
                ret = s_add_node(Node(obj_name,
                                      label=label,
                                      **instance_settings))
            else:
                ret = s_add_node(Node(obj_name,
                                      label=label,
                                      **class_settings))
        elif isinstance(rdf_obj, Literal):
            ret = s_add_node(Node(obj_name,
                                  label=label,
                                  **literal_settings))
        else:
            logger.warn(f"unknown object {rdf_obj}")
            logger.warn(f"{rdf_obj.n3()=}, {type(rdf_obj)=}")

        return ret

    def add_edge(self, rdf_sub, rdf_pred, rdf_obj, graph):
        """
        rdflibのトリプルを元に、pydotグラフにエッジを追加する。
        """
        sub_name = self.node_mapping(rdf_sub)
        obj_name = self.node_mapping(rdf_obj)
        label = encode_label(rdf_pred.n3(graph.namespace_manager))
        super().add_edge(Edge(sub_name, obj_name,
                              label=label,
                              **edge_settings))
