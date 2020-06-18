"""Interface module"""
import time
import os
import gettext
import random
import pygame

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
black = 0, 0, 0

info = pygame.display.Info()
size = width, height = info.current_w, info.current_h
print(size)

gettext.install("client", os.path.dirname(os.path.abspath(__file__)))

size_orig = size
w_orig = width
h_orig = height
w_offset = 0
h_offset = 0
SETTINGS = False
EXIT = False
TURN = True
RESIZE = False
font_file = os.path.dirname(os.path.abspath(__file__)) +\
    "/../fonts/Chilanka-Custom.ttf"
CLOCK = pygame.time.Clock()
UPD = False
PATH = os.path.dirname(os.path.abspath(__file__)) + _("/en/")  # noqa: F821
PATH_R = os.path.dirname(os.path.abspath(__file__)) + "/../resources/"
FIRST_TURN = True


def check_resize(event):
    """Check resize and prepare vars to new size of screen."""
    global size, size_orig
    global width, w_orig, w_offset
    global height, h_orig, h_offset
    global RESIZE
    size_orig = event.size
    w_orig = event.w
    h_orig = event.h
    width = min(event.w, int(event.h * 1920 / 1080))
    height = int(width * 1080 / 1920)
    size = (width, height)
    h_offset = int((h_orig - height) / 2)
    w_offset = int((w_orig - width) / 2)
    RESIZE = True


def game_result(com, backend):
    """Show game results."""
    global EXIT, TURN, RESIZE
    RESIZE = True
    players = com.game_results
    while len(players) == 0:
        players = com.game_results
        time.sleep(0.1)
    bg_file = PATH + "play_bg_1.png"
    bg_img = pygame.image.load(bg_file)
    color_else = 0xFF, 0xFF, 0xFF
    color_leader = 0xFF, 0xFF, 0x00
    ok_file = PATH + "ok.png"
    ok_img = pygame.image.load(ok_file)
    while True:
        if RESIZE:
            shift = int(height / 120)
            # Background
            bg = pygame.transform.scale(bg_img, size)
            bgrect = bg.get_rect()
            bgrect[0], bgrect[1] = w_offset, h_offset
            # Players
            players_pos = [w_offset + int(width / 4),
                           h_offset + int(width / 12)]
            font_size = int(height / 12)
            font = pygame.font.Font(font_file, font_size)
            players_rect = []
            players_text = []
            players_score = []
            for i in players:
                color = color_leader if i[3] else color_else
                p_name = i[1]
                players_text.append(font.render(p_name, True, color))
                while players_text[-1].get_size()[0] > int(width / 4):
                    p_name = p_name[:-1]
                    players_text[-1] = font.render(p_name, True, color)
                players_rect.append(players_text[-1].get_rect())
                players_rect[-1][0] = players_pos[0]
                players_rect[-1][1] = players_pos[1]
                players_score.append(font.render(str(i[0]), True, color))
                players_pos[1] += int(height / 12 + shift)
            # OK button
            ok_scale = (int(width / 3), int(height * 33 / 216))
            ok = pygame.transform.scale(ok_img, ok_scale)
            okrect = ok.get_rect()
            okrect[0], okrect[1] = int(width * 2 / 3 + width /
                                       12) + w_offset, h_offset
            # RENDERING
            screen.fill(black)
            screen.blit(bg, bgrect)
            screen.blit(ok, okrect)
            for i in range(len(players)):
                screen.blit(players_text[i], (players_rect[i][0],
                                              players_rect[i][1]))
                screen.blit(players_score[i], (players_rect[i][0] + shift
                                               + int(width / 4),
                                               players_rect[i][1]))
            pygame.display.flip()

            RESIZE = False
        # MAINLOOP
        for event in pygame.event.get():
            # EVENTS HANDLING
            # MOUSE EVENTS
            if event.type == pygame.MOUSEBUTTONDOWN:
                if okrect.collidepoint(event.pos):
                    TURN = False
                    return None
            # KEYBOARD EVENTS
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
            # OTHER EVENTS
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None
            if event.type == pygame.VIDEORESIZE:
                check_resize(event)

        CLOCK.tick(30)


