import bisect
import matplotlib.pyplot as plt
import numpy as np
import pyparsing 
import graphviz 
import dot2tex
import openfst_python as fst 

# import openfst_python as fst
# import matplotlib2tikz

# matplotlib2tikz.save("test.tex")

class Matcher(object):
    def __init__(self, l):
        self.l = l # l is a string 
        self.probes = 0

    def __call__(self, w):
        self.probes += 1
        pos = bisect.bisect_left(self.l, w) # we are looking for the lower point of insertion of the character w in the string l so that the string l might be able to be sorted
        if pos < len(self.l):
            return self.l[pos]
        else:
            return None


class NFA(object):
    # Definition of the different types of transitions in the Levenshtein Automaton
    EPSILON = 'epsilon' # EPSILON transition = deletion 
    ANY = 'any' # ANY transition = substitution or insertion

    def __init__(self, start_state):
        self.transitions = {}
        self.final_states = set()
        self._start_state = start_state

    def __str__(self):
        nfa_def = "Initial States : " + str(self.start_state) + "\n\nTransitions : " + str(self.transitions) + "\n\nFinal States : " + str(self.final_states)

       # for iterator in enumerate(self.final_states):
       #    nfa_def = nfa_def + " \n " + str(self.final_states(iterator)) 

        return nfa_def

    @property
    def start_state(self):
        return frozenset(self._expand(set([self._start_state]))) # a frozen set is a set object but in which items are unchangeable

    # The expand method updates the set containing the states composing the Levenshtein automaton

    # Builds the set containing the start states, extracts the start states from the set cont   aining all the states of the automaton

    def add_transition(self, src, input, dest):
        self.transitions.setdefault(src, {}).setdefault(input, set()).add(dest) # The setdefault() method returns the value of the items with the specified key, if the key does not exist, insert the key with the specified value

    # Builds the transitions between two adjacent states
    # src is the consummate character
    # input is the start state of the transition
    # dest is the arrival state of the transition
    # We build the transition from the start state to the arrival state consumming a given character called src

    def add_final_state(self, state):
        self.final_states.add(state) 

    # Builds the set containing the final states

    def is_final(self, states):
        return self.final_states.intersection(states) # The intersection function performs the intersection between two sets and return the subset containing all the shared items 
    
    # Returns the subset from the set "states" only composed of the final states

    def _expand(self, states):
        frontier = set(states) # The set function creates a set object, the items in a set list are unordered so it will appear in random order
        # frontier is the set composed of all the states of the automaton
        while frontier:
            state = frontier.pop() # The pop() method removes the specified item from the dictionary or the list, the value of the removed item is the return value of the pop()
            new_states = self.transitions.get(state, {}).get(NFA.EPSILON, set()).difference(states) # The difference() method returns the items of set x which differ from the one of the set y 
            frontier.update(new_states) # The update() method can insert the specified items to the dictionary, the specified items can be a dictionary or an iterable object       
            states.update(new_states)
            # We add to the set containing all the states of the automaton, the new state 
        return states 
    # Returns the updated set containing the states of the automaton

    def next_state(self, states, input):
        dest_states = set()     
        for state in states: # equivalent of foreach state in the list of states 
            state_transitions = self.transitions.get(state, {})
            dest_states.update(state_transitions.get(input, [])) 
            dest_states.update(state_transitions.get(NFA.ANY, []))
            
            # At each time that a transition between two states (a start state and an arrival state) is built, we insert the arrival state to the set containing the destination states 
        return frozenset(self._expand(dest_states)) # The function expand() returns the upadated list of states, in this case it is the list of destination states updated at each time that we built a new transition that is at each time that we create a new destination state

    # We obtain the frozenset (set with unchangeable items) of the destination states of the transitions of the automaton 

    def get_inputs(self, states):
        inputs = set()
        for state in states:
            inputs.update(self.transitions.get(state, {}).keys()) # We add to the set containing all the start states of the transitions, the start states as they are created 
        return inputs

    # We obtain the set containing all the start states of the transitions of the automaton    
      
    def to_dfa(self): # This method aims at converting a NFA (Non Deterministic Finite Automaton) in DFA (Deterministic Finite Automaton)
        dfa = DFA(self.start_state)
        frontier = [self.start_state]                   
        seen = set()
        while frontier:
            current = frontier.pop() # foreach start state in the set called "frontier", we extract the start state and we equate the variable called "current" to this start state
            inputs = self.get_inputs(current) # get the start states of the set "curent" that are inputs for the transitions of the automaton
            for input in inputs: # equivalent of foreach 
                if input == NFA.EPSILON: continue # To convert a NFA into DFA we withdraw the epsilon transition consequently foreach epsilon transition we skip to the creation of a new state
                new_state = self.next_state(current, input) # We create a new state as input of a new transitions
                if new_state not in seen:
                    frontier.append(new_state) # The append() function inserts an item to the end of the list, We add newly created state to the set containing all the states of the automaton 
                    seen.add(new_state) # We add the newly created state to the set called "seen"
                    if self.is_final(new_state):
                        dfa.add_final_state(new_state) # If the newly created state is a final state, we add this state to the dfa as final state
                if input == NFA.ANY: 
                    dfa.set_default_transition(current, new_state) # If the transition is of type ANY that is a substitution or an insertion, we create a default transition
                else:
                    dfa.add_transition(current, input, new_state) # In the case where the transition is neither of type EPSILON nor of type ANY, we create a transition between the current state and the new state while consumming a character "input"
        return dfa
    # This method creates a dfa from a nfa (the nfa has epsilon transitions and loop which allow to come back on the different states whereas the dfa has not)    

    def display_nfa(self):
        # structure_begin = "\ begin{tikzpicture}"
        # print(structure_begin)
        nodes = set()

        # print("List of States :")
        # print

        # The transitions attribute is a list containing all the transitions of the automaton 
        # Each transition of the list has 3 attributes : the input state or start state (src), the label which is the consummate character between two adjacent states, and the final state or arrival state or destianation state (dst)
        # We create 3 loops 

        for i, src in enumerate(self.transitions): # We cross the list containing all the transitions of the automata, each transition being defined by the initial and the final states as well as the consumption (label : char, any, epsilon...)
            for j, label in enumerate(self.transitions[src]): # for each start state, there are several transitions which are able to derive from
                for k, dst in enumerate(self.transitions[src][label]): # for each start state and e
                    nodes.add(src)
                    nodes.add(dst)

        # print(nodes)
        # print

        # for i, state in enumerate(nodes):
        #     if i == 0:
        #         display_states = "\ node[state, initial]" + "(" + str(i) + ")" + "{$" + str(state) + "$};"
        #     elif i == len(nodes):
        #         display_states = "\ node[state, accepting]" + "(" + str(i) + ")" + "{$" + str(state) + "$};"
        #     else:
        #         display_states = "\ node[state]" + "(" + str(i) + ")" + "{$" + str(state) + "$};"
            
        #     print(display_states)
            

        # print("Transitions :")
        # print

        # structure_edges = "\ path[->]"
        # print(structure_edges)  
        print("digraph G {")
        for i, src in enumerate(self.transitions): # We cross the list containing all the transitions of the automata, each transition being defined by the initial and the final states as well as the consumption (label : char, any, epsilon...)
            #  print(t, self.transitions[t])
            display_node = str(i) + "[texlbl = \"" + str(src) + "\", lblstyle = \" red \"];"
            print(display_node)
            for j, label in enumerate(self.transitions[src]): 
                for k, dst in enumerate(self.transitions[src][label]):
                    # display_edge = "(" + str(i) + ")" + "edge [bend left] node [swap]" + "{" + label + "}" + "(" + str(k) + ")"
                    display_edge = str(src[0])+str(src[1]) + "->" + str(dst[0])+str(dst[1]) + "[label=\"" + label + "\", lblstyle = \" rounded corners, fill = blue!20 \"];"
                    print(display_edge)
                    # print(src, dst, label)

        # structure_end = "\ end{tikzpicture}"
        # print(structure_end)
        print("}")
        
