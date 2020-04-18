import pygame as pg
import ui

# Dictionaries needed to better handle squares/columns
letter_dict = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8}
reverse_letter_dict = {1: "a", 2: "b", 3: "c", 4: "d", 5: "e", 6: "f", 7: "g", 8: "h"}
pos = pg.mouse.get_pos()
all_pieces = pg.sprite.Group()
white_pieces = pg.sprite.Group()
black_pieces = pg.sprite.Group()
captured = pg.sprite.Group()
clicked_squares = []
previous = ()
en_passant = ""
white_to_move = None
score_w = 0
score_b = 0


class Piece(pg.sprite.Sprite):
    def __init__(self, square, color, name):
        pg.sprite.Sprite.__init__(self)
        self.square = square
        self.color = color
        self.name = name
        self.clicked = False
        # convert_alpha(), to properly show transparent background
        self.img = pg.image.load("images/" + self.name + ".png").convert_alpha()
        self.has_moved = False

    def get_coord(self):
        # Returns a tuple of coordinates of a piece using its square (e.g. "e4")
        for square in ui.all_squares:
            if square.name == self.square:
                coord = square.x + 10, square.y + 10
                return coord

    def show_piece(self):
        coord = self.get_coord()
        # print("Piece placed at: " + str(coord))
        ui.window.blit(self.img, coord)

    def vertical(self, u):
        # if u > 0 --> Up from white perspective
        # move u squares vertically
        if self.color == "b":
            u *= -1
        # Can obviously only move between rows 1 to 8.
        if 0 < int(self.square[1:]) + u <= 8:
            return reverse_letter_dict[letter_dict[self.square[:1]]] + str(int(self.square[1:]) + u)

    def horizontal(self, v):
        # if v > 0 --> Going to the right from white's perspective/white at the bottom
        if self.color == "b":
            v *= -1
        if 0 < letter_dict[self.square[:1]] + v <= 8:
            return reverse_letter_dict[letter_dict[self.square[:1]] + v] + str(int(self.square[1:]))

    def diagonal_r(self, w):
        # Diagonal to the right (when going up)
        if self.color == "b":
            w *= -1
        if 0 < letter_dict[self.square[:1]] + w <= 8 and 0 < int(self.square[1:]) + w <= 8:
            return reverse_letter_dict[letter_dict[self.square[:1]] + w] + str(int(self.square[1:]) + w)

    def diagonal_l(self, w):
        if self.color == "b":
            w *= -1
        if 0 < letter_dict[self.square[:1]] - w <= 8 and 0 < int(self.square[1:]) + w <= 8:
            return reverse_letter_dict[letter_dict[self.square[:1]] - w] + str(int(self.square[1:]) + w)


def get_piece_color(square):
    for piece in all_pieces:
        if piece.square == square:
            return piece.color


def set_previous(piece, square1, square2):
    global previous
    previous = (piece, square1, square2)


