# -*- coding: utf-8 -*-
import bisect
import matplotlib.pyplot as plt
import numpy as np
import pyparsing 
import graphviz 
import dot2tex
import openfst_python as fst

def convertSymToLabel(symbol):
    newSym = None
    if(len(symbol) == 1):
        newSym = ord(symbol)
        
    elif(symbol == "epsilon"):
        newSym = 1
        
    return (newSym)

def label2int(label, ref_string):
    return (len(ref_string)+1)*int(label[2])+int(label[0])


def get_index(label, automate, states_dict):
    if label not in states_dict:
        state_index = automate.add_state()
        states_dict[label] = state_index

    return states_dict[label]


def add_arc_to_automate(src_state_label, dst_state_label, arc_label, automate, states_dict):

    src_state_index = get_index(src_state_label, automate, states_dict)

    dst_state_index = get_index(dst_state_label, automate, states_dict)

    label_string = arc_label.split(":")
    # print(label_string[0], label_string[1], label_string[2])
    consummed_char = convertSymToLabel(label_string[0])
    # print(consummed_char)
    transmitted_char = convertSymToLabel(label_string[1])
    # print(transmitted_char)
    weight = int(label_string[2])
    # print(weight)

    automate.add_arc(
        src_state_index,
        fst.Arc(
            transmitted_char,
            consummed_char,
            fst.Weight(automate.weight_type(), weight),
            dst_state_index
        )
    )

