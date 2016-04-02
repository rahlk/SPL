import numpy as np
import random
import pickle
import os


class Node(object):
    def __init__(self, identification, parent=None, node_type='o'):
        self.id = identification
        self.parent = parent
        self.node_type = node_type
        self.children = []
        if node_type == 'g':
            self.g_u = 1
            self.g_d = 0

    def add_child(self, node):
        node.parent = self
        self.children.append(node)

    def __repr__(self):
        # return '\n id: %s\n type:%s \n' % (
        #     self.id,
        #     self.node_type)
        return '%s|%s' % (self.node_type, self.id)


class Constraint(object):
    def __init__(self, identification, literals, literals_pos):
        self.id = identification
        self.literals = literals
        self.li_pos = literals_pos

    def __repr__(self):
        return self.id + '\n' + str(self.literals) + '\n' + str(self.li_pos)

    def is_correct(self, ft, filled_form):
        for (li, pos) in zip(self.literals, self.li_pos):
            i = ft.find_fea_index_by_id(li)
            if int(pos) == filled_form[i]:
                return True
        return False


class FeatureTree(object):
    def __init__(self):
        self.root = None
        self.features = []
        self.groups = []
        self.leaves = []
        self.con = []
        self.cost = []
        self.time = []
        self.featureNum = 0

    def set_root(self, root):
        self.root = root

    def add_constraint(self, con):
        self.con.append(con)

    def find_fea_index_by_id(self, identification):
        for i, x in enumerate(self.features):
            if x.id == identification:
                return i

    # fetch all the features in the tree basing on the children structure
    def set_features_list(self):
        def setting_feature_list(node):
            if node.node_type == 'g':
                node.g_u = int(node.g_u) if node.g_u != np.inf else len(node.children)
                node.g_d = int(node.g_d) if node.g_d != np.inf else len(node.children)
                self.features.append(node)
                self.groups.append(node)
            if node.node_type != 'g':
                self.features.append(node)
            if len(node.children) == 0:
                self.leaves.append(node)
            for i in node.children:
                setting_feature_list(i)

        setting_feature_list(self.root)
        self.featureNum = len(self.features)

    def post_order(self, node, func, extra_args=[]):
        if node.children:
            for c in node.children:
                self.post_order(c, func, extra_args)
        func(node, *extra_args)

    # setting the form by the structure of feature tree
    # leaves should be filled in the form in advanced
    # all not filled feature should be -1 in the form
    def fill_form4all_fea(self, form):
        def filling(node):
            index = self.features.index(node)
            if form[index] != -1:
                return
            # handling the group features
            if node.node_type == 'g':
                sum = 0
                for c in node.children:
                    i_index = self.features.index(c)
                    sum += form[i_index]
                form[index] = 1 if node.g_d <= sum <= node.g_u else 0
                return

            """
            # the child is a group
            if node.children[0].node_type == 'g':
                form[index] = form[index+1]
                return
            """

            # handling the other type of node
            m_child = [x for x in node.children if x.node_type in ['m', 'r', 'g']]
            o_child = [x for x in node.children if x.node_type == 'o']
            if len(m_child) == 0:  # all children are optional
                s = 0
                for o in o_child:
                    i_index = self.features.index(o)
                    s += form[i_index]
                form[index] = 1 if s > 0 else 0
                return
            for m in m_child:
                i_index = self.features.index(m)
                if form[i_index] == 0:
                    form[index] = 0
                    return
            form[index] = 1
            return

        self.post_order(self.root, filling)

    def fill_subtree_0(self, subtree_root, fulfill):
        """
        Setting the subtree rooted by node zeros.
        Fulfill vector will be modified
        NOTHING WILL BE RETURNED
        """
        def fill_zero(node, fill_vec):
            node_index = self.features.index(node)
            fill_vec[node_index] = 0

        self.post_order(subtree_root, fill_zero, [fulfill])

    def get_feature_num(self):
        return len(self.features) - len(self.groups)

    def get_cons_num(self):
        return len(self.con)

    def _gen_random_cost(self, tofile):
        tmp_list = [random.uniform(1, 10) * (i % 3+1) for i in range(len(self.features))]
        # note to upper line: try to diverse the data
        random.shuffle(tmp_list)
        self.cost = tmp_list
        with open(tofile, 'w+') as f:
            pickle.dump(self.cost, f)

    def _gen_random_time(self, target_file):
        tmp_list = [random.uniform(5, 15) * (i % 4+1) for i in range(len(self.features))]
        # note to upper line: try to diverse the data
        random.shuffle(tmp_list)
        self.time = tmp_list
        with open(target_file, 'w+') as f:
            pickle.dump(self.time, f)

    def load_cost(self, model_name):
        import sys
        spl_address = [i for i in sys.path if i.endswith('/SPL')][0]
        fromfile = spl_address + "/input/" + model_name + ".cost"

        if not os.path.isfile(fromfile):
            self._gen_random_cost(fromfile)

        with open(fromfile, 'r') as f:
            self.cost = pickle.load(f)

    def load_time(self, model_name):
        import sys
        spl_address = [i for i in sys.path if i.endswith('/SPL')][0]
        fromfile = spl_address + "/input/" + model_name + ".time"

        if not os.path.isfile(fromfile):
            self._gen_random_time(fromfile)

        with open(fromfile, 'r') as f:
            self.time = pickle.load(f)