class Pawn(Piece):
    def __init__(self, square, color, piece):
        super().__init__(square, color, piece)
        self.score = 1

    def possible_moves(self):
        possible_moves = {self.vertical(1), self.vertical(2), self.diagonal_l(1), self.diagonal_r(1)}
        return possible_moves

    def legal_moves(self):
        global en_passant
        # discard() --> no error or exception when element is not in set
        legal_moves = self.possible_moves().copy()
        # Pawns can move 2 squares if they are on their starting square
        if self.color == "w" and self.square[1:] != "2":
            legal_moves.discard(self.vertical(2))
        if self.color == "b" and self.square[1:] != "7":
            legal_moves.discard(self.vertical(2))
        # When their path is blocked they can't move
        if occupied(self.vertical(1)):
            legal_moves.discard(self.vertical(1))
            legal_moves.discard(self.vertical(2))
        if occupied(self.vertical(2)):
            legal_moves.discard(self.vertical(2))
        if occupied(self.diagonal_l(1)) is False or self.color == get_piece_color(self.diagonal_l(1)):
            legal_moves.discard(self.diagonal_l(1))
        if occupied(self.diagonal_r(1)) is False or self.color == get_piece_color(self.diagonal_r(1)):
            legal_moves.discard(self.diagonal_r(1))
        # Checking whether a previous move exists to determine whether en passant is available:
        if previous:
            if "Pawn" in str(previous[0]) and self.square[1:] == previous[2][1:]:
                if self.color == "w":
                    if previous[1][1:] == "7" and previous[2][1:] == "5":
                        # Columns müssen gleich +-1 sein bei +1 und weiß --> diag_r -1 u. weiß --> diag_l
                        if letter_dict[self.square[:1]] + 1 == letter_dict[previous[2][:1]]:
                            legal_moves.add(self.diagonal_r(1))
                            en_passant = self.diagonal_r(1)
                            # print("En passant available.")
                        if letter_dict[self.square[:1]] - 1 == letter_dict[previous[2][:1]]:
                            legal_moves.add(self.diagonal_l(1))
                            en_passant = self.diagonal_l(1)
                if self.color == "b":
                    if previous[1][1:] == "2" and previous[2][1:] == "4":
                        # Columns müssen gleich +-1 sein bei +1 und weiß --> diag_r -1 u. weiß --> diag_l
                        if letter_dict[self.square[:1]] + 1 == letter_dict[previous[2][:1]]:
                            legal_moves.add(self.diagonal_l(1))
                            en_passant = self.diagonal_l(1)
                        if letter_dict[self.square[:1]] - 1 == letter_dict[previous[2][:1]]:
                            legal_moves.add(self.diagonal_r(1))
                            en_passant = self.diagonal_r(1)
        return legal_moves

    def attacking(self):
        # Returns the string name of the squares this piece is attacking.
        w = 1
        if self.color == "b":
            w *= -1
        if 0 < letter_dict[self.square[:1]] + w <= 8 and 0 < int(self.square[1:]) + w <= 8:
            square1 = reverse_letter_dict[letter_dict[self.square[:1]] + w] + str(int(self.square[1:]) + w)
        else:
            square1 = None
        if 0 < letter_dict[self.square[:1]] - w <= 8 and 0 < int(self.square[1:]) + w <= 8:
            square2 = reverse_letter_dict[letter_dict[self.square[:1]] - w] + str(int(self.square[1:]) + w)
        else:
            square2 = None
        return {square1, square2}


