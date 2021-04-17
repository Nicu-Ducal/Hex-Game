import pygame as pg
from math import sin, cos, ceil, pi
from queue import Queue
from heapq import heapify, heappush, heappop
# from fibheap import *
from copy import deepcopy
from time import time

from constants import *
pg.font.init()

BUTTON_FONT = pg.font.SysFont('comicsans', 20)
TEXT_FONT = pg.font.SysFont('comicsans', 40)


# UI COMPONENTS
class Button:
    def __init__(self, x, y, width, height, color, text, font_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        # self.font_size = font_size
        self.font_color = font_color
        self.selected = False
        self.rect = pg.Rect(x, y, width, height)

    def draw(self, window):
        text_font = BUTTON_FONT.render(
            self.text, True, self.font_color if not self.selected else BLACK)
        pg.draw.rect(
            window, self.color if not self.selected else DARK_GRAY, self.rect)
        window.blit(text_font, (self.x + (self.width - text_font.get_width()
                                          ) // 2, self.y + self.height // 2 - text_font.get_height() // 2))

    def select_button(self, coord):
        if self.rect.collidepoint(coord):
            self.selected = True
            return True
        return False


class ButtonGroup:
    ROW_SPACE = 15
    COL_SPACE = 15

    @classmethod
    def create_buttons(self, x, y, width, height, lista, per_row):
        res = []
        next_x, next_y = x, y
        for (i, (text, col_but, col_font)) in enumerate(lista):
            res.append(Button(next_x, next_y, width,
                       height, col_but, text, col_font))
            if i % per_row == per_row - 1:
                next_x, next_y = x, next_y + height + ButtonGroup.COL_SPACE
            else:
                next_x += width + ButtonGroup.ROW_SPACE
        return res

    def __init__(self, x, y, width, height, text, lista_texte, per_row=3):
        self.selected = None
        self.total_width = min(
            per_row, len(lista_texte)) * (width + ButtonGroup.ROW_SPACE) - ButtonGroup.ROW_SPACE
        self.total_height = ceil(len(lista_texte) / per_row) * \
            (height + ButtonGroup.COL_SPACE) - ButtonGroup.COL_SPACE
        self.x = x - self.total_width // 2
        self.y = y
        self.text = text
        self.per_row = per_row
        self.button_list = ButtonGroup.create_buttons(
            self.x, self.y, width, height, lista_texte, per_row)
        self.selected_button = None

    def select_button(self, coord):
        for idx, buttton in enumerate(self.button_list):
            if buttton.select_button(coord):
                if self.selected_button is not None:
                    self.button_list[self.selected_button].selected = False
                self.selected_button = idx
                return True
        return False

    def draw(self, window, other_selected=None):
        text_font = TEXT_FONT.render(self.text, True, BLACK)
        window.blit(text_font, (self.x + self.total_width // 2 - text_font.get_width() //
                    2, self.y - 2 * ButtonGroup.COL_SPACE - text_font.get_height() // 2))
        for idx, button in enumerate(self.button_list):
            if idx != other_selected:
                button.draw(window)


class TextBox:
    '''
    Clasa pentru TextBox-uri pentru GUI in Pygame. 
    Sursa: https://stackoverflow.com/questions/47491451/how-to-implement-two-input-boxes-in-pygame-without-having-to-repeat-code
    '''

    def __init__(self, x, y):
        self.font = TEXT_FONT
        self.input_box = pg.Rect(x, y, 100, 35)
        self.color_inactive = BLACK
        self.color_active = DARKER_GRAY
        self.color = BLACK
        self.text = ''
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.active = self.input_box.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    try:
                        dim = int(self.text)
                        if 3 <= dim <= 11:
                            return dim
                        raise Exception()
                    except ValueError:
                        self.text = ''
                        print(
                            "Dimensiunea nu poate contine alte caractere decat numerice")
                    except Exception:
                        self.text = ''
                        print("Dimensiunea trebuie sa fie un numar intre 3 si 11")
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if self.font.render(self.text + event.unicode, True, BLACK).get_width() + 10 < self.input_box.width:
                        self.text += event.unicode

    def draw(self, window, text_box_width=100):
        text_input = self.font.render(self.text, True, BLACK)
        # Fix the width
        self.input_box.width = text_box_width
        window.blit(text_input, (self.input_box.x + 5, self.input_box.y + 5))
        pg.draw.rect(window, self.color, self.input_box, 2)


# GEOMETRIC + UI COMPONENTS
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line:
    def __init__(self, p1, p2):
        self.x1 = p1.x
        self.y1 = p1.y
        self.x2 = p2.x
        self.y2 = p2.y


class Hexagon:
    # Numarul de laturi/puncte
    n = 6

    @classmethod
    def compute_points(self, center, radius):
        return [Point(center.x + radius * sin(2 * pi * i / Hexagon.n), center.y + radius * cos(2 * pi * i / Hexagon.n))
                for i in range(Hexagon.n)]

    @classmethod
    def compute_edges(self, points):
        lines = list(zip(points, points[1:] + points[:1]))
        return [Line(line[0], line[1]) for line in lines]

    def __init__(self, center, radius):
        self.x = center.x
        self.y = center.y
        self.radius = radius
        self.points = Hexagon.compute_points(center, radius)
        self.edges = Hexagon.compute_edges(self.points)
        self.selected = None

    def draw_laturi(self, window, color=BLACK, border_width=5):
        pg.draw.lines(window, color, True, [(p.x, p.y)
                      for p in self.points], border_width)

    def draw(self, window, color=LIGHT_GRAY):
        pg.draw.polygon(window, color, [(point.x, point.y)
                        for point in self.points])
        self.draw_laturi(window)

    def check_inside(self, point):
        """Metoda a clasei Hexagon care verifica daca un punct primit ca input se afla in interiorul hexagonului. Se efectuaza cu algorimtul "Ray casting algorithm".
        Algoritmul presupune calcularea numarului de muchii ale unui poligon (in cazul nostru hexagon) care se intersecteaza cu un ray (o semidreapta care porneste in punctul
        pentru care dorim sa verificam). Daca numarul de intersectari este impar sau punctul se afla pe o muchie, atunci punctul este considerat in interiorul poligornului, in
        caz contrar (daca numarul este par), atunci punctul este in exterior.

        Args:
            point (Point): Puncul pe care vrem sa aflam daca se afla in interiorul hexagonului

        Returns:
            bool: True daca punctul se afla in interiorul hexagonului, in caz contrar False
        """
        intersections = 0
        for line in self.edges:
            # Daca punctul nostru este in afara range-ului de y al muchiei, nu are sens sa o verificam, pentru ca sigur nu se va intersecta
            if not (min(line.y1, line.y2) <= point.y <= max(line.y1, line.y2)):
                continue
            # Daca muchia este verticala (o dreapta de ecuatie x = t), atunci verificam daca punctul se alfa inaintea muchiei (adica daca punct.x < muchie.x)
            if line.x1 == line.x2:
                if point.x <= line.x1:
                    intersections += 1
                continue
            # Daca avem o muchie oblica sau orizontala, aflam ecuatia acesteia
            a = (line.y2 - line.y1) / (line.x2 - line.x1)
            b = line.y1 - a * line.x1

            # Calculam x-ul punctului corespunzator lui punct.y pe linia noastra. Daca punctul se afla inaintea punctului de pe segment (punct.x < punct_muchie.x), atunci e inaintea acestuia
            x_line = (point.y - b) / a
            if point.x <= x_line:
                intersections += 1
        return intersections % 2 == 1


class HexGame:
    """
    Clasa care defineste un joc si contine si hexagoanele acestuia
    """

    def __init__(self, game, hexagons):
        self.game = game
        self.hexagons = hexagons

    def new_hexagon(self):
        for i in range(Game.ROWS):
            for j in range(Game.COLS):
                if self.game.game_state[i][j] != Game.EMPTY and self.game.game_state[i][j] != self.hexagons[i][j].selected:
                    return i, j

    def select_hexagon(self, selected, player):
        i, j = selected
        if self.hexagons[i][j].selected is None:
            self.hexagons[i][j].selected = player
            return True
        return False

    def draw(self, window, hovered, path=[]):
        for i in range(Game.ROWS):
            for j in range(Game.COLS):
                if self.hexagons[i][j].selected != None:
                    self.hexagons[i][j].draw(
                        window, INITIAL_TO_COLOR[self.hexagons[i][j].selected])
                    if (i, j) in path:
                        pg.draw.circle(
                            window, BLACK, (self.hexagons[i][j].x, self.hexagons[i][j].y), self.hexagons[i][j].radius - 20)
                elif hovered != None and i == hovered[0] and j == hovered[1]:
                    self.hexagons[i][j].draw(window, hovered[2])
                else:
                    self.hexagons[i][j].draw(window)


# ALGORITHM COMPONENTS
class Game:
    """
    Clasa care defineste tabla jocului curent
    """
    ROWS = None
    COLS = None
    MIN_PLAYER = None
    MAX_PLAYER = None
    EMPTY = '#'

    @classmethod
    def initialize_game(self, rows, cols, min_player, max_player):
        Game.ROWS = rows
        Game.COLS = cols
        Game.MIN_PLAYER = min_player
        Game.MAX_PLAYER = max_player

    def __init__(self, game_state):
        self.game_state = game_state

    def console_show(self):
        space = 0
        for i in range(Game.ROWS):
            print(" " * space, end="")
            for j in range(Game.COLS):
                print(self.game_state[i][j], end=" ")
                # print(
                #     Game.EMPTY if not self.hexagons[i][j].selected else self.hexagons[i][j].selected, end=" ")
            space += 1
            print()

    # Functie care determina daca e valida pozitia sau nu
    def is_valid(self, i, j):
        return (0 <= i < Game.ROWS and 0 <= j < Game.COLS)

    def final(self):
        # st = time()
        # Ideea: Verificare cu BFS
        q = Queue()
        # Vectori de directie
        dx = [0, 0, -1, 1, -1, 1]
        dy = [-1, 1, 0, 0, 1, -1]

        # Mai intai verificam pentru primul jucator luand toate nodurile de pe prima coloana (stanga) si daca ajungem intr-una din dreapta, atunci avem castig
        marked = [[False] * Game.COLS for _ in range(Game.ROWS)]
        for i in range(Game.ROWS):
            if self.game_state[i][0] == Game.MIN_PLAYER:
                q.put((i, 0))
                marked[i][0] = True
        while not q.empty():
            i, j = q.get()

            # Daca am ajuns pe partea dreapta a tablei:
            if j == Game.COLS - 1:
                return Game.MIN_PLAYER
            for k in range(6):
                if self.is_valid(i + dx[k], j + dy[k]) and self.game_state[i + dx[k]][j + dy[k]] == Game.MIN_PLAYER and not marked[i + dx[k]][j + dy[k]]:
                    q.put((i + dx[k], j + dy[k]))
                    marked[i + dx[k]][j + dy[k]] = True
        # Acelasi approach si pentru al doilea jucator, doar ca de sus in jos (primul rand spre ultimul rand)
        marked = [[False] * Game.COLS for _ in range(Game.ROWS)]
        for i in range(Game.COLS):
            if self.game_state[0][i] == Game.MAX_PLAYER:
                q.put((0, i))
                marked[0][i] = True
        while not q.empty():
            i, j = q.get()

            # Daca am ajuns pe partea de jos a tablei:
            if i == Game.ROWS - 1:
                return Game.MAX_PLAYER
            for k in range(6):
                if self.is_valid(i + dx[k], j + dy[k]) and self.game_state[i + dx[k]][j + dy[k]] == Game.MAX_PLAYER and not marked[i + dx[k]][j + dy[k]]:
                    q.put((i + dx[k], j + dy[k]))
                    marked[i + dx[k]][j + dy[k]] = True

        # Jocul Hex nu poate avea remiza, deci daca am ajuns aici nu e stare finala
        # print(time() - st)
        return False

    def final_path(self, player):
        path = []
        parent = [[None] * Game.COLS for _ in range(Game.ROWS)]
        q = Queue()

        dx = [0, 0, -1, 1, -1, 1]
        dy = [-1, 1, 0, 0, 1, -1]

        if player == Game.MIN_PLAYER:
            for i in range(Game.ROWS):
                if self.game_state[i][0] == Game.MIN_PLAYER:
                    q.put((i, 0))
                    parent[i][0] = -1
        else:
            for i in range(Game.COLS):
                if self.game_state[0][i] == Game.MAX_PLAYER:
                    q.put((0, i))
                    parent[0][i] = -1
        while not q.empty():
            i, j = q.get()

            # Daca am ajuns pe partea dreapta a tablei si suntem MIN:
            if (j == Game.COLS - 1 and player == Game.MIN_PLAYER) or (i == Game.ROWS - 1 and player == Game.MAX_PLAYER):
                path.append((i, j))
                break

            for k in range(6):
                if self.is_valid(i + dx[k], j + dy[k]) and self.game_state[i + dx[k]][j + dy[k]] == player and not parent[i + dx[k]][j + dy[k]]:
                    q.put((i + dx[k], j + dy[k]))
                    parent[i + dx[k]][j + dy[k]] = (i, j)

        cur_pos = path[0]
        while parent[cur_pos[0]][cur_pos[1]] != -1:
            cur_pos = parent[cur_pos[0]][cur_pos[1]]
            path.append(cur_pos)

        return path

    def select_position(self, pos, player):
        i, j = pos
        if self.game_state[i][j] == Game.EMPTY:
            self.game_state[i][j] = player

    # Hexagoanele din jurul unui hexagon dat
    def next_hexagons(self, pos):
        i, j = pos
        dx = [0, 0, -1, 1, -1, 1]
        dy = [-1, 1, 0, 0, 1, -1]

        next_to = []
        for k in range(6):
            if self.is_valid(i + dx[k], j + dy[k]):
                next_to.append((i + dx[k], j + dy[k]))
        return next_to

    # Determina puntile existente in tabla
    def bridges(self, pos):
        i, j = pos
        # Locurile unde ar fi potentiale bridge-uri
        dx = [-1, 1, 2, 1, -1, -2]
        dy = [-1, -2, -1, 1, 2, 1]
        # Locurile dintre ele
        bdx = [-1, 0, 1, 1, 0, -1]
        bdy = [0, -1, -1, 0, 1, 1]

        bridges = []
        intre_bridge = []
        for k in range(6):
            if self.is_valid(i + dx[k], j + dy[k]):
                bridges.append((i + dx[k], j + dy[k]))
                intre_bridge.append(
                    [(i + bdx[k], j + bdy[k]), (i + bdx[(k + 1) % 6], j + bdy[(k + 1) % 6])])
        return bridges, intre_bridge

    # Determina puntile dintre edge si celula curenta

    def bridges_with_edge(self, pos):
        i, j = pos
        # Determinam daca suntem pe penultima coloana
        bridge_to_edges = []
        if self.game_state[i][j] == Game.MIN_PLAYER:
            if j == 1:
                bridge_to_edges = [(i, 0), (min(Game.ROWS - 1, i + 1), 0)]
            elif j == Game.COLS - 2:
                bridge_to_edges = [(i, j + 1), (max(0, i - 1), j + 1)]
        elif self.game_state[i][j] == Game.MAX_PLAYER:
            if i == 1:
                bridge_to_edges = [(0, j), (0, min(Game.COLS - 1, j + 1))]
            elif i == Game.ROWS - 2:
                bridge_to_edges = [(i + 1, j), (i + 1, max(0, j - 1))]
        return bridge_to_edges

    # Toate mutarile posibile dintr-o stare
    def mutari(self, player):
        lista_mutari = []
        for i in range(Game.ROWS):
            for j in range(Game.COLS):
                if self.game_state[i][j] == '#':
                    # st = time()
                    new_game = Game(deepcopy(self.game_state))
                    new_game.select_position((i, j), player)
                    # print(time() - st)
                    lista_mutari.append(new_game)
        return lista_mutari

    # Computam doar mutarile logice care ne-ar interesa (aproape de hexagoanele noastre/ale oponentului/bridge-uri)
    def mutari_logice(self, player):
        lista_mutari = []
        marked = [[False] * Game.COLS for _ in range(Game.ROWS)]

        for i in range(Game.ROWS):
            for j in range(Game.COLS):
                if self.game_state[i][j] != Game.EMPTY:
                    if marked[i][j]:
                        continue
                    next_nodes = self.next_hexagons((i, j))
                    bridges, intre = self.bridges((i, j))
                    edges = self.bridges_with_edge((i, j))
                    next_nodes.extend(bridges)
                    next_nodes.extend(edges)
                    for x, y in next_nodes:
                        if not marked[x][y] and self.game_state[x][y] == Game.EMPTY:
                            marked[x][y] = True
                            new_game = Game(
                                deepcopy(self.game_state))
                            new_game.select_position((x, y), player)
                            lista_mutari.append(new_game)
        return lista_mutari

    def oponent(self, player):
        return Game.MAX_PLAYER if player == Game.MIN_PLAYER else Game.MIN_PLAYER

    # Euristica care calculeaza chestiile esentiale pentru noi (bridges, apropierea de randul/coloanele finale)
    def euristica_1(self, player, turn):
        marked = [[False] * Game.COLS for _ in range(Game.ROWS)]
        next_to_score = 0
        opponent_score = 0
        block_score = 0
        bridge_score = 0
        destroy_bridge_score = 0
        connect_bridge = 0
        edge_score = 0  # Maximum 10 si cred ca min -10 oare
        destroy_edge_score = 0
        connect_edge = 0

        for i in range(Game.ROWS):
            for j in range(Game.COLS):
                if self.game_state[i][j] == player:
                    marked[i][j] = True
                    # Check nearby
                    for x, y in self.next_hexagons((i, j)):
                        if self.game_state[x][y] == player:
                            next_to_score += 1
                        elif self.game_state[x][y] == self.oponent(player):
                            opponent_score += 1
                    if next_to_score > 3:
                        next_to_score = -4 if next_to_score == 4 else (
                            -8 if next_to_score == 5 else -11)
                    # Check if it blocks to left or right
                    if player == Game.MAX_PLAYER and ((j == 0 and (self.game_state[i][1] == self.oponent(player) or self.game_state[max(0, i - 1)][1] == self.oponent(player)))
                                                      or (j == Game.COLS - 1 and (self.game_state[i][j - 1] == self.oponent(player) or self.game_state[min(Game.ROWS - 1, i + 1)][j - 1] == self.oponent(player)))):
                        block_score += 1
                    # else:
                    #     next_to_score = 3 if next_to_score == 1 else (
                    #         5 if next_to_score == 2 else 7)
                    # Find bridges
                    bridges, intre_bridges = self.bridges((i, j))
                    for idx, pos in enumerate(bridges):
                        bi, bj = pos
                        if marked[bi][bj]:
                            continue
                        intre = intre_bridges[idx]
                        if self.game_state[bi][bj] == self.oponent(player):
                            destroy_bridge_score += 1
                        elif self.game_state[bi][bj] == self.game_state[i][j]:
                            pos1, pos2 = intre
                            hex_intre = [
                                self.game_state[pos1[0]][pos1[1]], self.game_state[pos2[0]][pos2[1]]]
                            # or player in hex_intre
                            if hex_intre == [Game.EMPTY, Game.EMPTY]:
                                bridge_score = min(bridge_score + 1, 5)
                            elif sorted(hex_intre) == sorted([player, self.oponent(player)]):
                                connect_bridge = min(5, connect_bridge + 1)
                    # Check for edges if it's near it
                    edges = self.bridges_with_edge((i, j))
                    if edges != []:
                        pos1, pos2 = edges
                        hex_edge = [self.game_state[pos1[0]][pos1[1]],
                                    self.game_state[pos2[0]][pos2[1]]]
                        if sorted(hex_edge) == sorted([player, self.oponent(player)]):
                            connect_edge = min(3, connect_edge + 1)
                        elif hex_edge == [self.oponent(player), self.oponent(player)]:
                            destroy_edge_score -= 1
                        elif edges == [Game.EMPTY, Game.EMPTY] or player in edges:
                            edge_score = min(
                                3, edge_score + 1)
        # print(f"bridge = {bridge_score}, edge = {edge_score}")
        return ((1 if turn == player else 0) + 50 * block_score + 15 * opponent_score + 10 * next_to_score + 5 * bridge_score + 3 * edge_score + 10 * connect_bridge + 7 * connect_edge + 10 * destroy_bridge_score + 5 * destroy_edge_score)

    def euristica_2(self, player, turn):
        scor_eur1 = self.euristica_1(player, turn)

        marked = [[None] * Game.COLS for _ in range(Game.ROWS)]
        de_examinat = []
        # Mai intai gasim nodurile noastre care sunt disjuncte, pentru ca astfel am gasi exact din ce noduri calculam distantele. Facem asta cu BFS sau DFS
        for i in range(Game.ROWS):
            for j in range(Game.COLS):
                if self.game_state[i][j] == player and not marked[i][j]:
                    de_examinat.append((i, j))
                    q = Queue()
                    q.put((i, j))
                    marked[i][j] = True
                    while not q.empty():
                        pos = q.get()

                        vecini = self.next_hexagons(pos)
                        for x, y in vecini:
                            if self.game_state[x][y] == player and not marked[x][y]:
                                marked[x][y] = True
                                q.put((x, y))
        # Ar trebui sa facem un algoritm de shortest path din fiecare clasa de hexagoane, precum A*, BFS, Dijskstra sau BellmanFord
        goal = INF
        for hex in de_examinat:
            heap = []
            # In python nu prea sunt cozi cu prioritate bune, asa ca voi folosi o clasa care ofera operatii de heap
            # Pentru un rezultat mai bun, putem folosi si un heap fibbonaci (pip install fibheap)
            heappush(heap, (0, hex))
            distance = [[INF] * Game.COLS for _ in range(Game.ROWS)]
            distance[hex[0]][hex[1]] = 0
            while len(heap) > 0:
                dist, pos = heappop(heap)
                i, j = pos
                if distance[i][j] < dist:
                    continue
                for x, y in self.next_hexagons(pos):
                    if self.game_state[x][y] == Game.EMPTY and distance[x][y] > distance[i][j] + 1:
                        distance[x][y] = distance[i][j] + 1
                        heappush(heap, (distance[x][y], (x, y)))
                    elif self.game_state[x][y] == player and distance[x][y] > distance[i][j]:
                        distance[x][y] = distance[i][j]
                        heappush(heap, (distance[x][y], (x, y)))
            # Verificam ce distante minime avem pe side-uri:
            min_1, min_2 = INF, INF
            if player == Game.MAX_PLAYER:
                # In cazul de max, trebuie sa verificam ce distanta minima este sus si jos
                for i in range(Game.COLS):
                    min_1 = min(min_1, distance[0][i])
                    min_2 = min(min_2, distance[Game.ROWS - 1][i])
            else:
                # In cazul de min, trebuie sa verificam ce distanta minima este la left si right
                for i in range(Game.ROWS):
                    min_1 = min(min_1, distance[i][0])
                    min_2 = min(min_2, distance[i][Game.COLS - 1])
            # Facem update la distanta daca e nevoie
            goal = min(goal, min_1 + min_2)

        # Euristica noastra va fi un % anumit din distanta minima si euristica 1
        # Pentru ca noi vrem sa minimizam cat mai mult drumul, dar sa avem un scor mai mare, scadem distanta drumului dintr-un numar care sigur nu va depasi distanta unui drum
        # De exemplu, 50 nu ar putea sa fie distanta unui drum intr-un moment de timp
        return 50 * (50 - goal) + 10 * scor_eur1

    def estimeaza_scor(self, depth, final_state, player_turn, heuristic=1):
        if final_state == Game.MIN_PLAYER:
            return -500000 - depth
        elif final_state == Game.MAX_PLAYER:
            return 500000 + depth
        # scor MAX - MIN
        if heuristic == 1:
            return self.euristica_1(Game.MAX_PLAYER, player_turn) - self.euristica_1(Game.MIN_PLAYER, player_turn)
        return self.euristica_2(Game.MAX_PLAYER, player_turn) - self.euristica_2(Game.MIN_PLAYER, player_turn)


class State:
    """
    Clasa folosita de catre algoritmii Minimax si ALfa-Beta
    """

    def __init__(self, game, current_player, depth, parinte=None, scor=None):
        self.game = game
        self.current_player = current_player

        # Adancimea in arborele de stari
        self.depth = depth

        # Scorul starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.scor = scor

        # Lista de mutari posibile din starea curenta
        self.mutari_posibile = []

        # Cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        self.next_state = None

    def jucator_opus(self):
        if self.current_player == Game.MIN_PLAYER:
            return Game.MAX_PLAYER
        else:
            return Game.MIN_PLAYER

    def mutari(self):
        l_mutari = self.game.mutari_logice(self.current_player)
        juc_opus = self.jucator_opus()
        l_stari_mutari = [
            State(mutare, juc_opus, self.depth - 1, parinte=self) for mutare in l_mutari]

        return l_stari_mutari

    def __str__(self):
        sir = str(self.next_state) + \
            "(Joc curent:" + self.current_player + ")\n"
        return sir
