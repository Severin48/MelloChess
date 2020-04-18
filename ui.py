import pygame as pg
import os
import pieces as p

x = 450
y = 30
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)
window = pg.display.set_mode((640, 800))
screen_width = 640
screen_height = 800
square_side = 80
reverse_letter_dict = {1: "a", 2: "b", 3: "c", 4: "d", 5: "e", 6: "f", 7: "g", 8: "h"}
# Colors: RGB (Red, Green, Blue)
black = (0, 0, 0)
white = (255, 255, 255)
red = (240, 20, 20)
teal = (30, 128, 224)
all_squares = []
match_ended = False
max_time = 600000
timer_w = max_time  # 600.000 ms = 10 min
timer_b = max_time
rounded_time_w = ""
rounded_time_b = ""
score_w = 0
score_b = 0
delta_w = 0
delta_b = 0


class Square:
    def __init__(self, name, color, x, y):
        self.name = name
        if color == "w":
            self.color = white
        else:
            self.color = black
        self.x = x
        self.y = y
        self.flipped = False
        self.occupied = False
        self.temp_color = None
        self.attacked_by_white = False
        self.attacked_by_black = False

    def draw(self):
        if self.temp_color is None:
            pg.draw.rect(window, self.color, [self.x, self.y, square_side, square_side])
        else:
            pg.draw.rect(window, self.temp_color, [self.x, self.y, square_side, square_side])

    def on_square(self, pos):
        if self.x < pos[0] < self.x + square_side and self.y < pos[1] < self.y + square_side:
            return True


def square_by_pos(pos):
    for square in all_squares:
        if square.x < pos[0] < square.x + square_side and square.y < pos[1] < square.y + square_side:
            return square.name


def square_by_name(name):
    for square in all_squares:
        if square.name == name:
            return square


