import pygame as pg
from components import *
from varname import nameof
from time import time
from random import randint
import os

from constants import *
from utility import *
import algorithms

pg.init()

FPS = 60
INF = float('inf')
EXIT_AND_STATS = pg.USEREVENT + 1
EXIT_BUTTON = Button(WIDTH - 105, 15, 90, 35, RED, "EXIT", WHITE)

# Optional
NODES = 0
TIMES_TAKEN = []
TOTAL_NODES = []
START_TIME = 0
PROGRAM_TIME = 0
MUTARI = [0, 0]


WIN = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Ducal Nicolae, Hex Game")
BACKGROUND = pg.transform.scale(pg.image.load(
    os.path.join('assets', 'nude_background.png')), (WIDTH, HEIGHT))
TITLE_FONT = pg.font.SysFont('comicsans', 80)
NORMAL_FONT = pg.font.SysFont('comicsans', 40)
SMALL_FONT = pg.font.SysFont('comicsans', 15)

# DATELE JOCULUI
SIZE = [None, None]
NEXT_MENU = False
GAME = None
PLAYER_TURN = None
PLAY_GAME = False
WINNER = None


def update_game_window(hovered, mouse_click, game_mode):
    global PLAYER_TURN
    WIN.blit(BACKGROUND, (0, 0))

    GAME.draw(WIN, hovered)
    # Al cui move este acum:
    player_name = get_player_name(
        game_mode, PLAYER_TURN, Game.MIN_PLAYER, Game.MAX_PLAYER)
    next_move_text = NORMAL_FONT.render(player_name + "'s Turn", True, BLACK)
    WIN.blit(next_move_text, (10, HEIGHT - next_move_text.get_height() - 10))
    # Exit button:
    EXIT_BUTTON.draw(WIN)
    if mouse_click != None and EXIT_BUTTON.select_button(mouse_click):
        pg.event.post(pg.event.Event(EXIT_AND_STATS))
    pg.display.update()


def update_final_window(winner, mouse_click, game_mode):
    WIN.blit(BACKGROUND, (0, 0))

    path = GAME.game.final_path(winner)
    GAME.draw(WIN, None, path)
    # Cine a castigat
    player_name = get_player_name(
        game_mode, winner, Game.MIN_PLAYER, Game.MAX_PLAYER).upper()
    next_move_text = TITLE_FONT.render(player_name + " WINS", True, BLACK)
    WIN.blit(next_move_text, (10, HEIGHT - next_move_text.get_height() - 10))
    # Exit button:
    EXIT_BUTTON.draw(WIN)
    if mouse_click != None and EXIT_BUTTON.select_button(mouse_click):
        pg.event.post(pg.event.Event(EXIT_AND_STATS))
    pg.display.update()


def update_first_menu_window(size_buttons, size_text_boxes, mode_buttons, next_button, mouse_click):
    global SIZE, NEXT_MENU
    WIN.blit(BACKGROUND, (0, 0))
    title_text = TITLE_FONT.render("HEX GAME", True, BLACK)
    WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 70))

    if mouse_click != None:
        size_buttons.select_button(mouse_click)
        mode_buttons.select_button(mouse_click)

    size_buttons.draw(WIN)
    mode_buttons.draw(WIN)

    if size_buttons.selected_button != None:
        dim = size_buttons.selected_button + 3
        SIZE = [dim, dim] if dim < 12 else SIZE

    CUSTOM_SIZE_SEL = size_buttons.selected_button == len(
        size_buttons.button_list) - 1
    if CUSTOM_SIZE_SEL:
        for sztb in size_text_boxes:
            sztb.draw(WIN)
        aux_text = NORMAL_FONT.render("x", True, BLACK)
        WIN.blit(aux_text, (WIDTH // 2 - aux_text.get_width() // 2, 305))
        help_text = SMALL_FONT.render(
            "(Dimensiunile tablei pot varia intre 3 si 11 pentru randuri si coloane. Pentru a confirma selectia, tastati ENTER cand e selectat textbox-ul)", True, BLACK)
        WIN.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, 345))

    # Verificare daca corespund size-urile cu cele din textbox-uri
    GOOD_CUSTOM = CUSTOM_SIZE_SEL and ([str(SIZE[0]), str(SIZE[1])] == [
                                       size_text_boxes[0].text, size_text_boxes[1].text])
    if None not in SIZE and (CUSTOM_SIZE_SEL == GOOD_CUSTOM) and size_buttons.selected_button != None and mode_buttons.selected_button != None:
        next_button.draw(WIN)
        if mouse_click != None and next_button.select_button(mouse_click):
            NEXT_MENU = True
    pg.display.update()


