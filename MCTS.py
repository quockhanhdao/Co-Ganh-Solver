import math
import copy

import game

class Solver:
    def __init__(self,
                 prev_board: list = None,
                 board: list = None,
                 player: int = 1,
                 simu_threshold: int = 10):
        self.prev_board = copy.deepcopy(prev_board)
        self.board = copy.deepcopy(board)
        self.player, self.opponent = player, -1 * player
        self.simu_threshold = simu_threshold
        self.total_simu = 0
        
        self.cg = game.CoGanh()

    # depend on the ratio win_simu / nums_sime of each node
    def choose_1(self, children):
        best_move = None
        max_ratio = 0
        
        for node in children:
            ratio = node.ratio()
            if ratio >= max_ratio:
                max_ratio = ratio
                best_move = node
                
        return best_move
    
    # depend on the total numbers of simulation of each node
    def choose_2(self, children):
        best_move = None
        max_simu = 0
        
        for node in children:
            simu = node.nums_simu
            if simu >= max_simu:
                max_simu = simu
                best_move = node
                
        return best_move

    # Evaluate function to balance the exploration and exploitation
    def evaluate(self, node, c = 1.414):
        x = node.ratio()
        if node.nums_simu > 0:
            y = math.sqrt(math.log(self.total_simu) / node.nums_simu)
        else:
            y = 0
        
        return x + c * y
    
    def Selection(self, list):
        if len(list) == 0:
            return None
        elif len(list) == 1:
            return list[0]
        
        max_eval = -100
        best_node = None
        for node in list:
            eval = self.evaluate(node)
            if eval >= max_eval:
                max_eval = eval
                best_node = node
                
        return best_node
    
    # Using simple simulation and selection to expand the tree for both player and opponent
    def Expansion(self, node):
        ply, oppo = 0, 0
        if node.parent == None:
            ply = self.player
        else:
            board1, board2 = node.parent.board, node.board
            for i in range(5):
                for j in range(5):
                    if board1[i][j] == 0 and board2[i][j] != 0:
                        ply, oppo = -1 * board2[i][j], board2[i][j]
        
        trap = None
        if node.parent != None:
            trap = self.cg.checkTrap(node.parent.board, node.board, oppo)
        
        pos = self.cg.getPosition(node.board, ply)
        possible_moves = []
        
        for p in pos:
            possible_moves += self.cg.move_gen_2(node, p, trap) 

        isTrap = False
        for move in possible_moves:
            if move[1]:
                isTrap = True
                break
            
        for move in possible_moves:
            if isTrap:
                if not move[1]:
                    continue
            node.child.append(move[0])
            
    # Just an idea that using Minimax to calculate the next step of the opponent
    # instead of using simulation and selection like the original MCTS
    def Expansion_2(self, node):
        ply = 0
        if node.parent == None:
            ply = self.player
        else:
            board1, board2 = node.parent.board, node.board
            for i in range(5):
                for j in range(5):
                    if board1[i][j] == 0 and board2[i][j] != 0:
                        ply = -1 * board2[i][j]
        
        if ply == self.opponent:
            return 0
        else:
            return 0
    
    def Simulation(self, node):
        ply = 0
        if node.parent == None:
            ply = self.player
        else:
            board1, board2 = node.parent.board, node.board
            for i in range(5):
                for j in range(5):
                    if board1[i][j] == 0 and board2[i][j] != 0:
                        ply = -1 * board2[i][j]
                        
        final_step = copy.deepcopy(node)
        
        while not self.cg.end_game(final_step.board, False):
            final_step = self.cg.random_move_2(final_step, ply)
            ply *= -1
            
        self.total_simu += 1
        node.nums_simu += 1
        prev = node.parent
        while prev != None:
            prev.nums_simu += 1
            prev = prev.parent
            
        if self.player == 1:
            if self.cg.X_win(final_step.board):
                return True
            return False
        else:
            if self.cg.O_win(final_step.board):
                return True
            return False

    def Update(self, node, win):
        if win:
            node.win_simu += 1
            prev = node.parent
            while prev != None:
                prev.win_simu += 1
                prev = prev.parent
        return
    
    def solv(self):
        node = game.Node_2(self.board)
        
        while self.total_simu < self.simu_threshold:
            # Selection
            selected_node = node
            while len(selected_node.child) > 0:
                list = selected_node.child
                selected_node = self.Selection(list)
            
            # Expansion
            self.Expansion(selected_node)
            
            # Simulation
            res = self.Simulation(selected_node)
            
            # Update
            self.Update(selected_node, res)
            
        best_move = self.choose_1(node.child)
        start, end = self.cg.back_prop(self.board, best_move.board, self.player)
        
        return (start, end)