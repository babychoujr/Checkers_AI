from __future__ import division
from random import randint
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

#What I added
import datetime
from random import choice
from math import log, sqrt
from copy import deepcopy


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

        # ---------- What we added -----------

        self.calc_time = datetime.timedelta(seconds = 3)
        self.max_moves = 35
        self.wins = {}
        self.plays = {}
        self.max_depth = 0
        self.C = 1.4
        self.colors = {1:"B", 2:"W"}
        self.letters = {"B":1, "W":2}
        self.states = []

    def run_sim(self, board):
        player = self.colors[self.color]
        number = self.letters[player]
        visited_states = set()

        expand = True

        for i in range(self.max_moves):

            moves = board.get_all_possible_moves(number)

            if len(moves) == 0:
                return

            if all(self.plays.get((player, x)) for move in moves for x in move):
                max_move = self.selection(moves, player)
            else:
                index = randint(0, len(moves) - 1)
                inner_index = randint(0, len(moves[index]) - 1)
                max_move = moves[index][inner_index]

            board.make_move(max_move, number)

            if expand == True and (player, max_move) not in self.plays:
                expand = False
                self.expand(player,max_move)

            visited_states.add((player, max_move))

            winner = board.is_win("W")
            if winner == 1 or winner == 2 or winner == -1:
                break

            if player == "W":
                player = "B"
                number = 1
            else:
                player = "W"
                number = 2

        if winner == 0:
            return
        elif winner == -1:
            winner == self.colors[self.color]
        else:
            winner = self.colors[winner]

        self.back_propagate(visited_states, winner)

    def selection(self, moves, player):
        max = -100000
        max_move = ""
        sum_plays = 0
        for g in moves:
            for x in g:
                sum_plays = sum_plays + self.plays.get((player, x), 0)
        for g in moves:
            for x in g:
                try:
                    one = self.wins[(player, x)] / self.plays[(player, x)]
                    score = one + self.C * sqrt(log(sum_plays) / self.plays[(player, x)])
                except:
                    score = -100000
                if score > max:
                    max = score
                    max_move = x
        return max_move

    def back_propagate(self, visited_states, winner):
        for player, move in visited_states:
            if (player, move) not in self.plays:
                continue
            self.plays[(player, move)] += 1
            if player == winner:
                self.wins[(player, move)] += 1

    def expand(self, player, move):
        self.plays[(player, move)] = 0
        self.wins[(player, move)] = 0

    def get_move(self,move):
        first = False
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
            first = True

        player = self.colors[self.color]
        moves = self.board.get_all_possible_moves(self.color)
        index = randint(0, len(moves) - 1)
        inner_index = randint(0, len(moves[index]) - 1)
        move = moves[index][inner_index]

        if first:
            self.board.make_move(move, self.color)
            return move

        games = 0
        begin = datetime.datetime.utcnow()
        new_board = deepcopy(self.board)
        while datetime.datetime.utcnow() - begin < self.calc_time:
            self.run_sim(new_board)
            games += 1

        max_move = self.selection(moves, player)
        if max_move == "":
            max_move = move

        self.board.make_move(max_move,self.color)
        if max_move == "":
            return move

        return max_move

"""
    def get_move(self, move):

        first = False
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
            print("done")
        else:
            self.color = 1
            print("hi")
            first = True

        self.max_depth = 0
        self.states = self.board.get_all_possible_moves(self.color)

        index = randint(0, len(self.states) - 1)
        inner_index = randint(0, len(self.states[index]) - 1)
        state = self.states[index][inner_index]

        if first:
            return state

        player = self.colors[self.color]
        moves = self.states

        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calc_time:
            sim_board = self.board
            self.run_sim(state, sim_board)
            games += 1

        move_states = []
        for i in moves:
            new_board = self.board
            n = (i, new_board.make_move(i, self.color))
            move_states.append(n)

        percent_wins, move = max(
            (self.wins.get((player, S), 0) /
             self.plays.get((player, S), 1),
             i)
            for i, S in move_states
        )

        self.board.make_move(move, self.color)
        return move
    """

