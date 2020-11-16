def MCTS_agent(observation, configuration):
    """
    Connect X agent based on MCTS.
    """
    import random
    import math
    import time
    global current_state  # so tree can be recycled

    init_time = time.time()
    EMPTY = 0
    T_max = configuration.timeout - 0.35  # time per move, left some overhead
    Cp_default = 1
#     DEBUG = False  # DEBUG

    def play(board, column, mark, config):
        columns = config.columns
        rows = config.rows
        row = max([r for r in range(rows) if board[column + (r * columns)] == EMPTY])
        board[column + (row * columns)] = mark

    def is_win(board, column, mark, config, has_played=True):
        columns = config.columns
        rows = config.rows
        inarow = config.inarow - 1
        row = (
            min([r for r in range(rows) if board[column + (r * columns)] == mark])
            if has_played
            else max([r for r in range(rows) if board[column + (r * columns)] == EMPTY])
        )

        def count(offset_row, offset_column):
            for i in range(1, inarow + 1):
                r = row + offset_row * i
                c = column + offset_column * i
                if (
                        r < 0
                        or r >= rows
                        or c < 0
                        or c >= columns
                        or board[c + (r * columns)] != mark
                ):
                    return i - 1
            return inarow

        return (
                count(1, 0) >= inarow  # vertical.
                or (count(0, 1) + count(0, -1)) >= inarow  # horizontal.
                or (count(-1, -1) + count(1, 1)) >= inarow  # top left diagonal.
                or (count(-1, 1) + count(1, -1)) >= inarow  # top right diagonal.
        )

    def is_tie(board):
        return all(mark != EMPTY for mark in board)

    def check_finish_and_score(board, column, mark, config):
        if is_win(board, column, mark, config, has_played=True):
            return (True, 1)
        if is_tie(board):
            return (True, 0.5)
        else:
            return (False, None)

    def uct_score(node_total_score, node_total_visits, parent_total_visits, Cp=Cp_default):
        if node_total_visits == 0:
            return math.inf
        return node_total_score / node_total_visits + Cp * math.sqrt(
            2 * math.log(parent_total_visits) / node_total_visits)

    def opponent_mark(mark):
        return 3 - mark

    def opponent_score(score):
        return 1 - score

    def random_action(board, config):
        return random.choice([c for c in range(config.columns) if board[c] == EMPTY])

#     def print_board(board, config):  # DEBUG
#         import numpy as np
#         print(np.reshape(board, [config.rows, config.columns]))

    def default_policy_simulation(board, mark, config):
        """
        Run a random play simulation. Starting state is assumed to be a non-terminal state.
        """
        original_mark = mark
        board = board.copy()
        column = random_action(board, config)
        play(board, column, mark, config)
        # print_board(board, config)  # DEBUG
        is_finish, score = check_finish_and_score(board, column, mark, config)
        while not is_finish:
            mark = opponent_mark(mark)
            column = random_action(board, config)
            play(board, column, mark, config)
            # print_board(board, config)  # DEBUG
            is_finish, score = check_finish_and_score(board, column, mark, config)
        if mark == original_mark:
            return score
        return opponent_score(score)
    
    def find_action_taken_by_opponent(new_board, old_board, config):
        for i, piece in enumerate(new_board):
            if piece != old_board[i]:
                return i % config.columns
        return -1

    class State():
        def __init__(self, board, mark, config, parent=None, is_terminal=False, terminal_score=None, action_taken=None):
            self.board = board.copy()
            self.mark = mark
            self.config = config
            self.children = []
            self.parent = parent
            self.node_total_score = 0
            self.node_total_visits = 0
            self.available_moves = [c for c in range(config.columns) if board[c] == EMPTY]
            self.expandable_moves = self.available_moves.copy()
            self.is_terminal = is_terminal
            self.terminal_score = terminal_score
            self.action_taken = action_taken

        def is_expandable(self):
            return (not self.is_terminal) and (len(self.expandable_moves) > 0)

        def expand_and_simulate_child(self):
            column = random.choice(self.expandable_moves)
            child_board = self.board.copy()
            play(child_board, column, self.mark, self.config)
            is_terminal, terminal_score = check_finish_and_score(child_board, column, self.mark, self.config)
            self.children.append(State(child_board, opponent_mark(self.mark),
                                       self.config, parent=self,
                                       is_terminal=is_terminal,
                                       terminal_score=terminal_score,
                                       action_taken=column
                                       ))
            simulation_score = self.children[-1].simulate()
            self.children[-1].backpropagate(simulation_score)
            self.expandable_moves.remove(column)

        def choose_strongest_child(self, Cp):
            """
            Cp=1 will choose best UCB1 child, Cp=0 will choose best exploit child (to play).
            """
            children_scores = [uct_score(child.node_total_score,
                                         child.node_total_visits,
                                         self.node_total_visits,
                                         Cp) for child in self.children]
            max_score = max(children_scores)
            best_child_index = children_scores.index(max_score)
            return self.children[best_child_index]
            
        def choose_play_child(self):
            children_scores = [child.node_total_score for child in self.children]
            max_score = max(children_scores)
            best_child_index = children_scores.index(max_score)
            return self.children[best_child_index]

        def tree_single_run(self):
            if self.is_terminal:
                self.backpropagate(self.terminal_score)
                return
            if self.is_expandable():
                self.expand_and_simulate_child()
                return
            self.choose_strongest_child(Cp_default).tree_single_run()

        def simulate(self):
            if self.is_terminal:
                # print_board(self.board, self.config)  # DEBUG
                return self.terminal_score
            return opponent_score(default_policy_simulation(self.board, self.mark, self.config))

        def backpropagate(self, simulation_score):
            self.node_total_score += simulation_score
            self.node_total_visits += 1
            if self.parent is not None:
                self.parent.backpropagate(opponent_score(simulation_score))
                
        def choose_child_via_action(self, action):
            for child in self.children:
                if child.action_taken == action:
                    return child
            return None

    board = observation.board
    mark = observation.mark
    try:  # if current_state already exists
        current_state = current_state.choose_child_via_action(
            find_action_taken_by_opponent(board, current_state.board, configuration))
        current_state.parent = None  # make current_state the root node and dereference siblings
        
    except:
        current_state = State(board, mark,  # This state is considered after the opponent's move
                              configuration, parent=None, is_terminal=False, terminal_score=None, action_taken=None)
   
    while time.time() - init_time <= T_max: # or DEBUG  # DEBUG
        current_state.tree_single_run()
        
    current_state = current_state.choose_play_child()
    current_state.parent = None  # make current_state the root node and dereference siblings
    return current_state.action_taken