def SimpleAutomata(ref_string, levenshtein_distance):
    automate = fst.Fst()
    states_dict = {}
    final_dst_state_label = str(len(ref_string)) + ";" + str(levenshtein_distance)

    init_state_index = get_index('0;0', automate, states_dict)

    for consummed_char_number in range(len(ref_string) + 1):
        for operations_number in range(levenshtein_distance + 1):
            src_state_label = str(consummed_char_number) + ";" + str(operations_number)
            # print(str(consummed_char_number != len(ref_string)) + "-" + str(operations_number == levenshtein_distance))
            print(str(consummed_char_number == len(ref_string)) + "-" + str(operations_number == levenshtein_distance))

            if(consummed_char_number == (len(ref_string)) and operations_number == levenshtein_distance):
                final_dst_state_label = src_state_label
                print("output state")
            elif(consummed_char_number == (len(ref_string)) and operations_number != levenshtein_distance):
                insertion_dst_state_label = str(consummed_char_number) + ";" + str(operations_number + 1)
                insertion_arc_label = "*:epsilon:1" 
                add_arc_to_automate(src_state_label, insertion_dst_state_label, insertion_arc_label, automate, states_dict)
            elif(consummed_char_number != (len(ref_string)) and operations_number == levenshtein_distance):
                accepting_dst_state_label = str(consummed_char_number + 1) + ";" + str(operations_number)
                print(accepting_dst_state_label)
                accepting_arc_label = ref_string[consummed_char_number] + ":" + ref_string[consummed_char_number] + ":" + str(0)
                add_arc_to_automate(src_state_label, accepting_dst_state_label, accepting_arc_label, automate, states_dict)
            else:
                accepting_dst_state_label = str(consummed_char_number + 1) + ";" + str(operations_number)
                accepting_arc_label = ref_string[consummed_char_number] + ":" + ref_string[consummed_char_number] + ":" + str(0)
                add_arc_to_automate(src_state_label, accepting_dst_state_label, accepting_arc_label, automate, states_dict)

                deletion_dst_state_label = str(consummed_char_number + 1) + ";" + str(operations_number + 1)
                deletion_arc_label = "epsilon:" + ref_string[consummed_char_number] + ":" + str(1)
                add_arc_to_automate(src_state_label, deletion_dst_state_label, deletion_arc_label, automate, states_dict)

                substitution_dst_state_label = str(consummed_char_number + 1) + ";" + str(operations_number + 1)
                substitution_arc_label = "*:" + ref_string[consummed_char_number] + ":" + str(1)
                add_arc_to_automate(src_state_label, substitution_dst_state_label, substitution_arc_label, automate, states_dict)

                insertion_dst_state_label = str(consummed_char_number) + ";" + str(operations_number + 1)
                insertion_arc_label = "*:" + ref_string[consummed_char_number] + ":" + str(1) 
                add_arc_to_automate(src_state_label, insertion_dst_state_label, insertion_arc_label, automate, states_dict)


    automate.set_start(init_state_index)
    automate.set_final(states_dict[final_dst_state_label], fst.Weight(automate.weight_type(), 1.5))
    automate.draw("automata.dot")
    print(automate)
    return automate

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
    
    automate = fst.Fst()
    automata = {}
    weights = [0, 1, 1,1]
    arcs_labels = []
    dst_states = []
    automata_voc = ["epsilon", "*"]
    automata_voc.extend(ref_string)

    initial_state_index = automate.add_state() # label2int("0;0", ref_string)
    final_state_index = automate.add_state() # label2int("5;2", ref_string)
    automate.set_start(initial_state_index)
    automate.set_final(final_state_index, fst.Weight(automate.weight_type(), 1.5))

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
        up_dst_index = label2int(up_dst_label, ref_string)
        # print("up", up_dst_label)
        insertion_arc_label = "*" + ":" + "epsilon" + ":" + str(1)
        insertion_split = insertion_arc_label.split(":")
        insertion_consummed_char = convertSymToLabel(insertion_split[0])
        insertion_transmitted_char = convertSymToLabel(insertion_split[1])
        insertion_weight = convertSymToLabel(insertion_split[2])
        
        diag_dst_label = str(nb_consummed_chars + 1) + ";" + str(nb_elementary_operations + 1)
        diag_dst_index = label2int(diag_dst_label, ref_string)
        # print("diag", diag_dst_label)
        deletion_arc_label = "epsilon:" + char_from_ref_str + ":" + str(weights[1])
        deletion_split = deletion_arc_label.split(":")
        deletion_consummed_char = convertSymToLabel(deletion_split[0])
        deletion_transmitted_char = convertSymToLabel(deletion_split[1])
        deletion_weight = convertSymToLabel(deletion_split[2])
        
        substitution_arc_label = "*:" + char_from_ref_str + ":" + str(weights[1])
        substitution_split = substitution_arc_label.split(":")
        substitution_consummed_char = convertSymToLabel(substitution_split[0])
        substitution_transmitted_char = convertSymToLabel(substitution_split[1])
        substitution_weight = convertSymToLabel(substitution_split[2])
        
        right_dst_label = str(nb_consummed_chars + 1) + ";" + str(nb_elementary_operations)
        right_dst_index = label2int(right_dst_label, ref_string)
        # print("right", right_dst_label)
        accepting_arc_label = char_from_ref_str + ":" + char_from_ref_str + ":" + str(weights[0])
        accepting_split = accepting_arc_label.split(":")
        accepting_consummed_char = convertSymToLabel(accepting_split[0])
        accepting_transmitted_char = convertSymToLabel(accepting_split[1])
        accepting_weight = convertSymToLabel(accepting_split[2])
        
        is_last_column = nb_consummed_chars == len(ref_string) # booleen renvoie true si le nombre de caracteres conssommes est egal a la longueur de la chaine et false sinon
        is_last_row = nb_elementary_operations == levenshtein_distance # booleen renvoie true si le nombre d'operations elementaires est egal a la distance de levenshtein et false sinon
        if is_last_column and is_last_row:
            output_arc_label = "epsilon" + ":" + "epsilon" + ":" + str(0)            
            set_arcs[output_arc_label] = []
        elif is_last_column:
            arcs_labels.append(insertion_arc_label)
            dst_states.append(up_dst_label)

            set_arcs[insertion_arc_label] = [up_dst_label]
            automate.add_arc(state_index, fst.Arc(insertion_consummed_char, insertion_transmitted_char, fst.Weight(automate.weight_type(), insertion_weight), up_dst_index))

        elif is_last_row:
            arcs_labels.append(accepting_arc_label)
            dst_states.append(right_dst_label)
            set_arcs[accepting_arc_label] = [right_dst_label]

            automate.add_arc(state_index, fst.Arc(accepting_consummed_char, accepting_transmitted_char, fst.Weight(automate.weight_type(), accepting_weight),right_dst_index))

        else:
            arcs_labels.append(accepting_arc_label)
            dst_states.append(right_dst_label)
            set_arcs[accepting_arc_label] = [right_dst_label]
            automate.add_arc(state_index, fst.Arc(accepting_consummed_char, accepting_transmitted_char, fst.Weight(automate.weight_type(), accepting_weight),right_dst_index))
            
            arcs_labels.append(deletion_arc_label)
            dst_states.append(diag_dst_label)
            set_arcs[deletion_arc_label] = [diag_dst_label]
            automate.add_arc(state_index, fst.Arc(deletion_consummed_char, deletion_transmitted_char, fst.Weight(automate.weight_type(), deletion_weight), diag_dst_index))

            arcs_labels.append(substitution_arc_label)
            dst_states.append(diag_dst_label)
            automate.add_arc(state_index, fst.Arc(substitution_consummed_char, substitution_transmitted_char, fst.Weight(automate.weight_type(), substitution_weight), diag_dst_index))

            arcs_labels.append(insertion_arc_label)
            dst_states.append(up_dst_label)
            automate.add_arc(state_index, fst.Arc(insertion_consummed_char, insertion_transmitted_char, fst.Weight(automate.weight_type(), insertion_weight), up_dst_index))            
            
            set_arcs[substitution_arc_label] = [diag_dst_label, up_dst_label] # insertion et substitution ont les memes labels d'arcs

        automata[state_label] = set_arcs
        
        # print(automata[state_label])

        # for idx in range(len(dst_states)):
        #     dst_state_label = dst_states[idx]
        #     dst_state_index = dict_levenshtein_states[dst_state_label]

        #     consummed_char = convertSymToLabel(char_from_ref_str)
        #     dst_states[idx]
        #     transmitted_char = info[1]
        #     weight = info[2]

        #     automate.add_arc(
        #             state_index,
        #             fst.Arc(
        #                 transmitted_char,
        #                 consummed_char,
        #                 fst.Weight(automate.weight_type(), weight),
        #                 dst_state_index)
        #         )


    print(automata)

    # Display Automata in LaTeX : 

    return(automata) 



def main():

    # Levenshtein_Automata_Dico("manon", 2)
    SimpleAutomata("manon", 2)
    # print(SimpleAutomata())

 
    
if __name__ == "__main__":
    # execute only if run as a script
    main()