import sys, parse
import time, os, copy, random
from collections import deque

class Gamestate:    # object that stores current state of the game
    def __init__(self, map, Py, Px, ghosts, food):
        self.map = map
        self.Py = Py
        self.Px = Px
        self.ghosts = ghosts
        self.food = food
        self.score = 0
        self.winner = ''
        self.hasEnded = False
        self.utility = 0

    def validMoves(self, player):
        moves = []
        if player == 'P':       # find valid moves for pacman in alphabetic order
            y = self.Py
            x = self.Px

            if not(self.map[y][x+1] == '%'):
                moves.append('E')
            if not(self.map[y-1][x] == '%'):
                moves.append('N')
            if not(self.map[y+1][x] == '%'):
                moves.append('S')
            if not(self.map[y][x-1] == '%'):
                moves.append('W')
        else:       # find valid moves for ghost in alphabetic order
            y = self.ghosts[player][0]
            x = self.ghosts[player][1]

            if not(self.map[y][x+1] == '%') and [y, x+1] not in self.ghosts.values():
                moves.append('E')
            if not(self.map[y-1][x] == '%') and [y-1, x] not in self.ghosts.values():
                moves.append('N')
            if not(self.map[y+1][x] == '%') and [y+1, x] not in self.ghosts.values():
                moves.append('S')
            if not(self.map[y][x-1] == '%') and [y, x-1] not in self.ghosts.values():
                moves.append('W')
        
        return moves

    def getUtility(self):
        visited = set((self.Py, self.Px))
        queue = [(self.Py, self.Px)]
        dist = {(self.Py, self.Px): 0}
        
        ghost_search = 3        # only consider ghosts within this distance
        dist_food = float('inf')
        dist_ghost = 10
        
        while queue:        # find closest food and check if there are ghost within distance of ghost_search
            curr = queue.pop(0)
            if self.map[curr[0]][curr[1]] == '.':
                dist_food = min(dist_food, dist[curr])

            if [curr[0], curr[1]] in self.ghosts.values():
                dist_ghost = min(dist_ghost, dist[curr])

            if (dist_food < float('inf')):       # check if can end loop
                if dist_ghost < 10 or dist[curr] > ghost_search:       # ghost has been found within search distance
                    break
                
            # append valid neighbours to queue
            if not(self.map[curr[0]][curr[1]+1] == '%'):     # E
                if (curr[0], curr[1]+1) not in visited:
                    dist[(curr[0], curr[1]+1)] = dist[curr] + 1
                    queue.append((curr[0], curr[1]+1))
                    visited.add((curr[0], curr[1]+1))
            if not(self.map[curr[0]-1][curr[1]] == '%'):     # N
                if (curr[0]-1, curr[1]) not in visited:
                    dist[(curr[0]-1, curr[1])] = dist[curr] + 1
                    queue.append((curr[0]-1, curr[1]))
                    visited.add((curr[0]-1, curr[1]))
            if not(self.map[curr[0]+1][curr[1]] == '%'):     # S
                if (curr[0]+1, curr[1]) not in visited:
                    dist[(curr[0]+1, curr[1])] = dist[curr] + 1
                    queue.append((curr[0]+1, curr[1]))
                    visited.add((curr[0]+1, curr[1]))
            if not(self.map[curr[0]][curr[1]-1] == '%'):     # W
                if (curr[0], curr[1]-1) not in visited:
                    dist[(curr[0], curr[1]-1)] = dist[curr] + 1
                    queue.append((curr[0], curr[1]-1))
                    visited.add((curr[0], curr[1]-1))

        self.utility = dist_ghost * dist_ghost / 0.7 * (dist_food +1)     # evaluation function

    def makeMove(self, player, move):   # move player and update map and score
        if player == 'P':       # pacman is making a move
            if (move == 'N'):
                self.Py -= 1
            elif (move == 'E'):
                self.Px += 1
            elif (move == 'S'):
                self.Py += 1
            elif (move == 'W'):
                self.Px -= 1
            self.score -= 1      # score - 1 when pacman moves
            
            if self.map[self.Py][self.Px] == '.':
                self.food -= 1
                self.map[self.Py][self.Px] = ' '
                self.score += 10     # score + 10 when pacman eats food
        else:       # ghost is making a move
            if (move == 'N'):
                self.ghosts[player][0] -= 1
            elif (move == 'E'):
                self.ghosts[player][1] += 1
            elif (move == 'S'):
                self.ghosts[player][0] += 1
            elif (move == 'W'):
                self.ghosts[player][1] -= 1
        
        # check game end conditions
        if [self.Py, self.Px] in self.ghosts.values():   # check if ghost catches pacman
            self.score -= 500
            self.winner = "Ghost"
            self.hasEnded = True
        elif self.food == 0:    # check if pacman has eaten all food
            self.score += 500
            self.winner = "Pacman"
            self.hasEnded = True

