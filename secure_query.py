import json
import myutil
from sql_parser import Query, QueryType
from execution import ExecutionTree, MatchBitsNode, NodeType
from execution_pass import Pass
import numpy as np
from Pyfhel import Pyfhel, PyCtxt

class SecureQuery():
    def __init__(self, query: Query=None, schema=None, HE=None, config=None, 
                 exe_tree=None, mapping_batch_ciphers=None):
        if query == None:
            self.exe_tree = exe_tree
            self.mapping_batch_ciphers = mapping_batch_ciphers
            return
        # Run Pass to optimize the execution tree
        assert MatchBitsNode.bit_width == config["execution"]["basic_block_bit_width"]
        exe_tree = ExecutionTree(query, schema)
        exe_tree = Pass.remove_or(exe_tree)
        self.exe_tree = Pass.decompose_equal(exe_tree)
        self.exe_tree = Pass.decompose_range(exe_tree)
        # Encrypt the execution tree
        n = 1 << config["he"]["poly_modulus_degree_bit_size"]
        mapping_batchs = []
        def group_mappings(node):
            if node.type == NodeType.BASIC:
                if not mapping_batchs or len(mapping_batchs[-1]) == n:
                    mapping_batchs.append([])
                node.mapping_cipher_id = len(mapping_batchs)
                node.mapping_cipher_offset = len(mapping_batchs[-1])
                mapping_batchs[-1] += node.generate_mapping
                node.values = None
                return
            for child in node.children:
                group_mappings(child)
        group_mappings(exe_tree.root)
        self.mapping_batch_ciphers = []
        for mapping_batch in mapping_batchs:
            mapping_batch_plain = np.array(mapping_batch, dtype=np.int64)
            self.mapping_batch_ciphers.append(HE.encryptInt(mapping_batch_plain))

    def serialize_to_json(self):
        return {
            "exe_tree": self.exe_tree.serialize_to_json(),
            "mapping_batch_ciphers": list(range(len(self.mapping_batch_ciphers)))
        }

    def dump(self): # Return type: str, List[bytes]
        ciphers_bytes = [cipher.to_bytes() 
                         for cipher in self.mapping_batch_ciphers]
        return json.dumps(self.serialize_to_json()), ciphers_bytes
    
    @staticmethod
    def from_dump(secure_query_dump, ciphers_bytes, HE_pub):
        secure_query_json = json.dumps(secure_query_dump)
        secure_query = SecureQuery(exe_tree=ExecutionTree.deserialize_from_json(secure_query_json["exe_tree"]))
        secure_query.mapping_batch_ciphers = []
        for id in secure_query_json["mapping_batch_ciphers"]:
            cipher = PyCtxt(pyfhel=HE_pub).from_bytes(ciphers_bytes[id])
            secure_query.mapping_batch_ciphers.append(cipher)
        return secure_query