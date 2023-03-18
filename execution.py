import json
from enum import Enum
import myutil
from sql_parser import Query, QueryType, Predicate
from database import DataBase, DataType, Table
import numpy as np
import he

class NodeType(Enum):
    RETURN = "return"
    RETRIEVAL = "retrieval"
    AGGREGATION = "aggregation"
    AND = "and"
    OR = "or"
    NOT = "not"
    EQUAL = "equal"
    RANGE = "range"
    BASIC = "basic"

class ComputationNode():
    def __init__(self, type=None):
        self.type = type
        self.children = []

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
    def deserialize_from_json(node_json, expand=True): 
        type = NodeType(node_json["type"])
        if type == NodeType.RETURN:
            node = ReturnNode(node_json["concerned_table"])
        elif type == NodeType.RETRIEVAL:
            node = RetrievalNode(node_json["concerned_columns"])
        elif type == NodeType.AGGREGATION:
            node = AggregationNode(node_json["agg_type"], node_json["concerned_column"])
        elif type == NodeType.AND:
            node = AndNode()
        elif type == NodeType.OR:
            node = OrNode()
        elif type == NodeType.NOT:
            node = NotNode()
        elif type == NodeType.EQUAL:
            node = EqualNode(
                concerned_column = node_json["concerned_column"],
                bit_width = node_json["bit_width"],
                need_int_to_uint_conversion = node_json["need_int_to_uint_conversion"],
                need_str_to_uint_conversion = node_json["need_str_to_uint_conversion"],
                value = node_json["value"],
            )
        elif type == NodeType.RANGE:
            node = RangeNode(
                concerned_column = node_json["concerned_column"],
                bit_width = node_json["bit_width"],
                need_int_to_uint_conversion = node_json["need_int_to_uint_conversion"],
                value_l = node_json["value_l"],
                value_r = node_json["value_r"]
            )
        elif type == NodeType.BASIC:
            node = MatchBitsNode(
                need_int_to_uint_conversion = node_json["need_int_to_uint_conversion"],
                need_str_to_uint_conversion = node_json["need_str_to_uint_conversion"],
                concerned_column = node_json["concerned_column"],
                offset = node_json["offset"],
                values = node_json["values"],
                mapping_cipher_id = node_json["mapping_cipher_id"],
                mapping_cipher_offset = node_json["mapping_cipher_offset"]
            )
        if expand:
            for child_json in node_json["children"]:
                node.children.append(ComputationNode.deserialize_from_json(child_json))
        return node
    
    def dump(self):
        return json.dumps(self.serialize_to_json())
    
    @staticmethod
    def from_dump(node_dump):
        return ComputationNode.deserialize_from_json(json.loads(node_dump))


class ReturnNode(ComputationNode):
    def __init__(self, concerned_table):
        super().__init__(NodeType.RETURN)
        self.concerned_table = concerned_table
        
    def serialize_to_json(self, expand=True):
        ret = super().serialize_to_json(expand)
        ret["concerned_table"] = self.concerned_table
        return ret
    
    def process(db: DataBase, config):
        pass

class RetrievalNode(ComputationNode):
    def __init__(self, concerned_columns):
        super().__init__(NodeType.RETRIEVAL)
        self.concerned_columns = concerned_columns
    
    def serialize_to_json(self, expand=True):
        ret = super().serialize_to_json(expand)
        ret["concerned_columns"] = self.concerned_columns
        return ret
    
    def process(table, config):
        raise NotImplementedError

class AggregationNode(ComputationNode):
    def __init__(self, agg_type: QueryType, concerned_column):
        super().__init__(NodeType.AGGREGATION)
        self.agg_type = agg_type
        self.concerned_column = concerned_column
    
    def serialize_to_json(self, expand=True):
        ret = super().serialize_to_json(expand)
        ret["agg_type"] = self.agg_type.value
        ret["concerned_column"] = self.concerned_column
        return ret
    
    def process(table, config):
        pass

class AndNode(ComputationNode):
    def __init__(self):
        super().__init__(NodeType.AND)
    
    def process(table, config):
        pass

