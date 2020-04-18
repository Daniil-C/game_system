import threading
import readline
from http.server import HTTPServer, SimpleHTTPRequestHandler
import time
from random import shuffle, randrange
from connection import connection
import server.environment as env


class Monitor:
    def __init__(self):
        object.__setattr__(self, "_Monitor_sem", threading.Semaphore(1))

    def __setattr__(self, name, value):
        object.__getattribute__(self, "_Monitor_sem").acquire()
        object.__setattr__(self, name, value)
        object.__getattribute__(self, "_Monitor_sem").release()

    def __getattribute__(self, name):
        object.__getattribute__(self, "_Monitor_sem").acquire()
        val = object.__getattribute__(self, name)
        object.__getattribute__(self, "_Monitor_sem").release()
        return val


class Resources(Monitor):
    def __init__(self, res_name, res_link):
        Monitor.__init__(self)
        self.name = res_name
        self.link = res_link


class HTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)

    def log_message(self, format, *args):
        self.logger.info("HTTP: " + (format % args))

    log_error = log_message


class ResourceServer(Monitor):
    def __init__(self, logger):
        Monitor.__init__(self)
        self.logger = logger
        self.server = None
        self.thread = None

    def main(self):
        ip_addr = env.get_ip()
        port = env.get_res_port()

        handler = HTTPHandler
        handler.logger = self.logger
        self.server = HTTPServer((ip_addr, port),
                                 (lambda *args, **kwargs:
                                  handler(*args, directory="server/resources", **kwargs)))
        self.server.serve_forever(poll_interval=0.5)
        self.server.server_close()

    def start(self):
        self.thread = threading.Thread(target=ResourceServer.main, args=(self,))
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.thread.join()


class GameState(Monitor):
    def __init__(self, initial_state):
        Monitor.__init__(self)
        self.state = initial_state
        self.card_set = 0


class Player(Monitor):
    def __init__(self, sock, status, sem, m_sem, res, game_st, plist, number, logger):
        Monitor.__init__(self)
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
        self.thread = None
        self.thread_active = False
        self.plist = plist
        self.get_broadcast = False
        self.cards = list()
        self.has_turn = False
        self.number = number
        self.logger = logger
        self.current_card = None
        self.selected_card = None

    def start(self):
        self.thread = threading.Thread(target=Player.main, args=(self,))
        self.thread.start()
        self.thread_active = True

    def __hash__(self):
        return self.number

    def stop(self):
        self.valid = False
        if self.thread_active:
            self.main_sem.release()
            self.control_sem.release()
            self.control_sem.release()
            self.thread.join()
            self.thread_active = False
        if not self.conn is None:
            self.conn.close()
            self.conn = None

    def sync(self):
        if not self.valid:
            raise Exception("thread stop on sync")
        self.control_sem.acquire()
        self.main_sem.release()
        self.control_sem.acquire()
        if not self.valid:
            raise Exception("thread stop on sync")

    def main(self):
        try:
            self.check_version()
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
                        raise Exception("START_GAME message error")
                self.player_socket.settimeout(None)
            self.sync()
            self.conn.send("BEGIN " + str(self.game_st.card_set) + " " +
                           ",".join(map(str, self.cards)))
            res = self.conn.get()
            if res != "READY":
                raise Exception("READY message error")
            self.sync()
            while self.game_st.state == "GAME":
                # Turn group 1
                self.sync() # sync 1
                # turn group 2
                if self.game_st.state != "GAME":
                    break
                if not self.has_turn:
                    res = self.conn.get().split()
                    if len(res) != 2 or res[0] != "CARD" or not res[1].isnumeric():
                        raise Exception("CARD message error")
                    self.current_card = int(res[1])
                self.plist.broadcast("#SELF", info=self)
                self.sync() # sync 2
                # turn group 3
                self.sync() # sync 3
                if not self.has_turn:
                    res = self.conn.get().split()
                    if len(res) != 2 or res[0] != "CARD" or not res[1].isnumeric():
                        raise Exception("CARD message error")
                    self.selected_card = int(res[1])
                self.sync() # sync 4
                # turn group 4
                self.sync() # sync 5
                # next turn group
                res = self.conn.get()
                if res != "NEXT_TURN":
                    raise Exception("NEXT_TURN message error")
                self.sync() # sync 6
                self.sync() # sync 7
                if self.game_st.state != "GAME":
                    return
                self.conn.send("CARDS " + ",".join(map(str, self.cards)))
                self.sync() # sync 8
        except Exception as ex:
            self.valid = False
            self.logger.error("Player " + str(self.number) + ": " + str(ex))
            self.main_sem.release()

    def check_version(self):
        self.conn.send("VERSION " + str(self.number) + " " + self.status + " " + self.res.name +
                       " " + self.res.link)
        res = self.conn.get().split()
        if self.valid:
            if len(res) != 2 or res[0] != "OK":
                raise Exception("version check error")
            else:
                self.name = res[1]


