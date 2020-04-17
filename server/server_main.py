import socket
from connection import connection
import threading
import readline
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import server.environment as env
import time
from random import shuffle, randrange


class monitor:
    def __init__(self):
        object.__setattr__(self, "_monitor_sem", threading.Semaphore(1))

    def __setattr__(self, name, value):
        object.__getattribute__(self, "_monitor_sem").acquire()
        object.__setattr__(self, name, value)
        object.__getattribute__(self, "_monitor_sem").release()

    def __getattribute__(self, name):
        object.__getattribute__(self, "_monitor_sem").acquire()
        val = object.__getattribute__(self, name)
        object.__getattribute__(self, "_monitor_sem").release()
        return val


class resources(monitor):
    def __init__(self, res_name, res_link):
        monitor.__init__(self)
        self.name = res_name
        self.link = res_link


class HTTPHandler(SimpleHTTPRequestHandler):
    def __init__(*args, **kwargs):
        SimpleHTTPRequestHandler.__init__(*args, **kwargs)

    def log_message(self, format, *args):
        self.logger.info("HTTP: " + (format % args))

    log_error = log_message


class resource_server(monitor):
    def __init__(self, logger):
        monitor.__init__(self)
        self.logger = logger

    def main(self):
        ip = env.get_ip()
        port = env.get_res_port()

        handler = HTTPHandler
        handler.logger = self.logger
        self.server = HTTPServer((ip, port), (lambda *args, **kwargs:
                    handler(*args, directory="server/resources", **kwargs)))
        self.server.serve_forever(poll_interval=0.5)
        self.server.server_close()

    def start(self):
        self.thread = threading.Thread(target=resource_server.main,
                args=(self,))
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.thread.join()


class game_state(monitor):
    def __init__(self, initial_state):
        monitor.__init__(self)
        self.state = initial_state
        self.card_set = 0


class player(monitor):
    def __init__(self, sock, status, sem, m_sem, res, game_st, plist):
        monitor.__init__(self)
        self.player_socket = sock
        self.status = status
        self.control_sem = sem
        self.main_sem = m_sem
        self.conn = connection(self.player_socket)
        self.valid = True
        self.name = "Player"
        self.res = res
        self.game_st = game_st
        self.score = 0
        self.thread_active = False
        self.plist = plist
        self.get_broadcast = False
        self.cards = [ ]
        self.has_turn = False

    def start(self):
        self.thread = threading.Thread(target=player.main,
                    args=(self,))
        self.thread.start()
        self.thread_active = True

    def stop(self):
        self.valid = False
        if self.thread_active:
            self.control_sem.release()
            self.thread.join()
            self.thread_active = False
        if self.conn != None:
            self.conn.close()
            self.conn = None

    def main(self):
        self.check_version()
        if not self.valid:
            return
        if not self.conn.status:
            self.valid = False
            return
        self.get_broadcast = True
        self.plist.broadcast("#PLAYER_LIST")
        if self.status == "MASTER":
            self.player_socket.settimeout(0.1)
            while self.game_st.state == "PLAYER_CONN":
                try:
                    res = self.conn.get().split()
                except:
                    continue
                if len(res) == 2 and res[1].isnumeric() and res[0] == "START_GAME":
                    self.game_st.card_set = int(res[1])
                    self.game_st.state = "GAME"
                else:
                    self.valid = False
                    return
            self.player_socket.settimeout(None)
        self.control_sem.acquire()
        if not self.valid:
            return
        self.main_sem.release()
        if not self.valid:
            return
        self.control_sem.acquire()
        if not self.valid:
            return
        self.conn.send("BEGIN " + str(self.game_st.card_set) + " " +
                    ",".join([str(i) for i in self.cards]))
        res = self.conn.get()
        if not self.conn.status:
            self.valid = False
            return
        if res != "READY":
            self.valid = False
            return
        self.control_sem.acquire()
        if not self.valid:
            return
        self.main_sem.release()
        while self.game_st.state == "GAME":
            self.control_sem.acquire()
            if not self.valid:
                return
            if self.game_st.state != "GAME":
                break
            if not self.has_turn:
                res = self.conn.get().split()
                if len(res) != 2 or res[0] != "CARD" or not res[1].isnumeric():
                    self.valid = False
                    return
                self.current_card = int(res[1])
            self.plist.broadcast("#SELF", info=self)
            self.main_sem.release()
            self.control_sem.acquire()
            if not self.valid:
                return
            if not self.has_turn:
                res = self.conn.get().split()
                if len(res) != 2 or res[0] != "CARD" or not res[1].isnumeric():
                    self.valid = False
                    return
                self.selected_card = int(res[1])
            self.control_sem.acquire()
            self.main_sem.release()
            res = self.conn.get()
            if res != "NEXT_TURN":
                self.valid = False
                return
            self.main_sem.release()
            self.control_sem.acquire()
            if game_st.state != "GAME":
                return
            self.conn.send("CARDS " + ",".join(self.cards))

    def check_version(self):
        self.conn.send("VERSION " + self.res.name + " " + self.res.link)
        res = self.conn.get().split()
        if self.valid:
            if len(res) != 2 or res[0] != "OK":
                self.valid = False
            else:
                self.name = res[1]