class King(Piece):
    def __init__(self, square, color, piece):
        super().__init__(square, color, piece)
        self.score = 100

    def is_attacked(self):
        # Returns True when the king is in check --> This influences the possible moves overall
        if self.color == "w" and ui.square_by_name(self.square).attacked_by_black:
            return True
        elif self.color == "b" and ui.square_by_name(self.square).attacked_by_white:
            return True
        else:
            return False

    def castle_possible(self, side):
        # White king-side - "wks"
        if side == "wks":
            if self.color == "w" and self.has_moved is False:
                if self.square == "e1" and self.is_attacked() is False:
                    if ui.square_by_name("g1").attacked_by_black is False:
                        if get_piece("h1") is not None:
                            if get_piece("h1").has_moved is False and get_piece("h1").name == "wR":
                                if occupied("f1") is False and occupied("g1") is False:
                                    if get_piece("e1") is not None and get_piece("h1") is not None:
                                        if get_piece("e1").name == "wK" and get_piece("h1").name == "wR":
                                            # White kingside castle is added
                                            # available.append("wks")
                                            return True
            return False
        # White queen-side - "wqs"
        if side == "wqs":
            if self.color == "w" and self.has_moved is False:
                if ui.square_by_name("c1").attacked_by_black is False:
                    if get_piece("a1") is not None:
                        if get_piece("a1").has_moved is False and get_piece("a1").name == "wR":
                            # Add white queen side to castling rights
                            if occupied("b1") is False and occupied("c1") is False and occupied("d1") is False:
                                if get_piece("e1") is not None and get_piece("a1") is not None:
                                    if get_piece("e1").name == "wK" and get_piece("a1").name == "wR":
                                        # available.append("wqs")
                                        return True
            return False
        # Black king-side - "bks"
        if side == "bks":
            if self.color == "b" and self.has_moved is False:
                if self.square == "e8" and self.is_attacked() is False:
                    if ui.square_by_name("b8").attacked_by_white is False:
                        if get_piece("a8") is not None:
                            if get_piece("a8").has_moved is False and get_piece("a8").name == "bR":
                                if occupied("f8") is False and occupied("g8") is False:
                                    if get_piece("e8") is not None and get_piece("a8") is not None:
                                        if get_piece("e8").name == "bK" and get_piece("a8").name == "bR":
                                            # White kingside castle is added
                                            # available.append("bks")
                                            return True
                return False
        # Black queen-side - "bqs"
        if side == "bqs":
            if self.color == "b" and self.has_moved is False:
                if ui.square_by_name("f8").attacked_by_white is False:
                    if get_piece("h8") is not None:
                        if get_piece("h8").has_moved is False and get_piece("h8").name == "bR":
                            if occupied("b8") is False and occupied("c8") is False and occupied("d8") is False:
                                if get_piece("e8") is not None and get_piece("h8") is not None:
                                    if get_piece("e8").name == "bK" and get_piece("h8").name == "bR":
                                        # Add white queen side to castling rights
                                        # available.append("bqs")
                                        return True
                return False

    def possible_moves(self):
        possible_moves = {self.vertical(1), self.vertical(-1), self.horizontal(1), self.horizontal(-1),
                          self.diagonal_r(1), self.diagonal_r(-1), self.diagonal_l(1), self.diagonal_l(-1)}
        return possible_moves

    def legal_moves(self):
        possible = self.possible_moves()
        legal_moves = possible.copy()
        attackers = set()
        attackers.clear()
        for move in possible:
            if move is not None:
                square = ui.square_by_name(move)
                if self.color == "w":
                    for wp in white_pieces:
                        if move == wp.square:
                            legal_moves.discard(move)
                    # The king can't move into an attacked square i.e. put himself in check
                    for attacker in black_pieces:
                        if attacker.square in possible and self.square in attacker.legal_moves():
                            attackers.add(attacker)
                    for attacker in attackers:
                        if attacker.square in possible and ui.square_by_name(attacker.square).attacked_by_black:
                            legal_moves.discard(attacker.square)
                    if square.attacked_by_black:
                        legal_moves.discard(move)
                if self.color == "b":
                    for bp in black_pieces:
                        if move == bp.square:
                            legal_moves.discard(move)
                    for attacker in white_pieces:
                        if attacker.square in possible and self.square in attacker.legal_moves():
                            attackers.add(attacker)
                    for attacker in attackers:
                        if attacker.square in possible and ui.square_by_name(attacker.square).attacked_by_white:
                            legal_moves.discard(attacker.square)
                    if square.attacked_by_white:
                        legal_moves.discard(move)
        if self.castle_possible("wqs"):
            legal_moves.add(self.horizontal(-2))
        if self.castle_possible("wks"):
            legal_moves.add(self.horizontal(2))
        if self.castle_possible("bqs"):
            legal_moves.add(self.horizontal(2))
        if self.castle_possible("bks"):
            legal_moves.add(self.horizontal(-2))
        return legal_moves


