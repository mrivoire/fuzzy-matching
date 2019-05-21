import matplotlib.pyplot as plt
import numpy as np
import pyparsing 
import graphviz 
import dot2tex

def main():
   
    # nodes_dict = {
    #   1: "a_1",
    #   2: "b_2",
    #   3: "c_3",
    #   4: "d_4",
    #   5: "e_5"
    # }
    
    # for key, state in nodes_dict:
    #     for index, label in nodes_dict[state]:
    #         print(nodes_dict[state][index])

    nodes_list = ["a_1", "b_2","c_3", "d_4","e_5"]
    for i in enumerate(nodes_list):
        print(nodes_list[i])
    
if __name__ == "__main__":
    # execute only if run as a script
    main()
