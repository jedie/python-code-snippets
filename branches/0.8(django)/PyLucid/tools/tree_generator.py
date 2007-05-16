
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

    def make_dict(self, data, key_name):
        """
        generate a dict based on key_name
        """
        result = {}
        for row in data:
            key = row[key_name]
            if not key in result:
                result[key] = [row]
            else:
                result[key].append(row)

        return result

    def generate(self, data):
        """
        returns the tree data
        """
        parent_dict = self.make_dict(data, "parent")

        root = parent_dict.pop(None)
        root = self.insert_level(root, self.start_level)

        tree = self.gen(root, parent_dict, level=self.start_level+1)
        return tree


    def gen(self, block, data, level):
        """
        generate recurive the tree data
        """
        for row in block:
            id = row["id"]
            if id in data:
                subitems = data.pop(id)
                subitems = self.insert_level(subitems, level)
                row["subitems"] = self.gen(subitems, data, level+1)

        return block


if __name__ == "__main__":
    from pprint import pprint

    data = [
        {'id': 1,   'parent': None,  'name': '1. Entry'},
        {'id': 2,   'parent': 1,  'name': '1.1. first subitem'},
        {'id': 3,   'parent': 1,  'name': '1.2. second subitem'},
        {'id': 4,   'parent': 2,  'name': '1.2.1 first sub-subitem'},
        {'id': 5,   'parent': 2,  'name': '1.2.2 second sub-subitem'},
        {'id': 6,   'parent': None,  'name': '2. Entry'},
        {'id': 7,   'parent': 6,  'name': '2.1. first subitem'},
    ]

    tree = TreeGenerator().generate(data)
    pprint(tree)