class Queen(Piece):
    def __init__(self, square, color, piece):
        super().__init__(square, color, piece)
        self.score = 10

    def possible_moves(self):
        possible_moves = set()
        for i in range(1, 9):
            if occupied(self.vertical(i)):
                possible_moves.add(self.vertical(i))
                break
            else:
                possible_moves.add(self.vertical(i))
        for i in range(1, 9):
            if occupied(self.vertical(-i)):
                possible_moves.add(self.vertical(-i))
                break
            else:
                possible_moves.add(self.vertical(-i))
        for i in range(1, 9):
            if occupied(self.horizontal(i)):
                possible_moves.add(self.horizontal(i))
                break
            else:
                possible_moves.add(self.horizontal(i))
        for i in range(1, 9):
            if occupied(self.horizontal(-i)):
                possible_moves.add(self.horizontal(-i))
                break
            else:
                possible_moves.add(self.horizontal(-i))
        for i in range(1, 9):
            if occupied(self.diagonal_r(i)):
                possible_moves.add(self.diagonal_r(i))
                break
            else:
                possible_moves.add(self.diagonal_r(i))
        for i in range(1, 9):
            if occupied(self.diagonal_r(-i)):
                possible_moves.add(self.diagonal_r(-i))
                break
            else:
                possible_moves.add(self.diagonal_r(-i))
        for i in range(1, 9):
            if occupied(self.diagonal_l(i)):
                possible_moves.add(self.diagonal_l(i))
                break
            else:
                possible_moves.add(self.diagonal_l(i))
        for i in range(1, 9):
            if occupied(self.diagonal_l(-i)):
                possible_moves.add(self.diagonal_l(-i))
                break
            else:
                possible_moves.add(self.diagonal_l(-i))
        return possible_moves

    def legal_moves(self):
        legal_moves = self.possible_moves().copy()
        return legal_moves


class Rook(Piece):
    def __init__(self, square, color, piece):
        super().__init__(square, color, piece)
        self.score = 5

    def possible_moves(self):
        possible_moves = set()
        for i in range(1, 9):
            if occupied(self.vertical(i)):
                possible_moves.add(self.vertical(i))
                break
            else:
                possible_moves.add(self.vertical(i))
        for i in range(1, 9):
            if occupied(self.vertical(-i)):
                possible_moves.add(self.vertical(-i))
                break
            else:
                possible_moves.add(self.vertical(-i))
        for i in range(1, 9):
            if occupied(self.horizontal(i)):
                possible_moves.add(self.horizontal(i))
                break
            else:
                possible_moves.add(self.horizontal(i))
        for i in range(1, 9):
            if occupied(self.horizontal(-i)):
                possible_moves.add(self.horizontal(-i))
                break
            else:
                possible_moves.add(self.horizontal(-i))
        return possible_moves

    def legal_moves(self):
        legal_moves = self.possible_moves().copy()
        return legal_moves


class Knight(Piece):
    def __init__(self, square, color, piece):
        super().__init__(square, color, piece)
        self.score = 3

    def jump(self, move):
        # c - center, u - up, d - down, l - left, r - right
        # 1st available move is cur --> Clockwise
        w = 1
        if self.color == "b":
            w *= -1
        if move == 1:
            # cur
            if 0 < letter_dict[self.square[:1]] + w <= 8 and 0 < int(self.square[1:]) + 2*w <= 8:
                return reverse_letter_dict[letter_dict[self.square[:1]] + w] + str(int(self.square[1:]) + 2*w)
        if move == 2:
            # ru
            if 0 < letter_dict[self.square[:1]] + 2*w <= 8 and 0 < int(self.square[1:]) + w <= 8:
                return reverse_letter_dict[letter_dict[self.square[:1]] + 2*w] + str(int(self.square[1:]) + w)
        if move == 3:
            # rd
            if 0 < letter_dict[self.square[:1]] + 2*w <= 8 and 0 < int(self.square[1:]) - w <= 8:
                return reverse_letter_dict[letter_dict[self.square[:1]] + 2*w] + str(int(self.square[1:]) - w)
        if move == 4:
            # dr
            if 0 < letter_dict[self.square[:1]] + w <= 8 and 0 < int(self.square[1:]) - 2*w <= 8:
                return reverse_letter_dict[letter_dict[self.square[:1]] + w] + str(int(self.square[1:]) - 2*w)
        if move == 5:
            # dl
            if 0 < letter_dict[self.square[:1]] - w <= 8 and 0 < int(self.square[1:]) - 2*w <= 8:
                return reverse_letter_dict[letter_dict[self.square[:1]] - w] + str(int(self.square[1:]) - 2*w)
        if move == 6:
            # ld
            if 0 < letter_dict[self.square[:1]] - 2*w <= 8 and 0 < int(self.square[1:]) - w <= 8:
                return reverse_letter_dict[letter_dict[self.square[:1]] - 2*w] + str(int(self.square[1:]) - w)
        if move == 7:
            # lu
            if 0 < letter_dict[self.square[:1]] - 2*w <= 8 and 0 < int(self.square[1:]) + w <= 8:
                return reverse_letter_dict[letter_dict[self.square[:1]] - 2*w] + str(int(self.square[1:]) + w)
        if move == 8:
            # ul
            if 0 < letter_dict[self.square[:1]] - w <= 8 and 0 < int(self.square[1:]) + 2*w <= 8:
                return reverse_letter_dict[letter_dict[self.square[:1]] - w] + str(int(self.square[1:]) + 2*w)

    def possible_moves(self):
        possible_moves = set()
        for i in range(1,9):
            possible_moves.add(self.jump(i))
        return possible_moves

    def legal_moves(self):
        legal_moves = self.possible_moves().copy()
        return legal_moves