def result(com, backend):
    """Show results of the turn."""
    global EXIT, TURN, RESIZE
    RESIZE = True
    nxttrn = False
    header = ""
    leader = com.turn
    header_rect = 0
    res = com.vote_results
    mode = com.mode
    header_text = _("Wait for other players")  # noqa: F821
    h_color = 0xAD, 0xE5, 0xF3
    bg_file = PATH + "play_bg_1.png"
    bg_img = pygame.image.load(bg_file)
    cards = com.player.cards
    cards_img = []
    for i in res:
        name = "".join((PATH_R, mode, "/", str(i[1]), ".png"))
        cards_img.append(pygame.image.load(name))
    color_else = 0xFF, 0xFF, 0xFF
    color_leader = 0xFF, 0xFF, 0x00
    green = 0x00, 0xFF, 0x00
    card = False
    b_card = None
    key_pressed = [False for i in range(len(cards))]
    pressed = False
    pygame.time.set_timer(pygame.USEREVENT, 100)
    players = com.get_players_list()
    leader_name = ""
    if leader:
        for i in players:
            if i[3]:
                leader_name = i[1]
                break
        for i in res:
            if i[0] == leader_name:
                if len(i[2]) == 0:
                    n = random.randint(0, 4)
                    s = "bad_" + str(n) + ".mp3"
                    pygame.mixer.music.load(PATH + "../Sounds/" + s)
                    pygame.mixer.music.play()
                    break
                elif len(i[2]) == len(res) - 1:
                    n = random.randint(0, 4)
                    s = "good_" + str(n) + ".mp3"
                    pygame.mixer.music.load(PATH + "../Sounds/" + s)
                    pygame.mixer.music.play()
                    break
    ok_file = PATH + "ok.png"
    ok_img = pygame.image.load(ok_file)
    while True:
        if RESIZE:
            shift = int(height / 120)
            # Background
            bg = pygame.transform.scale(bg_img, size)
            bgrect = bg.get_rect()
            bgrect[0], bgrect[1] = w_offset, h_offset
            # Cards
            cards_w = min(int(height / 6), int(width * 3 / 32))
            cards_h = int(cards_w * 3 / 2)
            cards_size = (cards_w, cards_h)
            c_num = len(res)
            card_pos = [int((width - cards_w * c_num) / (c_num + 1)),
                        int(height * 0.7)]
            card_pos[0] += w_offset
            card_pos[1] += h_offset
            cards_row = []
            cards_rect = []
            for i in range(len(res)):
                cards_row.append(pygame.transform.scale(cards_img[i],
                                                        cards_size))
                cards_rect.append(cards_row[-1].get_rect())
                cards_rect[-1][0] = card_pos[0]
                cards_rect[-1][1] = card_pos[1]
                card_pos[0] += int((width - cards_w * len(res)) /
                                   (len(res) + 1) + cards_w)
            # Players
            players_pos = [w_offset, h_offset]
            font_size = int(height / 30)
            font = pygame.font.Font(font_file, font_size)
            players_rect = []
            players_size = (int(width / 6), int(height / 8))
            players_text = []
            players_score = []
            for i in players:
                color = color_leader if i[3] else color_else
                players_rect.append(pygame.Rect(*players_pos, *players_size))
                p_name = i[1]
                players_text.append(font.render(p_name, True, color))
                while players_text[-1].get_size()[0] > int(width / 6):
                    p_name = p_name[:-1]
                    players_text[-1] = font.render(p_name, True, color)
                score = "".join((_("Score: "), str(i[0])))  # noqa: F821
                players_score.append(font.render(score, True, color))
                players_pos[1] += int(height / 12)
            rect_rect = pygame.Rect(w_offset, h_offset, int(width / 6),
                                    int(height / 12) * len(players))
            # Big card
            card_w = min(int(height / 3), int(width * 3 / 16))
            card_h = int(card_w * 3 / 2)
            card_size = (card_w, card_h)
            card_pos = (int(width / 2 - card_w / 2) + w_offset,
                        int(height / 12) + h_offset)
            card_rect = (*card_pos, *card_size)
            # OK button
            ok_scale = (int(width / 3), int(height * 33 / 216))
            ok = pygame.transform.scale(ok_img, ok_scale)
            okrect = ok.get_rect()
            okrect[0], okrect[1] = int(width * 2 / 3 + width /
                                       12) + w_offset, h_offset
            # Header
            h_font_size = int(height / 12)
            h_font = pygame.font.Font(font_file, h_font_size)
            header = h_font.render(header_text, True, h_color)
            header_rect = header.get_rect()
            shift = int(height / 120)
            header_rect[1] = shift + h_offset
            w = header_rect[2]
            header_rect[0] = int(width / 2 - w / 2) + w_offset

            RESIZE = False
        # MAINLOOP
        if com.finish_game:
            game_result(com, backend)
            return None
        for event in pygame.event.get():
            # EVENTS HANDLING
            # MOUSE EVENTS
            if event.type == pygame.MOUSEBUTTONDOWN:
                if okrect.collidepoint(event.pos) and not nxttrn:
                    nxttrn = True
                    backend.next_turn()
            # USER EVENTS
            if event.type == pygame.USEREVENT and not pressed:
                for i in range(len(res)):
                    if cards_rect[i].collidepoint(pygame.mouse.get_pos()):
                        card = True
                        b_card = pygame.transform.scale(cards_img[i],
                                                        card_size)
                        b_text = [_("Owner:"),  # noqa: F821
                                  res[i][0], _("Voted:"),  # noqa: F821
                                  *res[i][2]]
                        b_rend = []
                        b_rend.append(font.render(b_text[0], True, green))
                        b_rend.append(font.render(b_text[1], True,
                                                  color_leader))
                        while b_rend[-1].get_size()[0] > int(width / 6):
                            b_text[1] = b_text[1][:-1]
                            b_rend[-1] = (font.render(b_text[1],
                                                      True, color_leader))
                        b_rend.append(font.render(b_text[2], True, green))
                        for j in range(len(res[i][2])):
                            b_rend.append(font.render(b_text[3 + j],
                                                      True, color_else))
                            while b_rend[-1].get_size()[0] > int(width / 6):
                                b_text[3 + j] = b_text[3 + j][:-1]
                                b_rend[-1] = (font.render(b_text[3 + j],
                                                          True, color_leader))
                        break
                else:
                    card = False
                    b_card = None
            # KEYBOARD EVENTS
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
                            b_card = pygame.transform.scale(cards_img[i],
                                                            card_size)
                            b_text = [_("Owner:"), res[i][0],  # noqa: F821
                                      _("Voted:"), *res[i][2]]  # noqa: F821
                            b_rend = []
                            b_rend.append(font.render(b_text[0], True, green))
                            b_rend.append(font.render(b_text[1],
                                          True, color_leader))
                            while b_rend[-1].get_size()[0] > int(width / 6):
                                b_text[1] = b_text[1][:-1]
                                b_rend[-1] = (font.render(b_text[1],
                                                          True, color_leader))
                            b_rend.append(font.render(b_text[2], True, green))
                            for j in range(len(res[i][2])):
                                b_rend.append(font.render(b_text[3 + j],
                                                          True, color_else))
                                while b_rend[-1].get_size()[0] > int(width
                                                                     / 6):
                                    b_text[3 + j] = b_text[3 + j][:-1]
                                    b_rend[-1] = (font.render(b_text[3 + j],
                                                              True,
                                                              color_leader))
                            break
                    else:
                        card = False
                        b_card = None
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
            # OTHER EVENTS
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None
            if event.type == pygame.VIDEORESIZE:
                check_resize(event)

        # RENDERING
        screen.fill(black)
        screen.blit(bg, bgrect)
        if not nxttrn:
            screen.blit(ok, okrect)
        for i in range(len(cards_row)):
            screen.blit(cards_row[i], cards_rect[i])
            color = color_leader if players[i][3] else color_else
            p_name = res[i][0]
            text_img = font.render(p_name, True, color)
            while text_img.get_size()[0] > cards_rect[i][2]:
                p_name = p_name[:-1]
                text_img = font.render(p_name, True, color)
            color = black
            num_t = str(len(res[i][2]))
            num_img = font.render(num_t, True, color)
            num_w = int((cards_rect[i][2] - num_img.get_size()[0]) /
                        2) + cards_rect[i][0]
            num_h = cards_rect[i][1] + cards_rect[i][3] + shift
            screen.blit(num_img, (num_w, num_h))
            screen.blit(text_img, (cards_rect[i][0],
                                   cards_rect[i][1] - shift - font_size))
        for i in range(len(players)):
            screen.blit(players_text[i], (players_rect[i][0] + shift,
                                          players_rect[i][1] + shift))
            screen.blit(players_score[i], (players_rect[i][0] + shift,
                                           players_rect[i][1] + shift * 6))
        color = color_else
        pygame.draw.rect(screen, color, rect_rect, 2)
        if card:
            screen.blit(b_card, card_rect)
            text_pos = [card_rect[0] + card_rect[2] + shift, card_rect[1]]
            for i in b_rend:
                screen.blit(i, text_pos)
                text_pos[1] += font_size + shift
        if nxttrn:
            screen.blit(header, header_rect)
        pygame.display.flip()
        CLOCK.tick(30)
        if com.next_turn:
            com.approved = True
            return None