class OrNode(ComputationNode):
    def __init__(self):
        super().__init__(NodeType.OR)

class NotNode(ComputationNode):
    def __init__(self):
        super().__init__(NodeType.NOT)
    
    def process():
        pass

class EqualNode(ComputationNode):
    def __init__(self, concerned_column, value, schema=None,
                 bit_width=None, need_int_to_uint_conversion=None, need_str_to_uint_conversion=None): 
        super().__init__(NodeType.EQUAL)
        if schema == None:
            self.concerned_column = concerned_column
            self.bit_width = bit_width
            self.need_int_to_uint_conversion = need_int_to_uint_conversion
            self.need_str_to_uint_conversion = need_str_to_uint_conversion
            self.value = value
            return
        dtype = schema.get_type(concerned_column)
        temp = { # DataType: (bit_width, need_int_to_uint_conversion, need_str_to_uint_conversion)
            DataType.UINT8: (8, False, False),
            DataType.UINT16: (16, False, False),
            DataType.UINT32: (32, False, False),
            DataType.INT8: (8, True, False),
            DataType.INT16: (16, True, False),
            DataType.INT32: (32, True, False),
            DataType.STR: (32, False, True),
        }
        self.bit_width, self.need_int_to_uint_conversion, self.need_str_to_uint_conversion = temp(dtype)
        if self.need_str_to_uint_conversion:
            self.value = myutil.str_to_uint(value)
        elif self.need_int_to_uint_conversion:
            self.value = myutil.int_to_uint(value)
        else:
            self.value = value

    def serialize_to_json(self, expand=True):
        ret = super().serialize_to_json(expand)
        ret["concerned_column"] = self.concerned_column
        ret["bit_width"] = self.bit_width
        ret["need_int_to_uint_conversion"] = self.need_int_to_uint_conversion
        ret["need_str_to_uint_conversion"] = self.need_str_to_uint_conversion
        ret["value"] = self.value
        return ret
        
class RangeNode(ComputationNode):
    def __init__(self, concerned_column, value=None, schema=None, pred_type=None,
                bit_width=None, need_int_to_uint_conversion=None, value_l=None, value_r=None):
        super().__init__(NodeType.RANGE)
        if schema == None:
            self.concerned_column = concerned_column
            self.bit_width = bit_width
            self.need_int_to_uint_conversion = need_int_to_uint_conversion
            self.value_l = value_l
            self.value_r = value_r
            return
        self.concerned_column = concerned_column
        dtype = schema.get_type(concerned_column)
        temp = { # DataType: (bit_width, need_int_to_uint_conversion)
            DataType.UINT8: (8, False),
            DataType.UINT16: (16, False),
            DataType.UINT32: (32, False),
            DataType.INT8: (8, True),
            DataType.INT16: (16, True),
            DataType.INT32: (32, True),
        }
        self.bit_width, self.need_int_to_uint_conversion = temp(dtype)
        if self.need_int_to_uint_conversion:
            value = myutil.int_to_uint(value)
        _min, _max = 0, (1 << self.bit_width) - 1
        temp = { # PredicateType: (value_l, value_r)
            "<": (_min, value-1), 
            "<=": (_min, value),
            ">": (value+1, _max),
            ">=": (value, _max)
        } # Potential bug here: <0, >_max
        self.value_l, self.value_r = temp(pred_type)

    def serialize_to_json(self, expand=True):
        ret = super().serialize_to_json(expand)
        ret["concerned_column"] = self.concerned_column
        ret["bit_width"] = self.bit_width
        ret["need_int_to_uint_conversion"] = self.need_int_to_uint_conversion
        ret["value_l"] = self.value_l
        ret["value_r"] = self.value_r
        return ret
        
