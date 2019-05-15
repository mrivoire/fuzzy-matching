# -*- coding: utf-8 -*-
import bisect
import matplotlib.pyplot as plt
import numpy as np
import pyparsing 
import graphviz 
import dot2tex
import openfst_python as fst

def printTxt(txt):
    print(txt)

automate = fst.Fst() # creation de l'automate
automate_states = {} # dictionnaire contenant tous les etats de l'automate : les cles sont les labels des etats et les valeurs sont les etats crees 

# La fonction add_automate_state est appelee lors du parcours de l'automate et permet de creer un dict contenant tous les etats de l'automate une et une fois seulement
# Si le label fait deja partie du dictionnaire alors, elle ne fait rien, sinon elle ajoute le nouveau label et cree l'etat correspondant avec add_state()
def add_automate_state(state_label): 
    if not (state_label in automate_states):
        automate_states[state_label] = automate.add_state()

def creation_automata():

    # transitions = {
    #     "s0": {
    #         "1:1:0": [
    #             "s0",
    #             "s1"
    #         ],
    #         "2:3:1": [
    #             "s0",
    #             "s2"
    #         ]
    #     }
    # }
    # La methode iteritems appliquee a un dictionnaire permet de decomposer les differents "niveaux de profondeur" du dictionnaire en tableaux
    # iteritems appliquee a transitions transforme le dict en un tableau contenant les differentes transitions (la transition s0 a l'index 0, la transition s1 a l'index 1 etc...) puis pour chaque tableau de transition celui-ci contient encore 2 tableaux l'un pour le label (s_i a l'index 0) et l'autre pour la valeur associee (la chaine de caracteres contenant tous les arcs a l'index 1)
    # iteritems appliquee a arcs transforme le dict d'arcs en un tableau ou chaque cellule contient un arc et pour chaque cellule contenant un arc, il y a un tableau contenant a l'index 0 le label de l'arc et a l'index 1 la valeur de l'arc c'est a dire la liste de destinations
    # les etats de destinations sont contenus dans une liste donc il n'y a pas besoin d'utiliser la methode iteritems.
    
    for src_state_label, arcs in transitions.iteritems(): # parcours du 1er niveau du dict : les cles sont les labels des etats sources et les objets sont les arcs associes a ces etats sources
        add_automate_state(src_state_label) 
        for arc_label, set_dsts_states in arcs.iteritems(): # parcours du 2eme niveau du dict : les cles sont les labels des arcs et les objets parcourus sont les listes d'etats de destination 
            for dst_state_label in set_dsts_states: # parcours du 3eme niveau du dict : le 3eme niveau n'est pas un dictionnaire mais une liste ce qui signifie que les etats ne sont pas indexes par une cle quelconque mais par un entier : les objets parcourus sont les etats de destination
                add_automate_state(dst_state_label)
    
    for state_label, arcs in transitions.iteritems():
        for arc_label, set_dsts_states in arcs.iteritems():
            chars = arc_label.split(':')
            for dst_state_label in set_dsts_states:
                automate.add_arc(automate_states[state_label], fst.Arc(int(chars[0]), int(chars[1]), fst.Weight(automate.weight_type(), int(chars[2])), automate_states[dst_state_label]))

    automate.set_start(automate_states['s0'])
    automate.set_final(automate_states['s2'], fst.Weight(automate.weight_type(), 1.5))

    print(automate)


    # Generation du code LaTeX au format GraphViz

    # Affichage des noeuds avec leurs labels
    i = 0
    print("digraph G {")
    for state_label, state in automate_states.iteritems():
        index = state_label.split("s")[1]
        display_node = index + " [label = \"" + state_label + "\"]"
        i += 1
        print(display_node)
    
    # Affichage des arcs avec leurs labels
    for src_state_label, arcs in transitions.iteritems():
        src_index = src_state_label.split("s")[1]
        for arc_label, set_dsts_states in arcs.iteritems():
            for dst_state_label in set_dsts_states:
                dst_index = dst_state_label.split("s")[1]
                display_edge = src_index + "->" + dst_index + " [label = \"" + arc_label + "\"]"
                print(display_edge)

    print("}")

    return(automate)


def convertSymToLabel(symbol):
    if(len(symbol) == 1):
        newSym = ord(symbol)
    elif(symbol == "epsilon"):
        newSym = 1
    return(newSym)