def vote(com, backend):
    """Interface for vote."""
    global EXIT, RESIZE
    RESIZE = True
    selected = False
    leader = com.turn
    mode = com.mode
    bg_file = PATH + "play_bg.png"
    bg_play = pygame.image.load(bg_file)
    leader = com.turn
    header_text = ""
    if leader:
        header_text = _("Wait for other players")  # noqa: F821
    else:
        header_text = _("Guess leader's card")  # noqa: F821
    h_color = 0xAD, 0xE5, 0xF3
    cards = com.vote_cards
    cards_row = []
    for i in cards:
        name = pygame.image.load("".join((PATH_R,
                                          mode, "/", str(i), ".png")))
        cards_row.append(name)
    assoc_text = com.ass
    a_color = 0xAD, 0xE5, 0xF3
    card = False
    b_card = None
    key_pressed = [False for i in range(len(cards))]
    pressed = False
    pygame.time.set_timer(pygame.USEREVENT, 100)

    while True:
        if com.end_vote:
            result(com, backend)
            return None
        if RESIZE:
            bg = pygame.transform.scale(bg_play, size)
            bgrect = bg.get_rect()
            bgrect[0], bgrect[1] = w_offset, h_offset
            h_font_size = int(height / 12)
            h_font = pygame.font.Font(font_file, h_font_size)
            header = h_font.render(header_text, True, h_color)
            header_rect = header.get_rect()
            shift = int(height / 120)
            header_rect[1] = shift + h_offset
            w = header_rect[2]
            header_rect[0] = int(width / 2 - w / 2) + w_offset
            card_pos = [int((width - height * len(cards) / 6) /
                            (len(cards) + 1)) + w_offset,
                        int(height * 0.7) + h_offset]
            cards_img = []
            cards_rect = []
            cards_size = (int(height / 6), int(height / 4))
            for i in range(len(cards)):
                cards_img.append(pygame.transform.scale(cards_row[i],
                                                        cards_size))
                cards_rect.append(cards_img[-1].get_rect())
                cards_rect[-1][0] = card_pos[0]
                cards_rect[-1][1] = card_pos[1]
                card_pos[0] += int((width - height * len(cards) / 6) /
                                   (len(cards) + 1) + height / 6)
            a_font_size = int(height / 30)
            a_font = pygame.font.Font(font_file, a_font_size)
            assoc = a_font.render(assoc_text, True, a_color)
            a_rect = assoc.get_rect()
            card_size = (int(height / 3), int(height / 2))
            card = False
            card_rect = []
            RESIZE = False

        # MAINLOOP
        for event in pygame.event.get():
            # EVENTS HANDLING
            # MOUSE EVENTS
            tmp = not leader and not selected
            if event.type == pygame.MOUSEBUTTONDOWN and tmp:
                for i in range(1, len(cards)):
                    if cards_rect[i].collidepoint(event.pos):
                        backend.set_card(cards[i])
                        header_text = _("Wait for other players")  # noqa: F821
                        header = h_font.render(header_text, True, h_color)
                        header_rect = header.get_rect()
                        shift = int(height / 120)
                        header_rect[1] = shift + h_offset
                        w = header_rect[2]
                        header_rect[0] = int(width / 2 - w / 2) + w_offset

                        selected = True
            # USER EVENTS
            if event.type == pygame.USEREVENT and not pressed:
                for i in range(len(cards)):
                    if cards_rect[i].collidepoint(pygame.mouse.get_pos()):
                        card = True
                        b_card = pygame.transform.scale(cards_row[i],
                                                        card_size)
                        card_rect = b_card.get_rect()
                        card_rect[0] = int(width / 2 - height / 6) + w_offset
                        card_rect[1] = int(height / 6) + h_offset
                        break
                else:
                    card = False
                    b_card = None
                    card_rect = []
            # KEYBOARD EVENTS
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
                            b_card = pygame.transform.scale(cards_row[i],
                                                            card_size)
                            card_rect = b_card.get_rect()
                            card_rect[0] = int(width / 2 - height /
                                               6) + w_offset
                            card_rect[1] = int(height / 6) + h_offset
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

            # OTHER EVENTS
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None
            if event.type == pygame.VIDEORESIZE:
                check_resize(event)

        # RENDERING
        screen.fill(black)
        shift = int(height / 120)
        screen.blit(bg, bgrect)
        for i in range(len(cards_img)):
            screen.blit(cards_img[i], cards_rect[i])
        screen.blit(header, header_rect)
        screen.blit(assoc, (int(width - a_rect[2]) / 2 + w_offset,
                    int(height / 12 + 2 * shift) + h_offset))
        if card:
            screen.blit(b_card, card_rect)
        pygame.display.flip()
        CLOCK.tick(30)


def game_wait(com, backend):
    """Wait when all players choose their card."""
    global EXIT, RESIZE
    RESIZE = True
    pygame.mixer.music.stop()
    bg_file = PATH + "play_bg.png"
    bg_play = pygame.image.load(bg_file)
    header_text = _("Wait for other players")  # noqa: F821
    h_color = 0xAD, 0xE5, 0xF3
    color_good = 0x00, 0xFF, 0x00
    color_bad = 0xFF, 0x00, 0x00
    players = com.get_vote_list()
    while len(players) == 0:
        players = com.get_vote_list()
        time.sleep(0.1)
    while True:
        if RESIZE:
            bg = pygame.transform.scale(bg_play, size)
            bgrect = bg.get_rect()
            bgrect[0], bgrect[1] = w_offset, h_offset
            h_font_size = int(height / 12)
            h_font = pygame.font.Font(font_file, h_font_size)
            header = h_font.render(header_text, True, h_color)
            header_rect = header.get_rect()
            shift = int(height / 120)
            header_rect[1] = shift + h_offset
            w = header_rect[2]
            header_rect[0] = int(width / 2 - w / 2) + w_offset
            players_pos = [w_offset, h_offset]
            font_size = int(height / 30)
            font = pygame.font.Font(font_file, font_size)
            RESIZE = False
        players_rect = []
        players_size = (int(width / 6), int(height / 8))
        players_text = []
        players_score = []
        for i in players:
            players_rect.append(pygame.Rect(*players_pos, *players_size))
            color = color_good if i[3] else color_bad
            players_text.append(font.render(i[1], True, color))
            text = i[1]
            while players_text[-1].get_size()[0] > int(width / 6):
                text = text[:-1]
                players_text[-1] = font.render(text, True, color)
            score = "".join((_("Score: "), str(i[0])))  # noqa: F821
            players_score.append(font.render(score, True, color))
            players_pos[1] += int(height / 12)
        rect_rect = pygame.Rect(w_offset, h_offset, int(width / 6),
                                int(height / 12) * len(players))

        players = com.get_vote_list()
        if com.vote_time:
            vote(com, backend)
            return None
        # MAINLOOP
        for event in pygame.event.get():
            # EVENTS HANDLING
            # MOUSE EVENTS
            # KEYBOARD EVENTS
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None

            # OTHER EVENTS
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None
            if event.type == pygame.VIDEORESIZE:
                check_resize(event)

        # RENDERING
        screen.fill(black)
        shift = int(height / 120)
        screen.blit(bg, bgrect)
        players = com.get_vote_list()
        players_pos = [w_offset, h_offset]
        for i in range(len(players)):
            screen.blit(players_text[i], (players_rect[i][0] + shift,
                        players_rect[i][1] + shift))
            screen.blit(players_score[i], (players_rect[i][0] + shift,
                        players_rect[i][1] + shift * 6))
        color = 0xFF, 0xFF, 0xFF
        pygame.draw.rect(screen, color, rect_rect, 2)
        screen.blit(header, header_rect)
        pygame.display.flip()
        CLOCK.tick(30)


