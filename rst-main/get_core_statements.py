from nltk.tree import ParentedTree


def clean_result(core_stat):
    clean_string = " ".join(core_stat)\
            .strip("_!")\
            .replace(" .",".")\
            .replace(" ,",",")\
            .replace(" ?","?").replace(" !","!")\
            .strip()

    return clean_string


def traverse(tree, core_statements):
    """
    Traverses the nltk.ParentedTree with the RST annotations according
    to the Strong Nuclearity Hypothese (Marcu, 2000) and returns all
    EDUs found in this way in a list of strings.

    :param tree: RST annotated ParentedTree
    :param core_statements: list
    :return: core_statements
    """
    if type(tree) == ParentedTree:
        for child in tree:
            if type(child) == ParentedTree:
                if child.label() == "Nucleus":
                    if child.height() == 3:
                        for c in child:
                            if c.label() == "text":
                                temp_core_stat = clean_result(c.leaves())
                                core_statements.append(temp_core_stat)

                    traverse(child, core_statements)


def get_core_statements(tree):
    """Wrapper function for the tree traverse function."""
    core_statements = []
    traverse(tree, core_statements)
    return core_statements
