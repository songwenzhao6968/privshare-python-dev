from execution import AndNode, OrNode, NotNode, MatchBitsNode, NodeType

class Pass:
    @staticmethod
    def remove_or(exe_tree):
        def rewrite_or_node(node):
            if node.type == NodeType.OR:
                node_not0, node_not1, node_not2 = NotNode(), NotNode(), NotNode()
                node_and = AndNode()
                node_not0.link(node_and)
                node_and.link(node_not1); node_and.link(node_not2)
                node_not1.link(rewrite_or_node(node.children[0]))
                node_not2.link(rewrite_or_node(node.children[1]))
                return node_not0
            children = node.children
            node.children = []
            for child in children:
                node.link(rewrite_or_node(child))
            return node
        
        exe_tree.root = rewrite_or_node(exe_tree.root)
        return exe_tree
    
    @staticmethod
    def decompose_equal(exe_tree):
        def rewrite_equal_node(node):
            if node.type == NodeType.EQUAL:
                if node.bit_width == 8:
                    node_mb = MatchBitsNode.decompose_equal(node, 0)
                    return node_mb
                elif node.bit_width == 16:
                    node_mb0 = MatchBitsNode.decompose_equal(node, 0)
                    node_mb1 = MatchBitsNode.decompose_equal(node, 8)
                    node_and = AndNode()
                    node_and.link(node_mb0); node_and.link(node_mb1)
                    return node_and
                elif node.bit_width == 32:
                    node_mb0 = MatchBitsNode.decompose_equal(node, 0)
                    node_mb1 = MatchBitsNode.decompose_equal(node, 8)
                    node_mb2 = MatchBitsNode.decompose_equal(node, 16)
                    node_mb3 = MatchBitsNode.decompose_equal(node, 24)
                    node_and0, node_and1, node_and2 = AndNode(), AndNode(), AndNode()
                    node_and0.link(node_and1); node_and0.link(node_and2)
                    node_and1.link(node_mb0); node_and1.link(node_mb1)
                    node_and2.link(node_mb2); node_and2.link(node_mb3)
                    return node_and0
            children = node.children
            node.children = []
            for child in children:
                node.link(rewrite_equal_node(child))
            return node
        
        exe_tree.root = rewrite_equal_node(exe_tree.root)
        return exe_tree

    @staticmethod
    def decompose_range(exe_tree):
        def rewrite_range_node(node):
            if node.type == NodeType.RANGE:
                if node.bit_width == 8:
                    node_mb = MatchBitsNode.decompose_range(node, 0, False, True, True)
                    return node_mb
                elif node.bit_width == 16:
                    _min, _max = 0, (1 << node.bit_width) - 1
                    if node.value_l == _min: # Right side  
                        node_mb0 = MatchBitsNode.decompose_range(node, 8, False, False, True, False, True)
                        node_mb1 = MatchBitsNode.decompose_range(node, 8, True, False, True)
                        node_mb2 = MatchBitsNode.decompose_range(node, 0, False, False, True, False, False)
                        node_and = AndNode()
                        node_or = OrNode()
                        node_and.link(node_mb1); node_and.link(node_mb2)
                        node_or.link(node_and, node_mb0)
                        return node_or
                    else:
                        raise NotImplementedError
                elif node.bit_width == 32:
                    raise NotImplementedError
            children = node.children
            node.children = []
            for child in children:
                node.link(rewrite_range_node(child))
            return node
        
        exe_tree.root = rewrite_range_node(exe_tree.root)
        return exe_tree