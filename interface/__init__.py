import sys
import pygame
import time
import os


pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)#, pygame.FULLSCREEN)
black = 0, 0, 0

info = pygame.display.Info()
size = width, height = info.current_w, info.current_h
print(size)

SETTINGS = False
EXIT = False
TURN = True
RESIZE = False

def check_resize(event):
    global size
    global width
    global height
    global RESIZE
    size = event.size
    width = event.w
    height = event.h
    RESIZE = True

def vote(com, backend):
    global EXIT
    leader = com.turn
    mode = com.mode
    bg_play = "interface/play_bg.png"
    BG = pygame.transform.scale(pygame.image.load(bg_play), size)
    BGrect = BG.get_rect()
    header_text = "Guess leader's card"
    h_font_size = int(height / 8)
    h_font = pygame.font.Font("fonts/Chilanka-Custom.ttf", h_font_size)
    h_color = 0xAD, 0xE5, 0xF3
    header = h_font.render(header_text, True, h_color)
    header_rect = header.get_rect()
    shift = int(height / 120)
    header_rect[1] = shift
    w = header_rect[2]
    header_rect[0] = int(width / 2 - w / 2)
    cards = com.vote_cards #TODO
    #cards = [34, 35, 36, 37, 38, 39]
    card_pos = [int((width - height * len(cards) / 6) / (len(cards) + 1)), int(height * 0.7)]
    cards_img = []
    cards_rect = []
    cards_size = (int(height / 6), int(height / 4))
    for i in cards:
        name = "".join(("resources/", mode, "/", str(i), ".png"))
        cards_img.append(pygame.transform.scale(pygame.image.load(name), cards_size))
        cards_rect.append(cards_img[-1].get_rect())
        cards_rect[-1][0] = card_pos[0]
        cards_rect[-1][1] = card_pos[1]
        card_pos[0] += int((width - height * len(cards) / 6) / (len(cards) + 1) + height / 6)
    assoc_text = com.ass
    a_font_size = int(height / 30)
    a_font = pygame.font.Font("fonts/Chilanka-Custom.ttf", a_font_size)
    a_color = 0xAD, 0xE5, 0xF3
    assoc = a_font.render(assoc_text, True, a_color)
    a_rect = assoc.get_rect()
    card = False
    b_card = None
    card_size = (int(height / 3), int(height / 2))
    card_rect = []
    key_pressed = [False for i in range(len(cards))]
    pressed = False
    pygame.time.set_timer(pygame.USEREVENT, 100)

    while True:
        """MAINLOOP"""
        for event in pygame.event.get():
            """EVENTS HANDLING"""

            """MOUSE EVENTS"""
            if event.type == pygame.MOUSEBUTTONDOWN and not leader:
                for i in range(len(cards)):
                    if cards_rect[i].collidepoint(event.pos):
                        backend.set_card(cards[i])

            """USER EVENTS"""
            if event.type == pygame.USEREVENT and not pressed:
                for i in range(len(cards)):
                    if cards_rect[i].collidepoint(pygame.mouse.get_pos()):
                        card = True
                        name = "".join(("resources/", mode, "/", str(cards[i]), ".png"))
                        b_card = pygame.transform.scale(pygame.image.load(name), card_size)
                        card_rect = b_card.get_rect()
                        card_rect[0] = int(width / 2 - height / 6)
                        card_rect[1] = int(height / 6)
                        break
                else:
                    card = False
                    b_card = None
                    card_rect = []

            """KEYBOARD EVENTS"""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
                else:
                    for i in range(len(cards_rect)):
                        atr = "K_" + str(i + 1)
                        if event.key == pygame.__getattribute__(atr):
                            key_pressed[i] = True
                            pressed = True 
                            card = True
                            name = "".join(("interface/", str(cards[i]), ".png"))
                            b_card = pygame.transform.scale(pygame.image.load(name), card_size)
                            card_rect = b_card.get_rect()
                            card_rect[0] = int(width / 2 - height / 6)
                            card_rect[1] = int(height / 6)
                            break
                    else:
                        card = False
                        b_card = None
                        card_rect = []
            elif event.type == pygame.KEYUP:
                for i in range(len(cards_rect)):
                    atr = "K_" + str(i + 1)
                    if event.key == pygame.__getattribute__(atr):
                        key_pressed[i] = False
                        pressed = False
                        for j in key_pressed:
                            pressed = pressed or j
                        if not pressed:
                            card = False
                            b_card = None
                            card_rect = []

            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None

        """RENDERING"""
        shift = int(height / 120)
        screen.blit(BG, BGrect)
        for i in range(len(cards_img)):
            screen.blit(cards_img[i], cards_rect[i])
        screen.blit(header, (int(width / 6) + shift, shift))
        screen.blit(assoc, (int(width - a_rect[2]) / 2, int(height / 6 + 2 * shift)))
        if card:
            screen.blit(b_card, card_rect)
        pygame.display.flip()