class Button:
    def __init__(self, color, x, y, width, height, font_size, text_color, text=""):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font_size = font_size
        self.text_color = text_color

    def draw(self, window2, outline=None):
        if outline:
            pg.draw.rect(window2, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)
        pg.draw.rect(window2, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != "":
            font = pg.font.SysFont("arial", self.font_size)
            text = font.render(self.text, 1, self.text_color)
            window2.blit(text, (self.x + (self.width / 2 - text.get_width() / 2), self.y +
                                (self.height / 2 - text.get_height() / 2)))

    def is_over(self, pos):
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True
        return False


# All Buttons
start_button = Button((80, 250, 40), 280, 680, 80, 40, 30, (0, 0, 0), "Play")
flip_button = Button((80, 250, 40), 380, 680, 80, 40, 30, (0, 0, 0), "Flip")
time_w = Button((0, 0, 0), 40, 680, 80, 40, 16, (255, 255, 255), "")
time_b = Button((0, 0, 0), 140, 680, 80, 40, 16, (255, 255, 255), "")
score_button_w = Button((0, 0, 0), 480, 680, 80, 40, 20, (255, 255, 255), "")
score_button_b = Button((0, 0, 0), 480, 680, 80, 40, 20, (255, 255, 255), "")
name_label = Button(black, screen_width - 80, screen_height - 40, 80, 40, 14, white, text="Severin Hotz")
game_over_message = Button(red, 0, 0, screen_width, screen_height, 60, white, text="Game Over")


def draw_board(game_ended):
    if game_ended:
        window.fill(red)
        game_over_message.draw(window, red)
        start_button.draw(window, black)
        name_label.color = red
        name_label.draw(window, red)
    else:
        name_label.color = black
        name_label.draw(window, black)
        for square in all_squares:
            square.draw()
        reset_score()
        for piece in p.all_pieces:
            piece.show_piece()
            get_delta(piece)


def setup_board():
    pg.display.set_caption("Mello Chess")
    # Small icon in the top left of the window
    pg.display.set_icon(pg.image.load("images/chess-board.png"))
    start_button.draw(window, white)
    create_squares()
    for square in all_squares:
        square.draw()


def flip_board(flipped):
    for square in all_squares:
        for i in range(0, 8):
            if flipped:
                if square.flipped is True and square.y == i*square_side:
                    square.y = (7-i)*square_side
                    square.flipped = False
            else:
                if square.flipped is False and square.y == i*square_side:
                    square.y = (7-i)*square_side
                    square.flipped = True


def create_squares():
    for row in range(0, 8):
        for column in range(0, 8):
            x = column * square_side
            y = row * square_side
            square = reverse_letter_dict[column + 1] + str(8 - row)
            if (row + column) % 2 == 0:
                all_squares.append(Square(square, "w", x, y))
            if (row + column) % 2 != 0:
                all_squares.append(Square(square, "b", x, y))


def start_timer():
    time_w.text = "White: " + str(rounded_time_w)
    time_b.text = "Black: " + str(rounded_time_b)
    time_w.draw(window, white)
    time_b.draw(window, white)
    global clock
    clock = pg.time.Clock()


def restart_timer():
    global rounded_time_w
    global rounded_time_b
    global timer_w
    global timer_b
    timer_w = max_time
    timer_b = max_time
    rounded_time_b = "10:00"
    rounded_time_w = "10:00"


def calculate_time(color):
    global rounded_time_w
    global rounded_time_b
    global timer_w
    global timer_b
    if color == "w":
        time_w.color = teal
        time_b.color = black
        timer_w -= clock.tick()
        for i in range(0, 11):
            # print(timer_w)
            if i <= timer_w / 60000 <= i + 1:
                if i < 10:
                    minutes = "0" + str(i)
                else:
                    minutes = str(i)
                seconds = round((60000*(10-i) - (600000 - timer_w))/1000)
                if seconds == 60 and i < 9:
                    rounded_time_w = "0" + str(i+1) + ":00"
                    break
                if seconds == 60 and i >= 9:
                    rounded_time_w = str(i+1) + ":00"
                    break
                if 0 <= seconds < 1:
                    rounded_time_w = minutes + ":00"
                    break
                if 1 <= seconds < 10:
                    rounded_time_w = minutes + ":0" + str(seconds)
                    break
                else:
                    rounded_time_w = minutes + ":" + str(seconds)
                    break
    else:
        time_b.color = teal
        time_w.color = black
        timer_b -= clock.tick()
        for i in range(0, 11):
            if i <= timer_b / 60000 <= i + 1:  # i in min
                if i < 10:
                    minutes = "0" + str(i)
                else:
                    minutes = str(i)
                seconds = round((60000 * (10 - i) - (600000 - timer_b)) / 1000)
                if seconds == 60 and i < 9:
                    rounded_time_b = "0" + str(i + 1) + ":00"
                    break
                if seconds == 60 and i >= 9:
                    rounded_time_b = str(i + 1) + ":00"
                    break
                if 0 <= seconds < 1:
                    rounded_time_b = minutes + ":00"
                    break
                if 1 <= seconds < 10:
                    rounded_time_b = minutes + ":0" + str(seconds)
                    break
                else:
                    rounded_time_b = minutes + ":" + str(seconds)
                    break


def reset_score():
    global score_w
    global score_b
    global delta_w
    global delta_b
    score_w = 0
    score_b = 0
    delta_w = 0
    delta_b = 0


# Delta is the score difference
def get_delta(piece):
    global delta_w
    global delta_b
    if piece.color == "w":
        delta_w += piece.score
    else:
        delta_b += piece.score


def calculate_score(flipped):
    global score_w
    global score_b
    global delta_w
    global delta_b
    score_w = delta_w - delta_b
    score_b = delta_b - delta_w
    if p.score_w > 0:
        score_button_w.text = "Score: +" + str(score_w)
    else:
        score_button_w.text = "Score: " + str(score_w)
    if p.score_b > 0:
        score_button_b.text = "Score: +" + str(score_b)
    else:
        score_button_b.text = "Score: " + str(score_b)
    if flipped:
        score_button_b.draw(window, white)
    else:
        score_button_w.draw(window, white)


def game_over():
    if timer_w <= 0:
        game_over_message.font_size = 28
        game_over_message.text = "Black wins! White ran out of time."
        return True
    if timer_b <= 0:
        game_over_message.font_size = 28
        game_over_message.text = "White wins! Black ran out of time."
        return True
    if p.checkmated() == "w":
        game_over_message.font_size = 28
        game_over_message.text = "Black won by checkmate!"
        return True
    if p.checkmated() == "b":
        game_over_message.font_size = 28
        game_over_message.text = "White won by checkmate!"
        return True
    if p.stalemate():
        game_over_message.font_size = 28
        game_over_message.text = "Game drawn - Stalemate!"
        return True
    return False