class CLI(Monitor):
    def __init__(self, players, game_st):
        Monitor.__init__(self)
        self.players = players
        self.game_st = game_st
        readline.set_completer(self.completer)
        readline.set_completer_delims("")
        readline.parse_and_bind("tab: complete")
        self.thread = None
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
                    if not self.players is None:
                        self.players.acquire()
                        print("CLI:", len(self.players), "player" + "s"*int(len(self.players) != 1))
                        out = list()
                        m_len = [len("number"), len("name"), len("score")]
                        for i in self.players:
                            out.append((str(i.number), i.name, str(i.score), i.status == "MASTER"))
                            m_len = [max(m_len[0], len(str(i.number))), max(m_len[1], len(i.name)),
                                     max(m_len[2], len(str(i.score)))]
                        if len(out) > 0:
                            print("number" + " "*(m_len[0] - len("number")),
                                  "name" + " "*(m_len[1] - len("name")),
                                  "score" + " "*(m_len[2] - len("score")))
                            for i in out:
                                string = ""
                                for idx in range(3):
                                    string += i[idx] + " "*(m_len[idx] - len(i[idx]) + 1)
                                if i[3]:
                                    string += "master"
                                print(string.strip())
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


class Disconnector(Monitor):
    def __init__(self, sock, logger):
        Monitor.__init__(self)
        self.sock = sock
        self.thread = None
        self.active = False
        self.logger = logger

    def start(self):
        self.active = True
        self.thread = threading.Thread(target=Disconnector.main, args=(self,))
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


class PlayerList(Monitor):
    def __init__(self, logger, game_st):
        Monitor.__init__(self)
        self.players = list()
        self.sem = threading.Semaphore(1)
        self.check = False
        self.check_thread = None
        self.logger = logger
        self.game_st = game_st

    def checker(self):
        while self.check:
            self.acquire()
            for i in range(len(self.players)):
                if not (self.players[i].valid and self.players[i].conn.status):
                    self.players[i].stop()
                    if self.players[i].status == "MASTER":
                        if self.game_st.state == "PLAYER_CONN":
                            self.game_st.state = "ERROR"
                    del self.players[i]
                    if self.game_st.state == "PLAYER_CONN":
                        self.broadcast("#PLAYER_LIST")
                    break
            self.release()
            time.sleep(0.1)

    def __iter__(self):
        for player in self.players:
            if player.valid:
                yield player

    def __len__(self):
        i = 0
        for player in self:
            i += 1
        return i

    def next_player(self, player):
        p_idx = 0
        for i in range(len(self.players)):
            if self.players[i] is player:
                p_idx = i
                break
        iteration = 0
        while iteration < len(self.players) * 2:
            p_idx += 1
            iteration += 1
            if p_idx >= len(self.players):
                p_idx = 0
            if self.players[p_idx].valid:
                return self.players[p_idx]
        return None

    def start_check(self):
        self.check = True
        self.check_thread = threading.Thread(target=PlayerList.checker, args=(self,))
        self.check_thread.start()

    def stop(self):
        self.check = False
        self.check_thread.join()
        for i in range(len(self.players)):
            self.players[i].stop()
        self.players.clear()

    def acquire(self):
        self.sem.acquire()

    def release(self):
        self.sem.release()

    def add_player(self, is_master, res, sock, number):
        self.acquire()
        control_sem = threading.Semaphore(0)
        main_sem = threading.Semaphore(0)
        new_player = Player(sock, "MASTER" if is_master else "PLAYER",
                            control_sem, main_sem, res, self.game_st, self, number, self.logger)
        new_player.start()
        self.players.append(new_player)
        self.release()

    def sync(self):
        for player in self:
            player.control_sem.release()
        for player in self:
            player.main_sem.acquire()
        for player in self:
            player.control_sem.release()

    def broadcast(self, data, info=None):
        if data == "#PLAYER_LIST":
            data = "PLAYER_LIST " + ",".join([str(i.number) + ";" + i.name for i in self])
        if data == "#SELF":
            data = "PLAYER " + str(info.number)
        for i in self:
            if i.get_broadcast:
                i.conn.send(data)


