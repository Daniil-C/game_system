import sys
import pygame

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
black = 0, 0, 0

info = pygame.display.Info()
size = width, height = info.current_w, info.current_h
print(size)

SETTINGS = False


def wait_menu(com, backend):
    """Wait players"""
    font_size = int(height / 10)
    font = pygame.font.SysFont("Chilanka", font_size)
    w_shift = int(height / 120)
    h_shift = int(height / 14 - height / 20)
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

#   num = com.get_number()
    num = 0
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

        for event in pygame.event.get():
            """EVENTS HANDLING"""

            """MOUSE EVENTS"""
            if event.type == pygame.MOUSEBUTTONDOWN:
                if backrect.collidepoint(event.pos):
#                   backend.exit()
                    return None

            """KEYBOARD EVENTS"""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()

            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                sys.exit()

        clock.tick(2)

        """RENDERING"""
        screen.blit(BG, BGrect)
#       players = backend.get_players_list()
        players = [["num", 1], ["vfhkg", 3], ["cfc", 2]]
        p_size = (int(width / 3), int(height / 7))
        p_pos = (int(width * 2 / 3), 0)
        prect = pygame.Rect(p_pos[0], p_pos[1], p_size[0], p_size[1])
        for i in range(len(players)):
            plr = str(i + 1) + ". " + players[i][0]
            player_box = font.render(plr, True, (0xAD, 0xE5, 0xF3))
            screen.blit(player_box, (prect[0] + w_shift, prect[1] + h_shift))
            pygame.draw.rect(screen, (0xAD, 0xE5, 0xF3), prect, 2)
            prect[1] += int(height / 7)
        screen.blit(back, backrect)
        if num == 0:
            screen.blit(play, playrect)
        pygame.display.flip()


def settings_menu(com, backend):
    """settings menu"""

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
#           backend.set_connection_params(ip_text, int(port_text))
            global SETTINGS
            SETTINGS = True
#           com.is_connected = False
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
    font = pygame.font.SysFont("Chilanka", font_size)
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
#                   backend.exit()
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
                    sys.exit()
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
                sys.exit()

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
    """Background"""
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
#                    backend.exit()
                    return None
            """KEYBOARD EVENTS"""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()

            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                sys.exit()

        """RENDERING"""
        screen.blit(BG_rule, BG_rulerect)
        screen.blit(back, backrect)
        pygame.display.flip()


def play_menu_2(com, backend):
    """DRAW NAME INSERTION INTERFACE"""
    """Background"""
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
    font = pygame.font.SysFont("Chilanka", font_size)
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
#           backend.set_name(name_text)
            name_text = ""
            wait_menu(com, backend)
#           backend.exit()
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
#                   backend.exit()
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
                    sys.exit()
                if name_active:
                    if event.key == pygame.K_RETURN:
                        name_active = False
                        save_fun()
                    elif event.key == pygame.K_BACKSPACE:
                        name_text = name_text[:-1]
                    elif len(name_text) < 20:
                        name_text += event.unicode

            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                sys.exit()

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
    """Background"""
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
                    sys.exit()

            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                sys.exit()

        """RENDERING"""
        screen.blit(BG, BGrect)
        screen.blit(ok, okrect)
        pygame.display.flip()


def connection(com, backend):
    """Wait to connection"""
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

#       if com.is_connected:
#           return True
        if i == 19:
            return True

        for event in pygame.event.get():
            """EVENTS HANDLING"""

            """KEYBOARD EVENTS"""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()

            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                sys.exit()

        clock.tick(2)

        """RENDERING"""
        screen.blit(BG, BGrect)
        pygame.display.flip()
    disconnection()
    global SETTINGS
    SETTINGS = False
    return False


def play_menu(com, backend):
    """DRAW PLAY MENU INTERFACE FOR MASTER (FIRST) PLAYER OR DOWNLOADING RESOURCES INTERFACE"""
    while not SETTINGS:
        """If the player hasn't specified connection parameters"""
        settings_menu(com, backend)
        return None
    if not connection(com, backend):
        return None

    """Start connection"""