class DFA(object):
    def __init__(self, start_state):
        self.start_state = start_state
        self.transitions = {}
        self.defaults = {}
        self.final_states = set()

    def add_transition(self, src, input, dest):
        self.transitions.setdefault(src, {})[input] = dest # We add a transition between two states a source (src) state and a destination states while consumming a character in input (called input)

    def set_default_transition(self, src, dest):
        self.defaults.setdefault(src, {})["epsilon"] = dest # A default transition corresponds to a transition allowing to pass from a source state to a destination state without consumming any character nor performing any elementary operation the reference string

    def add_final_state(self, state):
        self.final_states.add(state) # We add a final state to the automaton

    def is_final(self, state):
        return state in self.final_states # Returns a set containing all the final states of the automaton 

    def next_state(self, src, input):
        state_transitions = self.transitions.get(src, {})
        return state_transitions.get(input, self.defaults.get(src, None)) # Returns the consumme character "src" to reach the next state 

    def next_valid_string(self, input): # input is a string 
        state = self.start_state
        stack = [] # array containing all the consumme characters of the string at the end of the automaton process, we progressively fill this empty array

        # Evaluate the DFA as far as possible
        for i, x in enumerate(input):  # The enumerate() function takes a collection (eg: a tuple) and returns it as an enumerate object, it adds a counter as the key of the enumerate object 
            # In our case, the enumerate function returns the input string into an enumerate object (i corresponds to the indexes of the letters in the string and x corresponds to the character of index i in the string)
            stack.append((input[:i], state, x)) # We add to the array the character x of the string at the position i 
            state = self.next_state(state, x) # We go to the next state in the automaton                         
            if not state: break # If we already are in a final state, we stop the process 
        else:
            stack.append((input[:i + 1], state, None)) # In the case where we are not in a final state, we consumme the following character and we add it to the stack 

        if self.is_final(state):
            # Input word is already valid
            return input 

        # Perform a 'wall following' search for the lexicographically smallest
        # accepting state.
        while stack: # Once we have built the string and recorded its characters in an array called "stack", we cross the array
            path, state, x = stack.pop() # We extract the character x from the array
            x = self.find_next_edge(state, x)
            if x:
                path += x # We build the string (word) from the array containing all the consumme characters at the end of the automaton process
                state = self.next_state(state, x)
                if self.is_final(state):
                    return path # We return the string  
                stack.append((path, state, None))
        return None

    def find_next_edge(self, s, x):
        if x is None:
            x = u'\0'
        else:
            x = unichr(ord(x) + 1) # The ord() function returns the unicode code of a specified character, the unichr() function is the inverse of the ord() function, it converts a unicode code to the corresponding character
        state_transitions = self.transitions.get(s, {})
        if x in state_transitions or s in self.defaults:
            return x
        labels = sorted(state_transitions.keys()) # sorted list composed of the characters of the string
        pos = bisect.bisect_left(labels, x) # returns the lower position in the sorted list of the character x in the string labels
        if pos < len(labels): 
            return labels[pos]
        return None

    # def convert_defaults_to_transitions(self):
    #     self.defaults(self, src, dst) = self.transitions(self, src, "empty", dst)
    #     return(self.defaults)

    def display_dfa(self):   
        src_states = set()
        dst_states = set()
        all_states = set()
        all_labels = set()
        all_transitions = []
        
        for i, src in enumerate(self.transitions):
            for j, label in enumerate(self.transitions[src]):
                for k, dst in enumerate(self.transitions[src][label]):
                    src_states.add(src)
                    dst_states.add(dst) 
                    all_states.add(src)
                    all_states.add(dst)
                    all_labels.add(label)
                    all_transitions.append(self.transitions[src])
                    #print(src, label, dst)
        # print(all_states)

        for i, src in enumerate(self.defaults):
            # print i, src
            for j, label in enumerate(self.defaults[src]):
                # print j, label
                for k, dst in enumerate(self.defaults[src][label]):
                    # print k, dst
                    all_transitions.append(self.defaults[src])
                    all_states.add(src)
                    all_states.add(dst)
                    # print(src, label, dst)

        # print(all_transitions)
        nodes = set()
        for i, frozenset_states in enumerate(all_states):
            # print(frozenset_states)
            for j, state in enumerate(frozenset_states):
                # print(state)
                nodes.add(state) # nodes is a list containing all the states both source and destination states
        # print
        # print(nodes)

        # display_struct_start = "\ begin{tikzpicture}"
        # print(display_struct_start)
       
        # for i, state in enumerate(nodes):
        #     if i == 0:
        #         display_states_dfa = "\ node[state, initial]" + " (" + str(i) + ") " + "{$" + str(state) + "$};"
        #     elif i == len(nodes):
        #         display_states_dfa = "\ nodes[state, accepting]" + " (" + str(i) + ") " + "{$" + str(state) + "$};"
        #     else:
        #         display_states_dfa = "\ nodes[state]" + " (" + str(i) + ") " + "{$" + str(state) + "$};"

        #     print(display_states_dfa)

        # print("\path[->]")

        print("digraph G {")
        for i, src in enumerate(all_transitions):
            for j, label in enumerate(src):
                for k, dst in enumerate(label):
                    # display_edges_dfa = "(" + str(i) + ") " + "edge [bend left] node [swap]" + label + " (" + str(k) + ") "
                    # print(display_edges_dfa)
                    display_graph_dfa = str(src) + "->" + str(dst) + "[label=\"" + label + "\"];"
                    print(display_graph_dfa)
        print("}")
        # display_struct_end = "\ end{tikzpicture}"    
        # print(display_struct_end)

