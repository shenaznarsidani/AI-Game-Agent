import random
import sys
from read import readInput
from write import writeOutput
from copy import deepcopy

from host import GO

class my_Player_AlphaBeta():
    
    def __init__(self):
        self.type = 'AlphaBeta'
        self.depth = 3
        self.alpha = float("-inf")
        self.beta = float("inf")
        self.boardSize=5
        self.col = None
        
    def copyBoard(self, board):
        copied_board=deepcopy(board)
        return copied_board

    def koCheck(self, prevBoard, board):
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                if board[i][j] != prevBoard[i][j]:
                    return False
                else:
                    continue
        return True
    
    def getAction(self, currState, prevState, color):
        
        steps = list()
        bestScore = 0
        currStateCopy = self.copyBoard(currState)

        
        for step in self.findValidSteps(currState, prevState, color):
            nextState = self.applyStep(currState, color, step) 
            score = self.getScore(nextState, 3-color)
            evaluation = self.minMax(nextState, currStateCopy, self.depth-1, self.alpha, self.beta, score, 3-color)
            #evaluation = self.minMax(nextState, currStateCopy, self.depth, self.alpha, self.beta, score, color)
            currentScore = -evaluation
            if currentScore > bestScore or not steps:
                bestScore = currentScore
                alpha = bestScore
                steps = [step]
            elif currentScore == bestScore:
                if step not in steps:
                    steps.append(step)
                else:
                    None
        return steps
    
    def applyStep(self, board, player, step):
        newBoard = self.copyBoard(board)
        newBoard[step[0]][step[1]] = player
        newBoard = self.removeDeadCoins(newBoard, 3-player)
        return newBoard
        
    def minMax(self, currState, prevState, depth, alpha, beta, score, nextPlayer):
        if depth == 0:
            return score
        bestScore = score

        currStateCopy = self.copyBoard(currState)
        
        for step in self.findValidSteps(currState, prevState, nextPlayer):
            
            
            nextState = self.applyStep(currState, nextPlayer, step)
            
           
            score = self.getScore(nextState, 3-nextPlayer)
            evaluation = self.minMax(nextState, currStateCopy, depth - 1, 
                                        alpha, beta, score, 3-nextPlayer)

            currentScore = -evaluation
           
            if currentScore > bestScore:
                bestScore = currentScore
            
            newScore = -bestScore

            
            if nextPlayer == 3-self.col:
                playerScore = newScore
                
                if playerScore < alpha:
                    #return alpha
                    return bestScore
                elif bestScore > beta:
                    beta = bestScore
           
            elif nextPlayer == self.col:
                opponentScore = newScore
                
                if opponentScore < beta:
                    #return beta
                    return bestScore
                elif bestScore > alpha:
                    alpha = bestScore

        return bestScore
    
    def checkSurrounding(self, board, color, i, j, nextI, nextJ):

        currNeighbors = self.findAdjacentCoins(board, i, j)
        currNeighbors.remove((nextI, nextJ))
        
        nextNeighbors = self.findAdjacentCoins(board, nextI, nextJ)
        nextNeighbors.remove((i, j))
        neighbors = currNeighbors + nextNeighbors
        # currNeighbors.remove([nextI, nextJ])
        for pos in neighbors:
            if board[pos[0]][pos[1]] != color:
                return False
        if nextI == i + 1:
            corners = [[i - 1, j - 1], [i - 1, j + 1], [nextI + 1, nextJ - 1], [nextI + 1, nextJ + 1]]
        else:
            corners = [[i - 1, j - 1], [i + 1, j - 1], [nextI - 1, nextJ + 1], [nextI + 1, nextJ + 1]]
            
        for corner in corners:
            if corner[0] < 0 or corner[0] == 5 or corner[1] < 0 or corner[1] == 5:
                continue
            if board[corner[0]][corner[1]] != color:
                return False            
        return True
            
    def countEyes(self, board, color):
        eyes = 0
        for i in range(5):
            for j in range(5):
                if board[i][j] == 0:
                    if i + 1 < 5 and j + 1 < 5:
                        if board[i + 1][j] == 0 and self.checkSurrounding(board, color, i, j, i + 1, j):
                                eyes += 1
                        if board[i][j + 1] == 0 and self.checkSurrounding(board, color, i, j, i, j + 1):
                                eyes += 1
                    elif i + 1 < 5:
                        if board[i + 1][j] == 0 and self.checkSurrounding(board, color, i, j, i + 1, j):
                                eyes += 1
                    elif j + 1 < 5:
                        if board[i][j + 1] == 0 and self.checkSurrounding(board, color, i, j, i, j + 1):
                                eyes += 1
                    else:
                        continue
        return eyes
    
    def getScore(self, board, np):
        p1=0
        p2=0
        scoreP1=0
        scoreP2=0
        scoreP1 = 10 * self.countEyes(board, self.col)
        scoreP2 = 10 * self.countEyes(board, 3 - self.col)
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                if board[i][j] == self.col:
                    p1 += 1
                    scoreP1 += p1 + 2*self.groupLiberty(board, i, j) + 0.5*len(self.findSimilarNeighbors(board, i, j))
                    #scoreP1 += p1 + 0.1*len(self.findSimilarNeighbors(board, i, j)
                elif board[i][j] == 3 - self.col:
                    p2 += 1
                    scoreP2 += p2 + 2*self.groupLiberty(board, i, j) + 0.5*len(self.findSimilarNeighbors(board, i, j)) 
                    #scoreP2 += p2 + 0.1*len(self.findSimilarNeighbors(board, i, j)
                else:
                    continue
        if np == self.col:
            return scoreP1 - scoreP2
        else:
            return scoreP2 - scoreP1

    
    def findValidSteps(self, board, prevBoard, player):
        
        validSteps = list()
        
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                # position that has a 0 is empty
                if not self.isCellOccupied(board, i, j):
                    boardCopy = self.copyBoard(board)
                    #applyStep(boardCopy, player,(i,j)) 
                    boardCopy[i][j] = player
                    deadPieces = self.findDeadCoins(boardCopy, 3 - player)
                    boardCopy = self.removeDeadCoins(boardCopy, 3 - player)
                    if self.groupLiberty(boardCopy, i, j) >= 1 and not (deadPieces and self.koCheck(prevBoard, boardCopy)):
                        if((i,j) not in validSteps):
                            validSteps.append((i,j))
                        else:
                            None
        return validSteps
        
    def groupLiberty(self, board, row, col):
        count = 0
        
        for point in self.findSimilarGroup(board, row, col):
            a=point[0]
            b=point[1]
            
            for neighbor in self.findAdjacentCoins(board,a,b):
                i=neighbor[0]
                j=neighbor[1]
                if board[i][j] == 0:
                    count += 1
        return count
    
    def findSimilarGroup(self, board, row, col):
        
        queue = [(row, col)]
        group = list()

        while queue:
            node = queue.pop(0)
            group.append(node)
            for neighbor in self.findSimilarNeighbors(board, node[0], node[1]):
                if neighbor not in queue and neighbor not in group:
                    queue.append(neighbor)
        return group
        
        
    def removeCoins(self, board, locs):
        for loc in locs:
            i=loc[0]
            j=loc[1]
            board[i][j] = 0
        return board

    def removeDeadCoins(self, board, color):
        deadCoins = self.findDeadCoins(board, color)
        if not deadCoins:
            return board
        newBoard = self.removeCoins(board, deadCoins)
        return newBoard


    def findAdjacentCoins(self, board, i, j):
        
        board = self.removeDeadCoins(board, (i, j))
        neighbors = []
        if i > 0: neighbors.append((i-1, j))
        if i < (self.boardSize - 1): neighbors.append((i+1, j))
        if j > 0: neighbors.append((i, j-1))
        if j < (self.boardSize - 1): neighbors.append((i, j+1))
        return neighbors
           
    def findSimilarNeighbors(self, board, row, col):
        similarCoins = list()
        for point in self.findAdjacentCoins(board, row, col):
            i=point[0]
            j=point[1]
            if board[i][j] == board[row][col] and point not in similarCoins:
                similarCoins.append(point)
            else:
                None
        return similarCoins

    def isCellOccupied(self, board, a, b):
        if board[a][b] == 0 :
            return False
        else:
            return True
        
    def findDeadCoins(self, board, color):
        deadCoins = list()
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                if board[i][j] == color:
                    if not self.groupLiberty(board, i, j) and (i,j) not in deadCoins:
                        deadCoins.append((i, j))
                    else:
                        continue
                else:
                    continue
        #for coin in deadCoins:
        #    print(coin)
        return deadCoins

    def get_input(self, go, piece_type):
        '''
        Get one input.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: (row, column) coordinate of input.
        '''        
        
        
        flag = 0
        for i in range(5):
            if piece_type in go.board[i]:
                flag = 1
                break
        if flag == 0 and go.board[2][2] == 0:
            return [2,2]
        else:
            action = self.getAction(board, previous_board, piece_type)
            #    print(action)
            
            if action == []:
                action = 'PASS'
            
            else:
                action = random.choice(action)

            return action
    
    
if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = my_Player_AlphaBeta()
    player.col = piece_type
    action = player.get_input(go, piece_type)
    writeOutput(action)
    
    