#   backend.start_game()
#   num = com.get_number()
    num = 0        # number of the player
    if num == 0:
        """First player interface"""
        """Background"""
        BG = pygame.transform.scale(pygame.image.load("interface/BG_main.png"), size)
        BGrect = BG.get_rect()

        """Back button"""
        back_scale = (int(height * 21 / 216), int(height * 21 / 216))
        back = pygame.transform.scale(pygame.image.load("interface/back.png"), back_scale)
        backrect = back.get_rect()
        backrect[0] = 0
        backrect[1] = int(height * 185 / 216)

        """Mode 1 button"""
        mode1_scale = (int(width / 6), int(width / 6))
        mode1 = pygame.transform.scale(pygame.image.load("interface/classic.png"), mode1_scale)
        mode1rect = mode1.get_rect()
        mode1rect[0] = int(width / 8)
        mode1rect[1] = int(height * 29 / 216)

        """Mode 2 button"""
        mode2_scale = (int(width / 6), int(width / 6))
        mode2 = pygame.transform.scale(pygame.image.load("interface/ariadna.png"), mode2_scale)
        mode2rect = mode2.get_rect()
        mode2rect[0] = int(width * 5 / 12)
        mode2rect[1] = int(height * 29 / 216)

        """Mode 3 button"""
        mode3_scale = (int(width / 6), int(width / 6))
        mode3 = pygame.transform.scale(pygame.image.load("interface/himera.png"), mode3_scale)
        mode3rect = mode3.get_rect()
        mode3rect[0] = int(width * 17 / 24)
        mode3rect[1] = int(height * 29 / 216)

        """Mode 4 button"""
        mode4_scale = (int(width / 6), int(width / 6))
        mode4 = pygame.transform.scale(pygame.image.load("interface/Odiseya.png"), mode4_scale)
        mode4rect = mode4.get_rect()
        mode4rect[0] = int(width / 8)
        mode4rect[1] = int(height * 122 / 216)

        """Mode 5 button"""
        mode5_scale = (int(width / 6), int(width / 6))
        mode5 = pygame.transform.scale(pygame.image.load("interface/pandora.png"), mode5_scale)
        mode5rect = mode5.get_rect()
        mode5rect[0] = int(width * 5 / 12)
        mode5rect[1] = int(height * 122 / 216)

        """Mode 6 button"""
        mode6_scale = (int(width / 6), int(width / 6))
        mode6 = pygame.transform.scale(pygame.image.load("interface/persefona.png"), mode6_scale)
        mode6rect = mode6.get_rect()
        mode6rect[0] = int(width * 17 / 24)
        mode6rect[1] = int(height * 122 / 216)

        while True:
            """MAINLOOP"""
            for event in pygame.event.get():
                """EVENTS HANDLING"""

                """MOUSE EVENTS"""
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if backrect.collidepoint(event.pos):
#                       backend.exit()
                        return None
                    if mode1rect.collidepoint(event.pos):
#                       backend.set_mode(4)
                        play_menu_2(com, backend)
                        return None
                    if mode2rect.collidepoint(event.pos):
#                       backend.set_mode(4)
                        play_menu_2(com, backend)
                        return None
                    if mode3rect.collidepoint(event.pos):
#                       backend.set_mode(4)
                        play_menu_2(com, backend)
                        return None
                    if mode4rect.collidepoint(event.pos):
#                       backend.set_mode(4)
                        play_menu_2(com, backend)
                        return None
                    if mode5rect.collidepoint(event.pos):
#                       backend.set_mode(5)
                        play_menu_2(com, backend)
                        return None
                    if mode6rect.collidepoint(event.pos):