def game_wait(com, backend):
    """Wait when all players choose his card"""
    global EXIT
    bg_play = "interface/play_bg.png"
    BG = pygame.transform.scale(pygame.image.load(bg_play), size)
    BGrect = BG.get_rect()
    header_text = "Wait other players"
    h_font_size = int(height / 8)
    h_font = pygame.font.Font("fonts/Chilanka-Custom.ttf", h_font_size)
    h_color = 0xAD, 0xE5, 0xF3
    header = h_font.render(header_text, True, h_color)
    header_rect = header.get_rect()
    shift = int(height / 120)
    header_rect[1] = shift
    w = header_rect[2]
    header_rect[0] = int(width / 2 - w / 2)
    players = [[5, "agronom", 5], [5, "jmg", 5], [5, "dannon", 5]]
    players = com.get_vote_list()
    players_pos = [0, 0]
    font_size = int(height / 30)
    font = pygame.font.Font("fonts/Chilanka-Custom.ttf", font_size)
    color_good = 0x00, 0xFF, 0x00
    color_bad = 0xFF, 0x00, 0x00
    score = 0
    players_rect = []
    players_size = (int(width / 6), int(height / 8))
    players_text = []
    players_score = []
    for i in players:
        players_rect.append(pygame.Rect(*players_pos, *players_size))
        color = color_good if i[3] else color_bad
        players_text.append(font.render(i[1], True, color))
        score = "".join(("Score: ", str(i[0])))
        players_score.append(font.render(score, True, color))
        players_pos[1] += int(height / 8)
    rect_rect = pygame.Rect(0, 0, int(width / 6), int(height / 8) * len(players))

    while True:
        if com.vote_time:
            vote(com, backend)
            if EXIT:
                return None
        """MAINLOOP"""
        for event in pygame.event.get():
            """EVENTS HANDLING"""

            """MOUSE EVENTS"""

            """KEYBOARD EVENTS"""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None

            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None

        """RENDERING"""
        shift = int(height / 120)
        screen.blit(BG, BGrect)

        players = com.get_vote_list()
        players_pos = [0, 0]
        for i in range(len(players)):
            color = color_good if players[i][3] else color_bad
            players_text[i] = font.render(players[i][1], True, color)
            score = "".join(("Score: ", str(players[i][0])))
            players_score[i] = font.render(score, True, color)
            players_pos[1] += int(height / 8)
            screen.blit(players_text[i], (players_rect[i][0] + shift, players_rect[i][1] + shift))
            screen.blit(players_score[i], (players_rect[i][0] + shift, players_rect[i][1] + shift * 6))
        color = 0xFF, 0xFF, 0xFF
        pygame.draw.rect(screen, color, rect_rect, 2)
        screen.blit(header, (int(width / 6) + shift, shift))
        pygame.display.flip()


def set_association(com, backend):
    global EXIT
    bg_play = "interface/play_bg.png"
    mode = com.mode
    BG = pygame.transform.scale(pygame.image.load(bg_play), size)
    BGrect = BG.get_rect()
    header_text = "Enter your association"
    h_font_size = int(height / 8)
    h_font = pygame.font.Font("fonts/Chilanka-Custom.ttf", h_font_size)
    h_color = 0xAD, 0xE5, 0xF3
    header = h_font.render(header_text, True, h_color)
    header_rect = header.get_rect()
    shift = int(height / 120)
    header_rect[1] = shift
    w = header_rect[2]
    header_rect[0] = int(width / 2 - w / 2)
    card_size = (int(height / 3), int(height / 2))
    name = "interface/34.png" #TODO
    name = "".join(("resources/", mode, "/", str(com.get_card()), ".png"))
    b_card = pygame.transform.scale(pygame.image.load(name), card_size)
    card_rect = b_card.get_rect()
    card_rect[0] = int(width / 2 - height / 6)
    card_rect[1] = int(height / 6)
    back_scale = (int(height * 21 / 216), int(height * 21 / 216))
    back_name = "interface/back.png"
    back = pygame.transform.scale(pygame.image.load(back_name), back_scale)
    backrect = back.get_rect()
    backrect[0] = 0
    backrect[1] = int(height * 185 / 216)
    font_size = int(height / 30)
    font = pygame.font.Font("fonts/Chilanka-Custom.ttf", font_size)
    name_active = False
    name_text = ""

    """Text box aka Entry"""
    namebox_size = (int(width * 2 / 3), int(height * 3 / 60))
    namebox_pos = (int(width / 6), int(height * 3 / 4 - height / 20))
    namerect = pygame.Rect(namebox_pos[0], namebox_pos[1], namebox_size[0], namebox_size[1])
    inactive_color = 0xFF, 0xFF, 0xFF
    active_color = 0xAD, 0xE5, 0xF3
    name_color = inactive_color

    """OK button"""
    ok_scale = (int(width / 3), int(height * 33 / 216))
    ok = pygame.transform.scale(pygame.image.load("interface/ok.png"), ok_scale)
    okrect = ok.get_rect()
    okrect[0] = int(width / 3)
    okrect[1] = int(height * 170 / 216)

    while True:
        """MAINLOOP"""
        for event in pygame.event.get():
            """EVENTS HANDLING"""

            """MOUSE EVENTS"""
            if event.type == pygame.MOUSEBUTTONDOWN:
                if backrect.collidepoint(event.pos):        #TODO
                    return None
                if namerect.collidepoint(event.pos):
                    name_active = not name_active
                else:
                    name_active = False
                    if okrect.collidepoint(event.pos):
                        backend.set_ass(name_text)
                        game_wait(com, backend)
                        return None

            """KEYBOARD EVENTS"""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
                if name_active:
                    if event.key == pygame.K_RETURN:
                        name_active = False
                        backend.set_ass(name_text)
                        game_wait(com, backend)
                        return None
                    elif event.key == pygame.K_BACKSPACE:
                        name_text = name_text[:-1]
                    elif len(name_text) < 68:
                        name_text += event.unicode

            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None

        """RENDERING"""
        name_color = active_color if name_active else inactive_color
        screen.blit(BG, BGrect)
        screen.blit(back, backrect)
        screen.blit(ok, okrect)
        screen.blit(b_card, card_rect)
        screen.blit(header, header_rect)
        name_box = font.render(name_text, True, name_color)
        screen.blit(name_box, (namerect[0] + shift, namerect[1] + shift))
        pygame.draw.rect(screen, name_color, namerect, 2)
        pygame.display.flip()


