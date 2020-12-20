from __future__ import division
from random import randint
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

#What I added
import time
from random import choice
from math import log, sqrt
from copy import deepcopy

class Node():
    def __init__(self):
        self.state = None
        self.children = []
        self.expanded_nodes = set()
        self.move = None
        self.plays = 0
        self.wins = 0
        self.number = None
        self.parent = None

    def switchPlayer(self):
        if self.number == 1:
            self.number = 2
        else:
            self.number = 1
        return self.number

    def addChildren(self, node):
        self.children.append(node)

    def addState(self, board):
        self.state = deepcopy(board)

    def addNumber(self, number):
        self.number = number

    def printNode(self):
        print("Player: ", self.number)
        print("Wins: ", self.wins)
        print("Plays: ", self.plays)

class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2

        ##ADDED
        self.calc_time = 1999
        self.visited_tree = []
        self.C = 1.6
        self.colors = {1: "B", 2: "W"}
        self.letters = {"B": 1, "W": 2}

    def selection(self, node):

        child_values = {}

        for child in node.children:
            one = child.wins / child.plays
            score = one + (self.C * sqrt( log(child.parent.plays) / child.plays))
            child_values[child] = score

        try:
            best = max(child_values, key=child_values.get)
        except:
            return None

        return best


    def pick_unvisited(self, node):

        moves = node.state.get_all_possible_moves(self.opponent[node.number])

        #find all the unexpanded moves
        unexpanded = {move for g in moves for move in g if str(move) not in node.expanded_nodes}

        if len(unexpanded) == 0:
            return None

        #find random moves from all the unexpanded moves
        move = choice(tuple(unexpanded))
        #create new child node
        new_node = Node()
        new_node.state = self.next_state(move, self.opponent[node.number], node.state)
        new_node.number = self.opponent[node.number]
        new_node.move = move
        new_node.parent = node

        #parent --> child
        node.addChildren(new_node)
        node.expanded_nodes.add(str(move))

        return new_node

    # checks if the node is perfectly expanded

    def fully_expanded(self, node):
        win = node.state.is_win(self.opponent[node.number])
        if win != 0:
            return self.back_propagate(node, win)

        moves = node.state.get_all_possible_moves(self.opponent[node.number])
        list_moves = [move for g in moves for move in g]
        if len(node.children) < len(list_moves):
            return False
        return True

    def traverse(self, node):
        while self.fully_expanded(node):

            node = self.selection(node)
            if node == None:
                return None

        return self.pick_unvisited(node) or node

    def next_state(self, move, number, board):
        new_board = deepcopy(board)
        new_board.make_move(move, number)
        return new_board

    def non_terminal(self, node):
        moves = node.state.get_all_possible_moves(self.opponent[node.number])

        if len(moves) == 0:
            return False

        winner_2 = node.state.is_win(self.opponent[node.number])
        if winner_2 == 0:
            return True

        return False

    def rollout_policy(self, node):

        moves = choice(node.state.get_all_possible_moves(self.opponent[node.number]))

        node.move = choice(moves)
        node.state.make_move(node.move, self.opponent[node.number])
        node.number = self.opponent[node.number]

        return node

    def result(self, node):

        winner = node.state.is_win(node.number)

        return winner

    def rollout(self, node):

        node_copy = Node()
        node_copy.state = deepcopy(node.state)

        if node.number == 1:
            node_copy.number = 1
        else:
            node_copy.number = 2

        while self.non_terminal(node_copy):

            node_copy = self.rollout_policy(node_copy)

        return self.result(node_copy)

    #checks if the node is a root
    def is_root(self, node):
        if node.parent is None:
            return True
        return False

    #back_propagate the values up the true starting from the expanded node
    def back_propagate(self, node, winner):
        if self.is_root(node):
            node.plays += 1
            if node.number == winner:
                 node.wins += 1
            return None

        node.plays += 1
        if node.number == winner:
            node.wins += 1

        self.back_propagate(node.parent, winner)

    def best_child(self, root):
        most_wins = -1
        most_plays = -1
        best_move = []

        for child in root.children:
            wins = child.wins
            plays = child.plays
            if plays > most_plays:
                most_plays = plays
                best_move = [child.move]
                most_wins = wins
            elif plays == most_plays:
                if wins > most_wins:
                    best_move = [child.move]
                elif wins == most_wins:
                    best_move.append(child.move)

        return choice(best_move)

    def run_sim(self, root):
        ##Start of the Monte Carlo Algorithm

        begin = time.time()
        while (time.time() - begin) < self.calc_time:
            leaf = self.traverse(root)
            if leaf == None:
                continue
            winner = self.rollout(leaf)

            self.back_propagate(leaf, winner)

        return self.best_child(root)

    def get_move(self, move):
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1

        moves = self.board.get_all_possible_moves(self.color)
        list_moves = [move for g in moves for move in g]
        if len(list_moves) == 1:
            self.board.make_move(list_moves[0], self.color)
            return list_moves[0]

        root = Node()
        root.state = deepcopy(self.board)
        root.addNumber(self.opponent[self.color])

        max_move = self.run_sim(root)

        self.board.make_move(max_move, self.color)

        return max_move