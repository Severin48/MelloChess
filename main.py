# Python-Project coded by Severin Hotz
# MelloChess ver. 1.14
# Chess with Pygame
# Finished 27th March 2020
# main.py: 88 lines
# pieces.py: 792 lines
# ui.py: 318 lines
# Total: 1198 lines of code --> May change after comments have been removed/added

import pygame as pg
import pieces as p
import ui

pg.init()

flipped = started = False
ui.setup_board()

# ==================================================== Game loop =====================================================
run = True
while run:
    ui.start_timer()
    # Time delay in milliseconds - each loop 20ms pause
    pg.time.delay(20)
    ui.draw_board(ui.game_over())
    if not ui.game_over():
        ui.calculate_score(flipped)
        p.refresh()
        # In this loop all the events get caught (i.e. mouse click or pressing the exit button)
        for event in pg.event.get():
            # pos returns the position of the mouse in an (x, y)-tuple
            pos = pg.mouse.get_pos()
            if event.type == pg.QUIT:
                run = False
            if started:
                ui.start_button.text = "Restart"
                ui.start_button.draw(ui.window, ui.white)
                # pg.MOUSEBUTTONDOWN means a mouse button is clicked. In following if-statements it is specified
                # which mouse buttons are pressed. For example: event.button 1 is the left mouse button.
                # 2 is the mouse wheel and 3 is the right mouse button.
            if event.type == pg.MOUSEBUTTONDOWN:
                if ui.start_button.is_over(pos):
                    p.setup_pieces()
                    started = True
                    # White always starts in chess
                    p.white_to_move = True
                    ui.flip_button.draw(ui.window, ui.white)
                    ui.restart_timer()
                    p.refresh()
                if started and ui.flip_button.is_over(pos):
                    ui.flip_board(flipped)
                    flipped = not flipped

                if event.button == 1:
                    # Pieces are moved by clicking on two squares. The second square has to be a legal option.
                    p.move(pos)
                # You can manually deselect your clicked squares by pressing the right mouse button.
                if event.button == 3:
                    p.clicked_squares.clear()
                    for square in ui.all_squares:
                        square.temp_color = None
        p.en_passant = False
        if started and p.white_to_move:
            ui.calculate_time("w")
        if started and not p.white_to_move:
            ui.calculate_time("b")
    else:
        ui.game_over()
        for event in pg.event.get():
            pos = pg.mouse.get_pos()
            if event.type == pg.QUIT:
                run = False
            ui.start_button.text = "Restart"
            ui.start_button.draw(ui.window, ui.white)
            if ui.start_button.is_over(pos):
                if event.type == pg.MOUSEBUTTONDOWN:
                    ui.window.fill(ui.black)
                    p.setup_pieces()
                    started = True
                    p.white_to_move = True
                    ui.flip_button.draw(ui.window, ui.white)
                    ui.restart_timer()
                    p.refresh()

    pg.display.update()

# ================================================== Game loop end ==================================================

pg.quit()