def game(com, backend):
    global EXIT, TURN
    while TURN:
        """Background"""
        global EXIT
        while not com.got_list:
            time.sleep(1)
        leader = False #TODO
        leader = com.turn
        choose_flg = leader
        mode = com.mode
        bg_play = "interface/play_bg_1.png"
        BG = pygame.transform.scale(pygame.image.load(bg_play), size)
        BGrect = BG.get_rect()
        cards = com.player.cards #TODO
        print(cards)
        #cards = [34, 35, 36, 37, 38, 39]
        card_pos = [int((width - height * len(cards) / 6) / (len(cards) + 1)), int(height * 0.7)]
        cards_img = []
        cards_rect = []
        cards_size = (int(height / 6), int(height / 4))
        for i in cards:
            name = "".join(("resources/", mode, "/",  str(i), ".png"))
            cards_img.append(pygame.transform.scale(pygame.image.load(name), cards_size))
            cards_rect.append(cards_img[-1].get_rect())
            cards_rect[-1][0] = card_pos[0]
            cards_rect[-1][1] = card_pos[1]
            card_pos[0] += int((width - height * len(cards) / 6) / (len(cards) + 1) + height / 6)

        players = [[5, "agronom", 5, True], [5, "jmg", 5, False], [5, "dannon", 5, False]]
        players = com.get_players_list()
        players_pos = [0, 0]

        font_size = int(height / 30)
        font = pygame.font.Font("fonts/Chilanka-Custom.ttf", font_size)
        color_else = 0xFF, 0xFF, 0xFF
        color_leader = 0xFF, 0xFF, 0x00

        players_rect = []
        players_size = (int(width / 6), int(height / 8))
        players_text = []
        players_score = []
        for i in players:
            color = color_leader if i[3] else color_else
            players_rect.append(pygame.Rect(*players_pos, *players_size))
            players_text.append(font.render(i[1], True, color))
            score = "".join(("Score: ", str(i[0])))
            players_score.append(font.render(score, True, color))
            players_pos[1] += int(height / 8)
        rect_rect = pygame.Rect(0, 0, int(width / 6), int(height / 8) * len(players))
        card = False
        b_card = None
        card_size = (int(height / 3), int(height / 2))
        card_rect = []
        key_pressed = [False for i in range(len(cards))]
        pressed = False

        header_text = "choose a card" if leader else "wait for your turn"
        h_font_size = int(height / 6)
        h_font = pygame.font.Font("fonts/Chilanka-Custom.ttf", h_font_size)
        h_color = 0xAD, 0xE5, 0xF3
        header = h_font.render(header_text, True, h_color)
        assoc = None
        assoc_text = None
        a_rect = None

        pygame.time.set_timer(pygame.USEREVENT, 100)

        while True:
            """MAINLOOP"""
            breaker = False
            if (not leader) and com.got_ass:
                choose_flg = True
                header_text = "choose a card"
                header = h_font.render(header_text, True, h_color)
                assoc_text = com.ass
                a_font_size = int(height / 30)
                a_font = pygame.font.Font("fonts/Chilanka-Custom.ttf", a_font_size)
                a_color = 0xAD, 0xE5, 0xF3
                assoc = a_font.render(assoc_text, True, a_color)
                a_rect = assoc.get_rect()

            for event in pygame.event.get():
                """EVENTS HANDLING"""

                """MOUSE EVENTS"""
                if event.type == pygame.MOUSEBUTTONDOWN and (leader or choose_flg):
                    for i in range(len(cards)):
                        if cards_rect[i].collidepoint(event.pos):
                            backend.set_card(cards[i])
                            if leader:
                                set_association(com, backend)
                                if EXIT:
                                    return None
                            else:
                                game_wait(com, backend)
                                if EXIT:
                                    return None
                                else:
                                    breaker = True


                """USER EVENTS"""
                if event.type == pygame.USEREVENT and not pressed:
                    for i in range(len(cards)):
                        if cards_rect[i].collidepoint(pygame.mouse.get_pos()):
                            card = True
                            name = "".join(("resources/", mode, "/", str(cards[i]), ".png"))
                            b_card = pygame.transform.scale(pygame.image.load(name), card_size)
                            card_rect = b_card.get_rect()
                            card_rect[0] = int(width / 2 - height / 6)
                            card_rect[1] = int(height / 6)
                            break
                    else:
                        card = False
                        b_card = None
                        card_rect = []

                """KEYBOARD EVENTS"""
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        backend.stop()
                        pygame.quit()
                        EXIT = True
                        return None
                    else:
                        for i in range(len(cards_rect)):
                            atr = "K_" + str(i + 1)
                            if event.key == pygame.__getattribute__(atr):
                                key_pressed[i] = True
                                pressed = True 
                                card = True
                                name = "".join(("resources/", mode, "/", str(cards[i]), ".png"))
                                b_card = pygame.transform.scale(pygame.image.load(name), card_size)
                                card_rect = b_card.get_rect()
                                card_rect[0] = int(width / 2 - height / 6)
                                card_rect[1] = int(height / 6)
                                break
                        else:
                            card = False
                            b_card = None
                            card_rect = []
                elif event.type == pygame.KEYUP:
                    for i in range(len(cards_rect)):
                        atr = "K_" + str(i + 1)
                        if event.key == pygame.__getattribute__(atr):
                            key_pressed[i] = False
                            pressed = False
                            for j in key_pressed:
                                pressed = pressed or j
                            if not pressed:
                                card = False
                                b_card = None
                                card_rect = []

                """OTHER EVENTS"""
                if event.type == pygame.QUIT:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None

            """RENDERING"""
            shift = int(height / 120)
            screen.blit(BG, BGrect)
            for i in range(len(cards_img)):
                screen.blit(cards_img[i], cards_rect[i])
            for i in range(len(players)):
                screen.blit(players_text[i], (players_rect[i][0] + shift, players_rect[i][1] + shift))
                screen.blit(players_score[i], (players_rect[i][0] + shift, players_rect[i][1] + shift * 6))
            color = color_else
            pygame.draw.rect(screen, color, rect_rect, 2)
            screen.blit(header, (int(width / 6) + shift, shift))
            if (not leader) and choose_flg:
                screen.blit(assoc, (int(width - a_rect[2]) / 2, int(height / 6 + 2 * shift)))
            if card:
                screen.blit(b_card, card_rect)
            pygame.display.flip()
            if breaker:
                break