def update_second_menu_window(algorithm_buttons, difficulty_buttons, game_mode, player1_buttons, player2_buttons, next_button, mouse_click):
    global PLAY_GAME
    WIN.blit(BACKGROUND, (0, 0))
    title_text = TITLE_FONT.render("HEX GAME", True, BLACK)
    WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 70))

    if mouse_click != None:
        if game_mode != "pvp":
            algorithm_buttons.select_button(mouse_click)
            difficulty_buttons.select_button(mouse_click)
        player1_buttons.select_button(mouse_click)
        player2_buttons.select_button(mouse_click)

    if game_mode != "pvp":
        algorithm_buttons.draw(WIN)
        difficulty_buttons.draw(WIN)

    nu_afisa = player2_buttons.selected_button
    player1_buttons.draw(WIN, nu_afisa)
    nu_afisa = player1_buttons.selected_button
    player2_buttons.draw(WIN, nu_afisa)

    if ((game_mode != "pvp" and algorithm_buttons.selected_button != None and difficulty_buttons.selected_button != None) or game_mode == "pvp") and player1_buttons.selected_button != None and player2_buttons.selected_button != None:
        next_button.draw(WIN)
        if mouse_click != None and next_button.select_button(mouse_click):
            PLAY_GAME = True
    pg.display.update()


def menu_gui():
    global GAME, PLAY_GAME, NEXT_MENU
    run = True
    mouse_click = None

    # PRIMUL MENIU DE SELECTII
    size_buttons = ButtonGroup(
        WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT, "Selectati dimensiunea tablei", [(f"{i}x{i}", BLACK, WHITE) for i in range(3, 12)] + [("Custom", BLACK, WHITE)], 5)
    size_text_boxes = [
        TextBox(WIDTH // 2 - TEXT_BOX_WIDTH - 15, 300), TextBox(WIDTH // 2 + 15, 300)]
    mode_buttons = ButtonGroup(WIDTH // 2, 460, 180, BUTTON_HEIGHT, "Selectati regimul de joc", [("Player vs Player", RED, WHITE), (
        "Player vs Computer (Easy)", ORANGE, BLACK), ("Player vs Computer (Hard)", YELLOW, BLACK), ("Computer vs Computer", BLUE, WHITE)], 4)
    next_button = Button(WIDTH // 2 - BUTTON_WIDTH // 2, 650, BUTTON_WIDTH,
                         BUTTON_HEIGHT, BLACK, "NEXT", WHITE)
    clock = pg.time.Clock()
    while run:
        clock.tick(FPS)
        if NEXT_MENU:
            run = False
            break
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                break
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_click = pg.mouse.get_pos()

            for idx, sztb in enumerate(size_text_boxes):
                val = sztb.handle_event(event)
                if val != None:
                    SIZE[idx] = val
        update_first_menu_window(
            size_buttons, size_text_boxes, mode_buttons, next_button, mouse_click)
        mouse_click = None

    if NEXT_MENU:
        game_mode = GAME_MODE[mode_buttons.selected_button]
        heuristic = 1 if mode_buttons.selected_button == 1 else (
            2 if mode_buttons.selected_button == 2 else None)
        n, m = SIZE
    else:
        pg.quit()
        return

    # AL DOILEA MENIU DE SELECTII
    run = True
    algorithm_buttons = ButtonGroup(WIDTH // 2, 220, BUTTON_WIDTH, BUTTON_HEIGHT, "Selectati algoritmul", [
        ("Minimax", BLUE, WHITE), ("Alpha-Beta", RED, WHITE)])
    difficulty_buttons = ButtonGroup(WIDTH // 2, 360, BUTTON_WIDTH, BUTTON_HEIGHT, "Selectati dificultatea", [
        ("Incepator", RED, WHITE), ("Mediu", YELLOW, BLACK), ("Avansat", BLUE, WHITE)])
    player1_buttons = ButtonGroup(WIDTH // 3, 500 if game_mode != "pvp" else 350, BUTTON_WIDTH, BUTTON_HEIGHT, "Player 1" if game_mode == "pvp" else("Player" if game_mode != "cvc" else "Computer 1"), [
        (nameof(BLUE), BLUE, WHITE), (nameof(ORANGE), ORANGE, BLACK), (nameof(RED), RED, WHITE), (nameof(YELLOW), YELLOW, BLACK), (nameof(PINK), PINK, BLACK), (nameof(GREEN), GREEN, WHITE)])
    player2_buttons = ButtonGroup(2 * WIDTH // 3, 500 if game_mode != "pvp" else 350, BUTTON_WIDTH, BUTTON_HEIGHT, "Player 2" if game_mode == "pvp" else ("Computer" if game_mode == "pvc" else "Computer 2"), [
        (nameof(BLUE), BLUE, WHITE), (nameof(ORANGE), ORANGE, BLACK), (nameof(RED), RED, WHITE), (nameof(YELLOW), YELLOW, BLACK), (nameof(PINK), PINK, BLACK), (nameof(GREEN), GREEN, WHITE)])
    next_button = Button(WIDTH // 2 - BUTTON_WIDTH // 2, 650, BUTTON_WIDTH,
                         BUTTON_HEIGHT, BLACK, "PLAY", WHITE)
    clock = pg.time.Clock()
    while run:
        clock.tick(FPS)
        if PLAY_GAME:
            run = False
            break
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                break
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_click = pg.mouse.get_pos()
        update_second_menu_window(algorithm_buttons, difficulty_buttons, game_mode, player1_buttons,
                                  player2_buttons, next_button, mouse_click)
        mouse_click = None
    if PLAY_GAME:
        selected_algo, difficulty = None, None
        if game_mode != "pvp":
            selected_algo = "minimax" if algorithm_buttons.selected_button == 0 else "alphabeta"
            difficulty = difficulty_buttons.button_list[difficulty_buttons.selected_button].text
        # Initiala culorii jucatorului 1
        min_player = player1_buttons.button_list[player1_buttons.selected_button].text[0]
        # Initiala culorii jucatorului 2
        max_player = player2_buttons.button_list[player2_buttons.selected_button].text[0]
        game_gui(n, m, min_player, max_player, game_mode,
                 heuristic, selected_algo, difficulty)
    else:
        pg.quit()


