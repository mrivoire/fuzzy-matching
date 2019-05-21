import bisect
import matplotlib.pyplot as plt
import numpy as np
import pyparsing 
import graphviz 
import dot2tex
import openfst_python as fst 

def OpenFST_Automata_Example():
    f = fst.Fst()
    s0 = f.add_state()
    s1 = f.add_state()
    s2 = f.add_state()
    f.add_arc(s0, fst.Arc(1, 2, fst.Weight(f.weight_type(), 3.0), s1))
    f.add_arc(s0, fst.Arc(1, 3, fst.Weight.One(f.weight_type()), s2))
    f.add_arc(s1, fst.Arc(2, 1, fst.Weight(f.weight_type(), 1.0), s2))
    f.set_start(s0)
    f.set_final(s2, fst.Weight(f.weight_type(), 1.5))

    print(s0, s1, s2)
    print(f)

def Example_To_GraphViz():
    print("digraph G{")
    node0 = "0 [label = s0]"
    node1 = "1 [label = s1]"
    node2 = "2 [label = s2]"
    print(node0)
    print(node1)
    print(node2)

    edge_01 = "0 -> 1 [label=\"1:2 - 3.0\"]"  
    edge_02 = "0 -> 2 [label=\"1:3 - 2.0\"]"
    edge_12 = "1 -> 2 [label=\"2:1 - 1.0\"]"
    print(edge_01)
    print(edge_02)
    print(edge_12)
    print("}")

def OpenFST_Automata_Test(set_src_states, set_dst_states, set_labels):
    f = fst.Fst()

    for i, src in set_src_states:
        for j, label in set_labels[src]:
            for k, dst in set_dst_states[src][labels]:
                print(src, label, dst)


def printArcs(arcs):
    return str(arcs)

def printDsts(dsts):
    return(str(dsts))

def printTransitions(dico):
    print(dico["src"] + ' ' + printArcs(dico["arcs"]))# + ' ' + printDsts(dico["dsts"]))


def main():

    OpenFST_Automata_Example()
    Example_To_GraphViz()

    set_src_states = {
        "0": "s0",
        "1": "s1",
        "2": "s2"
    }
    print(set_src_states)

    set_labels = {
       "s0": ["1:1","epsilon"],
       "s1": ["1:2", "2:3"],
       "s2": ["2:2", "3:1"]
    }
    print(set_labels)

    set_dst_states = {
       "1:1": ["s1"],
       "1:2": ["s0"],
       "2:2": ["s0"],
       "2,3": ["s2"],
       "3:1": ["s0"],
       "epsilon": ["s2"]
    }
    print(set_dst_states)

    set_transitions = (
       {
           "src": "s0",
           "arcs": {
                {
                   "arc_label": "1:1",
                    "dsts": (
                        "s0",
                        "s1"
                    )
                },
                {
                   "arc_label": "epsilon",
                   "dsts": (
                        "s0",
                        "s2"
                    )
                }
            }
        },
        {   
           "src": "s1",
           "arcs": {
                {
                   "arc_label": "1:2",
                   "dsts": (
                        "s0",
                        "s2"
                    )
                },
                {
                   "arc_label": "2:3",
                   "dsts": (
                        "s1"
                    )
                }
                    
            }
        },
        {
           "src": "s2",
           "arcs": {
               {
                   "arc_label": "2:2",
                   "dsts": (
                       "s2"
                    )
               },
               {
                   "arc_label": "1:3",
                   "dsts": (
                       "s0",
                       "s1"
                   )
               }
            }
        }
    )
    # print(set_transitions)

    # for transition in set_transitions:
    #     for key_src, src in set_transitions[transition]:
    #         for key_arc, arc in enumerate(set_transitions[transition]):
    #             for key_dst, dst in enumerate(set_transitions[transition][arc]):
    #                 print(src, arc, dst)


    # map(printTransitions, set_transitions)
    


    
if __name__ == "__main__":
    # execute only if run as a script
    main()