def wait_menu(com, backend):
    global EXIT
    """Wait players"""
    global EXIT
    font_size = int(height / 20)
    font = pygame.font.Font("fonts/Chilanka-Custom.ttf", font_size)
    w_shift = int(height / 120)
    h_shift = int(height / 14 - height / 40)
    clock = pygame.time.Clock()
    """Background"""
    bg_name = "interface/wait_0.png"
    BG = pygame.transform.scale(pygame.image.load(bg_name), size)
    BGrect = BG.get_rect()

    """Back button"""
    back_scale = (int(height * 21 / 216), int(height * 21 / 216))
    back_name = "interface/back.png"
    back = pygame.transform.scale(pygame.image.load(back_name), back_scale)
    backrect = back.get_rect()
    backrect[0] = 0
    backrect[1] = int(height * 185 / 216)

    num = com.get_number()
    play = 0
    playrect = 0
    if num == 0:
        play_scale = (int(width / 3), int(height * 33 / 216))
        play_name = "interface/play.png"
        play = pygame.transform.scale(pygame.image.load(play_name), play_scale)
        playrect = play.get_rect()
        playrect[0] = int(width / 3)
        playrect[1] = int(height * 150 / 216)

    screen_iter = 0

    while True:
        """MAINLOOP"""
        n = screen_iter % 4
        screen_iter += 1
        img = "interface/wait_{}.png".format(str(n))
        BG = pygame.transform.scale(pygame.image.load(img), size)
        BGrect = BG.get_rect()
        if com.game_started:
            game(com, backend)
            return None

        for event in pygame.event.get():
            """EVENTS HANDLING"""

            """MOUSE EVENTS"""
            if event.type == pygame.MOUSEBUTTONDOWN:
                if backrect.collidepoint(event.pos):
                    backend.exit()
                    return None
                if num == 0 and playrect.collidepoint(event.pos):
                    backend.play()
                    game(com, backend)
                    return None


            """KEYBOARD EVENTS"""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None

            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None

        clock.tick(2)
        if not com.is_connected:
            disconnection()
            return None
        """RENDERING"""
        screen.blit(BG, BGrect)
        players = com.get_players_list()
        p_size = (int(width / 3), int(height / 7))
        p_pos = (int(width * 2 / 3), 0)
        prect = pygame.Rect(p_pos[0], p_pos[1], p_size[0], p_size[1])
        for i in range(len(players)):
            plr = str(i + 1) + ". " + players[i][1]
            player_box = font.render(plr, True, (0xAD, 0xE5, 0xF3))
            screen.blit(player_box, (prect[0] + w_shift, prect[1] + h_shift))
            # pygame.draw.rect(screen, (0xAD, 0xE5, 0xF3), prect, 2)
            prect[1] += int(height / 7)
        screen.blit(back, backrect)
        if num == 0:
            screen.blit(play, playrect)
        pygame.display.flip()


