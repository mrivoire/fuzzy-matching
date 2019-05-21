# -*- coding: utf-8 -*-
import bisect
import matplotlib.pyplot as plt
import numpy as np
import pyparsing 
import graphviz 
import dot2tex
import openfst_python as fst


def Matcher(tree, ref_string, hypothesis_string, root, first_char, accepted_chars = None, accepted_words = None, visited_states = None):
    if visited_states is None:
        visited_states = set()
    if accepted_chars is None:
        accepted_chars = []
    if accepted_words is None:
        accepted_words = set()

    visited_states.add(root)
    accepted_chars.append(first_char)
    word = word + first_char
    accepted_words.append(word)
    for next_node in tree[root] - visited_states:
        Matcher(tree, next_node, following_char, accepted_chars, accepted_words, visited_states)

    
    

    

def main():
    Matcher()
   
  

if __name__ == "__main__":
    # execute only if run as a script
    main()