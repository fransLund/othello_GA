import pygame
import random
import copy
from constants import *

pygame.init()

font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)  # För större sluttext


screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Othello')

# Define constants and variables
markers = []
clicked = False
pos = []
player = 1
game_over = False  # För att hantera slutet av spelet
winner_text = ""  # Variabel för att lagra vinnartexten
show_no_moves_message = False
shouldShowNoMovesMessage = False
message_start_time = 0

# Draw the grid
def draw_grid():
    bg = (43, 143, 95)
    grid = (36, 24, 7)
    screen.fill(bg)

    for x in range(1, tiles):
        pygame.draw.line(screen, grid, (0, x * tile_width), (800, x * tile_width), line_width)
        pygame.draw.line(screen, grid, (x * tile_width, 0), (x * tile_width, 800), line_width)

# Initialize the board
for x in range(tiles):
    row = [0] * tiles
    markers.append(row)

# Draw starting markers
def draw_startmarkers():
    markers[4][4] = -1
    markers[3][3] = -1
    markers[3][4] = 1
    markers[4][3] = 1

# Draw markers on the board
def draw_markers():
    for x in range(tiles):
        for y in range(tiles):
            if markers[x][y] == 1:
                pygame.draw.circle(screen, white, (x * 100 + 50, y * 100 + 50), 38)
            elif markers[x][y] == -1:
                pygame.draw.circle(screen, black, (x * 100 + 50, y * 100 + 50), 38)

def get_all_legal_moves(board, player):
    legal_moves = []
    for x in range(tiles):
        for y in range(tiles):
            if is_legal_move(board, x, y, player):
                legal_moves.append([x, y])

    return legal_moves

# Visar legal moves
def show_legal_moves(board, player):
    legal_moves = get_all_legal_moves(board, player)
    for legal_move in legal_moves:
        x, y = legal_move
        pygame.draw.circle(screen, gray, (x * 100 + 50, y * 100 + 50), 38, 4)

# Check which pieces to flip in a specific direction
def pieces_to_flip(board, x, y, dx, dy, player):
    x += dx
    y += dy
    pieces = []

    while 0 <= x < tiles and 0 <= y < tiles:
        if board[x][y] == 0:
            return []
        if board[x][y] == player:
            return pieces

        pieces.append((x, y))
        x += dx
        y += dy

    return []

# Check if the move is legal
def is_legal_move(board, x, y, player):
    try:
        if board[x][y] != 0:
            return False

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
        for dx, dy in directions:
            if pieces_to_flip(board, x, y, dx, dy, player):
                return True
        return False
    except:
        return False

# Flip pieces after a valid move
def flip_pieces(board, x, y, player):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]

    for dx, dy in directions:
        pieces = pieces_to_flip(board, x, y, dx, dy, player)
        for px, py in pieces:
            board[px][py] = player

# Function to count white, black, and total pieces
def count_pieces(board):
    white_count = 0
    black_count = 0

    for row in board:
        white_count += row.count(1)
        black_count += row.count(-1)

    total_pieces = white_count + black_count
    return white_count, black_count, total_pieces

def get_player_color(player):
    return "Vit" if player == 1 else "Svart"

# Function to display information about the game
def display_info(player):
    pygame.draw.rect(screen, white, (800, 0, 200, screen_height))

    player_color = get_player_color(player)
    white_count, black_count, total_pieces = count_pieces(markers)

    player_text = font.render(f"Tur: {player_color}", True, black)
    white_text = font.render(f"Vita: {white_count}", True, black)
    black_text = font.render(f"Svarta: {black_count}", True, black)
    total_text = font.render(f"Totalt: {total_pieces}", True, black)

    screen.blit(player_text, (820, 50))
    screen.blit(white_text, (820, 100))
    screen.blit(black_text, (820, 150))
    screen.blit(total_text, (820, 200))



def count_gamePieces(board, player):
    white_count, black_count, total_pieces = count_pieces(board)
    return black_count if player == -1 else white_count

def calculate_options(board, player):
    legal_moves = get_all_legal_moves(board, player)
    return len(legal_moves)

def positional_score(board, player):
    opponent = -player
    score = 0
    for row in range(tiles):
        for col in range(tiles):
            if board[row][col] == player:
                score += weights[row][col]
            elif board[row][col] == opponent:
                score -= weights[row][col]
    return score

def evaluate(board, player):
    opponent = -player
    disc_difference = count_gamePieces(board, player) - count_gamePieces(board, opponent)
    mobility = calculate_options(board, player) - calculate_options(board, opponent)
    position = positional_score(board, player)

    #print(f'{(10 * disc_difference) + (5 * mobility) + (2 * position)}, {disc_difference=}, {mobility=}, {position=}')
    # Tune weights based on importance

    #print(f'{get_all_legal_moves(board, player)=}')

    return (10 * disc_difference) + (5 * mobility) + (2 * position)

def is_terminal(board):
    # Check if either player has legal moves
    if has_legal_moves(board, 1) or has_legal_moves(board, -1):
        return False

    # Check if the board is full
    for row in board:
        if 0 in row:
            return False

    return True