def set_association(com, backend):
    """Interface for leader. Field for association."""
    global EXIT, RESIZE
    RESIZE = True
    bg_file = PATH + "play_bg.png"
    bg_play = pygame.image.load(bg_file)
    mode = com.mode
    header_text = _("Enter your association")  # noqa: F821
    h_color = 0xAD, 0xE5, 0xF3
    name = "".join((PATH_R, mode, "/",
                    str(com.get_card()), ".png"))
    card_img = pygame.image.load(name)
    name_active = True
    name_text = ""
    inactive_color = 0xFF, 0xFF, 0xFF
    active_color = 0xAD, 0xE5, 0xF3
    name_color = inactive_color
    ok_file = PATH + "ok.png"
    ok_img = pygame.image.load(ok_file)
    back_file = PATH + "back.png"
    back_img = pygame.image.load(back_file)

    while True:
        if RESIZE:
            # Background
            bg = pygame.transform.scale(bg_play, size)
            bgrect = bg.get_rect()
            bgrect[0], bgrect[1] = w_offset, h_offset
            # "Header
            h_font_size = int(height / 8)
            h_font = pygame.font.Font(font_file, h_font_size)
            header = h_font.render(header_text, True, h_color)
            header_rect = header.get_rect()
            shift = int(height / 120)
            header_rect[1] = shift + h_offset
            w = header_rect[2]
            header_rect[0] = int(width / 2 - w / 2) + w_offset
            # Card
            card_size = (int(height / 3), int(height / 2))
            b_card = pygame.transform.scale(card_img, card_size)
            card_rect = b_card.get_rect()
            card_rect[0] = int(width / 2 - height / 6) + w_offset
            card_rect[1] = int(height / 6) + h_offset
            # Back button
            back_scale = (int(height * 21 / 216), int(height * 21 / 216))
            back = pygame.transform.scale(back_img, back_scale)
            backrect = back.get_rect()
            backrect[0] = w_offset
            backrect[1] = int(height * 185 / 216) + h_offset
            font_size = int(height / 30)
            font = pygame.font.Font(font_file, font_size)
            # Text box aka Entry
            namebox_size = (int(width * 2 / 3), int(height * 3 / 60))
            namebox_pos = (int(width / 6) + w_offset,
                           int(height * 3 / 4 - height / 20) + h_offset)
            namerect = pygame.Rect(namebox_pos[0], namebox_pos[1],
                                   namebox_size[0], namebox_size[1])
            # OK button
            ok_scale = (int(width / 3), int(height * 33 / 216))
            ok = pygame.transform.scale(ok_img, ok_scale)
            okrect = ok.get_rect()
            okrect[0] = int(width / 3) + w_offset
            okrect[1] = int(height * 170 / 216) + h_offset
            RESIZE = False
        # MAINLOOP
        for event in pygame.event.get():
            # EVENTS HANDLING
            # MOUSE EVENTS
            if event.type == pygame.MOUSEBUTTONDOWN:
                if backrect.collidepoint(event.pos):
                    return None
                if namerect.collidepoint(event.pos):
                    name_active = not name_active
                else:
                    name_active = False
                    if okrect.collidepoint(event.pos):
                        if len(name_text) > 0:
                            name_active = False
                            backend.set_ass(name_text)
                            game_wait(com, backend)
                            return None
            # KEYBOARD EVENTS
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
                if name_active:
                    if event.key == pygame.K_RETURN:
                        if len(name_text):
                            name_active = False
                            backend.set_ass(name_text)
                            game_wait(com, backend)
                            return None
                    elif event.key == pygame.K_BACKSPACE:
                        name_text = name_text[:-1]
                    elif len(name_text) < 68:
                        name_text += event.unicode

            # OTHER EVENTS
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None
            if event.type == pygame.VIDEORESIZE:
                check_resize(event)

        # RENDERING
        screen.fill(black)
        name_color = active_color if name_active else inactive_color
        screen.blit(bg, bgrect)
        screen.blit(back, backrect)
        screen.blit(ok, okrect)
        screen.blit(b_card, card_rect)
        screen.blit(header, header_rect)
        name_box = font.render(name_text, True, name_color)
        screen.blit(name_box, (namerect[0] + shift, namerect[1] + shift))
        pygame.draw.rect(screen, name_color, namerect, 2)
        pygame.display.flip()
        CLOCK.tick(30)


def game(com, backend):
    """Main field in game. Leader choose card, and other players do
    the same."""
    global EXIT, TURN, RESIZE
    pygame.mixer.music.load(PATH + "../Sounds/welcome.mp3")
    pygame.mixer.music.play()
    while TURN:
        bg_file = PATH + "play_bg_1.png"
        bg_img = pygame.image.load(bg_file)
        bg = pygame.transform.scale(bg_img, size)
        bgrect = bg.get_rect()
        bgrect[0], bgrect[1] = w_offset, h_offset
        screen.fill(black)
        screen.blit(bg, bgrect)
        pygame.display.flip()
        while not com.got_list:
            time.sleep(0.1)
        RESIZE = True

        leader = com.turn
        choose_flg = leader
        mode = com.mode
        bg_file = PATH + "play_bg_1.png"
        bg_img = pygame.image.load(bg_file)
        cards = com.player.cards
        cards_img = []
        for i in cards:
            name = "".join((PATH_R, mode, "/", str(i), ".png"))
            cards_img.append(pygame.image.load(name))
        color_else = 0xFF, 0xFF, 0xFF
        color_leader = 0xFF, 0xFF, 0x00
        card = False
        b_card = None
        key_pressed = [False for i in range(len(cards))]
        pressed = False
        header_text = ""
        if leader:
            header_text = _("Choose a card")  # noqa: F821
        else:
            header_text = _("Wait for your turn")  # noqa: F821
        h_color = 0xAD, 0xE5, 0xF3
        assoc = None
        assoc_text = None
        a_rect = None
        a_color = 0xAD, 0xE5, 0xF3
        pygame.time.set_timer(pygame.USEREVENT, 100)
        players = com.get_players_list()
        sound = 0

        while True:
            if RESIZE:
                shift = int(height / 120)
                a_font_size = int(height / 30)
                # Background
                bg = pygame.transform.scale(bg_img, size)
                bgrect = bg.get_rect()
                bgrect[0], bgrect[1] = w_offset, h_offset
                # Cards
                cards_w = min(int(height / 6), int(width * 3 / 32))
                cards_h = int(cards_w * 3 / 2)
                cards_size = (cards_w, cards_h)
                c_num = len(cards)
                card_pos = [int((width - cards_w * c_num) / (c_num + 1)),
                            int(height * 0.7)]
                card_pos[0] += w_offset
                card_pos[1] += h_offset
                cards_row = []
                cards_rect = []
                for i in range(len(cards)):
                    cards_row.append(pygame.transform.scale(cards_img[i],
                                                            cards_size))
                    cards_rect.append(cards_row[-1].get_rect())
                    cards_rect[-1][0] = card_pos[0]
                    cards_rect[-1][1] = card_pos[1]
                    card_pos[0] += int((width - cards_w * len(cards)) /
                                       (len(cards) + 1) + cards_w)
                # Players
                players_pos = [w_offset, h_offset]
                font_size = int(height / 30)
                font = pygame.font.Font(font_file, font_size)
                players_rect = []
                players_size = (int(width / 6), int(height / 8))
                players_text = []
                players_score = []
                for i in players:
                    color = color_leader if i[3] else color_else
                    players_rect.append(pygame.Rect(*players_pos,
                                                    *players_size))
                    p_name = i[1]
                    players_text.append(font.render(p_name, True, color))
                    while players_text[-1].get_size()[0] + shift > int(width
                                                                       / 6):
                        p_name = p_name[:-1]
                        players_text[-1] = font.render(p_name, True, color)
                    score = "".join((_("Score: "), str(i[0])))  # noqa: F821
                    players_score.append(font.render(score, True, color))
                    players_pos[1] += int(height / 12)
                rect_rect = pygame.Rect(w_offset, h_offset, int(width / 6),
                                        int(height / 12) * len(players))
                # Big card
                card_w = min(int(height / 3), int(width * 3 / 16))
                card_h = int(card_w * 3 / 2)
                card_size = (card_w, card_h)
                card_pos = (int(width / 2 - card_w / 2) + w_offset,
                            int(height / 6) + h_offset)
                card_rect = (*card_pos, *card_size)
                # Header
                h_font_size = int(height / 12)
                h_font = pygame.font.Font(font_file, h_font_size)
                header = h_font.render(header_text, True, h_color)
                RESIZE = False
            # MAINLOOP
            breaker = False
            if (not leader) and com.got_ass:
                choose_flg = True
                sound += 1
                header_text = _("Choose a card")  # noqa: F821
                header = h_font.render(header_text, True, h_color)
                assoc_text = com.ass
                a_font = pygame.font.Font(font_file, a_font_size)
                assoc = a_font.render(assoc_text, True, a_color)
                a_rect = assoc.get_rect()

            for event in pygame.event.get():
                # EVENTS HANDLING
                # MOUSE EVENTS
                tmp = leader or choose_flg
                if event.type == pygame.MOUSEBUTTONDOWN and tmp:
                    for i in range(len(cards)):
                        if cards_rect[i].collidepoint(event.pos):
                            backend.set_card(cards[i])
                            if leader:
                                set_association(com, backend)
                                if EXIT:
                                    return None
                                else:
                                    breaker = True
                            else:
                                game_wait(com, backend)
                                if EXIT:
                                    return None
                                else:
                                    breaker = True
                # USER EVENTS
                if event.type == pygame.USEREVENT and not pressed:
                    for i in range(len(cards)):
                        if cards_rect[i].collidepoint(pygame.mouse.get_pos()):
                            card = True
                            b_card = pygame.transform.scale(cards_img[i],
                                                            card_size)
                            break
                    else:
                        card = False
                        b_card = None
                # KEYBOARD EVENTS
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
                                b_card = pygame.transform.scale(cards_img[i],
                                                                card_size)
                                break
                        else:
                            card = False
                            b_card = None
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
                # OTHER EVENTS
                if event.type == pygame.QUIT:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
                if event.type == pygame.VIDEORESIZE:
                    check_resize(event)

            if breaker:
                break

            # RENDERING
            screen.fill(black)
            screen.blit(bg, bgrect)
            for i in range(len(cards_row)):
                screen.blit(cards_row[i], cards_rect[i])
            for i in range(len(players)):
                screen.blit(players_text[i], (players_rect[i][0] + shift,
                                              players_rect[i][1] + shift))
                screen.blit(players_score[i],
                            (players_rect[i][0] + shift,
                             players_rect[i][1] + shift * 6))
            color = color_else
            pygame.draw.rect(screen, color, rect_rect, 2)

            header_pos = (int((width - header.get_size()[0]) / 2) + w_offset,
                          shift + h_offset)
            screen.blit(header, header_pos)
            if (not leader) and choose_flg:
                a_pos = (int((width - a_rect[2]) / 2) + w_offset,
                         int(height / 12 + 2 * shift) + h_offset)
                screen.blit(assoc, a_pos)
            if card:
                screen.blit(b_card, card_rect)
            pygame.display.flip()
            if sound == 1:
                s_f = PATH + "/../Sounds/" + "gong.mp3"
                pygame.mixer.music.load(s_f)
                pygame.mixer.music.play(0)
            CLOCK.tick(30)


