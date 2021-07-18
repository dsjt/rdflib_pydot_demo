import logging
logger = logging.getLogger(__name__)

class Mapping(object):
    """
    RDFとpydotのオブジェクト間の対応関係を示す。
    """
    def __init__(self, naming):
        # obj -> node
        self.mapping = {}
        # node -> obj
        self.rev_map = {}

        self.count = 0
        self.naming = naming

    def increment(self):
        self.count += 1
        return self.count

    def register(self, obj):
        if obj not in self.mapping:
            self.mapping[obj] = self.naming(self.increment())
            self.rev_map[self.mapping[obj]] = obj
        return self.mapping[obj]

    def __call__(self, obj):
        """
        obj -> node
        """
        if obj not in self.mapping:
            self.register(obj)
        return self.mapping[obj]

    def rev(self, node):
        """
        node -> obj
        """
        return self.rev_map[node]

    def __str__(self):
        return "\n".join([f"{k}:{v}" for k, v in self.mapping.items()])


def nodename(identifier):
    return "node"+str(identifier)

def edgename(identifier):
    return "edge"+str(identifier)