class CLI(monitor):
    def __init__(self, players, game_st):
        monitor.__init__(self)
        self.players = players
        self.game_st = game_st
        readline.set_completer(self.completer)
        readline.set_completer_delims("")
        readline.parse_and_bind("tab: complete")
        self.work = False

    def start(self):
        self.thread = threading.Thread(target=CLI.main, args=(self,))
        self.thread.start()

    def stop(self):
        self.work = False
        self.thread.join()

    def main(self):
        self.work = True
        print("CLI started")
        while self.work:
            try:
                cmdline = input("\x1b[1;32m>\x1b[0m$ ").split()
            except Exception as ex:
                print("CLI: error:", str(ex))
                continue

            if not self.work:
                break

            if len(cmdline) == 0:
                continue

            try:
                if cmdline[0] == "help":
                    print("CLI commands:")
                    print("\thelp")
                    print("\tplayers")
                    print("\tstart <card set number>")
                    print("\tstatus")
                    print("\tstop")
                elif cmdline[0] == "players":
                    if self.players != None:
                        self.players.acquire()
                        print("CLI:", len(self.players.players), "players")
                        for i in self.players.players:
                            if i.status == "MASTER":
                                print(i.name, i.score, "M")
                            else:
                                print(i.name, i.score)
                        self.players.release()
                    else:
                        print("CLI: error: no player list available")
                elif cmdline[0] == "start":
                    if len(cmdline) == 2 and cmdline[1].isnumeric():
                        self.game_st.card_set = int(cmdline[1])
                        self.game_st.state = "GAME"
                        print("CLI: Starting game")
                    else:
                        print("CLI: error: expected start <card set number>")
                elif cmdline[0] == "stop":
                    self.game_st.state = "SHUTDOWN"
                    print("CLI: exit")
                    self.work = False
                elif cmdline[0] == "status":
                    print(self.game_st.state)
                else:
                    print("CLI: error: unknown command")
            except Exception as ex:
                print("CLI: error: " + str(ex))

    def completer(self, text, state):
        commands = ["help", "players", "start ", "status", "stop"]
        for i in commands:
            if i.startswith(text):
                if state == 0:
                    return i
                else:
                    state = state - 1
        return None


class disconnector(monitor):
    def __init__(self, sock, logger):
        monitor.__init__(self)
        self.sock = sock
        self.active = False
        self.logger = logger

    def start(self):
        self.active = True
        self.thread = threading.Thread(target=disconnector.main, args=(self,))
        self.thread.start()

    def stop(self):
        self.active = False
        self.thread.join()

    def main(self):
        while self.active:
            try:
                new_sock = self.sock.accept()
            except:
                continue
            self.logger.info("Disconnector: " + str(new_sock[1]))
            conn = connection(new_sock[0])
            conn.close()