def settings_menu(com, backend):
    """settings menu"""
    global EXIT

    def checker(IP, PORT):
        """Check data in settings fields"""
        ip_pars = IP.split(".")
        ip_flg = False
        port_flg = False
        if len(ip_pars) == 4:
            for i in ip_pars:
                if i.isnumeric():
                    if int(i) <= 255 and int(i) >= 0:
                        continue
                    else:
                        break
                else:
                    break
            else:
                ip_flg = True
        if PORT.isnumeric():
            if int(PORT) >= 1024 and int(PORT) <= 65535:
                port_flg = True
        return ip_flg and port_flg

    BG = 0
    BGrect = 0
    ip_text = ""
    port_text = ""

    def save_fun(*arg):
        """Save ip and port"""
        nonlocal BG, BGrect, ip_text, port_text
        if checker(ip_text, port_text):
            backend.set_connection_params(ip_text, int(port_text))
            global SETTINGS
            SETTINGS = True
            com.is_connected = False
            bg_name = "interface/BG_settings_saved.png"
            BG = pygame.transform.scale(pygame.image.load(bg_name), size)
            BGrect = BG.get_rect()
            ip_text = ""
            port_text = ""
        else:
            bg_name = "interface/BG_settings_not_saved.png"
            BG = pygame.transform.scale(pygame.image.load(bg_name), size)
            BGrect = BG.get_rect()

    """Text"""
    font_size = int(height / 30)
    font = pygame.font.Font("fonts/Chilanka-Custom.ttf", font_size)
    ip_active = False
    port_active = False
    inactive_color = 0xFF, 0xFF, 0xFF
    active_color = 0xAD, 0xE5, 0xF3

    """Text box for ip"""
    ip_size = (int(width / 3), int(height * 3 / 60))
    ip_pos = (int(width / 3), int(height * 53 / 216))
    iprect = pygame.Rect(ip_pos[0], ip_pos[1], ip_size[0], ip_size[1])
    ip_color = inactive_color

    """Text box for port"""
    port_size = (int(width / 3), int(height * 3 / 60))
    port_pos = (int(width / 3), int(height * 137 / 216))
    portrect = pygame.Rect(*port_pos, *port_size)
    port_color = inactive_color

    """Background"""
    BG = pygame.transform.scale(pygame.image.load("interface/BG_settings.png"), size)
    BGrect = BG.get_rect()

    """Back button"""
    back_scale = (int(height * 21 / 216), int(height * 21 / 216))
    back = pygame.transform.scale(pygame.image.load("interface/back.png"), back_scale)
    backrect = back.get_rect()
    backrect[0] = 0
    backrect[1] = int(height * 185 / 216)

    """Save buton"""
    save_scale = (int(width * 7 / 128), int(height * 12 / 216))
    save = pygame.transform.scale(pygame.image.load("interface/save.png"), save_scale)
    saverect = save.get_rect()
    saverect[0] = int(width * 227 / 480)
    saverect[1] = int(height * 7 / 9)

    while True:
        """MAINLOOP"""
        for event in pygame.event.get():
            """MOUSE EVENTS"""
            if event.type == pygame.MOUSEBUTTONDOWN:
                if backrect.collidepoint(event.pos):
                    #backend.exit()
                    return None
                if iprect.collidepoint(event.pos):
                    port_active = False
                    ip_active = not ip_active
                elif portrect.collidepoint(event.pos):
                    ip_active = False
                    port_active = not port_active
                else:
                    ip_active = False
                    port_active = False
                    if saverect.collidepoint(event.pos):
                        save_fun()

            """KEYBOARD EVENTS"""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
                if ip_active:
                    if event.key == pygame.K_RETURN:
                        ip_active = False
                        port_active = True
                    elif event.key == pygame.K_BACKSPACE:
                        ip_text = ip_text[:-1]
                    elif len(ip_text) < 20:
                        ip_text += event.unicode
                elif port_active:
                    if event.key == pygame.K_RETURN:
                        ip_active = False
                        port_active = False
                        save_fun()
                    elif event.key == pygame.K_BACKSPACE:
                        port_text = port_text[:-1]
                    elif len(port_text) < 22:
                        port_text += event.unicode

            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None

        """RENDERING"""
        ip_color = active_color if ip_active else inactive_color
        port_color = active_color if port_active else inactive_color

        shift = int(height / 120)
        screen.blit(BG, BGrect)
        screen.blit(back, backrect)
        screen.blit(save, saverect)
        ip_box = font.render(ip_text, True, ip_color)
        port_box = font.render(port_text, True, port_color)
        screen.blit(ip_box, (iprect[0] + shift, iprect[1] + shift))
        screen.blit(port_box, (portrect[0] + shift, portrect[1] + shift))
        pygame.draw.rect(screen, ip_color, iprect, 2)
        pygame.draw.rect(screen, port_color, portrect, 2)
        pygame.display.flip()