def levenshtein_automata(term, k): # term is the reference string and k is the fixed distance of Levenshtein 
    nfa = NFA((0, 0)) # initialization of a NFA
    for i, c in enumerate(term): # We convert the string term into an enumerate which is an indexed object and we cross the enumerate (i is the index and c is the character at the position i in the string)
        for e in range(k + 1): # While the Levenshtein distance is lower than k (k+1 as we start from 0) we continue to cross the Levenshtein automaton
            # Correct character
            nfa.add_transition((i, e), c, (i + 1, e)) # We add a transition between the states of coordinates (i,e) and (i, e+1) and we assign to this transition the character c 
            if e < k: # If the Levenshtein distance is lower to the given tolerance we can continue to cross the Levenshtein automaton and make primary operations
                # Deletion
                nfa.add_transition((i, e), NFA.ANY, (i, e + 1)) # We add a transition of type ANY to perform a deletion between the states of coordinates (i, e) and (i, e+1)
                # Insertion
                nfa.add_transition((i, e), NFA.EPSILON, (i + 1, e + 1)) # We add a transition of type EPSILON to perform an insertion between the states of coordinates (i, e) and (i+1, e+1)
                # Substitution
                nfa.add_transition((i, e), NFA.ANY, (i + 1, e + 1)) # We add a transition of type ANY to perform a substitution between the states of coordinates (i, e) and (i+1, e+1)
    for e in range(k + 1):
        if e < k: # We build the final states with their transitions of the automaton 
            nfa.add_transition((len(term), e), NFA.ANY, (len(term), e + 1))
        nfa.add_final_state((len(term), e))
    return nfa
   # This method builds the Levenshtein automaton 

