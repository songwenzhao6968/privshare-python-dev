import json
from enum import Enum
from sql_parser import Predicate, Query
import numpy as np
from Pyfhel import Pyfhel

class NType(Enum):
    RETURN = "return",
    RETRIEVAL = "retrieval",
    AGGREGATION = "aggregation",
    AND = "and",
    OR = "or",
    NOT = "not",
    EQUAL = "equal",
    RANGE = "range",
    BASIC = "basic"

class ComputationNode():
    def __init__(self, type=None):
        self.type = type
        self.children = []
        self.parent = None

    def serialize_to_json(self, expand=True):
        children_json = []
        if expand:
            for child in self.children:
                children_json.append(child.serialize_to_json())
        return {
            "type": self.type.value,
            "children": children_json
            }

    @staticmethod
    def deserialize_from_json(json_node):
        node = ComputationNode()
        node.type = NType(json_node["type"])
        if node.type == NType.


        

class ReturnNode(ComputationNode):
    def __init__(self):
        super().__init__(NType.RETURN)