def game_gui(n, m, min_player, max_player, game_mode, heuristic, algo, difficulty):
    global GAME, PLAYER_TURN, WINNER, START_TIME, PROGRAM_TIME, MUTARI, TIMES_TAKEN, TOTAL_NODES
    run = True
    mouse_click = None
    mouse_hover = None
    selected = None
    hovered = None
    if game_mode != "pvp":
        depth = DEPTHS[difficulty]
    clock = pg.time.Clock()

    HEXAGONS, GAME_STATE = create_hexagons(
        n, m, INITIAL_CENTER)
    Game.initialize_game(n, m, min_player, max_player)
    GAME = HexGame(Game(GAME_STATE), HEXAGONS)
    PLAYER_TURN = Game.MIN_PLAYER
    GAME.game.console_show()
    PROGRAM_TIME = time()
    START_TIME = time()
    while run:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                break
            if event.type == EXIT_AND_STATS:
                show_stats(game_mode, time() - START_TIME,
                           TIMES_TAKEN, TOTAL_NODES, MUTARI)
                run = False
                break
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_click = pg.mouse.get_pos()
            if event.type == pg.MOUSEMOTION:
                mouse_hover = pg.mouse.get_pos()
        # PLAYER VERSUS COMPUTER
        if game_mode == "pvc" and not WINNER and run:
            if PLAYER_TURN == Game.MIN_PLAYER:
                is_hover = False
                for i in range(Game.ROWS):
                    for j in range(Game.COLS):
                        if mouse_click != None and GAME.hexagons[i][j].check_inside(Point(mouse_click[0], mouse_click[1])):
                            selected = i, j, RED
                        elif mouse_hover != None and GAME.hexagons[i][j].check_inside(Point(mouse_hover[0], mouse_hover[1])):
                            hovered = i, j, DARK_GRAY
                            is_hover = True
                if not is_hover or (selected != None and hovered != None and selected[:2] == hovered[:2]):
                    hovered = None
                # Selectam, daca a fost ales un hexagon de catre utilizator
                if selected != None:
                    i, j = selected[:2]
                    if GAME.select_hexagon((i, j), PLAYER_TURN):
                        GAME.game.select_position((i, j), PLAYER_TURN)
                        print("Good choice")
                        GAME.game.console_show()
                        show_user_stats("Player", time() - START_TIME)
                        MUTARI[0] += 1
                        PLAYER_TURN = Game.MIN_PLAYER if PLAYER_TURN == Game.MAX_PLAYER else Game.MAX_PLAYER
                    else:
                        print("Already selected")
            else:
                START_TIME = time()
                if algo == "minimax":
                    next_table = algorithms.min_max(
                        State(deepcopy(GAME.game), Game.MAX_PLAYER, depth), heuristic)
                else:
                    next_table = algorithms.alpha_beta(-INF, INF,
                                                       State(deepcopy(GAME.game), Game.MAX_PLAYER, depth), heuristic)
                time_taken = time() - START_TIME
                GAME.game = next_table.next_state.game
                # print(GAME.new_hexagon())
                GAME.select_hexagon(GAME.new_hexagon(), PLAYER_TURN)
                print("Computer has played it's move:")
                GAME.game.console_show()
                TOTAL_NODES.append(algorithms.NODES)
                TIMES_TAKEN.append(time_taken)
                MUTARI[1] += 1
                show_computer_stats("Computer",
                                    time_taken, algorithms.NODES, next_table.scor)
                algorithms.NODES = 0
                PLAYER_TURN = Game.MIN_PLAYER
                START_TIME = time()
        # PLAYER VERSUS PLAYER
        elif game_mode == "pvp" and not WINNER and run:
            if WINNER:
                continue
            is_hover = False
            for i in range(Game.ROWS):
                for j in range(Game.COLS):
                    if mouse_click != None and GAME.hexagons[i][j].check_inside(Point(mouse_click[0], mouse_click[1])):
                        selected = i, j, RED
                    elif mouse_hover != None and GAME.hexagons[i][j].check_inside(Point(mouse_hover[0], mouse_hover[1])):
                        hovered = i, j, DARK_GRAY
                        is_hover = True
            if not is_hover or (selected != None and hovered != None and selected[:2] == hovered[:2]):
                hovered = None
            # Selectam, daca a fost ales un hexagon de catre utilizator
            if selected != None:
                i, j = selected[:2]
                if GAME.select_hexagon((i, j), PLAYER_TURN):
                    GAME.game.select_position((i, j), PLAYER_TURN)
                    print("Good choice")
                    GAME.game.console_show()
                    show_user_stats(
                        f"Player {1 if PLAYER_TURN == Game.MIN_PLAYER else 2}", time() - START_TIME)
                    MUTARI[0 if Game.MIN_PLAYER == PLAYER_TURN else 1] += 1
                    PLAYER_TURN = Game.MIN_PLAYER if PLAYER_TURN == Game.MAX_PLAYER else Game.MAX_PLAYER
                else:
                    print("Already selected")
        # COMPUTER VS COMPUTER
        elif game_mode == "cvc" and not WINNER and run:
            START_TIME = time()
            heuristic = 1 if PLAYER_TURN == Game.MIN_PLAYER else 2
            if sum(MUTARI) == 0:  # Prima mutare o facem random (pentru diversitatea jocului)
                i, j = randint(0, Game.ROWS - 1), randint(0, Game.COLS - 1)
                GAME.game.select_position((i, j), PLAYER_TURN)
            else:
                if algo == "minimax":
                    next_table = algorithms.min_max(
                        State(deepcopy(GAME.game), PLAYER_TURN, depth), heuristic)
                else:
                    next_table = algorithms.alpha_beta(-INF, INF, State(
                        deepcopy(GAME.game), PLAYER_TURN, depth), heuristic)
                GAME.game = next_table.next_state.game

            time_taken = time() - START_TIME
            GAME.select_hexagon(GAME.new_hexagon(), PLAYER_TURN)
            print(f"Computer {heuristic} has played it's move:")
            GAME.game.console_show()
            TOTAL_NODES.append(algorithms.NODES)
            TIMES_TAKEN.append(time_taken)
            player_name = f"Computer {heuristic}"
            if sum(MUTARI) != 0:
                show_computer_stats(player_name,
                                    time_taken, algorithms.NODES, next_table.scor)
            MUTARI[heuristic - 1] += 1
            algorithms.NODES = 0
            PLAYER_TURN = GAME.game.oponent(PLAYER_TURN)

        # Daca am castigat, afisam asta
        WINNER = GAME.game.final() if not WINNER else WINNER
        if not WINNER:
            update_game_window(hovered, mouse_click, game_mode)
        else:
            program_time_taken = time() - PROGRAM_TIME
            show_stats(game_mode, program_time_taken,
                       TIMES_TAKEN, TOTAL_NODES, MUTARI)
            game_mode = "pvc"
            PLAYER_TURN = Game.MIN_PLAYER  # Sa avem acces la mouse
            update_final_window(WINNER, mouse_click, game_mode)

        # Anulam selectia anterioara
        selected = None
        mouse_click = None
    pg.quit()