def wait_menu(com, backend):
    """Interface for waiting players."""
    global EXIT, RESIZE, TURN
    TURN = True
    RESIZE = True

    bg_img = []
    for i in range(4):
        bg_file = PATH + "wait_{}.png".format(str(i))
        bg_img.append(pygame.image.load(bg_file))
    back_file = PATH + "back.png"
    back_img = pygame.image.load(back_file)
    play_file = PATH + "play.png"
    play_img = pygame.image.load(play_file)
    num = com.get_number()
    screen_iter, n = 0, 0
    pygame.time.set_timer(pygame.USEREVENT, 500)
    while True:
        if RESIZE:
            font_size = int(height / 20)
            font = pygame.font.Font(font_file, font_size)
            h_shift = int(height / 14 - height / 40)
            # Background
            bg = pygame.transform.scale(bg_img[n], size)
            bgrect = bg.get_rect()
            bgrect[0], bgrect[1] = w_offset, h_offset
            # Back button
            icon_size = min(int(height * 21 / 216), int(width * 7 / 128))
            back_scale = (icon_size, icon_size)
            back = pygame.transform.scale(back_img, back_scale)
            backrect = back.get_rect()
            backrect[0], backrect[1] = w_offset, int(height * 185 /
                                                     216) + h_offset
            if num == 0:
                play_scale = (int(width / 3), int(height * 33 / 216))
                play = pygame.transform.scale(play_img, play_scale)
                playrect = play.get_rect()
                playrect[0] = int(width / 3) + w_offset
                playrect[1] = int(height * 150 / 216) + h_offset
            RESIZE = False
        # MAINLOOP
        if com.game_started and com.got_list:
            game(com, backend)
            RESIZE = True
            return None

        for event in pygame.event.get():
            # EVENTS HANDLING
            # MOUSE EVENTS
            if event.type == pygame.MOUSEBUTTONDOWN:
                if backrect.collidepoint(event.pos):
                    backend.exit()
                    return None
                if num == 0 and playrect.collidepoint(event.pos):
                    backend.play()
            # USER EVENTS
            if event.type == pygame.USEREVENT:
                n = screen_iter % 4
                screen_iter += 1
                bg = pygame.transform.scale(bg_img[n], size)
                bgrect = bg.get_rect()
                bgrect[0], bgrect[1] = w_offset, h_offset
            # KEYBOARD EVENTS
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
            # OTHER EVENTS
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None
            if event.type == pygame.VIDEORESIZE:
                check_resize(event)

        if not com.is_connected:
            disconnection(com, backend)
            RESIZE = True
            return None
        # RENDERING
        screen.fill(black)
        screen.blit(bg, bgrect)
        players = com.get_players_list()
        p_size = (int(width / 3), int(height / 7))
        p_pos = (int(width * 2 / 3) + w_offset, h_offset)
        prect = pygame.Rect(*p_pos, *p_size)
        for i in range(len(players)):
            plr = str(i + 1) + ". " + players[i][1]
            player_box = font.render(plr, True, (0xAD, 0xE5, 0xF3))
            while player_box.get_size()[0] + prect[0] > width + w_offset:
                plr = plr[:-1]
                player_box = font.render(plr, True, (0xAD, 0xE5, 0xF3))
            screen.blit(player_box, (prect[0], prect[1] + h_shift))
            prect[1] += int(height / 7)
        screen.blit(back, backrect)
        if num == 0:
            screen.blit(play, playrect)
        pygame.display.flip()
        CLOCK.tick(30)


