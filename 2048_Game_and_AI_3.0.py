# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 13:13:01 2019

@author: Matthijs Schrage
"""
import random
from numpy import transpose, array, any
#import numpy as np

class Game():
    def __init__(self, config):
        self.config = config
    
    #Make transpose and reverse function for the right, up and down movement of the board
    def transpose(board):
        return array(transpose(board)) #Returns a transpose of the matrix
    
    def reverse(board):
        new_config = []
        for row in board:
            new_config.append(row[::-1])
        return array(new_config) #Returns every row of the matrix reversed
    
    #A help function that is nescessary for the 'heuristic' function later. Returns the coordinates of all possible neighbours of one tile on the board
    def neighbours(board, row, col):
        neighbour = []
        realneighbours = []
        #All possible beighbours
        neighbour.append([row+1, col])
        neighbour.append([row-1, col])
        neighbour.append([row, col+1])
        neighbour.append([row, col-1])
        for rownum, coordinate in enumerate(neighbour):
            if 4 in coordinate: #Checks if the neigbour falls out of the matrix (in this case on the bottom and on the right), then does not add that neighbour to the real neighbours
                pass
            elif -1 in coordinate: #Does the same as the previous one, only checks if the coordinate falls out of the matrix on the top or on the left
                pass
            else:
                realneighbours.append(coordinate)
        return realneighbours

    #Spawn a "2" in a random empty position
    def spawn(board, n=1):
        indices = [[ i for i, x in enumerate(row) if x == 0] for row in board] #Gets the positions of all the zeros
        zeros = []
        for rownum, rowval in enumerate(indices):
            for colval in rowval:
                zeros.append([rownum, colval]) #Converts the positions of the zeros to actual coordinates
        random_spawn = random.choice(zeros) #Chooses a random empty position
        board[random_spawn[0]][random_spawn[1]] = 2 #Replaces the zero with a 2
        return board
    
    #A function that handles the merging of numbers. The function is written for a left-swipe.
    #So for the rest of the moves we need to use transpose and reverse to make this function work.
    def merge(board):
        slides = []
        #Get all the tiles that are not 0
        if any(board): 
            for row in board:
                
                slide = [x for x in row if x != 0]  #Gets every value in the row that is not zero
                pairs=[] #Going to store the values that can actually merge in this list
                
                #Identify the tiles that can be paired and just apppending the rest if they cannot be paired
                for idx, val in enumerate(slide):
                    if idx == len(slide)-1: #If the number is the last one in the row, just add it to the list of pairs
                        pairs.append(val)
                        break
                    elif val == slide[idx+1]: #If the number is the same as the next number, add the double value to that place and remove the next one
                        pairs.append(val*2)
                        slide[idx+1] = None
                    else:
                        pairs.append(val)
                        
                #Return the slides and fill the rest of the field with 0's
                slide = [pair for pair in pairs if pair] 
                slide.extend([0] * (len(row) - len(slide))) #Add zeros to fill the board again
                slides.append(slide)
        
        return array(slides)
    
    #Functions for all the possible moves. Move returns 'None' if the move is not possible.
    def left(board):
        new_board = Game.merge(board)
        if any(new_board != board): #Only returns a new board if there is [any]number different from the old board
            return new_board
    
    def right(board):
        new_board = Game.reverse(Game.merge(Game.reverse(board) ) )
        if any(new_board != board):#Only returns a new board if there is [any]number different from the old board
            return new_board
        
    def up(board):
        new_board = Game.transpose(Game.merge(Game.transpose(board) ) )
        if any(new_board != board):#Only returns a new board if there is [any]number different from the old board
            return new_board
    
    def down(board):
        new_board = Game.transpose(Game.reverse(Game.merge(Game.reverse(Game.transpose(board) ) ) ) )
        if any(new_board != board):#Only returns a new board if there is [any]number different from the old board
            return new_board
    
    #Adds all possible moves to the list of children
    def expand(board):
        children = []
        
        upchild = Game.up(board)
        downchild = Game.down(board)
        leftchild = Game.left(board)
        rightchild = Game.right(board)
        
        #Adds the children that are not 'None'. They are None if the move returns the same state as the old state, which means that the move is not possible
        if any(downchild != None): #Some pythonism. If you remove 'any' you will get an error
            children.append(downchild)
        if any(rightchild != None):
            children.append(rightchild)
        if any(leftchild != None):
            children.append(leftchild)
        if any(upchild != None):
            children.append(upchild)
        
        return children

#A function that returns the best possible move for the AI
def AImove(board):
    
    #Can give a score for a certain confifuration of the board
    def heuristic(board):
        score = 0
        penalty = 0
        
        #Weight matrix represents the maximum value that can be multiplied with the boardvalue in that spot of the board
        weight_matrix1 = [[15, 14, 13, 12], 
                         [8,   9,  10, 11], 
                         [7,   6,  5,  4 ], 
                         [0,   1,  2,  3 ]]
        
        weight_matrix2 = [[15,   12.5, 10,  7.5], 
                          [12.5, 10,   7.5, 5  ], 
                          [10,   7.5,  5,   2.5], 
                          [7.5,  5,    2.5, 0  ]]
        
        #Adds to the score if higher values are more in the top left
        #Gives a penalty for any high value that is next to a low value, the bigger the gap, the bigger the penalty
        """Penalty does not work properly so I commented it out"""
        for i in range(4):
            for j in range(4):
                score += (weight_matrix1[i][j] * board[i][j])
                score += (weight_matrix2[i][j] * board[i][j])
#                for neighbour in Game.neighbours(board, i, j):
#                    penalty += abs(board[i][j] - board[(neighbour[0])][(neighbour[1])])
        return score - penalty
    
    #The search funtion searches 4x500 nodes deep and chooses the move that will most likely get the best configuration
    def search(board):
        
        bestmove = []
        bestscore = -float('inf') #Best score is initiated by negative infinity
        search = True
        
        #All the possible children will get checked individually to see which one ahs the highest potential score
        """There is probably a better (and shorter) way to check the score of all the children of a node, but I have found that this method is pretty fast"""
        upchild = Game.up(board)
        downchild = Game.down(board)
        leftchild = Game.left(board)
        rightchild = Game.right(board)
        
        while search == True: #While not all nodes are checked, the function keeps searching
           
            #Only upchild is explained here, the rest of the children are checked in the same way
            if any(upchild):
                end = False #As long as the queue is less than 20 nodes long, children will be added
                queue = [] #queue is the list of nodes that will be checked
                queue.append(upchild) #First initiate the searchspace with upchild
                upscore = -float('inf')
                while queue:
                    node = queue.pop(0) #Pop the front node of the queue
                    nodescore = heuristic(node) #Check the score of that node
                    if nodescore > upscore: #Check if it has a better score than the highest value for upscore
                        upscore = nodescore
                    if end == False:
                        if len(queue) < 25: #We check 25 nodes deep
                            queue.extend(Game.expand(Game.spawn(node))) #Expand the children of the current node if the queue is less than 20 nodes long
                        else: 
                            end = True
                if upscore > bestscore: #Check if the best possible score from this child is better than the best score
                    bestmove = upchild
                    bestscore = upscore
            
            if any(leftchild):
                end = False
                queue = []
                queue.append(leftchild)
                leftscore = -float('inf')
                while queue:
                    node = queue.pop(0)
                    nodescore = heuristic(node)
                    if nodescore > leftscore:
                        leftscore = nodescore
                    if end == False:
                        if len(queue) < 25:
                            queue.extend(Game.expand(Game.spawn(node)))
                        else:
                            end = True
                if leftscore > bestscore:
                    bestmove = leftchild
                    bestscore = leftscore
            
            if any(rightchild):
                end = False
                queue = []
                queue.append(rightchild)
                rightscore = -float('inf')
                while queue:
                    node = queue.pop(0)
                    nodescore = heuristic(node)
                    if nodescore > rightscore:
                        rightscore = nodescore
                    if end == False:
                        if len(queue) < 25:
                            queue.extend(Game.expand(Game.spawn(node)))
                        else:
                            end = True
                if rightscore > bestscore:
                    bestmove = rightchild
                    bestscore = rightscore
                    
            if any(downchild):
                end = False
                queue = []
                queue.append(downchild)
                downscore = -float('inf')
                while queue:
                    node = queue.pop(0)
                    nodescore = heuristic(node)
                    if nodescore > downscore:
                        downscore = nodescore
                    if end == False:
                        if len(queue) < 25:
                            queue.extend(Game.expand(Game.spawn(node)))
                        else:
                            end = True
                if downscore > bestscore:
                     bestmove = downchild
                     bestscore = downscore  
                     
            search = False
            
        return bestmove
    #Returns a bestmove which has already spawned a new 2, so in main we don't need to use spawn anymore
    return search(board)


#Main function runs until the game is over
def main():
    
    #Starting board
    board = [[2, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0], 
             [0, 0, 0, 0]]
    
    Game_Over = Game.expand(board)
    
    while Game_Over != []: #The loop runs if there are possible moves. Expand automaticly returns '[]' if there are no moves left
        Game_Over = Game.expand(board) #Checks game-over
        board = AImove(board) #Returns the new board with a new spawn
        print(board)

    print("Game over")

main()