class Bishop(Piece):
    def __init__(self, square, color, piece):
        super().__init__(square, color, piece)
        self.score = 3

    def possible_moves(self):
        possible_moves = set()
        for i in range(1, 9):
            if occupied(self.diagonal_r(i)):
                possible_moves.add(self.diagonal_r(i))
                break
            else:
                possible_moves.add(self.diagonal_r(i))
        for i in range(1, 9):
            if occupied(self.diagonal_r(-i)):
                possible_moves.add(self.diagonal_r(-i))
                break
            else:
                possible_moves.add(self.diagonal_r(-i))
        for i in range(1, 9):
            if occupied(self.diagonal_l(i)):
                possible_moves.add(self.diagonal_l(i))
                break
            else:
                possible_moves.add(self.diagonal_l(i))
        for i in range(1, 9):
            if occupied(self.diagonal_l(-i)):
                possible_moves.add(self.diagonal_l(-i))
                break
            else:
                possible_moves.add(self.diagonal_l(-i))
        return possible_moves

    def legal_moves(self):
        legal_moves = self.possible_moves().copy()
        return legal_moves


def occupied(test_square):
    for piece in all_pieces:
        if str(test_square) == str(piece.square):
            return True
        else:
            continue
    return False


def setup_pieces():
    all_pieces.empty()
    white_pieces.empty()
    black_pieces.empty()
    wpawns = []
    # --> with list comprehension: my_calculator.buttons = [tkinter.Button(root, text=i) for i in range(10)]
    for i in range(1, 9):
        square = reverse_letter_dict[i] + "2"
        wpawns.append(Pawn(square, "w", "wP"))
        wpawns[i - 1].show_piece()
        all_pieces.add(wpawns[i - 1])
        white_pieces.add(wpawns[i - 1])
    bpawns = []
    for j in range(1, 9):
        square = reverse_letter_dict[j] + "7"
        bpawns.append(Pawn(square, "b", "bP"))
        bpawns[j - 1].show_piece()
        all_pieces.add(bpawns[j - 1])
        black_pieces.add(bpawns[j - 1])
    wK = King("e1", "w", "wK")
    wQ = Queen("d1", "w", "wQ")
    wR1 = Rook("a1", "w", "wR")
    wR2 = Rook("h1", "w", "wR")
    wKn1 = Knight("b1", "w", "wKn")
    wKn2 = Knight("g1", "w", "wKn")
    wB1 = Bishop("c1", "w", "wB")
    wB2 = Bishop("f1", "w", "wB")
    bK = King("e8", "b", "bK")
    bQ = Queen("d8", "b", "bQ")
    bR1 = Rook("a8", "b", "bR")
    bR2 = Rook("h8", "b", "bR")
    bKn1 = Knight("b8", "b", "bKn")
    bKn2 = Knight("g8", "b", "bKn")
    bB1 = Bishop("c8", "b", "bB")
    bB2 = Bishop("f8", "b", "bB")
    all_pieces.add(wK, wQ, wR1, wR2, wKn1, wKn2, wB1, wB2, bK, bQ, bR1, bR2, bKn1, bKn2, bB1, bB2)
    white_pieces.add(wK, wQ, wR1, wR2, wKn1, wKn2, wB1, wB2)
    black_pieces.add(bK, bQ, bR1, bR2, bKn1, bKn2, bB1, bB2)
    for piece in all_pieces:
        piece.show_piece()