def settings_menu(com, backend):
    """Inerface of settings menu."""
    def checker(IP, PORT):
        """Check data in settings fields."""
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

    def save_fun(*arg):
        """Save ip and port."""
        nonlocal bg, bgrect, ip_text, port_text, bg_img
        if checker(ip_text, port_text):
            backend.set_connection_params(ip_text, int(port_text))
            global SETTINGS
            SETTINGS = True
            com.is_connected = False
            bg_name = PATH + "BG_settings_saved.png"
            bg_img = pygame.image.load(bg_name)
            bg = pygame.transform.scale(bg_img, size)
            bgrect = bg.get_rect()
            bgrect[0], bgrect[1] = w_offset, h_offset
            ip_text = ""
            port_text = ""
        else:
            bg_name = PATH + "BG_settings_not_saved.png"
            bg_img = pygame.image.load(bg_name)
            bg = pygame.transform.scale(bg_img, size)
            bgrect = bg.get_rect()
            bgrect[0], bgrect[1] = w_offset, h_offset

    global EXIT, RESIZE
    RESIZE = True

    ip_text, port_text = "", ""
    inactive_color = 0xFF, 0xFF, 0xFF
    active_color = 0xAD, 0xE5, 0xF3
    bg_file = PATH + "BG_settings.png"
    bg_img = pygame.image.load(bg_file)
    back_file = PATH + "back.png"
    back_img = pygame.image.load(back_file)
    save_file = PATH + "save.png"
    save_img = pygame.image.load(save_file)
    while True:
        if RESIZE:
            shift = int(height / 120)
            # Text
            font_size = int(height / 30)
            font = pygame.font.Font(font_file, font_size)
            ip_active = False
            port_active = False
            # Text box for ip
            ip_size = (int(width / 3), int(height * 3 / 60))
            ip_pos = (int(width / 3) + w_offset,
                      int(height * 53 / 216) + h_offset)
            iprect = pygame.Rect(*ip_pos, *ip_size)
            ip_color = inactive_color
            # Text box for port
            port_size = (int(width / 3), int(height * 3 / 60))
            port_pos = (int(width / 3) + w_offset,
                        int(height * 137 / 216) + h_offset)
            portrect = pygame.Rect(*port_pos, *port_size)
            port_color = inactive_color
            # Background
            bg = pygame.transform.scale(bg_img, size)
            bgrect = bg.get_rect()
            bgrect[0], bgrect[1] = w_offset, h_offset
            # Back button
            icon_size = min(int(height * 21 / 216), int(width * 7 / 128))
            back_scale = (icon_size, icon_size)
            back = pygame.transform.scale(back_img, back_scale)
            backrect = back.get_rect()
            backrect[0], backrect[1] = w_offset, int(height * 185
                                                     / 216) + h_offset
            # Save buton
            save_scale = (int(width * 7 / 128), int(height * 12 / 216))
            save = pygame.transform.scale(save_img, save_scale)
            saverect = save.get_rect()
            saverect[0] = int(width * 227 / 480) + w_offset
            saverect[1] = int(height * 7 / 9) + h_offset
            RESIZE = False
        # MAINLOOP
        for event in pygame.event.get():
            # MOUSE EVENTS
            if event.type == pygame.MOUSEBUTTONDOWN:
                if backrect.collidepoint(event.pos):
                    backend.exit()
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
            # KEYBOARD EVENTS
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
                    elif len(ip_text) < 16:
                        ip_text += event.unicode
                elif port_active:
                    if event.key == pygame.K_RETURN:
                        ip_active = False
                        port_active = False
                        save_fun()
                    elif event.key == pygame.K_BACKSPACE:
                        port_text = port_text[:-1]
                    elif len(port_text) < 6:
                        port_text += event.unicode
            # OTHER EVENTS
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None
            if event.type == pygame.VIDEORESIZE:
                check_resize(event)

        # RENDERING
        screen.fill(black)
        ip_color = active_color if ip_active else inactive_color
        port_color = active_color if port_active else inactive_color
        screen.blit(bg, bgrect)
        screen.blit(back, backrect)
        screen.blit(save, saverect)
        ip_box = font.render(ip_text, True, ip_color)
        port_box = font.render(port_text, True, port_color)
        screen.blit(ip_box, (iprect[0] + shift, iprect[1] + shift))
        screen.blit(port_box, (portrect[0] + shift, portrect[1] + shift))
        pygame.draw.rect(screen, ip_color, iprect, 2)
        pygame.draw.rect(screen, port_color, portrect, 2)
        pygame.display.flip()
        CLOCK.tick(30)


def rule_menu(com, backend):
    """Draw rule menu interface."""
    global EXIT, RESIZE
    RESIZE = True
    bg_file = PATH + "rule_menu.png"
    bg_img = pygame.image.load(bg_file)
    back_file = PATH + "back.png"
    back_img = pygame.image.load(back_file)

    while True:
        if RESIZE:
            # Background
            bg_rule = pygame.transform.scale(bg_img, size)
            bg_rulerect = bg_rule.get_rect()
            bg_rulerect[0], bg_rulerect[1] = w_offset, h_offset
            # Back button
            icon_size = min(int(height * 21 / 216), int(width * 7 / 128))
            back_scale = (icon_size, icon_size)
            back = pygame.transform.scale(back_img, back_scale)
            backrect = back.get_rect()
            backrect[0], backrect[1] = w_offset, int(height * 185 /
                                                     216) + h_offset

            # RENDERING
            screen.fill(black)
            screen.blit(bg_rule, bg_rulerect)
            screen.blit(back, backrect)
            pygame.display.flip()

            RESIZE = False
        # MAINLOOP
        for event in pygame.event.get():
            # EVENTS HANDLING
            # MOUSE EVENTS
            if event.type == pygame.MOUSEBUTTONDOWN:
                if backrect.collidepoint(event.pos):
                    backend.exit()
                    return None
            # KEYBOARD EVENTS
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
            # OTHER EVENTS
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None
            if event.type == pygame.VIDEORESIZE:
                check_resize(event)

        CLOCK.tick(30)


def play_menu_2(com, backend):
    """Draw name intersection interface."""
    def save_fun(*arg):
        """Save Name."""
        nonlocal bg, bgrect, name_text
        if name_text.isalnum():
            backend.set_name(name_text)
            name_text = ""
            wait_menu(com, backend)
            backend.exit()
            return True
        else:
            bg_file = PATH + "BG_name_bad.png"
            bg_img = pygame.image.load(bg_file)
            bg = pygame.transform.scale(bg_img, size)
            bgrect = bg.get_rect()
            bgrect[0], bgrect[1] = w_offset, h_offset
            return False

    global EXIT, RESIZE
    RESIZE = True

    bg_file = PATH + "BG_name.png"
    bg_img = pygame.image.load(bg_file)
    back_file = PATH + "back.png"
    back_img = pygame.image.load(back_file)
    ok_file = PATH + "ok.png"
    ok_img = pygame.image.load(ok_file)
    inactive_color = 0xFF, 0xFF, 0xFF
    active_color = 0xAD, 0xE5, 0xF3
    name_active = False
    name_text = ""
    name_full = ""
    shift = int(height / 120)

    while True:
        if RESIZE:
            shift = int(height / 120)
            # Background
            bg = pygame.transform.scale(bg_img, size)
            bgrect = bg.get_rect()
            bgrect[0], bgrect[1] = w_offset, h_offset
            # Back button
            icon_size = min(int(height * 21 / 216), int(width * 7 / 128))
            back_scale = (icon_size, icon_size)
            back = pygame.transform.scale(back_img, back_scale)
            backrect = back.get_rect()
            backrect[0], backrect[1] = w_offset, int(height * 185
                                                     / 216) + h_offset
            # Text
            font_size = int(height / 30)
            font = pygame.font.Font(font_file, font_size)
            # Text box aka Entry
            namebox_size = (int(width / 3), int(height * 3 / 60))
            namebox_pos = (int(width / 3) + w_offset,
                           int(height * 53 / 216) + h_offset)
            namerect = pygame.Rect(*namebox_pos, *namebox_size)
            name_color = inactive_color
            name_text = name_full
            name_box = font.render(name_text, True, name_color)
            while name_box.get_size()[0] > namebox_size[0] - shift:
                name_text = name_text[:-1]
                name_box = font.render(name_text, True, name_color)
            # OK button
            ok_scale = (int(width / 3), int(height * 33 / 216))
            ok = pygame.transform.scale(ok_img, ok_scale)
            okrect = ok.get_rect()
            okrect[0] = int(width / 3) + w_offset
            okrect[1] = int(height * 115 / 216) + h_offset
            RESIZE = False

        # MAINLOOP
        for event in pygame.event.get():
            # EVENTS HANDLING
            # MOUSE EVENTS
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
            # KEYBOARD EVENTS
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
                        name_full = name_full[:-1]
                    else:
                        name_full += event.unicode
                    name_text = name_full
                    name_box = font.render(name_text, True, name_color)
                    while name_box.get_size()[0] > namebox_size[0] - shift:
                        name_text = name_text[:-1]
                        name_full = name_full[:-1]
                        name_box = font.render(name_text, True, name_color)
            # OTHER EVENTS
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None
            if event.type == pygame.VIDEORESIZE:
                check_resize(event)

        # RENDERING
        screen.fill(black)
        name_color = active_color if name_active else inactive_color
        screen.blit(bg, bgrect)
        screen.blit(back, backrect)
        screen.blit(ok, okrect)
        name_box = font.render(name_text, True, name_color)
        name_pos = (namerect[0] + shift, namerect[1] + shift)
        screen.blit(name_box, name_pos)
        pygame.draw.rect(screen, name_color, namerect, 2)
        pygame.display.flip()
        CLOCK.tick(30)