class player_list(monitor):
    def __init__(self, logger, game_st):
        monitor.__init__(self)
        self.players = [ ]
        self.semaphores = [ ]
        self.main_semaphores = [ ]
        self.sem = threading.Semaphore(1)
        self.locked = False
        self.check = False
        self.master_lost = False
        self.logger = logger
        self.game_st = game_st

    def checker(self):
        while self.check:
            self.acquire()
            for i in range(len(self.players)):
                if not self.players[i].valid:
                    self.players[i].stop()
                    if self.players[i].status == "MASTER":
                        self.master_lost = True
                        if self.game_st.state == "PLAYER_CONN":
                            self.game_st.state = "ERROR"
                    del self.semaphores[i]
                    del self.main_semaphores[i]
                    del self.players[i]
                    if game_st.state == "PLAYER_CONN":
                        self.broadcast("#PLAYER_LIST")
                    break
            self.release()
            time.sleep(0.5)

    def start_check(self):
        self.check = True
        self.check_thread = threading.Thread(target=player_list.checker,
                    args=(self,))
        self.check_thread.start()

    def stop(self):
        self.check = False
        self.check_thread.join()
        for i in range(len(self.players)):
            self.players[i].stop()
        self.players.clear()
        self.semaphores.clear()
        self.main_semaphores.clear()

    def acquire(self):
        self.sem.acquire()
        self.locked = True

    def release(self):
        self.locked = False
        self.sem.release()

    def add_player(self, is_master, res, sock):
        self.acquire()
        control_sem = threading.Semaphore(0)
        main_sem = threading.Semaphore(0)
        new_player = player(sock, "MASTER" if is_master else "PLAYER",
                    control_sem, main_sem, res, self.game_st, self)
        new_player.start()
        self.players.append(new_player)
        self.semaphores.append(control_sem)
        self.main_semaphores.append(main_sem)
        self.release()

    def broadcast(self, data, info=None):
        if data == "#PLAYER_LIST":
            data = ("PLAYER_LIST " + ",".join([str(i) + ";" +
                        self.players[i].name
                        for i in range(len(self.players))]))
        if data == "#SELF":
            for i in range(len(self.players)):
                p = None
                if self.players[i] is info:
                    p = i
            if p != None:
                data = "PLAYER " + str(p)
            else:
                self.release()
                return
        for i in self.players:
            if i.get_broadcast and i.valid:
                i.conn.send(data)
                if not i.conn.status:
                    i.valid = False
                    i.stop()