#                       backend.set_mode(6)
                        play_menu_2(com, backend)
                        return None

                """KEYBOARD EVENTS"""
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()

                """OTHER EVENTS"""
                if event.type == pygame.QUIT:
                    sys.exit()

            """RENDERING"""
            screen.blit(BG, BGrect)
            screen.blit(back, backrect)
            screen.blit(mode1, mode1rect)
            screen.blit(mode2, mode2rect)
            screen.blit(mode3, mode3rect)
            screen.blit(mode4, mode4rect)
            screen.blit(mode5, mode5rect)
            screen.blit(mode6, mode6rect)
            pygame.display.flip()

    elif num > 0:
        """Not first player"""
        play_menu_2(com, backend)
        return None
    else:
        """Download interface"""
        clock = pygame.time.Clock()
        """Background"""
        BG = pygame.transform.scale(pygame.image.load("interface/BG_main.png"), size)
        BGrect = BG.get_rect()

        """Back button"""
        back_scale = (int(height * 21 / 216), int(height * 21 / 216))
        back = pygame.transform.scale(pygame.image.load("interface/back.png"), back_scale)
        backrect = back.get_rect()
        backrect[0] = 0
        backrect[1] = int(height * 185 / 216)

#       while not backend.end.upd():
        for i in range(15):
            """MAINLOOP"""
            for event in pygame.event.get():
                """EVENTS HANDLING"""

                """MOUSE EVENTS"""
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if backrect.collidepoint(event.pos):
#                       backend.exit()
                        return None

                """KEYBOARD EVENTS"""
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()

                """OTHER EVENTS"""
                if event.type == pygame.QUIT:
                    sys.exit()

            clock.tick(1)

            """RENDERING"""
            screen.blit(BG, BGrect)
            screen.blit(back, backrect)
            pygame.display.flip()

        return None


def main_menu(com, backend):
    """DRAW MAIN MENU INTERFACE"""
    """Background"""
    BG = pygame.transform.scale(pygame.image.load("interface/BG.png"), size)
    BGrect = BG.get_rect()

    """Play button"""
    play_scale = (int(width / 3), int(height * 33 / 216))
    play = pygame.transform.scale(pygame.image.load("interface/play.png"), play_scale)
    playrect = play.get_rect()
    playrect[0] = int(width / 3)
    playrect[1] = int(height * 64 / 216)

    """Exit button"""
    exit_scale = (int(width / 3), int(height * 33 / 216))
    exit = pygame.transform.scale(pygame.image.load("interface/exit.png"), exit_scale)
    exitrect = exit.get_rect()
    exitrect[0] = int(width / 3)
    exitrect[1] = int(height * 115 / 216)

    """Settings button"""
    settings_scale = (int(height * 21 / 216), int(height * 21 / 216))
    settings = pygame.transform.scale(pygame.image.load("interface/settings.png"), settings_scale)
    settingsrect = settings.get_rect()
    settingsrect[0] = 0
    settingsrect[1] = int(height * 185 / 216)

    """Rule button"""
    rule_scale = settings_scale = (int(height * 21 / 216), int(height * 21 / 216))
    rule = pygame.transform.scale(pygame.image.load("interface/rule.png"), rule_scale)
    rulerect = rule.get_rect()
    rule_offset = int(width - rule_scale[0])
    rulerect[0] = rule_offset
    rulerect[1] = int(height * 185 / 216)

    while True:
        """MAINLOOP"""
        for event in pygame.event.get():
            """EVENTS HANDLING"""

            """MOUSE EVENTS"""
            if event.type == pygame.MOUSEBUTTONDOWN: 
                if exitrect.collidepoint(event.pos):
                    sys.exit()
                elif settingsrect.collidepoint(event.pos):
                    settings_menu(com, backend)
                elif rulerect.collidepoint(event.pos):
                    rule_menu(com, backend)
                elif playrect.collidepoint(event.pos):
                    play_menu(com, backend)

            """KEYBOARD EVENTS"""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()

            """OTHER EVENTS"""
            if event.type == pygame.QUIT:
                sys.exit()

        """RENDERING"""
        screen.blit(BG, BGrect)
        screen.blit(play, playrect)
        screen.blit(exit, exitrect)
        screen.blit(settings, settingsrect)
        screen.blit(rule, rulerect)
        pygame.display.flip()


def init_interface(com, backend):
    main_menu(com, backend)

init_interface(-1, -1)
