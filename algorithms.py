from components import *

NODES = 0


def min_max(stare: State, heuristic: int):
    global NODES
    NODES += 1
    is_final = stare.game.final()
    if stare.depth == 0 or is_final:
        stare.scor = stare.game.estimeaza_scor(
            stare.depth, is_final, stare.current_player, heuristic)
        return stare
    # Calculez toate mutarile posibile din starea curenta
    stare.mutari_posibile = stare.mutari()

    # Aplic algoritmul minimax pe toate mutarile posibile (calculand astfel subarborii lor)
    mutari_scor = [min_max(x, heuristic) for x in
                   stare.mutari_posibile]  # Expandez(constr subarb) fiecare nod x din mutari posibile

    if stare.current_player == Game.MAX_PLAYER:
        # Daca jucatorul e JMAX aleg starea-fiica cu scorul maxim
        stare.next_state = max(mutari_scor, key=lambda x: x.scor)
    else:
        # Daca jucatorul e JMIN aleg starea-fiica cu scorul minim
        stare.next_state = min(mutari_scor, key=lambda x: x.scor)

    stare.scor = stare.next_state.scor
    return stare


def alpha_beta(alpha: int, beta: int, stare: State, heuristic: int):
    global NODES
    NODES += 1
    is_final = stare.game.final()
    if stare.depth == 0 or is_final:
        stare.scor = stare.game.estimeaza_scor(
            stare.depth, is_final, stare.current_player, heuristic)
        return stare

    if alpha > beta:
        return stare  # Este intr-un interval invalid deci nu o mai procesez

    stare.mutari_posibile = stare.mutari()

    if stare.current_player == Game.MAX_PLAYER:
        scor_curent = float('-inf')
        for mutare in stare.mutari_posibile:
            # Calculeaza scorul
            # Aici construim subarborele pentru stare_noua
            stare_noua = alpha_beta(alpha, beta, mutare, heuristic)

            if (scor_curent < stare_noua.scor):
                stare.next_state = stare_noua
                scor_curent = stare_noua.scor
            if (alpha < stare_noua.scor):
                alpha = stare_noua.scor
                if alpha >= beta:
                    break
    elif stare.current_player == Game.MIN_PLAYER:
        scor_curent = float('inf')
        for mutare in stare.mutari_posibile:
            # Calculeaza scorul
            # Aici construim subarborele pentru stare_noua
            stare_noua = alpha_beta(alpha, beta, mutare, heuristic)

            if (scor_curent > stare_noua.scor):
                stare.next_state = stare_noua
                scor_curent = stare_noua.scor
            if (beta > stare_noua.scor):
                beta = stare_noua.scor
                if alpha >= beta:
                    break

    stare.scor = stare.next_state.scor
    return stare
