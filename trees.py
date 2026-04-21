


class TreeNode:
    def __init__(self, data: int, parent = None, lc=0):

        self.data: int = data
        self.parent: TreeNode|None = parent
        self.lc = lc
        if not isinstance(parent, TreeNode):
            self.parent = None
        self.children: list = []


    def add_child(self, child):
        if isinstance(child, TreeNode):
            self.children.append(child)
        else:
            raise Exception("Invalid Node Type")

    def __eq__(self, other):
        """Value-based equality: nodes are equal if their data and children (recursively, order-sensitive)
        are equal. Returns NotImplemented for non-TreeNode types so Python can fall back to other's comparison.
        Note: this performs a recursive comparison and will recurse indefinitely if the tree contains cycles.
        """
        if self is other:
            return True
        if not isinstance(other, TreeNode):
            return NotImplemented
        if self.data != other.data:
            return False
        if len(self.children) != len(other.children):
            return False
        return all(a == b for a, b in zip(self.children, other.children))

    def __repr__(self):
        return f"TreeNode rank ({self.data}), LineCode ({self.lc}), children count ({len(self.children)})"

    # mutable nodes shouldn't be hashable by default
    __hash__ = None

    # --- Serialization helpers ---------------------------------
    def to_dict(self) -> dict:
        """Return a JSON-serializable dict representing this node and its subtree.
        Parent references are intentionally omitted to avoid cycles; the structure is represented
        by nested children.
        """
        return {
            "data": self.data,
            "lc": self.lc,
            "children": [c.to_dict() for c in self.children]
        }

    @staticmethod
    def from_dict(d: dict, parent=None):
        """Reconstruct a TreeNode (and its subtree) from a dict produced by to_dict.
        The parent argument is used internally for recursive construction and should normally be left as None.
        """
        node = TreeNode(data=d.get("data"), parent=parent, lc=d.get("lc", 0))
        for child_d in d.get("children", []):
            child = TreeNode.from_dict(child_d, parent=node)
            node.add_child(child)
        return node

    def to_json(self) -> str:
        """Serialize node subtree to a JSON string."""
        import json
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(s: str):
        import json
        d = json.loads(s)
        return TreeNode.from_dict(d)


class TNUtils:

    @staticmethod
    def build_tree(codes, tree: TreeNode) -> TreeNode:
        if len(codes) == 0:
            return tree
        row = codes.iloc[0,]
        code = row['LineCode']
        rank = row['rank']
        # print(f"------------------------------------------------------")
        # print(f"LineCode: {code}, rank: {rank}")
        # print(f"tree data: {tree.data}, tree parent data: {tree.parent.data if tree.parent else None}")
        # if tree.parent is not None:
        #     print(f" rank {rank} - tree.data {tree.data}: {(rank - tree.data) if tree.parent else None}")
        #
        # print(f"------------------------------------------------------")
        if tree.parent is None:
            # print("at root")
            new_node = TreeNode(data=rank, parent=tree, lc=code)
            tree.add_child(new_node)
            codes = codes.iloc[1:, ]
            return TNUtils.build_tree(codes, new_node)

        elif (rank - tree.data) == 1:
            # print("child")
            new_node = TreeNode(data=rank, parent=tree, lc=code)
            tree.add_child(new_node)
            codes = codes.iloc[1:, ]
            return TNUtils.build_tree(codes, new_node)

        elif rank == tree.data:
            # sibling
            # print("sibling")
            new_node = TreeNode(data=rank, parent=tree.parent, lc=code)
            new_node.parent.add_child(new_node)
            codes = codes.iloc[1:, ]
            return TNUtils.build_tree(codes, new_node)

        elif (rank - tree.data) == -1:
            # next node is an uncle/aunt
            # print("uncle/aunt")
            new_node = TreeNode(data=rank, parent=tree.parent.parent, lc=code)
            new_node.parent.add_child(new_node)
            codes = codes.iloc[1:, ]
            return TNUtils.build_tree(codes, new_node)

        elif (rank - tree.data) == -2:
            # next node is a great uncle/aunt
            # print("great uncle/aunt")
            new_node = TreeNode(data=rank, parent=tree.parent.parent.parent, lc=code)
            new_node.parent.add_child(new_node)
            codes = codes.iloc[1:, ]
            return TNUtils.build_tree(codes, new_node)

        else:
            print("fuck it")
            return tree


    @staticmethod
    def print_tree(node: TreeNode, level=0):
        if node is None:
            return
        print(' ' * (level * 2) + str(node.data))
        for child in node.children:
            TNUtils.print_tree(child, level + 1)

    # Create a function for depth-first traversal (pre-order)
    @staticmethod
    def pre_order_traversal(node: TreeNode):
        if node is None:
            return
        print(node.data)
        for child in node.children:
            TNUtils.pre_order_traversal(child)


    # Create a function for depth-first search
    @staticmethod
    def depth_first_search(node: TreeNode, target):
        if node is None:
            return False
        if node.data == target:
            return True
        for child in node.children:
            if TNUtils.depth_first_search(child, target):
                return True
        return False

    @staticmethod
    def depth_first_lc_search(node: TreeNode, target_lc):
        if node is None:
            return None
        if node.lc == target_lc:
            return node
        for child in node.children:
            result = TNUtils.depth_first_lc_search(child, target_lc)
            if result is not None:
                return result
        return None


    # Create a function for insertion
    @staticmethod
    def insert_node(root: TreeNode, node: TreeNode):
        if root is None:
            root = node
        else:
            root.add_child(node)

    # Create a function for deletion
    @staticmethod
    def delete_node(root: TreeNode, target):

        if root is None:
            return None
        root.children = [child for child in root.children if child.data != target]
        for child in root.children:
            TNUtils.delete_node(child, target)


    # Create a function to calculate the height of a tree
    @staticmethod
    def tree_height(node: TreeNode):
        if node is None:
            return 0
        if not node.children:
            return 1
        return 1 + max(TNUtils.tree_height(child) for child in node.children)

    # --- JSON helpers -------------------------------------------------
    @staticmethod
    def to_json(node: TreeNode) -> str:
        """Serialize the subtree rooted at node to a JSON string."""
        import json
        return json.dumps(node.to_dict())

    @staticmethod
    def from_json(s: str) -> TreeNode:
        """Deserialize a JSON string (produced by to_json) back into a TreeNode."""
        import json
        d = json.loads(s)
        return TreeNode.from_dict(d)


