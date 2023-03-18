import json
import myutil
from sql_parser import Query
from execution import ExecutionTree, MatchBitsNode, NodeType
from execution_pass import Pass
import numpy as np
from he import PyCtxt

class SecureQuery():
    def __init__(self, query: Query=None, schema=None, HE=None, config=None, 
                 exe_tree=None, mapping_ciphers=None):
        if query == None:
            self.exe_tree = exe_tree
            self.mapping_ciphers = mapping_ciphers
            return
        # Run Pass to transform the execution tree
        assert MatchBitsNode.bit_width == config["basic_block_bit_width"]
        exe_tree = ExecutionTree(query, schema)
        exe_tree = Pass.remove_or(exe_tree)
        self.exe_tree = Pass.decompose_equal(exe_tree)
        self.exe_tree = Pass.decompose_range(exe_tree)
        # Encrypt the execution tree
        mappings = []
        def group_mappings(node):
            if node.type == NodeType.BASIC:
                if not mappings or len(mappings[-1]) == HE.n:
                    mappings.append([])
                node.mapping_cipher_id = len(mappings)
                node.mapping_cipher_offset = len(mappings[-1])
                mappings[-1] += node.generate_mapping()
                node.values = None
                return
            for child in node.children:
                group_mappings(child)
        group_mappings(exe_tree.root)
        self.mapping_ciphers = []
        for mapping in mappings:
            mapping = np.array(mapping, dtype=np.int64)
            self.mapping_ciphers.append(HE.encryptInt(mapping))

    def serialize_to_json(self):
        return {
            "exe_tree": self.exe_tree.serialize_to_json(),
            "mapping_ciphers": list(range(len(self.mapping_ciphers)))
        }

    def dump(self): # Return type: str, List[bytes]
        ciphers_bytes = [cipher.to_bytes() 
                         for cipher in self.mapping_ciphers]
        return json.dumps(self.serialize_to_json()), ciphers_bytes
    
    @staticmethod
    def from_dump(secure_query_dump, ciphers_bytes, HE):
        secure_query_json = json.dumps(secure_query_dump)
        secure_query = SecureQuery(exe_tree=ExecutionTree.deserialize_from_json(secure_query_json["exe_tree"]))
        secure_query.mapping_ciphers = []
        for id in secure_query_json["mapping_ciphers"]:
            cipher = PyCtxt(pyfhel=HE).from_bytes(ciphers_bytes[id])
            secure_query.mapping_ciphers.append(cipher)
        return secure_query