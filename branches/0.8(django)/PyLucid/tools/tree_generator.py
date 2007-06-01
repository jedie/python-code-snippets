
class TreeGenerator(object):
    def __init__(self, start_level=1):
        self.start_level = start_level

    def insert_level(self, data, level):
        """
        insert in every row a 'level'-key
        """
        for row in data:
            row["level"] = level
        return data

    def make_dict_list(self, data, key_name):
        """
        generate a dict based on key_name
        - every entry is a list!
        """
        result = {}
        for row in data:
            key = row[key_name]
            if not key in result:
                result[key] = [row]
            else:
                result[key].append(row)

        return result

    def make_unique_dict(self, data, key_name):
        """
        generate a dict based on key_name
        - The key must be unique!
        """
        result = {}
        for row in data:
            result[row[key_name]] = row

        return result

    def get_complete_tree(self, data):
        """
        returns the tree data for a sitemap
        """
        parent_dict = self.make_dict_list(data, "parent")

        root = parent_dict.pop(None)
        root = self.insert_level(root, self.start_level)

        tree = self.gen_complete_tree(root, parent_dict, self.start_level+1)
        return tree

    def gen_complete_tree(self, block, data, level):
        """
        generate recurive the tree data
        """
        for row in block:
            id = row["id"]
            if id in data:
                subitems = data.pop(id)
                subitems = self.insert_level(subitems, level)
                row["subitems"] = self.gen_complete_tree(subitems, data, level+1)

        return block

    def get_tree_menu(self, data, current_id):
        """
        returns a tree data for a tree menu
        """
        id_dict = self.make_unique_dict(data, "id")
        #~ print "id_dict:"
        #~ pprint(id_dict)

        parent_dict = self.make_dict_list(data, "parent")
        #~ print "\nparent_dict:"
        #~ pprint(parent_dict)
        #~ print

        try:
            subitems=parent_dict.pop(current_id)
            subitem_id=current_id
        except KeyError:
            # The current page has no sub pages
            subitems=None
            subitem_id=None

        tree_menu = self.gen_tree_menu(current_id, id_dict, parent_dict, subitems, subitem_id)
        return tree_menu

    def gen_tree_menu(self, current_id, id_dict, parent_dict, subitems=None,
                                                            subitem_id=None):

        current_page = id_dict.pop(current_id)
        #~ print "current_page:", current_page

        # get subitems for the next loop:
        parent_id = current_page["parent"]
        current_level_items = parent_dict.pop(parent_id)
        #~ print "current_level_items 1:", current_level_items

        for item in current_level_items:
            if item["id"] == subitem_id:
                item["subitems"] = subitems
                break

        #~ print "current_level_items 2:", current_level_items

        next_id = current_page["parent"]
        #~ print "next id:", next_id

        #~ print

        if next_id == None:
            return current_level_items
        else:
            return self.gen_tree_menu(
                next_id,
                id_dict, parent_dict,
                subitems=current_level_items,
                subitem_id = parent_id
            )


if __name__ == "__main__":
    from pprint import pprint
    import copy

    data = [
        {'id': 1, 'parent': None, 'name': '1. AAA'},
        {'id': 2, 'parent': 1,    'name': '1.1. BBB'},
        {'id': 3, 'parent': 1,    'name': '1.2. BBB'},
        {'id': 4, 'parent': 2,    'name': '1.2.1. CCC'},
        {'id': 5, 'parent': 2,    'name': '1.2.2. CCC'},
        {'id': 6, 'parent': None, 'name': '2. AAA'},
        {'id': 7, 'parent': 6,    'name': '2.1. BBB'},
    ]

    test_data = copy.deepcopy(data)
    tree = TreeGenerator().get_complete_tree(test_data)
    print "-"*80
    pprint(tree)

    print "-"*80

    test_data = copy.deepcopy(data)
    tree_menu = TreeGenerator().get_tree_menu(test_data, 2)
    print "-"*80
    pprint(tree_menu)

    print "-"*80

    test_data = copy.deepcopy(data)
    tree_menu = TreeGenerator().get_tree_menu(test_data, 6)
    print "-"*80
    pprint(tree_menu)