def disconnection(com, backend):
    """Disdpaying if backend can't connect to server."""
    global EXIT, RESIZE
    RESIZE = True

    bg_file = PATH + "BG_disconnect.png"
    bg_img = pygame.image.load(bg_file)
    ok_file = PATH + "ok.png"
    ok_img = pygame.image.load(ok_file)
    while True:
        if RESIZE:
            # Background
            bg = pygame.transform.scale(bg_img, size)
            bgrect = bg.get_rect()
            bgrect[0], bgrect[1] = w_offset, h_offset
            # Ok button
            ok_scale = (int(width / 3), int(height * 33 / 216))
            ok = pygame.transform.scale(ok_img, ok_scale)
            okrect = ok.get_rect()
            okrect[0] = int(width / 3) + w_offset
            okrect[1] = int(height * 115 / 216) + h_offset

            # RENDERING
            screen.fill(black)
            screen.blit(bg, bgrect)
            screen.blit(ok, okrect)
            pygame.display.flip()

            RESIZE = False

        # MAINLOOP
        for event in pygame.event.get():
            # EVENTS HANDLING
            # MOUSE EVENTS
            if event.type == pygame.MOUSEBUTTONDOWN:
                if okrect.collidepoint(event.pos):
                    return None
            # KEYBOARD EVENTS
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
            # OTHER EVENTS
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None
            if event.type == pygame.VIDEORESIZE:
                check_resize(event)

        CLOCK.tick(30)


def connection(com, backend):
    """Wait to connection to server."""
    global EXIT, RESIZE
    RESIZE = True

    bg_img = []
    for i in range(4):
        bg_name = PATH + "BG_{}.png".format(str(i))
        bg_img.append(pygame.image.load(bg_name))
    n, count = 0, 0
    pygame.time.set_timer(pygame.USEREVENT, 500)

    while count < 20:
        if RESIZE:
            # Background
            bg = pygame.transform.scale(bg_img[n], size)
            bgrect = bg.get_rect()
            bgrect[0], bgrect[1] = w_offset, h_offset
            RESIZE = False

        # MAINLOOP
        if com.is_connected:
            return True
        for event in pygame.event.get():
            # EVENTS HANDLING
            # USER EVENTS
            if event.type == pygame.USEREVENT:
                n = count % 4
                count += 1
                bg = pygame.transform.scale(bg_img[n], size)
                bgrect = bg.get_rect()
                bgrect[0], bgrect[1] = w_offset, h_offset
            # KEYBOARD EVENTS
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
            # OTHER EVENTS
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None
            if event.type == pygame.VIDEORESIZE:
                check_resize(event)

        # RENDERING
        screen.fill(black)
        screen.blit(bg, bgrect)
        pygame.display.flip()
        CLOCK.tick(30)

    disconnection(com, backend)
    return False


