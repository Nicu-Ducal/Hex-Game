from constants import *
from components import *
from math import pi, cos, sin, sqrt, floor

show_once = 1


def create_hexagons(n, m, INITIAL_POINT):
    HEXAGONS = [[] for _ in range(n)]
    GAME_STATE = [[] for _ in range(n)]
    RADIUS = INITIAL_RADIUS - 4 * max(n, m)
    HEX_HEIGHT = floor(RADIUS * sqrt(3) / 2)
    grid_width = ((n - 1) + 2 * (m - 1)) * HEX_HEIGHT
    grid_height = (n - 1) * 3 * RADIUS // 2

    cur_x, cur_y = INITIAL_POINT[0] // 2 - \
        grid_width // 2, INITIAL_POINT[1] // 2 - grid_height // 2
    HEXAGONS = [[] for _ in range(n)]
    for i in range(n):
        if i > 0:
            cur_x = HEXAGONS[i - 1][0].x + HEX_HEIGHT
        for j in range(m):
            HEXAGONS[i].append(Hexagon(Point(cur_x, cur_y), RADIUS))
            GAME_STATE[i].append(Game.EMPTY)
            cur_x += 2 * HEX_HEIGHT
        cur_y += 3 * RADIUS / 2
    return HEXAGONS, GAME_STATE


def get_player_name(game_mode, turn, minplayer, maxplayer):
    if game_mode == "pvp":
        return "Player 1" if turn == minplayer else "Player 2"
    elif game_mode == "pvc":
        return "Player" if turn == minplayer else "Computer"
    return "Computer 1" if turn == minplayer else "Computer 2"


def show_computer_stats(name, time, nodes, score):
    print(
        f"{name}'s Stats:\nTime taken: {round(time, 3)} sec\nNoduri calculate: {nodes}\nEstimarea avantajului pentru {name}: {score}\n")


def show_user_stats(name, time):
    print(f"{name}'s Stats:\nTime taken: {round(time, 3)}\n")


def show_stats(game_mode, prog_time, times, nodes, moves):
    global show_once
    if not show_once:
        return
    show_once -= 1
    print(f"Statistica jocului:\nRegimul jocului: " + "Player vs Player" if game_mode ==
          "pvp" else ("Player vs Computer" if game_mode == "pvc" else "Computer vs Computer"))
    if times != []:
        print(f"Timpul total de rulare a programului: {round(prog_time, 3)}")
        print(
            f"Timpul maxim de gandire al calculatorului: {round(max(times), 3)}\nTimpul minim de gandire al calculatorului: {round(min(times), 3)}")
        print(
            f"Timpul mediu de gandire: {round(mean(times), 3)}\nMediana timpului: {round(median(times), 3)}")
    if nodes != []:
        print(f"Numarul de noduri generate: {sum(nodes)}")
        print(
            f"Numarul maxim de noduri generate: {max(nodes)}\nNumarul minim de noduri generate: {min(nodes)}")
        print(
            f"Numarul mediu de noduri: {round(mean(nodes))}\nMediana numarului de noduri: {round(median(nodes))}")
    players = ["Player 1" if game_mode == "pvp" else("Player" if game_mode != "cvc" else "Computer 1"), "Player 2" if game_mode == "pvp" else(
        "Computer" if game_mode != "cvc" else "Computer 2")]
    print(
        f"Numarul de mutari al {players[0]}: {moves[0]}\nNumarul de mutari al {players[1]}: {moves[1]}")


def mean(array):
    return sum(array) / len(array)


def median(array):
    if len(array) % 2 == 1:
        return array[len(array) // 2]
    return (array[len(array) // 2] + array[(len(array) + 1) // 2]) / 2