def best_move(player):
    board_copy = copy.deepcopy(markers)
    legal_moves = get_all_legal_moves(board_copy, player)
    best_value = -float('inf') if player == -1 else float('inf')
    best_move = None

    alpha = -float('inf')
    beta = float('inf')

    for move in legal_moves:
        board_before_move = copy.deepcopy(board_copy)
        x, y = move
        board_copy[x][y] = player
        flip_pieces(board_copy, x, y, player)

        board_value = minimax(board_copy, depth=3, isMaximizingPlayer=(player == -1), player=-player, alpha=alpha, beta=beta)
        board_copy = copy.deepcopy(board_before_move)  # Undo move

        if (player == -1 and board_value > best_value) or (player == 1 and board_value < best_value):
            best_value = board_value
            best_move = move

    return best_move


    

        


def minimax(board, depth, isMaximizingPlayer, player, alpha, beta):
    if depth == 0 or is_terminal(board):  # Terminal condition
        return evaluate(board, player)

    if isMaximizingPlayer:
        best_value = -float('inf')
        for move in get_all_legal_moves(board, player):  # Generate possible moves
            board_before_move = copy.deepcopy(board)
            x, y = move
            board[x][y] = player
            flip_pieces(board, x, y, player)

            value = minimax(board, depth - 1, False, -player, alpha, beta)

            best_value = max(best_value, value)
            alpha = max(alpha, best_value)

            #print(f'{alpha=}, {beta=}')

            # Undo the move
            board = copy.deepcopy(board_before_move)

            # Prune the branch
            if beta <= alpha:
                break

        return best_value

    else:
        best_value = float('inf')
        for move in get_all_legal_moves(board, player):  # Generate possible moves
            board_before_move = copy.deepcopy(board)
            x, y = move
            board[x][y] = player
            flip_pieces(board, x, y, player)

            value = minimax(board, depth - 1, True, -player, alpha, beta)

            best_value = min(best_value, value)
            beta = min(beta, best_value)

            # Undo the move
            board = copy.deepcopy(board_before_move)

            # Prune the branch
            if beta <= alpha:
                break

        return best_value



def black_player_move():
    global player, shouldShowNoMovesMessage
    move = best_move(player)

    print(f'{move=}')

    if move:
        x, y = move
        markers[x][y] = player
        flip_pieces(markers, x, y, player)
        player *= -1
    else:
        if not has_legal_moves(markers, player):
            check_game_over(markers)
            if not game_over:
                shouldShowNoMovesMessage = True



# Show the winner with a large text in the center of the board
def show_winner():
    text_surface = large_font.render(winner_text, True, white)
    text_rect = text_surface.get_rect(center=(400, 400))  # Center på spelbrädet

    pygame.draw.rect(screen, black, text_rect.inflate(20, 20))  # Bakgrundsram
    screen.blit(text_surface, text_rect)
    pygame.display.update()

# Check if the game is over
def check_game_over(board):
    global game_over, winner_text
    white_count, black_count, _ = count_pieces(board)

    if all(not has_legal_moves(board, p) for p in [1, -1]):
        game_over = True
        if white_count > black_count:
            winner_text = "Vit vinner!"
        elif black_count > white_count:
            winner_text = "Svart vinner!"
        else:
            winner_text = "Oavgjort!"

# Check if a player has valid moves
def has_legal_moves(board, player):
    legal_moves = get_all_legal_moves(board, player)
    return len(legal_moves) > 0

# Start the game
def start_game():
    draw_startmarkers()

start_game()
run = True
while run:
    draw_grid()
    draw_markers()
    show_legal_moves(markers, player)
    display_info(player)

    if not show_no_moves_message and shouldShowNoMovesMessage:
        show_no_moves_message = True
        message_start_time = pygame.time.get_ticks()

    if show_no_moves_message:
        player_color = get_player_color(player)
        text_surface = large_font.render(f"Spelare {player_color} har inga drag", True, white)
        text_rect = text_surface.get_rect(center=(400, 400))  # Center på spelbrädet

        pygame.draw.rect(screen, black, text_rect.inflate(20, 20))  # Bakgrundsram
        screen.blit(text_surface, text_rect)

        # Check if three seconds have passed.
        if pygame.time.get_ticks() - message_start_time > 3000:
            shouldShowNoMovesMessage = False
            show_no_moves_message = False
            player *= -1

    if not game_over:
        if player == -1:
            black_player_move()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN and not clicked:
                    clicked = True
                if event.type == pygame.MOUSEBUTTONUP and clicked:
                    clicked = False
                    pos = pygame.mouse.get_pos() 
                    cell_x = pos[0] // 100
                    cell_y = pos[1] // 100

                    if is_legal_move(markers, cell_x, cell_y, player):
                        markers[cell_x][cell_y] = player
                        flip_pieces(markers, cell_x, cell_y, player)
                        player *= -1

            if not has_legal_moves(markers, player):
                check_game_over(markers)
                if not game_over and not shouldShowNoMovesMessage:
                    shouldShowNoMovesMessage = True

    else:
        show_winner()  # Visa vinnaren kontinuerligt tills spelaren stänger spelet

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

    pygame.display.update()

pygame.quit()