def find_all_matches(word, k, lookup_func): # word is the hypothesis word, k is the tolerance or maximal Levenshtein distance allowed
    """Uses lookup_func to find all words within levenshtein distance k of word.
    Args:
      word: The word to look up
      k: Maximum edit distance
      lookup_func: A single argument function that returns the first word in the
        database that is greater than or equal to the input argument.
    Yields:
      Every matching word within levenshtein distance k from the database.
    """
    lev = levenshtein_automata(word, k).to_dfa() # creation of the Levenshtein automata as a dfa 
    match = lev.next_valid_string(u'\0') # match contains all the valid strings that we have built by crossing the Levenshtein automata                             
    while match: # We cross the list containing all the valid strings 
        next = lookup_func(match) # build a subset called "next" containing all the strings from the Levenshtein automata that are at a distance of the hypothesis word lower than the given Levenshtein distance
        return
        if match == next:
            yield match # if the match list contains the same items than the next list then we print thanks to "yield" the items of match
            next = next + u'\0'     
        match = lev.next_valid_string(next) # otherwise, we add to the match list the items of the next list that are valid according the Levenshtein automata


def find_match(word, k, lookup_func): # word is the hypothesis string, k is the given Levenshtein distance or tolerance or maximal edit distance
    """Uses lookup_func to find all words within levenshtein distance k of word.

    Args:
      word: The word to look up
      k: Maximum edit distance
      lookup_func: A single argument function that returns the first word in the
        database that is greater than or equal to the input argument.
    Yields:
      Every matching word within levenshtein distance k from the database.
        """
    lev = levenshtein_automata(word, k).to_dfa() # Creates the Levenshtein automata as dfa
    match = lev.next_valid_string(u'\0') # list containing all the valid string built thanks to the Levenshtein automata
    while match: # We cross the list containing all the string from the Levenshtein automata
        next = lookup_func(match) # We fill a new list called "next" only with the word that are at a distance from the hypothesis word lower than the given Levenshtein distance
        if not next:
            return
        if match == next: # If the match list contains the same items than the next list we print the items of the match list
            yield match
            next = next + u'\0'
        match = lev.next_valid_string(next) # Otherwise, we add to the match list the string of the next list that are valid according to the Levenshtein automata


def main():

    #print(f.add_arc(s0, fst.Arc(1, 2, fst.Weight(f.weight_type(), 3, 0), s1)))
    nfa = levenshtein_automata("manon", 2)
    # var_str = nfa.__str__()

    nfa.display_nfa()
    # dfa = nfa.to_dfa()
    # dfa.display_dfa()
    # print(var_str)
    # print(nfa)

    # Test :
    # nodes_dict = {
    #   1: "a_1",
    #   2: "b_2",
    #   3: "c_3",
    #   4: "d_4",
    #   5: "e_5"
    # }
    # for key in nodes_dict:
    #     print(key, nodes_dict[key])

    # dest1 = ["b_2","c_3"]
    # dest2 = ["a_1"]
    # dest3 = ["b_2", "a_1"]
    # dest4 = ["a_1","b_2","e_5"]
    # dest5 = ["c_3","d_4"]

    # dest_dict ={
    #     1: dest1,
    #     2: dest2,
    #     3: dest3,
    #     4: dest4,
    #     5: dest5
    # }

    # for key in dest_dict:
    #     for dst in dest_dict[key]:
    #         for state in enumerate(dest_dict[key][dst]):
    #             print(key, dst, state)


    # nodes_list = ["a_1","b_2","c_3","d_4","e_5"]
    # print(nodes_list)
    # for value in nodes_list:
    #     print(value)


if __name__ == "__main__":
    # execute only if run as a script
    main()