class MatchBitsNode(ComputationNode):
    bit_width = 8
    def __init__(self, need_int_to_uint_conversion, need_str_to_uint_conversion, 
                    concerned_column, offset, values=None, mapping_cipher_id=None, mapping_cipher_offset=None):
        super().__init__(NodeType.BASIC)
        self.need_int_to_uint_conversion = need_int_to_uint_conversion
        self.need_str_to_uint_conversion = need_str_to_uint_conversion
        self.concerned_column = concerned_column
        self.offset = offset
        self.values = values
        self.mapping_cipher_id = mapping_cipher_id
        self.mapping_cipher_offset = mapping_cipher_offset

    @staticmethod
    def equal_decompose(node_eq: EqualNode, offset):
        node_mb = MatchBitsNode(
            need_int_to_uint_conversion = node_eq.need_int_to_uint_conversion,
            need_str_to_uint_conversion = node_eq.need_str_to_uint_conversion,
            concerned_column = node_eq.concerned_column,
            offset = offset
        )
        node_mb.values = [(node_eq.value >> offset) & ((1 << MatchBitsNode.bit_width) - 1)]

    @staticmethod
    def range_decompose(node_rg: RangeNode, offset, params):
        raise NotImplementedError

    def generate_mapping(self):
        mapping = [0] * (1 << MatchBitsNode.bit_width)
        for value in self.values:
            mapping[value] = 1
        return mapping

    def serialize_to_json(self, expand=True):
        ret = super().serialize_to_json(expand)
        ret["need_int_to_uint_conversion"] = self.need_int_to_uint_conversion
        ret["need_str_to_uint_conversion"] = self.need_str_to_uint_conversion
        ret["concerned_column"] = self.concerned_column
        ret["offset"] = self.offset
        ret["values"] = self.values
        ret["mapping_cipher_id"] = self.mapping_cipher_id
        ret["mapping_cipher_offset"] = self.mapping_cipher_offset
        return ret
    
    def process(self, table: Table, HE, config):
        concerned_column_id = table.schema.get_id(self.concerned_column)
        column = []
        for record in table.data:
            value = record[concerned_column_id]
            if self.need_str_to_uint_conversion:
                value = myutil.str_to_uint(value)
            elif self.need_int_to_uint_conversion:
                value = myutil.int_to_uint(value)
            value = (value >> self.offset) & ((1 << MatchBitsNode.bit_width) - 1)
            column.append(value)
            if len(column) == HE.n:
                x = np.array(column, dtype=np.int64)
                apply_elementwise_mapping()

            

        

class ExecutionTree():
    def __init__(self, query: Query=None, schema=None, root=None):
        if self.query == None:
            self.root = root
            return
        self.root = ReturnNode(query.concerned_table)
        if query.is_retrieve():
            node_op = RetrievalNode(query.concerned_column)
        elif query.is_aggregate():
            node_op = AggregationNode(query.type, query.concerned_column)
        self.root.children.append(node_op)

        def add_predicates(pred: Predicate, schema):
            if pred.type == "AND":
                node = AndNode()
            elif pred.type == "OR":
                node = OrNode()
            elif pred.type == "=":
                node = EqualNode(pred.concerned_column, pred.value, schema)
            elif pred.type == "!=":
                node_eq = EqualNode(pred.concerned_column, pred.value, schema)
                node = NotNode()
                node.children.append(node_eq)
            elif pred.type in ["<", "<=", ">", ">="]:
                node = RangeNode(pred.concerned_column, pred.value, schema, pred.type)
            if not pred.is_leaf:
                node.children = [add_predicates(pred.left_child, schema),
                                add_predicates(pred.right_child, schema),]
            return node
        node_op.children.append(add_predicates(query.pred, schema))
    
    def get_query_type(self):
        if self.root.children[0].type == NodeType.RETRIEVAL:
            return QueryType.RETRIEVE
        elif self.root.children[0].type == NodeType.AGGREGATION:
            return self.children[0].agg_type
    
    def serialize_to_json(self):
        return {"root": self.root.serialize_to_json()}
    
    @staticmethod
    def deserialize_from_json(exe_tree_json):
        return ExecutionTree(
            root = ComputationNode.deserialize_from_json(exe_tree_json["root"])
            )
    
    def dump(self):
        return json.dumps(self.serialize_to_json())
    
    @staticmethod
    def from_dump(exe_tree_dump):
        return ExecutionTree.deserialize_from_json(json.loads(exe_tree_dump))