def get_piece(square_in):
    for piece in all_pieces:
        if piece.square == square_in:
            return piece


def is_in_check(wtm_copy):
    # Checks whether the current player is in check - wtm copy = white_to_move boolean copy
    for wp in white_pieces:
        if "King" in str(wp):
            if wp.is_attacked() and wtm_copy:
                return True
    for bp in black_pieces:
        if "King" in str(bp):
            if bp.is_attacked() and not wtm_copy:
                return True
    return False


def refresh():
    for square in ui.all_squares:
        square.attacked_by_white = False
        square.attacked_by_black = False
    for wp in white_pieces:
        if "Pawn" not in str(wp):
            for move in wp.legal_moves():
                if move is not None:
                    ui.square_by_name(move).attacked_by_white = True
        else:
            # Pawns need a separate method for determining their attacked squares because they don't attack where
            # they move - they attack diagonally but move vertically.
            for move in wp.attacking():
                if move is not None:
                    square = ui.square_by_name(move)
                    square.attacked_by_white = True
    for bp in black_pieces:
        if "Pawn" not in str(bp):
            for move in bp.legal_moves():
                if move is not None:
                    ui.square_by_name(move).attacked_by_black = True
        else:
            for move in bp.attacking():
                if move is not None:
                    ui.square_by_name(move).attacked_by_black = True


# Promoting the pawn to a queen when it reaches the last row/rank
def promote(moving_piece):
    if "Pawn" in str(moving_piece) and not is_in_check(white_to_move):
        if moving_piece.color == "w" and clicked_squares[1][1:] == "8":
            all_pieces.remove(moving_piece)
            white_pieces.remove(moving_piece)
            moving_piece = Queen(clicked_squares[1], "w", "wQ")
            white_pieces.add(moving_piece)
            all_pieces.add(moving_piece)
        if moving_piece.color == "b" and clicked_squares[1][1:] == "1":
            all_pieces.remove(moving_piece)
            black_pieces.remove(moving_piece)
            moving_piece = Queen(clicked_squares[1], "b", "bQ")
            black_pieces.add(moving_piece)
            all_pieces.add(moving_piece)