def rule_menu(com, backend):
    """DRAW RULE MENU INTERFACE"""
    global EXIT
    """Background"""
    global EXIT
    BG_rule = pygame.transform.scale(pygame.image.load("interface/rule_menu.png"), size)
    BG_rulerect = BG_rule.get_rect()

    """Back button"""
    back_scale = (int(height * 21 / 216), int(height * 21 / 216))
    back = pygame.transform.scale(pygame.image.load("interface/back.png"), back_scale)
    backrect = back.get_rect()
    backrect[0] = 0
    backrect[1] = int(height * 185 / 216)

    while True:
        """MAINLOOP"""
        for event in pygame.event.get():
            """EVENTS HANDLING"""

            """MOUSE EVENTS"""
            if event.type == pygame.MOUSEBUTTONDOWN:
                if backrect.collidepoint(event.pos):
                    backend.exit()
                    return None
            """KEYBOARD EVENTS"""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None

            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None

        """RENDERING"""
        screen.blit(BG_rule, BG_rulerect)
        screen.blit(back, backrect)
        pygame.display.flip()


def play_menu_2(com, backend):
    """DRAW NAME INSERTION INTERFACE"""
    global EXIT
    """Background"""
    global EXIT
    BG = pygame.transform.scale(pygame.image.load("interface/BG_name.png"), size)
    BGrect = BG.get_rect()

    """Back button"""
    back_scale = (int(height * 21 / 216), int(height * 21 / 216))
    back = pygame.transform.scale(pygame.image.load("interface/back.png"), back_scale)
    backrect = back.get_rect()
    backrect[0] = 0
    backrect[1] = int(height * 185 / 216)

    """Text"""
    font_size = int(height / 30)
    font = pygame.font.Font("fonts/Chilanka-Custom.ttf", font_size)
    name_active = False
    name_text = ""

    """Text box aka Entry"""
    namebox_size = (int(width / 3), int(height * 3 / 60))
    namebox_pos = (int(width / 3), int(height * 53 / 216))
    namerect = pygame.Rect(namebox_pos[0], namebox_pos[1], namebox_size[0], namebox_size[1])
    inactive_color = 0xFF, 0xFF, 0xFF
    active_color = 0xAD, 0xE5, 0xF3
    name_color = inactive_color

    """OK button"""
    ok_scale = (int(width / 3), int(height * 33 / 216))
    ok = pygame.transform.scale(pygame.image.load("interface/ok.png"), ok_scale)
    okrect = ok.get_rect()
    okrect[0] = int(width / 3)
    okrect[1] = int(height * 115 / 216)

    def save_fun(*arg):
        """Save Name"""
        nonlocal BG, BGrect, name_text
        if name_text.isalnum():
            backend.set_name(name_text)
            name_text = ""
            wait_menu(com, backend)
            backend.exit()
            return True
        else:
            BG = pygame.transform.scale(pygame.image.load("interface/BG_name_bad.png"), size)
            BGrect = BG.get_rect()
            return False

    while True:
        """MAINLOOP"""
        for event in pygame.event.get():
            """EVENTS HANDLING"""

            """MOUSE EVENTS"""
            if event.type == pygame.MOUSEBUTTONDOWN:
                if backrect.collidepoint(event.pos):
                    backend.exit()
                    return None
                if namerect.collidepoint(event.pos):
                    name_active = not name_active
                else:
                    name_active = False
                    if okrect.collidepoint(event.pos):
                        if save_fun():
                            return None

            """KEYBOARD EVENTS"""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
                if name_active:
                    if event.key == pygame.K_RETURN:
                        name_active = False
                        if save_fun():
                            return None
                    elif event.key == pygame.K_BACKSPACE:
                        name_text = name_text[:-1]
                    elif len(name_text) < 20:
                        name_text += event.unicode

            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None

        """RENDERING"""
        name_color = active_color if name_active else inactive_color
        shift = int(height / 120)
        screen.blit(BG, BGrect)
        screen.blit(back, backrect)
        screen.blit(ok, okrect)
        name_box = font.render(name_text, True, name_color)
        screen.blit(name_box, (namerect[0] + shift, namerect[1] + shift))
        pygame.draw.rect(screen, name_color, namerect, 2)
        pygame.display.flip()