# Create a self-balancing tree (AVL tree)
# AVL tree implementation is complex, so we'll provide a basic example with the concept
# class AVLTreeNode(TreeNode):
#     def __init__(self, data):
#         super().__init__(data)
#         self.height = 1
#
#     def balance_factor(self):
#         left_height = self.children[0].height if self.children and len(self.children) > 0 else 0
#         right_height = self.children[1].height if self.children and len(self.children) > 1 else 0
#         return left_height - right_height
#
#     def update_height(self):
#         left_height = self.children[0].height if self.children and len(self.children) > 0 else 0
#         right_height = self.children[1].height if self.children and len(self.children) > 1 else 0
#         self.height = 1 + max(left_height, right_height)
#
#     def rotate_left(self):
#         new_root = self.children[1]
#         self.children[1] = new_root.children[0]
#         new_root.children[0] = self
#         self.update_height()
#         new_root.update_height()
#         return new_root
#
#     @staticmethod
#     def rotate_right(self):
#         new_root = self.children[0]
#         self.children[0] = new_root.children[1]
#         new_root.children[1] = self
#         self.update_height()
#         new_root.update_height()
#         return new_root
#
#     @staticmethod
#     def test2():
#         # Sample usage:
#         root = TreeNode("A")
#         child1 = TreeNode("B")
#         child2 = TreeNode("C")
#         child3 = TreeNode("D")
#
#         root.add_child(child1)
#         root.add_child(child2)
#         root.add_child(child3)
#
#         # Traversal example (pre-order)
#         print("Pre-order traversal:")
#         TNUtils.pre_order_traversal(root)
#
#         # Searching example
#         target_value = "D"
#         print(f"Is {target_value} present in the tree? {TNUtils.depth_first_search(root, target_value)}")
#
#         # Insertion example
#         new_node = TreeNode("E")
#         TNUtils.insert_node(child1, new_node)
#         print("After insertion:")
#         TNUtils.pre_order_traversal(root)
#
#         # Deletion example
#         TNUtils.delete_node(root, "C")
#         print("After deletion:")
#         TNUtils.pre_order_traversal(root)
#
#         # Height calculation example
#         print("Height of the tree:", TNUtils.tree_height(root))
#
#         # AVL tree example (basic concept)
#         avl_root = AVLTreeNode("M")
#         avl_child1 = AVLTreeNode("L")
#         avl_child2 = AVLTreeNode("R")
#
#         avl_root.add_child(avl_child1)
#         avl_root.add_child(avl_child2)
#
#         avl_child1.add_child(TreeNode("A"))
#         avl_child1.add_child(TreeNode("B"))
#
#         avl_child2.add_child(TreeNode("X"))
#
#         avl_root = avl_root.rotate_left()
#         print("After rotation (left):")
#         TNUtils.pre_order_traversal(avl_root)
#
#         avl_root = avl_root.rotate_right()
#         print("After rotation (right):")
#         TNUtils.pre_order_traversal(avl_root)
#
#
#     @staticmethod
#     def test(self):
#         root = TreeNode("A")
#         child1 = TreeNode("B")
#         child2 = TreeNode("C")
#         child3 = TreeNode("D")
#         # Add children to root
#         root.add_child(child1)
#         root.add_child(child2)
#         root.add_child(child3)
#
#         return root