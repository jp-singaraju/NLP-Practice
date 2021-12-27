import nltk
from nltk.corpus.reader import BracketParseCorpusReader

# read the file as corpus and parse it
reader = BracketParseCorpusReader('data', 'wsj_0010.mrg')


# combine the left and right siblings functions
def siblings(current_node):
    left_siblings(current_node)
    right_siblings(current_node)


# find all the left siblings, recursively, in the current node and print
def left_siblings(current_node):
    if current_node.left_sibling() is not None:
        print("Subtree: " + " ".join(current_node.left_sibling().leaves()) + "\n")
        left_siblings(current_node.left_sibling())


# find all the right siblings, recursively, in the current node and print
def right_siblings(current_node):
    if current_node.right_sibling() is not None:
        print("Subtree: " + " ".join(current_node.right_sibling().leaves()) + "\n")
        right_siblings(current_node.right_sibling())


# traverse through the tree, recursively
def traverse(t):
    # if the node contains only a pos and a word
    if t.height() == 2:

        # if the pos is a verb
        if t.label()[0] == 'V':
            print("\n" + "Verb: " + str(t) + "\n")
            current_node = t

            # while the node is not equal to the final top root node
            # call the siblings, then set node to the parent
            while current_node is not t.root():
                siblings(current_node)
                current_node = current_node.parent()
    # if the node contains more than only a pos and a word
    # then iterate and move onto the next child node
    else:
        for child in t:
            traverse(child)


# for each subtree in the reader, create a ParentedTree and call the traverse function
for subtree in reader.parsed_sents():
    tree = nltk.tree.ParentedTree.fromstring(str(subtree))
    traverse(tree)