def minmax(gamestate, depth, playerIdx, order):
    if depth == 0 or gamestate.hasEnded:   # check if is terminal node
        return gamestate.utility, None
    
    optMove = None
    player = order[playerIdx]
    choices = gamestate.validMoves(player)

    if player == 'P':       # maximizer
        utility = float('-inf')
        for move in choices:
            next_gamestate = copy.deepcopy(gamestate)
            next_gamestate.makeMove(player, move)
            next_gamestate.getUtility()
            next_utility, placeholder = minmax(next_gamestate, depth - 1, (playerIdx + 1) % len(order), order)
            if next_utility > utility:  # better move found for pacman
                utility = next_utility
                optMove = move 
    else:                   # minimizer
        utility = float('inf')
        for move in choices:
            next_gamestate = copy.deepcopy(gamestate)
            next_gamestate.makeMove(player, move)
            next_gamestate.getUtility()
            next_utility, placeholder = minmax(next_gamestate, depth - 1, (playerIdx + 1) % len(order), order)
            if next_utility < utility:  # better move found for ghost
                utility = next_utility
                optMove = move
    
    return utility, optMove

def formatMap(map, Py, Px, ghosts):     # format game board to solution
    temp_map = copy.deepcopy(map)
    temp_map[Py][Px] = 'P'
    for each in ghosts:
        temp_map[ghosts[each][0]][ghosts[each][1]] = each
    lines = [''.join(row) for row in temp_map]
    s = '\n'.join(lines)
    s += '\n'
    print(s)
    return s

def min_max_mulitple_ghosts(problem, k):
    seed = int(problem[0])
    gamestate = Gamestate(problem[1], problem[2], problem[3], problem[4], problem[5])
    playerNum = len(problem[4]) + 1
    turn = 1
    depth = k * playerNum

    solution = f"seed: {seed}\n0\n"
    solution += formatMap(gamestate.map, gamestate.Py, gamestate.Px, gamestate.ghosts)

    # player moving = order[turn % playerNum]
    if playerNum == 2:
        order = {0:'W', 1:'P'}
    elif playerNum == 3:
        order = {0:'X', 1:'P', 2:'W'}
    elif playerNum == 4:
        order = {0:'Y', 1:'P', 2:'W', 3:'X'}
    elif playerNum == 5:
        order = {0:'Z', 1:'P', 2:'W', 3:'X', 4:'Y'}

    while not gamestate.hasEnded:
        player = order[turn % playerNum]    # player that is going to make a move
        move = minmax(gamestate, k, turn % playerNum, order)[1]

        gamestate.makeMove(player, move)

        solution += f"{turn}: {player} moving {move}\n"
        solution += formatMap(gamestate.map, gamestate.Py, gamestate.Px, gamestate.ghosts)
        solution += f"score: {gamestate.score}\n"
        turn += 1

    return solution, gamestate.winner

if __name__ == "__main__":
    test_case_id = int(sys.argv[1])    
    problem_id = 5
    file_name_problem = str(test_case_id)+'.prob' 
    file_name_sol = str(test_case_id)+'.sol'
    path = os.path.join('test_cases','p'+str(problem_id)) 
    problem = parse.read_layout_problem(os.path.join(path,file_name_problem))
    k = int(sys.argv[2])
    num_trials = int(sys.argv[3])
    verbose = bool(int(sys.argv[4]))
    print('test_case_id:',test_case_id)
    print('k:',k)
    print('num_trials:',num_trials)
    print('verbose:',verbose)
    start = time.time()
    win_count = 0
    for i in range(num_trials):
        solution, winner = min_max_mulitple_ghosts(copy.deepcopy(problem), k)
        if winner == 'Pacman':
            win_count += 1
        if verbose:
            print(solution)
    win_p = win_count/num_trials * 100
    end = time.time()
    print('time: ',end - start)
    print('win %',win_p)