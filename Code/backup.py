import random
import sys
import os

from sklearn import neighbors
from read import readInput
from write import writeOutput
from copy import deepcopy
from host import GO
from os import path as file_path

class my_Player_AlphaBeta():
    
    def __init__(self, color):
        self.type = 'AlphaBeta'
        self.color = color
        
    def detect_neighbor(self, i, j, board): # from host
        '''
        Detect all the neighbors of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbors row and column (row, column) of position (i, j).
        '''
       
        neighbors = []
        # Detect borders and add neighbor coordinates
        if i > 0: neighbors.append((i-1, j))
        if i < len(board) - 1: neighbors.append((i+1, j))
        if j > 0: neighbors.append((i, j-1))
        if j < len(board) - 1: neighbors.append((i, j+1))
        return neighbors

    def detect_neighbor_ally(self, i, j, board): # from host
        '''
        Detect the neighbor allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbored allies row and column (row, column) of position (i, j).
        '''
        neighbors = self.detect_neighbor(i, j, board)  # Detect neighbors
        group_allies = []
        # Iterate through neighbors
        for piece in neighbors:
            # Add to allies list if having the same color
            if board[piece[0]][piece[1]] == board[i][j]:
                group_allies.append(piece)
        return group_allies

    def ally_dfs(self, i, j, board): # from host
        '''
        Using DFS to search for all allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the all allies row and column (row, column) of position (i, j).
        '''
        stack = [(i, j)]  # stack for DFS serach
        ally_members = []  # record allies positions during the search
        while stack:
            piece = stack.pop()
            ally_members.append(piece)
            neighbor_allies = self.detect_neighbor_ally(piece[0], piece[1], board)
            for ally in neighbor_allies:
                if ally not in stack and ally not in ally_members:
                    stack.append(ally)
        return ally_members

    def find_liberty(self, i, j, board): # from host
        '''
        Find liberty of a given stone. If a group of allied stones has no liberty, they all die.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: boolean indicating whether the given stone still has liberty.
        '''
        liberty = 0
        ally_members = self.ally_dfs(i, j, board)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1], board)
            for piece in neighbors:
                # If there is empty space around a piece, it has liberty
                if board[piece[0]][piece[1]] == 0:
                    liberty += 1
        # If none of the pieces in a allied group has an empty space, it has no liberty
        return liberty
    
            
    def find_died_pieces(self, board, piece_type): # from host
        '''
        Find the died stones that has no liberty in the board for a given piece type.

        :param piece_type: 1('X') or 2('O').
        :return: a list containing the dead pieces row and column(row, column).
        '''
        
        died_pieces = []

        for i in range(len(board)):
            for j in range(len(board)):
                # Check if there is a piece at this position:
                if board[i][j] == piece_type:
                    # The piece die if it has no liberty
                    if not self.find_liberty(i, j, board):
                        died_pieces.append((i,j))
        return died_pieces

    def is_present(self, board, color):
        for i in range(5):
            if color in board[i]:
                return True
        return False

    def get_input(self, go, piece_type):
        '''
        Get one input.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: (row, column) coordinate of input.
        '''        
        # possible_placements = []
        '''for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check = True):
                    possible_placements.append((i,j))'''
        base_hue_val = self.eval(go.board, piece_type)
        # if not self.is_present(go.board, piece_type):
        #     if go.board[2][2] == 0:
        #         return [2,2]
        #     elif go.board[4][0] == 0:
        #         return [4,0]
        #     elif go.board[0][4] == 0:
        #         return [0,4]
        #     else:
        #         return [0,0]
        _, action = self.minimax(go.board, go.previous_board, base_hue_val, 5, float('-inf'), float('inf'), piece_type, True)
        if action == []:
            return "PASS"
        return random.choice(action)
        # actions = self.minmax(go.board, go.previous_board, 2, float("-inf"), float("-inf"), piece_type)
        # if actions == []:
        #     return "PASS"
        # else:
        #     return random.choice(actions)
    
    def check_surrounding(self, board, color, i, j, next_i, next_j):
        neighbors_curr = self.detect_neighbor(i, j, board)
        neighbors_curr.remove((next_i, next_j))
        neighbors_next = self.detect_neighbor(next_i, next_j, board)
        neighbors_next.remove((i, j))
        neighbors = neighbors_curr + neighbors_next
        # neighbors_curr.remove([next_i, next_j])
        for pos in neighbors:
            if board[pos[0]][pos[1]] != color:
                return False
        if next_i == i + 1:
            corners = [[i - 1, j - 1], [i - 1, j + 1], [next_i + 1, next_j - 1], [next_i + 1, next_j + 1]]
        else:
            corners = [[i - 1, j - 1], [i + 1, j - 1], [next_i - 1, next_j + 1], [next_i + 1, next_j + 1]]
        for corner in corners:
            if corner[0] < 0 or corner[0] == 5 or corner[1] < 0 or corner[1] == 5:
                continue
            if board[corner[0]][corner[1]] != color:
                return False            
        return True
            

    def count_eyes(self, board, color):
        eyes = 0
        for i in range(5):
            for j in range(5):
                if board[i][j] == 0:
                    if i + 1 < 5 and j + 1 < 5:
                        if board[i + 1][j] == 0:
                            if self.check_surrounding(board, color, i, j, i + 1, j):
                                eyes += 1
                        if board[i][j + 1] == 0:
                            if self.check_surrounding(board, color, i, j, i, j + 1):
                                eyes += 1
                    elif i + 1 < 5:
                        if board[i + 1][j] == 0:
                            if self.check_surrounding(board, color, i, j, i + 1, j):
                                eyes += 1
                    elif j + 1 < 5:
                        if board[i][j + 1] == 0:
                            if self.check_surrounding(board, color, i, j, i, j + 1):
                                eyes += 1
                    else:
                        continue
        return eyes
    
    def count_connected_liberty(self, board, color):
        connected = []
        liberty = 0
        pieces = 0
        for i in range(5):
            for j in range(5):
                if board[i][j] == color:
                    pieces += 1
                    neighbors = self.detect_neighbor(i, j, board)
                    flag = 0
                    for piece in neighbors:
                        if board[piece[0]][piece[1]] == color:
                            flag = 1
                            if piece not in connected:
                                connected.append(piece)
                        elif board[piece[0]][piece[1]] == 0:
                            liberty += 1
                    if flag == 1:
                        connected.append([i, j])
        return [len(connected), 0.5 * liberty, 2 * pieces]

    def eval(self, board, curr_color):
        # player_hue_val = 0
        # opponent_hue_val = 0
        player_hue_val = sum(self.count_connected_liberty(board, curr_color)) + 10 * self.count_eyes(board, curr_color)
        opponent_hue_val = sum(self.count_connected_liberty(board, 3 - curr_color)) + 10 * self.count_eyes(board, 3 - curr_color)
        if curr_color == 2:
            player_hue_val += 2.5
        else:
            opponent_hue_val += 2.5
        if curr_color == self.color:
            return player_hue_val - opponent_hue_val
        else:
            return opponent_hue_val - player_hue_val

    # def eval(self, board, curr_color):
    #     player_pieces = 0
    #     opponent_pieces = 0
    #     player_hue_val = 10 * self.count_eyes(board, curr_color)
    #     opponent_hue_val = 10 * self.count_eyes(board, 3 - curr_color)
    #     for i in range(5):
    #         for j in range(5):
    #             if board[i][j] == curr_color:
    #                 player_pieces += 1
    #                 player_hue_val += (player_pieces + self.find_liberty(i, j, board))
    #             elif board[i][j] == 3 - curr_color:
    #                 opponent_pieces += 1
    #                 opponent_hue_val += (opponent_pieces + self.find_liberty(i, j, board))
    #     # if curr_color == 2:
    #     #     player_hue_val += 2.5
    #     # else:
    #     #     opponent_hue_val += 2.5
    #     if curr_color == self.color:
    #         return player_hue_val - opponent_hue_val
    #     else:
    #         return opponent_hue_val - player_hue_val

    def minimax(self, board, prev_board, base_hue_val, depth, alpha, beta, player, maximise):
        if depth == 0:
            return base_hue_val, None
        
        current_board_copy = self.copy_board(board)
        if player == 1:
            piecetype = 1
            otherpiece = 2
        else:
            piecetype = 2
            otherpiece = 1
        if maximise:
            max_hue_val = base_hue_val
            best_move = []
            appropriate_actions = self.get_appropriate_moves(player, current_board_copy, prev_board)
            for action in appropriate_actions:
                new_board_copy = self.copy_board(board)
                new_board_copy[action[0]][action[1]] = piecetype
                dead_pieces = self.find_died_pieces(new_board_copy, otherpiece)
                new_board_copy = self.remove_pieces(new_board_copy, dead_pieces)
                if player == 1:
                    hue_val = self.minimax(new_board_copy, current_board_copy, max_hue_val, depth - 1, alpha, beta, 2, False)[0]
                else:
                    hue_val = self.minimax(new_board_copy, current_board_copy, max_hue_val, depth - 1, alpha, beta, 1, False)[0]
                if max_hue_val <= hue_val:
                    max_hue_val = hue_val
                    best_move.append(action)
                if max_hue_val >= beta:
                    best_move = [action]
                    return max_hue_val, best_move
                alpha = max(alpha, hue_val)
            return max_hue_val, best_move
        else:
            min_hue_val = base_hue_val
            best_move = []
            appropriate_actions = self.get_appropriate_moves(player, current_board_copy, prev_board)
            for action in appropriate_actions:
                new_board_copy = self.copy_board(board)
                new_board_copy[action[0]][action[1]] = piecetype
                dead_pieces = self.find_died_pieces(new_board_copy, otherpiece)
                new_board_copy = self.remove_pieces(new_board_copy, dead_pieces)
                if player == 1:
                    hue_val = self.minimax(new_board_copy, current_board_copy, min_hue_val, depth - 1, alpha, beta, 2, True)[0]
                else:
                    hue_val = self.minimax(new_board_copy, current_board_copy, min_hue_val, depth - 1, alpha, beta, 1, True)[0]
                if min_hue_val >= hue_val:
                    min_hue_val = hue_val
                    best_move.append(action)
                if min_hue_val <= alpha:
                    best_move = [action]
                    return min_hue_val, best_move
                beta = min(beta, hue_val)
            return min_hue_val, best_move

    
        
    # def take_action(self, action, go, player):
    #     newboard = self.copy_board(go.board)
    #     piecetype=0
    #     otherpiece=0
    #     if(player=='X'):
    #         piecetype = 1
    #         otherpiece = 2
    #     elif(player=='O'):
    #         piecetype = 2
    #         otherpiece = 1
    #     newboard[action[0]][action[1]] = piecetype
    #     dead_pieces = self.find_died_pieces(newboard,otherpiece) 
    #     board_with_dead_removed = self.remove_pieces(newboard, dead_pieces)
    #     # find_dead_pieces(other player)
    #     # remove dead pieces
    #     return dead_pieces, board_with_dead_removed
        
    def remove_pieces(self, board, dead_pieces):
        if len(dead_pieces)==0:
            return board
        for piece in dead_pieces:
            board[piece[0]][piece[1]]=0
        return board
                  
    def copy_board(self, board):
        copied_board=deepcopy(board)
        return copied_board
                            
    def find_liberty_positions(self,board, i, j): # from host.py
        '''
        Find liberty of a given stone. If a group of allied stones has no liberty, they all die.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: boolean indicating whether the given stone still has liberty.
        '''
        positions=set()                    
        ally_members = self.ally_dfs(i, j, board)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1], board)
            for piece in neighbors:
                # If there is empty space around a piece, it has liberty
                if board[piece[0]][piece[1]] == 0:
                    positions.add(piece)
        list_of_positions = list(positions);                    
        return list_of_positions
                            
    def compare_board(self, board1, board2):
        for i in range(len(board)):
            for j in range(len(board)):
                if board1[i][j] == board2[i][j]:
                    continue
                else:
                    return False;        
        return True

    def get_appropriate_moves(self, player, curr_board, prev_board):
        app_moves=[]
        curr_board_copy = self.copy_board(curr_board)
        #find dead stones 
        dead_pieces = self.find_died_pieces(curr_board_copy, player)
        #remove dead stones
        curr_board_copy = self.remove_pieces(curr_board_copy, dead_pieces)               
        for i in range(5):
            for j in range(5):
                liberty_positions = self.find_liberty_positions(curr_board_copy,i,j);            
                if curr_board[i][j]==0 and len(liberty_positions)>0 and not(dead_pieces and self.compare_board(prev_board, curr_board_copy)):
                    app_moves.append([i,j])
        return app_moves
    
if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = my_Player_AlphaBeta(piece_type)
    checker=0
    checker_bool = False
    for i in range(5):
        for j in range(5):
            
            if board[i][j] != 0:
                if i == 2 and j == 2:
                    checker_bool = True
                checker += 1

    if (checker==0 and piece_type==1) or (checker==1 and piece_type==2 and checker_bool is False):
        action = [2,2]
    else:
        action = player.get_input(go, piece_type)
    writeOutput(action)