def play_menu(com, backend):
    """DRAW PLAY MENU INTERFACE FOR MASTER (FIRST) PLAYER OR DOWNLOADING
    RESOURCES INTERFACE."""
    global EXIT, SETTINGS, RESIZE
    RESIZE = True

    if not SETTINGS:
        # If the player hasn't specified connection parameters
        settings_menu(com, backend)
        return None
    global UPD
    if not UPD:
        backend.start_game()
    if not connection(com, backend):
        return None

    # Start connection
    num = com.get_number()
    if num == 0:
        # First player interface
        bg_file = PATH + "BG_main.png"
        bg_img = pygame.image.load(bg_file)
        back_file = PATH + "back.png"
        back_img = pygame.image.load(back_file)
        mode_img = []
        m_file = PATH + "classic.png"
        mode_img.append(pygame.image.load(m_file))
        m_file = PATH + "ariadna.png"
        mode_img.append(pygame.image.load(m_file))
        m_file = PATH + "himera.png"
        mode_img.append(pygame.image.load(m_file))
        m_file = PATH + "Odiseya.png"
        mode_img.append(pygame.image.load(m_file))
        m_file = PATH + "pandora.png"
        mode_img.append(pygame.image.load(m_file))
        m_file = PATH + "persefona.png"
        mode_img.append(pygame.image.load(m_file))
        selected_mode = ["imaginarium", "ariadna", "himera",
                         "odissey", "pandora", "persephone"]
        RESIZE = True
        while True:
            if RESIZE:
                # Background
                bg = pygame.transform.scale(bg_img, size)
                bgrect = bg.get_rect()
                bgrect[0], bgrect[1] = w_offset, h_offset
                # Back button
                icon_size = min(int(height * 21 / 216), int(width * 7 / 128))
                back_scale = (icon_size, icon_size)
                back = pygame.transform.scale(back_img, back_scale)
                backrect = back.get_rect()
                backrect[0], backrect[1] = w_offset, int(height * 185 /
                                                         216) + h_offset
                # Mods buttons
                m = int(width / 5)
                mode_size = (m, m)
                w_shift, h_shift = int((width - m * 3) /
                                       4), int((height - m * 2) / 3)
                w_pos, h_pos = w_shift, h_shift
                mode, mode_rect = [], []
                for i in range(len(mode_img)):
                    mode.append(pygame.transform.scale(mode_img[i], mode_size))
                    mode_rect.append(mode[i].get_rect())
                    mode_rect[i][0] = w_pos + w_offset
                    mode_rect[i][1] = h_pos + h_offset
                    w_pos += w_shift + m
                    if i == 2:
                        w_pos, h_pos = w_shift, h_shift * 2 + m

                # RENDERING
                screen.fill(black)
                screen.blit(bg, bgrect)
                screen.blit(back, backrect)
                for i in range(len(mode)):
                    screen.blit(mode[i], mode_rect[i])
                pygame.display.flip()

                RESIZE = False

            # MAINLOOP
            for event in pygame.event.get():
                # EVENTS HANDLING
                # MOUSE EVENTS
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if backrect.collidepoint(event.pos):
                        backend.exit()
                        return None
                    for i in range(len(mode_rect)):
                        if mode_rect[i].collidepoint(event.pos):
                            backend.set_mode(selected_mode[i])
                            play_menu_2(com, backend)
                            return None
                # KEYBOARD EVENTS
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        backend.stop()
                        pygame.quit()
                        EXIT = True
                        return None
                # OTHER EVENTS
                if event.type == pygame.QUIT:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
                if event.type == pygame.VIDEORESIZE:
                    check_resize(event)

            CLOCK.tick(30)

    elif num > 0:
        # Not first player
        play_menu_2(com, backend)
        return None
    else:
        # Download interface
        RESIZE = True
        sound = True
        bg_img = []
        for i in range(4):
            bg_name = PATH + "upd_{}.png".format(str(i))
            bg_img.append(pygame.image.load(bg_name))
        bg = pygame.transform.scale(pygame.image.load(bg_name), size)
        bgrect = bg.get_rect()
        bgrect[0], bgrect[1] = w_offset, h_offset
        p_file = PATH + "bar.png"
        progress_img = pygame.image.load(p_file)
        progress = pygame.transform.scale(progress_img, (0, int(height / 6)))
        progress_rect = progress.get_rect()
        progress_rect[0] = w_offset
        progress_rect[1] = int(height * 2 / 3) + h_offset
        screen_iter, n = 0, 0
        color = 0xAD, 0xE5, 0xF3

        pygame.time.set_timer(pygame.USEREVENT, 1000)

        while not com.updated:
            if RESIZE:
                bg = pygame.transform.scale(bg_img[n], size)
                bgrect = bg.get_rect()
                bgrect[0], bgrect[1] = w_offset, h_offset
                mul = com.get_progress()
                p_size = (int(width * mul / 3), int(height / 20))
                progress = pygame.transform.scale(progress_img, p_size)
                progress_rect = progress.get_rect()
                progress_rect[0] = w_offset + int(width / 3)
                progress_rect[1] = int(height * 2 / 3) + h_offset
                rect_rect = [w_offset + int(width / 3),
                             h_offset + int(height * 2 / 3),
                             int(width / 3),
                             int(height / 20)]

                # RENDERING
                screen.fill(black)
                screen.blit(bg, bgrect)
                pygame.draw.rect(screen, color, rect_rect, 2)
                pygame.display.flip()

                RESIZE = False

            # MAINLOOP
            for event in pygame.event.get():
                # EVENTS HANDLING
                # USER EVENTS
                if event.type == pygame.USEREVENT:
                    n = screen_iter % 4
                    screen_iter += 1
                    bg = pygame.transform.scale(bg_img[n], size)
                    bgrect = bg.get_rect()
                    bgrect[0], bgrect[1] = w_offset, h_offset
                    mul = com.get_progress()
                    if mul > 0.5 and sound:
                        sound = False
                        pygame.mixer.music.load(PATH + "/../Sounds/load.mp3")
                        pygame.mixer.music.play()
                    p_size = (int(width * mul / 3), int(height / 20))
                    progress = pygame.transform.scale(progress_img, p_size)
                    progress_rect = progress.get_rect()
                    progress_rect[0] = w_offset + int(width / 3)
                    progress_rect[1] = int(height * 2 / 3) + h_offset
                # KEYBOARD EVENTS
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        backend.stop()
                        pygame.quit()
                        EXIT = True
                        return None
                # OTHER EVENTS
                if event.type == pygame.QUIT:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
                if event.type == pygame.VIDEORESIZE:
                    check_resize(event)

            if not com.is_connected:
                disconnection(com, backend)
                RESIZE = True
                return None
            screen.blit(bg, bgrect)
            screen.blit(progress, progress_rect)
            pygame.draw.rect(screen, color, rect_rect, 2)
            pygame.display.flip()
            CLOCK.tick(30)
        UPD = True


def main_menu(com, backend):
    """DRAW MAIN MENU INTERFACE."""
    global EXIT, RESIZE
    RESIZE = True
    bg_file = PATH + "BG.png"
    bg_img = pygame.image.load(bg_file)
    play_file = PATH + "play.png"
    play_img = pygame.image.load(play_file)
    exit_file = PATH + "exit.png"
    exit_img = pygame.image.load(exit_file)
    settings_file = PATH + "settings.png"
    settings_img = pygame.image.load(settings_file)
    rule_file = PATH + "rule.png"
    rule_img = pygame.image.load(rule_file)
    while True:
        if RESIZE:
            # Background
            bg = pygame.transform.scale(bg_img, size)
            bgrect = bg.get_rect()
            bgrect[0], bgrect[1] = w_offset, h_offset
            # Play button
            play_scale = (int(width / 3), int(height * 33 / 216))
            play = pygame.transform.scale(play_img, play_scale)
            playrect = play.get_rect()
            playrect[0] = int(width / 3) + w_offset
            playrect[1] = int(height * 64 / 216) + h_offset
            # Exit button
            exit_scale = (int(width / 3), int(height * 33 / 216))
            exit_img = pygame.transform.scale(exit_img, exit_scale)
            exitrect = exit_img.get_rect()
            exitrect[0] = int(width / 3) + w_offset
            exitrect[1] = int(height * 115 / 216) + h_offset
            # Settings button
            icon_size = min(int(height * 21 / 216), int(width * 7 / 128))
            settings_scale = (icon_size, icon_size)
            settings = pygame.transform.scale(settings_img, settings_scale)
            settingsrect = settings.get_rect()
            settingsrect[0] = w_offset
            settingsrect[1] = int(height * 185 / 216) + h_offset
            # Rule button
            rule_scale = settings_scale
            rule = pygame.transform.scale(rule_img, rule_scale)
            rulerect = rule.get_rect()
            rule_offset = int(width - rule_scale[0])
            rulerect[0] = rule_offset + w_offset
            rulerect[1] = int(height * 185 / 216) + h_offset

            # RENDERING
            screen.fill(black)
            screen.blit(bg, bgrect)
            screen.blit(play, playrect)
            screen.blit(exit_img, exitrect)
            screen.blit(settings, settingsrect)
            screen.blit(rule, rulerect)
            pygame.display.flip()

            RESIZE = False
        # MAINLOOP
        for event in pygame.event.get():
            # EVENTS HANDLING
            # MOUSE EVENTS
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exitrect.collidepoint(event.pos):
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
                elif settingsrect.collidepoint(event.pos):
                    settings_menu(com, backend)
                    RESIZE = True
                    if EXIT:
                        return None
                elif rulerect.collidepoint(event.pos):
                    rule_menu(com, backend)
                    RESIZE = True
                    if EXIT:
                        return None
                elif playrect.collidepoint(event.pos):
                    global UPD
                    UPD = False
                    play_menu(com, backend)
                    if UPD:
                        play_menu(com, backend)
                    RESIZE = True
                    if EXIT:
                        return None
            # KEYBOARD EVENTS
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    backend.stop()
                    pygame.quit()
                    EXIT = True
                    return None
            # OTHER EVENTS
            if event.type == pygame.QUIT:
                backend.stop()
                pygame.quit()
                EXIT = True
                return None
            if event.type == pygame.VIDEORESIZE:
                check_resize(event)

        CLOCK.tick(30)


def init_interface(com, backend):
    """Init all interfaces."""
    global SETTINGS, TURN
    TURN = True
    SETTINGS = com.ip is not None
    main_menu(com, backend)
