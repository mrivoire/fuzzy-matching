# -*- coding: utf-8 -*-
import bisect
import matplotlib.pyplot as plt
import numpy as np
import pyparsing 
import graphviz 
import dot2tex
import openfst_python as fst

automate = fst.Fst()

def SimpleAutomata():
    src_state_label = "0;0"
    src_state_index = automate.add_state()

    dst_state_label = "0;1"
    dst_state_index = automate.add_state()
    arc_label = "2:4:1"
    label_string = arc_label.split(":")
    consummed_char = 2 # int(label_string[0])
    transmitted_char = 4 # int(label_string[1])
    weight = 1 # int(label_string[2])

    automate.add_arc(
        src_state_index,
        fst.Arc(
            transmitted_char,
            consummed_char,
            fst.Weight(automate.weight_type(), weight),
            dst_state_index
        )
    )
    
    print(automate)


def convertSymToLabel(symbol):
    if(len(symbol) == 1):
        newSym = ord(symbol)
    elif(symbol == "epsilon"):
        newSym = 1
    return(newSym)

def label2int(label, ref_string):
    return (len(ref_string)+1)*int(label[2])+int(label[0])


def create_states_dico(ref_string, levenshtein_distance):
    dict_levenshtein_states = {}
    for column in range(len(ref_string) + 1):
        for row in range(levenshtein_distance + 1):
            state_label = str(column) + ";" + str(row)
            dict_levenshtein_states[state_label] = label2int(state_label, ref_string)
    return dict_levenshtein_states

def print_dot_format(dico, ref_string, levenshtein_distance):
    dict_levenshtein_states = create_states_dico(ref_string, levenshtein_distance)
    print("digraph G {")
    i = 1
    states_ids = {}

    for state_label, state in dict_levenshtein_states.iteritems():
        display_node = "  " + str(i) + " [texlbl=\"" + state_label + "\"];"
        states_ids[state_label] = str(i)
        i = i + 1
        print(display_node)

    for src_state_label, partial_transitions in dico.iteritems():
        for arc_label, dsts_states in partial_transitions.iteritems():
            for dst_state_label in dsts_states:
                display_edge = "  " + states_ids[src_state_label] + "->" + states_ids[dst_state_label] + " [label=\""  + arc_label + "\"];"
                print(display_edge)    
    print("}")         


def Levenshtein_Automata_Dico(ref_string, levenshtein_distance):
    # Creation des etats de l'automate 
    dict_levenshtein_states = create_states_dico(ref_string, levenshtein_distance)

    # Creation des arcs emergeants de chaque etat
    # Pour les poids on pose que : d = 0 si on consomme un caractere, et 1 si on consomme etoile ou epsilon (insertion, deletion, substitution)
    # Pour les caracteres consommes et emis, on considere que les caracteres de la chaine de reference sont les caracteres consommes et les caracteres de la chaine hypothese seront les caracteres emis 
    
    
    automata = {}
    weights = [0, 1, 1,1]
    arcs_labels = []
    dst_states = []
    automata_voc = ["epsilon", "*"]
    automata_voc.extend(ref_string)

    for state_label, state_index in dict_levenshtein_states.iteritems():
        nb_consummed_chars = int(state_label.split(";")[0]) # 1er caractere du label
        nb_elementary_operations = int(state_label.split(";")[1]) # 2nd caractere du label

        set_arcs = {}
        arcs_labels = []
        char_from_ref_str = ''
        if nb_consummed_chars == len(ref_string):
            char_from_ref_str = "epsilon"
        else:
            char_from_ref_str = ref_string[nb_consummed_chars]

        up_dst_label = str(nb_consummed_chars) + ";" + str(nb_elementary_operations + 1)
        # print("up", up_dst_label)
        diag_dst_label = str(nb_consummed_chars + 1) + ";" + str(nb_elementary_operations + 1)
        # print("diag", diag_dst_label)
        right_dst_label = str(nb_consummed_chars + 1) + ";" + str(nb_elementary_operations)
        # print("right", right_dst_label)

        is_last_column = nb_consummed_chars == len(ref_string)
        is_last_row = nb_elementary_operations == levenshtein_distance
        if is_last_column and is_last_row:
            output_arc_label = "epsilon" + "::" + "epsilon" + "::" + str(0)            
            set_arcs[output_arc_label] = []
        elif is_last_column:
            insertion_arc_label = "*" + "::" + "epsilon" + "::" + str(1)
            arcs_labels.append(insertion_arc_label)

            up_dst_label = str(nb_consummed_chars) + ";" + str(nb_elementary_operations + 1)
            dst_states.append(up_dst_label)

            set_arcs[insertion_arc_label] = [up_dst_label]

        elif is_last_row:
            accepting_arc_label = char_from_ref_str + "::" + char_from_ref_str + "::" + str(weights[0])
            arcs_labels.append(accepting_arc_label)

            right_dst_label = str(nb_consummed_chars  + 1) + ";" + str(nb_elementary_operations)
            dst_states.append(right_dst_label)

            set_arcs[accepting_arc_label] = [right_dst_label]

        else:
            accepting_arc_label = char_from_ref_str + "::" + char_from_ref_str + "::" + str(weights[0])
            deletion_arc_label = "epsilon::" + char_from_ref_str + "::" + str(weights[1])
            substitution_arc_label = "*::" + char_from_ref_str + "::" + str(weights[1])
            insertion_arc_label = substitution_arc_label
            arcs_labels.append(accepting_arc_label)
            arcs_labels.append(deletion_arc_label)
            arcs_labels.append(substitution_arc_label)
            arcs_labels.append(insertion_arc_label)

            dst_states.append(up_dst_label)
            dst_states.append(diag_dst_label)
            dst_states.append(diag_dst_label)
            dst_states.append(right_dst_label)

            set_arcs[accepting_arc_label] = [right_dst_label]
            set_arcs[deletion_arc_label] = [diag_dst_label]
            set_arcs[substitution_arc_label] = [diag_dst_label, up_dst_label]

        automata[state_label] = set_arcs
        # print(automata[state_label])

        for idx in range(len(dst_states)):
            dst_state_label = dst_states[idx]
            dst_state_index = dict_levenshtein_states[dst_state_label]

            consummed_char = convertSymToLabel(char_from_ref_str)
            dst_states[idx]
            transmitted_char = info[1]
            weight = info[2]

            automate.add_arc(
                    state_index,
                    fst.Arc(
                        transmitted_char,
                        consummed_char,
                        fst.Weight(automate.weight_type(), weight),
                        dst_state_index)
                )


    print(automata)

    # Display Automata in LaTeX : 

    return(automata) 



def main():

    # Levenshtein_Automata_Dico("manon", 2)
    SimpleAutomata()
 
    
if __name__ == "__main__":
    # execute only if run as a script
    main()