def disconnection():
    """Disdpaying if backend can't connect to server"""
    global EXIT
    """Background"""
    global EXIT
    BG = pygame.transform.scale(pygame.image.load("interface/BG_disconnect.png"), size)
    BGrect = BG.get_rect()

    """Ok button"""
    ok_scale = (int(width / 3), int(height * 33 / 216))
    ok = pygame.transform.scale(pygame.image.load("interface/ok.png"), ok_scale)
    okrect = ok.get_rect()
    okrect[0] = int(width / 3)
    okrect[1] = int(height * 115 / 216)

    while True:
        """MAINLOOP"""
        for event in pygame.event.get():
            """EVENTS HANDLING"""

            """MOUSE EVENTS"""
            if event.type == pygame.MOUSEBUTTONDOWN:
                if okrect.collidepoint(event.pos):
                    return None

            """KEYBOARD EVENTS"""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None

            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None

        """RENDERING"""
        screen.blit(BG, BGrect)
        screen.blit(ok, okrect)
        pygame.display.flip()


def connection(com, backend):
    """Wait to connection"""
    global EXIT
    clock = pygame.time.Clock()
    """Background"""
    BG = pygame.transform.scale(pygame.image.load("interface/BG_0.png"), size)
    BGrect = BG.get_rect()

    for i in range(20):
        """MAINLOOP"""
        n = i % 4
        img = "interface/BG_{}.png".format(str(n))
        BG = pygame.transform.scale(pygame.image.load(img), size)
        BGrect = BG.get_rect()

        if com.is_connected:
            return True
        #if i == 19:
            #return True

        for event in pygame.event.get():
            """EVENTS HANDLING"""

            """KEYBOARD EVENTS"""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None

            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None

        clock.tick(2)

        """RENDERING"""
        screen.blit(BG, BGrect)
        pygame.display.flip()
    disconnection()
    global SETTINGS
    #SETTINGS = False
    return False


def play_menu(com, backend):
    """DRAW PLAY MENU INTERFACE FOR MASTER (FIRST) PLAYER OR DOWNLOADING RESOURCES INTERFACE"""
    global EXIT,  SETTINGS, RESIZE
    RESIZE = True

    if not SETTINGS:
        """If the player hasn't specified connection parameters"""
        settings_menu(com, backend)
        return None

    backend.start_game()
    if not connection(com, backend):
        return None

    """Start connection"""
    num = com.get_number()

    if num == 0:
        """First player interface"""
        bg_img = pygame.image.load("interface/BG_main.png")
        back_img = pygame.image.load("interface/back.png")
        mode_img = []
        mode_img.append(pygame.image.load("interface/classic.png"))
        mode_img.append(pygame.image.load("interface/ariadna.png"))
        mode_img.append(pygame.image.load("interface/himera.png"))
        mode_img.append(pygame.image.load("interface/Odiseya.png"))
        mode_img.append(pygame.image.load("interface/pandora.png"))
        mode_img.append(pygame.image.load("interface/persefona.png"))
        selected_mode = ["imaginarium", "ariadna", "himera", "odissey", "pandora", "persephone"]
        while True:
            if RESIZE:
                """Background"""
                BG = pygame.transform.scale(bg_img, size)
                BGrect = BG.get_rect()
                """Back button"""
                icon_size = min(int(height * 21 / 216), int(width * 7 / 128))
                back_scale = (icon_size, icon_size)
                back = pygame.transform.scale(back_img, back_scale)
                backrect = back.get_rect()
                backrect[0] = 0
                backrect[1] = int(height * 185 / 216)
                
                w = int(width / 5)
                h = int(height / 5)
                m = min(w, h)
                mode_size = (m, m)
                w_shift = int((width - m * 3) / 4)
                w_pos = w_shift
                h_shift = int((height - m * 2) / 3)
                h_pos = h_shift

                """Mods buttons"""
                mode = []
                mode_rect = []
                for i in range(len(mode_img)):
                    mode.append(pygame.transform.scale(mode_img[i], mode_size))
                    mode_rect.append(mode[i].get_rect())
                    mode_rect[i][0] = w_pos
                    mode_rect[i][1] = h_pos
                    w_pos += w_shift + m
                    if i == 2:
                        w_pos = w_shift
                        h_pos += h_shift + m

                RESIZE = False

            """MAINLOOP"""
            for event in pygame.event.get():
                """EVENTS HANDLING"""
                """MOUSE EVENTS"""
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if backrect.collidepoint(event.pos):
                        backend.exit()
                        return None
                    for i in range(len(mode_rect)):
                        if mode_rect[i].collidepoint(event.pos):
                            backend.set_mode(selected_mode[i])
                            play_menu_2(com, backend)
                            return None
                """KEYBOARD EVENTS"""
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        backend.stop()
                        pygame.quit()
                        EXIT = True
                        return None
                """OTHER EVENTS"""
                if event.type == pygame.QUIT:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
                if event.type == pygame.VIDEORESIZE:
                    check_resize(event)

            """RENDERING"""
            screen.blit(BG, BGrect)
            screen.blit(back, backrect)
            for i in range(len(mode)):
                screen.blit(mode[i], mode_rect[i])
            pygame.display.flip()

    elif num > 0:
        """Not first player"""
        play_menu_2(com, backend)
        return None
    else:
        """Download interface"""
        bg_name = "interface/wait_0.png"
        BG = pygame.transform.scale(pygame.image.load(bg_name), size)
        BGrect = BG.get_rect()
        progress = pygame.transform.scale(pygame.image.load("interface/bar.png"), (0, int(height / 6)))
        progress_rect = progress.get_rect()
        progress_rect[1] = int(height * 2 / 3)
        screen_iter = 0
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        while not com.updated:
            """MAINLOOP"""
            for event in pygame.event.get():
                """EVENTS HANDLING"""

                """MOUSE EVENTS"""
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pass
                """USER EVENTS"""
                if event.type == pygame.USEREVENT:
                    n = screen_iter % 4
                    screen_iter += 1
                    img = "interface/wait_{}.png".format(str(n))
                    BG = pygame.transform.scale(pygame.image.load(img), size)
                    BGrect = BG.get_rect()
                    mul = com.get_progress()
                    p_size = (int(width * mul), int(height / 6))
                    progress = pygame.transform.scale(pygame.image.load("interface/bar.png"), p_size)
                    progress_rect = progress.get_rect()
                    progress_rect[1] = int(height * 2 / 3)
                        

                """KEYBOARD EVENTS"""
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        backend.stop()
                        pygame.quit()
                        EXIT = True
                        return None

                """OTHER EVENTS"""
                if event.type == pygame.QUIT:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None

            if not com.is_connected:
                disconnection()
                return None
            """RENDERING"""
            screen.blit(BG, BGrect)
            screen.blit(progress, progress_rect)
            pygame.display.flip()