def Levenshtein_Automata_Dico(ref_string, levenshtein_distance):
    # Creation des etats de l'automate 
    dict_levenshtein_states = {}
    for column in range(len(ref_string) + 1):
        for row in range(levenshtein_distance + 1):
            state_label = str(column) + ";" + str(row)
            dict_levenshtein_states[state_label] = automate.add_state()

    # Creation des arcs emergeants de chaque etat
    # Pour les poids on pose que : d = 0 si on consomme un caractere, et 1 si on consomme etoile ou epsilon (insertion, deletion, substitution)
    # Pour les caracteres consommes et emis, on considere que les caracteres de la chaine de reference sont les caracteres consommes et les caracteres de la chaine hypothese seront les caracteres emis 
    
    
    automata = {}
    weights = [0, 1, 1,1]
    arcs_labels = []
    dsts_states = []
    automata_voc = ["epsilon", "*"]
    automata_voc.extend(ref_string)

    for state_label, state in dict_levenshtein_states.iteritems():
        nb_consummed_chars = int(state_label.split(";")[0]) # 1er caractere du label
        nb_elementary_operations = int(state_label.split(";")[1]) # 2nd caractere du label


        arcs_labels = []
        charFromRefStr = ref_string[nb_consummed_chars - 1]

        up_dst_label = [str(nb_consummed_chars) + ";" + str(nb_elementary_operations + 1)]
        # print("up", up_dst_label)
        diag_dst_label = [str(nb_consummed_chars + 1) + ";" + str(nb_elementary_operations + 1)]
        # print("diag", diag_dst_label)
        right_dst_label = [str(nb_consummed_chars + 1) + ";" + str(nb_elementary_operations)]
        # print("right", right_dst_label)

        is_last_column = nb_consummed_chars == len(ref_string)
        is_last_row = nb_elementary_operations == levenshtein_distance
        if is_last_column and is_last_row:
            output_arc_label = "end"
        elif is_last_column:
            insertion_arc_label = "*:epsilon:1"
            arcs_labels.append(insertion_arc_label)

            up_dst_label = str(nb_consummed_chars) + ";" + str(nb_elementary_operations)
            dsts_states.append(up_dst_label)
        elif is_last_row:
            accepting_arc_label = charFromRefStr + ":" + charFromRefStr + ":" + str(weights[0])
            arcs_labels.append(accepting_arc_label)

            right_dst_label = str(nb_consummed_chars) + ";" + str(nb_elementary_operations)
        else:
            accepting_arc_label = charFromRefStr + ":" + charFromRefStr + ":" + str(weights[0])
            deletion_arc_label = "epsilon:" + charFromRefStr + ":" + str(weights[1])
            substitution_arc_label = "*:" + charFromRefStr + ":" + str(weights[1])
            insertion_arc_label = substitution_arc_label
            arcs_labels.append(accepting_arc_label)
            arcs_labels.append(deletion_arc_label)
            arcs_labels.append(substitution_arc_label)
            arcs_labels.append(insertion_arc_label)

                    dsts_states.append(up_dst_label)
                    dsts_states.append(diag_dst_label)
                    dsts_states.append(diag_dst_label)
                    dsts_states.append(right_dst_label)

            # print('state_label', state_label)
            # print('charFromRefStr', charFromRefStr)
            # print('accepting_arc_label', accepting_arc_label)
            # print('deletion_arc_label', deletion_arc_label)
            # print('substitution_arc_label', substitution_arc_label)
            # print('insertion_arc_label', insertion_arc_label)

        # if state_label == '0;0' :
        #     print('state_label', state_label)
        #     print('charFromRefStr', charFromRefStr)
        #     print('accepting_arc_label', accepting_arc_label)
        #     print('deletion_arc_label', deletion_arc_label)
        #     print('substitution_arc_label', substitution_arc_label)
        #     print('insertion_arc_label', insertion_arc_label)

        set_arcs = {}
        for index in range(len(arcs_labels)):
            arc_label = arcs_labels[index]
            dst_state_label = dsts_states[index]
            set_arcs[arc_label] = (dst_state_label)
        
        automata[state_label] = set_arcs

    # print(automata)

    # Display Automata in LaTeX : 

    # print("digraph G {")

    # for state_label, state in dict_levenshtein_states.iteritems():
    #     node_index = state_label.split(";")[0] + state_label.split(";")[1]
    #     display_node = node_index + "[label=\"" + state_label + "\"];"
    #     print(display_node)

    # for state_label, state in automata.iteritems():
    #     # print("state_label: ", state_label, state)
    #     src_index = state_label.split(";")[0] + state_label.split(";")[1]
    #     # print(src_index)
    #     for arc_label, dsts_states in set_arcs.iteritems():
    #         # print("dsts_states: ", dsts_states)
    #         for dst_state_label in dsts_states:
    #             # print("dst_state_label: " + dst_state_label)
    #             dst_index = dst_state_label.split(";")[0] + dst_state_label.split(";")[1]
    #             # print(dst_index)
    #             display_edge = src_index + "->" + dst_index + "[label=\""  + arc_label + "\"];"
    #             # print(display_edge)    
    # print("}")         

    return(automata) 