def move(position):
    global white_to_move
    global score_w
    global score_b
    refresh()
    wtm_copy = white_to_move
    square_name = ui.square_by_pos(position)
    square = ui.square_by_name(square_name)
    for piece in captured:
        captured.remove(piece)
    # If no square has been clicked before this call of the function
    if len(clicked_squares) == 0:
        if occupied(square_name):
            square.temp_color = ui.red
            piece = get_piece(square_name)
            if white_to_move and piece.color == "w":
                clicked_squares.append(square_name)
            elif white_to_move is False and piece.color == "b":
                clicked_squares.append(square_name)
            else:
                for square in ui.all_squares:
                    square.temp_color = None
                clicked_squares.clear()
    elif len(clicked_squares) == 1:
        clicked_squares.append(square_name)
        if square is not None:
            square.temp_color = ui.red
        moving_piece = get_piece(clicked_squares[0])
        deleted_piece = get_piece(clicked_squares[1])

        if deleted_piece is not None:
            captured.add(deleted_piece)

        i = 0
        for legal in moving_piece.legal_moves():
            if get_piece(clicked_squares[1]) is not None and clicked_squares[1] == legal:
                if moving_piece.color != deleted_piece.color:
                    promote(moving_piece)
                    if deleted_piece.color == "w":
                        white_pieces.remove(deleted_piece)
                    else:
                        black_pieces.remove(deleted_piece)
                    # print("Piece captured!")
                    set_previous(moving_piece, square_name, legal)
                    all_pieces.remove(deleted_piece)
                    moving_piece.square = square_name
                    moving_piece.has_moved = True
                    white_to_move = not white_to_move
                    i = 1
                # else:
                #     print("You can not capture your own piece.")
            if get_piece(clicked_squares[1]) is None and clicked_squares[1] == legal:
                # Checking whether the move is a castling move --> If it is, moves the rook as well
                if moving_piece.name == "wK":
                    if moving_piece.square == "e1":
                        if clicked_squares[1] == "g1" and "g1" in moving_piece.legal_moves():
                            moving_rook = get_piece("h1")
                            moving_rook.square = "f1"
                        elif clicked_squares[1] == "c1" and "c1" in moving_piece.legal_moves():
                            moving_rook = get_piece("a1")
                            moving_rook.square = "d1"
                if moving_piece.name == "bK":
                    if moving_piece.square == "e8":
                        if clicked_squares[1] == "g8" and "g8" in moving_piece.legal_moves():
                            moving_rook = get_piece("h8")
                            moving_rook.square = "f8"
                        elif clicked_squares[1] == "c8" and "c8" in moving_piece.legal_moves():
                            moving_rook = get_piece("a8")
                            moving_rook.square = "d8"
                promote(moving_piece)
                if en_passant == clicked_squares[1]:
                    all_pieces.remove(previous[0])
                    if moving_piece.color == "w":
                        black_pieces.remove(previous[0])
                    else:
                        white_pieces.remove(previous[0])
                set_previous(moving_piece, moving_piece.square, legal)
                moving_piece.square = square_name
                moving_piece.has_moved = True
                white_to_move = not white_to_move
                i = 1

        # if i == 0:
        #     print("Not a legal move.")
        refresh()
        if is_in_check(wtm_copy):
            moving_piece.square = clicked_squares[0]
            for reborn_piece in captured:
                reborn_piece.square = clicked_squares[1]
                all_pieces.add(reborn_piece)
                if reborn_piece.color == "w":
                    white_pieces.add(reborn_piece)
                else:
                    black_pieces.add(reborn_piece)
                # print("Piece reborn!")
            white_to_move = wtm_copy
        for square in ui.all_squares:
            square.temp_color = None
        clicked_squares.clear()


def stalemate():
    king_not_in_check = False
    i = 0
    if white_to_move:
        for wp in white_pieces:
            if wp.name == "wK" and not wp.is_attacked():
                king_not_in_check = True
            if len(wp.legal_moves()) != 0 and wp.legal_moves() != {None}:
                i += 1
        if (i == 0 or i is None) and king_not_in_check:
            return True
        else:
            return False
    else:
        for bp in black_pieces:
            if bp.name == "bK" and not bp.is_attacked():
                if len(bp.legal_moves()) != 0 and bp.legal_moves() != {None}:
                    i += 1
            if i == 0 and king_not_in_check:
                return True
            else:
                return False


def checkmated():
    # If "w" is returned --> White got checkmated
    i = 0
    j = 0
    king = None
    if white_to_move:
        for piece in white_pieces:
            if piece.name == "wK" and piece.is_attacked():
                king = piece
        if king is not None:
            for attacker in black_pieces:
                if king.square in attacker.legal_moves():
                    i += 1
            if i >= 2:
                if king.legal_moves() == {None} or not len(king.legal_moves()):
                    return "w"
            if i == 1 and king.legal_moves() == {None}:
                for wp in white_pieces:
                    if attacker.square in wp.legal_moves():
                        break
                    return "w"
    if not white_to_move:
        for piece in black_pieces:
            if piece.name == "bK" and piece.is_attacked():
                king = piece
        if king is not None:
            for attacker in white_pieces:
                if king.square in attacker.legal_moves():
                    j += 1
            if j >= 2:
                if king.legal_moves() == {None} or not len(king.legal_moves()):
                    # pg.time.delay(2000)
                    return "b"
            if j == 1 and king.legal_moves() == {None}:
                for bp in black_pieces:
                    if attacker.square in bp.legal_moves():
                        break
                    # pg.time.delay(2000)
                    return "b"