def main_menu(com, backend):
    """DRAW MAIN MENU INTERFACE"""
    global EXIT, RESIZE
    RESIZE = True
    bg_img = pygame.image.load("interface/BG.png")
    play_img = pygame.image.load("interface/play.png")
    exit_img = pygame.image.load("interface/exit.png")
    settings_img = pygame.image.load("interface/settings.png")
    rule_img = pygame.image.load("interface/rule.png")
    while True:
        if RESIZE:
            """Background"""
            BG = pygame.transform.scale(bg_img, size)
            BGrect = BG.get_rect()
            """Play button"""
            play_scale = (int(width / 3), int(height * 33 / 216))
            play = pygame.transform.scale(play_img, play_scale)
            playrect = play.get_rect()
            playrect[0] = int(width / 3)
            playrect[1] = int(height * 64 / 216)
            """Exit button"""
            exit_scale = (int(width / 3), int(height * 33 / 216))
            exit = pygame.transform.scale(exit_img, exit_scale)
            exitrect = exit.get_rect()
            exitrect[0] = int(width / 3)
            exitrect[1] = int(height * 115 / 216)
            """Settings button"""
            icon_size = min(int(height * 21 / 216), int(width * 7 / 128))
            settings_scale = (icon_size, icon_size)
            settings = pygame.transform.scale(settings_img, settings_scale)
            settingsrect = settings.get_rect()
            settingsrect[0] = 0
            settingsrect[1] = int(height * 185 / 216)
            """Rule button"""
            rule_scale = settings_scale
            rule = pygame.transform.scale(rule_img, rule_scale)
            rulerect = rule.get_rect()
            rule_offset = int(width - rule_scale[0])
            rulerect[0] = rule_offset
            rulerect[1] = int(height * 185 / 216)

            RESIZE = False

        """MAINLOOP"""
        for event in pygame.event.get():
            """EVENTS HANDLING"""
            """MOUSE EVENTS"""
            if event.type == pygame.MOUSEBUTTONDOWN: 
                if exitrect.collidepoint(event.pos):
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
                elif settingsrect.collidepoint(event.pos):
                    settings_menu(com, backend)
                    if EXIT:
                        return None
                elif rulerect.collidepoint(event.pos):
                    rule_menu(com, backend)
                    if EXIT:
                        return None
                elif playrect.collidepoint(event.pos):
                    play_menu(com, backend)
                    if EXIT:
                        return None
            """KEYBOARD EVENTS"""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None
            if event.type == pygame.VIDEORESIZE:
                check_resize(event)

        """RENDERING"""
        screen.blit(BG, BGrect)
        screen.blit(play, playrect)
        screen.blit(exit, exitrect)
        screen.blit(settings, settingsrect)
        screen.blit(rule, rulerect)
        pygame.display.flip()


def init_interface(com, backend):
    global SETTINGS
    SETTINGS = com.ip is not None
    main_menu(com, backend)
    return 

#init_interface(-1, -1)
