import numpy as np
import pyparsing 
import graphviz 
import dot2tex
import openfst_python as fst

def convertSymToLabel(symbol):
    if(len(symbol) == 1):
        newSym = ord(symbol)
    elif(symbol == "epsilon"):
        newSym = 1
    return(newSym)

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

def InitAutomata():
    global automate, states_dict, init_state_index
    automate = fst.Fst()
    states_dict = {}
    init_state_index = get_index('0;0', automate, states_dict)
    print (states_dict, init_state_index)

def ReduceStatesDict():
    global states_dict, init_state_index
    print (states_dict, 'ici', init_state_index)
    states_dict = { "0;0": init_state_index }

def SimpleAutomata(ref_string, levenshtein_distance):
    final_dst_state_label = str(len(ref_string)) + ";" + str(levenshtein_distance)

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
    
    for nb_final_states in range(levenshtein_distance + 1):
        final_dst_state_label = str(len(ref_string)) + ";" + str(nb_final_states)
        automate.set_final(states_dict[final_dst_state_label], fst.Weight(automate.weight_type(), 1.5))

    automate.draw("automata.dot")
    print(automate)
    return automate, states_dict

def CloneAndDraw(n):
    a = automate.copy()
    a.set_start(init_state_index)
    a.draw("automata_" + str(n) + ".dot")
    

def FinishAutomata():
    automate.set_start(init_state_index)


def main():
    n = 0
    InitAutomata()
    SimpleAutomata("manon", 2)
    ReduceStatesDict()
    CloneAndDraw(n)
    n = n + 1
    SimpleAutomata("marion", 2)
    ReduceStatesDict()
    CloneAndDraw(n)
    FinishAutomata()
    automate.minimize(allow_nondet=True).draw("automata.dot")
  
    
if __name__ == "__main__":
    # execute only if run as a script
    main()