class GameServer:
    def __init__(self, listening_socket, logger):
        self.listening_socket = listening_socket
        self.logger = logger

    def main(self):
        game_st = GameState("PLAYER_CONN")
        cli = CLI(None, game_st)
        cli.start()

        while game_st.state != "SHUTDOWN":
            game_st.state = "PLAYER_CONN"
            players = PlayerList(self.logger, game_st)
            players.start_check()
            cards = list(range(98))
            shuffle(cards)

            res = Resources(env.get_res_name(), env.get_res_link())

            disc = Disconnector(self.listening_socket, self.logger)

            cli.players = players

            first_player = False

            # player connection loop and version check
            res_server = ResourceServer(self.logger)
            res_server.start()

            p_number = 0

            self.logger.info("Waiting for players to connect")

            while game_st.state == "PLAYER_CONN":
                try:
                    sock_info = self.listening_socket.accept()
                except:
                    continue

                players.add_player(not first_player, res, sock_info[0], p_number)
                first_player = True
                p_number += 1

            disc.start()
            res_server.stop()

            self.logger.info("Start game")

            try:
                if game_st.state != "GAME":
                    raise Exception(game_st.state + " state detected, end game")

                if len(players) == 4:
                    cards = cards[:len(cards) - 2]
                elif len(players) == 5:
                    cards = cards[:len(cards) - 23]
                elif len(players) == 6:
                    cards = cards[:len(cards) - 26]

                for player in players:
                    player.cards = cards[:6]
                    cards = cards[6:]

                players.sync()
                players.sync()

                current_player = players.players[randrange(len(players.players))]
                # game loop
                while game_st.state == "GAME":
                    # turn group 1
                    current_player = players.next_player(current_player)
                    if current_player is None:
                        raise Exception("No players left in game, exit")
                    for i in players:
                        if i is current_player:
                            i.has_turn = True
                        else:
                            i.has_turn = False
                    players.broadcast("TURN " + str(current_player.number))
                    get = current_player.conn.get().split(maxsplit=2)
                    if len(get) != 3 or get[0] != "TURN":
                        current_player.valid = False
                        continue
                    current_card = int(get[1])
                    current_player.current_card = current_card
                    current_player.selected_card = 0
                    players.broadcast("ASSOC " + get[2])
                    players.sync() # sync 1
                    # turn group 2
                    players.sync() # sync 2
                    #turn group 3
                    cards_list = [i.current_card for i in players]
                    players.acquire()
                    players.broadcast("VOTE " + ",".join(map(str, cards_list)))
                    players.release()
                    players.sync() # sync 3
                    # turn group 4
                    players.sync() # sync 4
                    players.acquire()
                    result = {p:0 for p in players}
                    for i in players:
                        for player in players:
                            if not player is current_player:
                                if i.current_card == player.selected_card:
                                    result[i] += 1
                    if result[current_player] == len(players) - 1:
                        for player in players:
                            if not player is current_player:
                                player.score += 3
                    else:
                        if result[current_player] != 0:
                            for player in players:
                                if not player is current_player:
                                    if player.selected_card == current_card:
                                        player.score += 3
                            current_player.score += 3
                        for i in players:
                            i.score += result[i]
                    player_cards_list = [str(i.number) + ";" + str(i.current_card) + ";" +
                                         str(i.selected_card) for i in players]
                    player_score_list = [str(i.number) + ";" + str(i.score) for i in players]
                    players.broadcast("STATUS " + str(current_card) + " " +
                                      ",".join(player_cards_list) + " " +
                                      ",".join(player_score_list))
                    players.sync() # sync 5
                    # next turn group
                    players.sync() # sync 6
                    for player in players:
                        player.cards = [i for i in player.cards if i != player.current_card]
                    if len(cards) >= len(players):
                        for player in players:
                            player.cards.append(cards[0])
                            cards = cards[1:]
                    players.release()
                    if len(players.players[0].cards) == 0:
                        game_st.state = "END"
                        players.acquire()
                        players.broadcast("END_GAME")
                        players.release()
                    players.sync() # sync 7
                    if game_st.state != "GAME":
                        break
                    players.sync() # sync 8

            except Exception as ex:
                self.logger.error(str(ex))

            cli.players = None
            players.stop()
            disc.stop()

        cli.stop()
