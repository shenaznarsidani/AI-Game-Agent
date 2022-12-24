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