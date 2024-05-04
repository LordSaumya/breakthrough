from turtle_oxford import *
import copy
import random

# Class for breakthrough utils
class utils:
    ROW, COL = 6, 6 # Board size
    INF: int = 999999999 # Represents infinity
    WIN: int = 99999999 # Represents evaluation for win

    Move = tuple[tuple[int, int], tuple[int, int]] # Move is a tuple of two tuples
    Board = list[list[str]] # Board is a 2D list-of-lists
    Score = int # Score is an integer

    # initial state
    initial_state = [
            list("BBBBBB"),
            list("BBBBBB"),
            list("______"),
            list("______"),
            list("WWWWWW"),
            list("WWWWWW"),
        ]

    # inverts board by modifying board state, or returning a new board with updated board state
    def invert_board(board: Board) -> Board:
        board.reverse()
        for r, row in enumerate(board):
            for c, tile in enumerate(row):
                if tile == "W":
                    board[r][c] = "B"
                elif tile == "B":
                    board[r][c] = "W"
        return board

    # checks if a move is valid. 
    # Move source: src (row, col), move destination: dst (row, col)
    def is_valid_move(
            board: Board,
            src: tuple[int, int],
            dst: tuple[int, int]
        ) -> bool:
        sr, sc = src
        dr, dc = dst
        if board[sr][sc] != "B": 
            # if move not made for black
            return False
        if dr < 0 or dr >= utils.ROW or dc < 0 or dc >= utils.COL: 
            # if move takes pawn outside the board
            return False
        if dr != sr + 1: 
            # if move takes more than one step forward
            return False
        if dc > sc + 1 or dc < sc - 1: 
            # if move takes beyond left/right diagonal
            return False
        if dc == sc and board[dr][dc] != "_": 
            # if pawn to the front, but still move forward
            return False
        if (dc == sc + 1 or dc == sc - 1) and board[dr][dc] == "B": 
            # if black pawn to the diagonal or front, but still move forward
            return False
        return True

    # generates a random move
    def generate_rand_move(board: Board) -> Move:
        valid_moves = utils.generate_valid_moves(board)
        return valid_moves[random.randint(0, len(valid_moves) - 1)]
                        
    # changes board state by making a move from src to dst
    def state_change(
            board: Board,
            src: tuple[int, int],
            dst: tuple[int, int],
        ) -> Board:
        
        board = copy.deepcopy(board)
        if utils.is_valid_move(board, src, dst):
            sr, sc = src
            dr, dc = dst
            board[sr][sc] = "_"
            board[dr][dc] = "B"
        return board

    # checks if game is over
    def is_game_over(board: Board) -> bool:
        if any(tile == "B" for tile in board[5]) or any(tile == "W" for tile in board[0]):
            return True
        wcount, bcount = 0, 0
        for row in board:
            for tile in row:
                if tile == "B":
                    bcount += 1
                elif tile == "W":
                    wcount += 1
        return bcount == 0 or wcount == 0
    
    # evaluates board state
    def evaluate(board: Board) -> Score:
        # The evaluation score is the difference between the number of black pawns and white pawns
        # If black pawns reach the last row, black wins (return WIN)
        # If white pawns reach the last row, white wins (return -WIN)
        # If no pawns of a colour are left, the other colour wins
        bcount = 0
        wcount = 0
        for r, row in enumerate(board):
            for tile in row:
                if tile == "B":
                    if r == 5:
                        return utils.WIN
                    bcount += 1
                elif tile == "W":
                    if r == 0:
                        return -utils.WIN
                    wcount += 1
        if wcount == 0:
            return utils.WIN
        if bcount == 0:
            return -utils.WIN
        return bcount - wcount
    
    # generates valid moves from a board state
    def generate_valid_moves(board: Board) -> list[Move]:
        moves: list[utils.Move] = []
        for row_num, row in enumerate(board):
            for col_num, tile in enumerate(row):
                if tile == "B":
                    possible_moves: list[tuple[int, int]] = [(row_num + 1, col_num - 1), (row_num + 1, col_num), (row_num + 1, col_num + 1)]
                    moves += [((row_num, col_num), (nr, nc)) for nr, nc in possible_moves if utils.is_valid_move(board, (row_num, col_num), (nr, nc))]
        return moves

    # negamax algorithm with alpha-beta pruning
    def negamax_alpha_beta(
        board: Board, 
        depth: int,
        max_depth: int,
        alpha: Score,
        beta: Score
    ) -> tuple[Score, Move]:
        
        # value function to calculate the value of a board state
        def value(board: utils.Board, depth: int, max_depth: int, alpha: utils.Score, beta: utils.Score
                  ) -> tuple[utils.Score, utils.Move]:
            
            # For terminal state, return the evaluation of the board state
            if depth == max_depth or utils.is_game_over(board):
                return utils.evaluate(board), None

            # Initialise best move and value
            v_curr: utils.Score = -utils.INF
            best_move: utils.Move = None

            # For each valid move, calculate the value of the next state
            for next_move in utils.generate_valid_moves(board):
                next_state: utils.Board = utils.state_change(board, next_move[0], next_move[1])
                next_state = utils.invert_board(next_state)
                # Negate the score as the next player is the opponent
                score, _ = value(next_state, depth + 1, max_depth, -beta, -alpha)
                score = -score
                if score > v_curr:
                    v_curr = score
                    best_move = next_move
                if v_curr >= beta:
                    # If the value is greater than or equal to beta, return the value and best move
                    return v_curr, best_move
                alpha = max(alpha, v_curr)
            return v_curr, best_move
            
        v, best_move = value(board, depth, max_depth, alpha, beta)
        return v, best_move