class game_server:
    def __init__(self, listening_socket, logger):
        self.listening_socket = listening_socket
        self.logger = logger

    def main(self):
        game_st = game_state("PLAYER_CONN")
        cli = CLI(None, game_st)
        cli.start()

        while game_st.state != "SHUTDOWN":
            game_st.state = "PLAYER_CONN"
            players = player_list(self.logger, game_st)
            players.start_check()
            cards = [i for i in range(98)]
            shuffle(cards)

            res = resources("res", env.get_res_link())

            disc = disconnector(self.listening_socket, self.logger)

            cli.players = players

            first_player = False

            # player connection loop and version check
            res_server = resource_server(self.logger)
            res_server.start()

            while game_st.state == "PLAYER_CONN":
                try:
                    sock_info = self.listening_socket.accept()
                except:
                    continue

                players.add_player(not first_player, res, sock_info[0])
                first_player = True

            disc.start()
            res_server.stop()

            try:
                if game_st.state != "GAME":
                    raise Exception(game_st.state + " state detected, end game")

                if len(players.players) == 4:
                    cards = cards[:len(cards) - 2]
                elif len(players.players) == 5:
                    cards = cards[:len(cards) - 23]
                elif len(players.players) == 6:
                    cards = cards[:len(cards) - 26]

                players.acquire()
                for p in players.players:
                    p.control_sem.release()
                for p in players.players:
                    p.main_sem.acquire()
                for p in players.players:
                    p.cards = cards[:6]
                    cards = cards[6:]
                for p in players.players:
                    p.control_sem.release()
                players.release()

                players.acquire()
                for p in players.players:
                    p.control_sem.release()
                for p in players.players:
                    p.main_sem.acquire()
                players.release()

                # game loop
                while game_st.state == "GAME":
                    current_player = randrange(len(players.players))
                    while current_player >= len(players.players):
                        current_player -= 1
                    if current_player < 0:
                        raise Exception("No players left in game, exit")
                    for i in range(len(players.players)):
                        if i == current_player:
                            players.players[i].has_turn = True
                        else:
                            players.players[i].has_turn = False
                    players.broadcast("TURN " + str(current_player))
                    get = players.players[current_player].conn.get().split(maxsplit=2)
                    if not players.players[current_player].conn.status or len(get) != 3 or get[0] != "TURN":
                        players.players[current_player].stop()
                        continue
                    current_card = int(get[1])
                    players.players[current_player].current_card = current_card
                    players.players[current_player].selected_card = 0
                    players.acquire()
                    players.broadcast("ASSOC " + get[2])
                    for p in players.players:
                        p.control_sem.release()
                    players.release()
                    for p in players.players:
                        p.main_sem.acquire()
                    cards_list = [i.current_card for i in players.players]
                    players.broadcast("VOTE " + ",".join(map(str, cards_list)))
                    players.acquire()
                    for p in players.players:
                        p.control_sem.release()
                    players.release()
                    for p in players.players:
                        p.main_sem.acquire()
                    players.acquire()
                    result = [0 for p in players.players]
                    for i in range(len(players.players)):
                        for p in players.players:
                            if not p is players.players[current_player]:
                                if players.players[i].current_card == p.selected_card:
                                    result[i] += 1
                    if result[current_player] == len(players.players) - 1:
                        for p in players.players:
                            if not p is players.players[current_player]:
                                p.score += 3
                    else:
                        if result[current_player] != 0:
                            for p in players.players:
                                if not p is players.players[current_player]:
                                    if p.selected_card == current_card:
                                        p.score += 3
                            players.players[current_player] += 3
                        for i in range(len(players.players)):
                            players.players[i].score += result[i]
                    player_cards_list = [str(i) + ";" + str(players.players[i].current_card) + ";" +
                                str(players.players[i].selected_card) for i in range(len(players.players))]
                    player_score_list = [str[i] + ";" + str(players.players[i].score)
                                for i in range(len(players.players))]
                    players.broadcast("STATUS " + str(current_card) + " " + ",".join(player_cards_list) +
                                " " + ",".join(player_score_list))
                    for p in players.players:
                        p.cards = [i for i in p.cards if i != p.current_card]
                    if len(cards) >= len(players.players):
                        for p in players.players:
                            p.cards.append(cards[0])
                            cards = cards[1:]
                        for p in players.players:
                            p.control_sem.release()
                    players.release()
                    players.acquire()
                    for p in players.players:
                        p.main_sem.acquire()
                    players.release()
                    if len(players.players[0].cards) == 0:
                        game_st.state = "END"
                        players.acquire()
                        players.broadcast("END_GAME")
                        players.release()
                    else:
                        players.acquire()
                        for p in players.players:
                            p.control_sem.release()
                        players.release()

                players.acquire()
                for p in players.players:
                    p.control_sem.release()
                players.release()

            except Exception as ex:
                self.logger.error(str(ex))

            cli.players = None
            players.stop()
            disc.stop()

        cli.stop()
        print("Exiting")