def Automata_Building(ref_string, levenshtein_distance, output_weight):
    levenshtein_automata = {}
    levenshtein_automata = Levenshtein_Automata_Dico(ref_string, levenshtein_distance)
    # print(levenshtein_automata)

    label_inital_state = "0;0"
    label_final_state = str(len(ref_string)) + ";" + str(levenshtein_distance)
    # Une fois l'automate represente sous forme de dictionnaire, on cree l'automate grace aux fonctions de la librairie openfst

    # Creation de tous les etats de l'automate (etats source et de destination confondus)
    # La fonction add automate state cree un dictionnaire automate states dont les cles sont les labels des etats et les valeurs associees sont les etats crees grace a la fonction de creation d'etats d'openfst
    
    for src_label, set_arcs in levenshtein_automata.iteritems():
        add_automate_state(src_label)
        for arc_label, set_dsts in set_arcs.iteritems():
            for dst_label in set_dsts:
                add_automate_state(dst_label)

    print(automate)
    # # Creation des arcs de l'automate

    for src_label, set_arcs in levenshtein_automata.iteritems():
        for arc_label, set_dsts in set_arcs.iteritems():
            transmitted_char = arc_label.split(":")[0]
            consummed_char = arc_label.split(":")[1]
            weight = arc_label.split(":")[2]
            # print(transmitted_char, consummed_char, weight)
            for dst_label in set_dsts:
                automate.add_arc(automate_states[src_label], fst.Arc(int(convertSymToLabel(transmitted_char)), int(convertSymToLabel(consummed_char)), fst.Weight(automate.weight_type(), int(weight)), automate_states[dst_label]))
    
    automate.set_start(automate_states[label_inital_state])
    automate.set_final(automate_states[label_final_state], fst.Weight(automate.weight_type(), output_weight))
    automate.draw("automata.dot")
    # print(automate)

    return(automate)

def Levenshtein_Matcher(ref_string, hypothesis_string, levenshtein_distance, output_weight):
    # automata = fst.Fst()
    # automata = Automata_Building(ref_string, levenshtein_distance, output_weight)
    
    accepted_string = []
    elementary_operations = []
    cumul_weights = 0

    length_ref = len(ref_string)
    length_hypothesis = len(hypothesis_string)

    difference = abs(length_ref - length_hypothesis)
    # print(difference)

    nb_comparisons = min(length_ref, length_hypothesis) + difference
    # print(nb_comparisons)

    if length_hypothesis > length_ref:
        longest_string = hypothesis_string
        shortest_string = ref_string
    else:
        longest_string = ref_string
        shortest_string = hypothesis_string

    while cumul_weights <= levenshtein_distance:
        for index in range(nb_comparisons):
            if hypothesis_string[index] == ref_string[index]:
                accepted_string.append(hypothesis_string[index])
                cumul_weights = cumul_weights
                elementary_operations.append("none")
            elif hypothesis_string[index] != ref_string[index] and hypothesis_string[index] == ref_string[index - 1]:
                accepted_string.append(hypothesis_string[index])
                cumul_weights = cumul_weights + 1
                elementary_operations.append("deletion")
            elif hypothesis_string[index] != ref_string[index] and hypothesis_string[index] == ref_string[index + 1]:
                accepted_string.append(hypothesis_string[index])
                cumul_weights = cumul_weights + 1
                elementary_operations.append("insertion")
            elif hypothesis_string[index] != ref_string[index] and hypothesis_string[index] != ref_string[index - 1] and hypothesis_string[index] != ref_string[index + 1]:
                accepted_string.append(hypothesis_string[index])
                cumul_weights = cumul_weights + 1
                elementary_operations.append("substitution")
    
    # print(accepted_string, cumul_weights)
    return(accepted_string)
           
def main():

    set_transitions = [
       {
           "src": "s0",
           "arcs": [
                {
                   "arc_label": "1:1",
                    "dsts": [
                        "s0",
                        "s1"
                    ]
                },
                {
                   "arc_label": "epsilon",
                   "dsts": [
                        "s0",
                        "s2"
                    ]
                }
           ]
        },
        {   
           "src": "s1",
           "arcs": [
                {
                   "arc_label": "1:2",
                   "dsts": [
                        "s0",
                        "s2"
                    ]
                },
                {
                   "arc_label": "2:3",
                   "dsts": [
                        "s1"
                    ]
                }
                    
           ]
        },
        {
           "src": "s2",
           "arcs": [
               {
                   "arc_label": "2:2",
                   "dsts": [
                       "s2"
                    ]
               },
               {
                   "arc_label": "1:3",
                   "dsts": [
                       "s0",
                       "s1"
                   ]
               }
           ]
        }
    ]

    # creation_automata()
    Levenshtein_Automata_Dico("manon", 2)
    # Automata_Building("manon", 2, 5)
    # Levenshtein_Matcher("manon", "marion", 2, 5)
    
  
    
if __name__ == "__main__":
    # execute only if run as a script
    main()