with turtle_canvas(600,600) as t:

    # Parameters
    canvas(0, 0, 1200, 1200)
    board_size: int = 1200
    num_squares: int = 6
    square_size = board_size // num_squares

    eval_depth: int = 3

    # Types are "AI" or "Random"
    white_type: str = "AI"
    black_type: str = "AI"

    # Utility & Drawing Functions
    square_to_coords = lambda square: (square[1] * square_size + square_size // 2, board_size - square[0] * square_size - square_size // 2)
    squares_inverted = lambda square: (5 - square[0], 5 - square[1])

    def erase_square(square: tuple[int, int]):
        noupdate()
        colour("white")
        x, y  = square_to_coords(square)
        setxy(x, y)
        blot(70)
        update()

    def draw_pawn(square: tuple[int, int], colour_set: str = "B"):
        square_size: int = board_size // num_squares
        noupdate()
        erase_square(square)
        x, y = square_to_coords(square)
        setxy(x, y)

        # Draw the pawn
        if colour_set == "B":
            colour("black")
        elif colour_set == "W":
            colour("white")
        else:
            return
        blot(50)
        colour("black")
        circle(50)
        update()

    def draw_squares():
        square_size: int = board_size // num_squares
        noupdate()
        colour("black")
        # Draw horizontal lines
        for i in range(num_squares + 1):
            y = board_size - i * square_size
            setxy(0, y)
            drawxy(board_size, 0)

        # Draw vertical lines
        for i in range(num_squares + 1):
            x = i * square_size
            setxy(x, 0)
            drawxy(0, board_size)
        update()
        

    def draw_board(board: utils.Board):
        noupdate()
        colour("white")
        blot(5000)
        draw_squares()
        for r, row in enumerate(board):
            for c, tile in enumerate(row):
                if tile == "B":
                    draw_pawn((r, c), "B")
                elif tile == "W":
                    draw_pawn((r, c), "W")
        update()
    
    def draw_move(board: utils.Board, src: tuple[int, int], dst: tuple[int, int], colour_set: str = "B"):
        # red dot at source and destination
        colour("red")
        if colour_set == "W":
            x_src, _ = square_to_coords(src)
            x_dst, _ = square_to_coords(dst)
            _ , y_src = square_to_coords(squares_inverted(src))
            _ , y_dst = square_to_coords(squares_inverted(dst))
        else:
            x_src, y_src = square_to_coords(src)
            x_dst, y_dst = square_to_coords(dst)
        setxy(x_src, y_src)
        blot(10)
        pause(150)
        setxy(x_dst, y_dst)
        blot(20)
    

    # Main Game Loop
    def play():
        print("Starting game:")
        print("Black: ", black_type)
        print("White: ", white_type)
        print("*************************")
        winner = False
        # Set board to initial state
        board = utils.initial_state
        draw_board(board)
        play_colour = "B"

        # Game Loop
        while not utils.is_game_over(board):
            # Make a move based on the type of player
            if play_colour == "B":
                if black_type == "Random":
                    src, dst = utils.generate_rand_move(board)
                else:
                    src, dst = utils.negamax_alpha_beta(board, 0, eval_depth, -utils.INF, utils.INF)[1]
                print("Black's move: ", src , " -> ", dst, "\n evaluation score: ", utils.evaluate(board))
                # Change board state and play colour
                board = utils.state_change(board, src, dst)
                play_colour = "W"
                draw_board(board)
                draw_move(board, src, dst, "B")
            else:
                # Invert board before using the same algorithm for white
                board = utils.invert_board(board)
                if white_type == "Random":
                    src, dst = utils.generate_rand_move(board)
                else:
                    src, dst = utils.negamax_alpha_beta(board, 0, eval_depth, -utils.INF, utils.INF)[1]
                board = utils.state_change(board, src, dst)
                print("White's move: ", src , " -> ", dst, "\n evaluation score: ", utils.evaluate(board))
                play_colour = "B"
                board = utils.invert_board(board)
                draw_board(board)
                draw_move(board, src, dst, "W")
                winner = True
            pause(500)
        setxy(250, 250)
        display("White Wins!" if winner else "Black Wins!", size = 50)
        print("White Wins!" if winner else "Black Wins!")
    play()