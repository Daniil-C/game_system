"""
Imaginarium game server.
"""

import threading
import socket
import readline
from http.server import HTTPServer, SimpleHTTPRequestHandler
import time
from random import shuffle, randrange
from connection import connection
import server.environment as env


class Monitor:
    """
    Base class for objects, accessable from multiple threads.
    """
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


class GameException(Exception):
    """
    Exceptions for error handling in this module.
    """
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message

    def __str__(self):
        return self.message


class Resources(Monitor):
    """
    Information about game resources.

    name: resources version name.
    link: new resources version address.
    """
    def __init__(self, res_name, res_link):
        Monitor.__init__(self)
        self.name = res_name
        self.link = res_link


class HTTPHandler(SimpleHTTPRequestHandler):
    """
    Handler for HTTP requests.

    It allows to access files in file system.
    """
    def __init__(self, *args, **kwargs):
        SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)

    def log_message(self, format, *args):
        """
        Log message from request handler.

        format: format string.
        args: arguments for log message.
        """
        self.logger.info("HTTP: " + (format % args))

    log_error = log_message


class ResourceServer(Monitor):
    """
    Server for downloading resource pack.
    """
    def __init__(self, logger):
        Monitor.__init__(self)
        self.logger = logger
        self.server = None
        self.thread = None

    def main(self):
        """
        Main server function.
        It should be started using start function.
        Executed in separate thread.
        """
        ip_addr = env.get_ip()
        port = env.get_res_port()

        handler = HTTPHandler
        handler.logger = self.logger
        self.server = HTTPServer((ip_addr, port),
                                 (lambda *args, **kwargs:
                                  handler(*args, directory="server/resources",
                                          **kwargs)))
        self.server.serve_forever(poll_interval=0.5)
        self.server.server_close()

    def start(self):
        """
        Start main server function.
        """
        self.thread = threading.Thread(target=ResourceServer.main,
                                       args=(self,))
        self.thread.start()

    def stop(self):
        """
        Stop server.
        """
        self.server.shutdown()
        self.thread.join()


class GameState(Monitor):
    """
    Information about game state.

    state: current game state.
    card_set: current card set number.
    """
    def __init__(self, initial_state):
        Monitor.__init__(self)
        self.state = initial_state
        self.card_set = 0


class Player(Monitor):
    """
    Player class is used for player connection handling.

    player_socket: socket, connected to player.
    status: player status: MASTER or PLAYER.
    control_sem, main_sem: semaphores, used for synchronization with main
                           thread.
    conn: connection object, containing player_socket.
    valid: is set to False if error occures.
    name: player name.
    res: Resources object.
    game_st: GameState object.
    score: current player score.
    plist: PlayerList object, containing this Player object.
    get_broadcast: will this player receive broadcast messages.
    cards: list of player's cards.
    number: player number.
    """
    def __init__(self, sock, status, sem, m_sem, res, game_st, plist, number,
                 logger):
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
        """
        Start player thread.
        """
        self.thread = threading.Thread(target=Player.main, args=(self,))
        self.thread.start()
        self.thread_active = True

    def __hash__(self):
        return self.number

    def stop(self):
        """
        Stop player thread and disconnect.
        """
        self.valid = False
        if self.thread_active:
            self.main_sem.release()
            self.control_sem.release()
            self.control_sem.release()
            self.thread.join()
            self.thread_active = False
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def sync(self):
        """
        Synchronize with main process.
        """
        if not self.valid:
            raise GameException("thread stop on sync")
        self.control_sem.acquire()
        self.main_sem.release()
        self.control_sem.acquire()
        if not self.valid:
            raise GameException("thread stop on sync")

    def main(self):
        """
        Main thread function.
        """
        try:
            self.check_version()
            self.get_broadcast = True
            self.plist.broadcast("#PLAYER_LIST")
            if self.status == "MASTER":
                self.wait_start()
            self.sync()
            self.conn.send("BEGIN " + str(self.game_st.card_set) + " " +
                           ",".join(map(str, self.cards)))
            res = self.conn.get()
            if res != "READY":
                raise GameException("READY message error")
            self.sync()
            while self.game_st.state == "GAME":
                # Turn group 1
                self.sync()  # sync 1
                # turn group 2
                if self.game_st.state != "GAME":
                    break
                if not self.has_turn:
                    self.current_card = self.get_card()
                self.plist.broadcast("#SELF", info=self)
                self.sync()  # sync 2
                # turn group 3
                self.sync()  # sync 3
                if not self.has_turn:
                    self.selected_card = self.get_card()
                self.sync()  # sync 4
                # turn group 4
                self.sync()  # sync 5
                # next turn group
                res = self.conn.get()
                if res != "NEXT_TURN":
                    raise GameException("NEXT_TURN message error")
                self.sync()  # sync 6
                self.sync()  # sync 7
                if self.game_st.state != "GAME":
                    return
                self.conn.send("CARDS " + ",".join(map(str, self.cards)))
                self.sync()  # sync 8
        except GameException as ex:
            self.valid = False
            self.logger.error("Player " + str(self.number) + ": " + str(ex))
            self.main_sem.release()

    def wait_start(self):
        """
        Wait for start message from MASTER player.
        """
        self.player_socket.settimeout(0.1)
        while self.game_st.state == "PLAYER_CONN":
            try:
                res = self.conn.get().split()
            except socket.timeout:
                continue
            if len(res) == 2 and res[1].isnumeric() and res[0] == "START_GAME":
                self.game_st.card_set = int(res[1])
                self.game_st.state = "GAME"
            else:
                raise GameException("START_GAME message error")
        self.player_socket.settimeout(None)

    def get_card(self):
        """
        Receive CARD message.
        """
        res = self.conn.get().split()
        if len(res) != 2 or res[0] != "CARD" or not res[1].isnumeric():
            raise GameException("CARD message error")
        return int(res[1])

    def check_version(self):
        """
        Check resources version.
        """
        self.conn.send("VERSION " + str(self.number) + " " + self.status +
                       " " + self.res.name +
                       " " + self.res.link)
        res = self.conn.get().split()
        if self.valid:
            if len(res) != 2 or res[0] != "OK":
                raise GameException("version check error")
            else:
                self.name = res[1]


class CLI(Monitor):
    """
    Game server command line interface.
    """
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
        """
        Start thread.
        """
        self.thread = threading.Thread(target=CLI.main, args=(self,))
        self.thread.start()

    def stop(self):
        """
        Stop thread.
        """
        self.work = False
        self.thread.join()

    def main(self):
        """
        Main thread function.
        """
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
                    self.comm_help()
                elif cmdline[0] == "players":
                    self.comm_players()
                elif cmdline[0] == "start":
                    self.comm_start(cmdline)
                elif cmdline[0] == "stop":
                    self.comm_stop()
                elif cmdline[0] == "status":
                    self.comm_status()
                else:
                    print("CLI: error: unknown command")
            except Exception as ex:
                print("CLI: error: " + str(ex))

    def completer(self, text, state):
        """
        Function for command completion.
        """
        commands = ["help", "players", "start ", "status", "stop"]
        for i in commands:
            if i.startswith(text):
                if state == 0:
                    return i
                state = state - 1
        return None

    def comm_help(self):
        """
        Execute 'help' command.
        """
        print("CLI commands:")
        print("\thelp")
        print("\tplayers")
        print("\tstart <card set number>")
        print("\tstatus")
        print("\tstop")

    def comm_players(self):
        """
        Execute 'players' command.
        """
        if self.players is not None:
            self.players.acquire()
            print("CLI:", len(self.players), "player" +
                  "s"*int(len(self.players) != 1))
            out = list()
            m_len = [len("number"), len("name"), len("score")]
            for i in self.players:
                out.append((str(i.number), i.name, str(i.score),
                            i.status == "MASTER"))
                m_len = [max(m_len[0], len(str(i.number))),
                         max(m_len[1], len(i.name)),
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
            print("CLI: error: player list is not available")

    def comm_start(self, cmdline):
        """
        Execute 'start' command.
        """
        if len(cmdline) == 2 and cmdline[1].isnumeric():
            self.game_st.card_set = int(cmdline[1])
            self.game_st.state = "GAME"
            print("CLI: Starting game")
        else:
            print("CLI: error: expected start <card set number>")

    def comm_stop(self):
        """
        Execute 'stop' command.
        """
        self.game_st.state = "SHUTDOWN"
        print("CLI: exit")
        self.work = False

    def comm_status(self):
        """
        Execute 'status' command.
        """
        print(self.game_st.state)


class Disconnector(Monitor):
    """
    Disconnector object is used for accepting connections
    on listening socket and closing them.
    """
    def __init__(self, sock, logger):
        Monitor.__init__(self)
        self.sock = sock
        self.thread = None
        self.active = False
        self.logger = logger

    def start(self):
        """
        Start thread.
        """
        self.active = True
        self.thread = threading.Thread(target=Disconnector.main, args=(self,))
        self.thread.start()

    def stop(self):
        """
        Stop thread.
        """
        self.active = False
        self.thread.join()

    def main(self):
        """
        Main thread function.
        """
        while self.active:
            try:
                new_sock = self.sock.accept()
            except socket.timeout:
                continue
            self.logger.info("Disconnector: " + str(new_sock[1]))
            conn = connection(new_sock[0])
            conn.close()


class PlayerList(Monitor):
    """
    Player objects container.
    """
    def __init__(self, logger, game_st):
        Monitor.__init__(self)
        self.players = list()
        self.sem = threading.Semaphore(1)
        self.check = False
        self.check_thread = None
        self.logger = logger
        self.game_st = game_st

    def checker(self):
        """
        Main thread function.

        Check errors im Player objects and delete objects with errors.
        """
        while self.check:
            self.acquire()
            for i in range(len(self.players)):
                if not (self.players[i].valid and self.players[i].conn.status):
                    self.players[i].stop()
                    self.logger.info("Checker: collected player %d",
                                     self.players[i].number)
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
        return len(tuple(iter(self)))

    def next_player(self, player):
        """
        Get next player in player sequence.
        """
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
        """
        Start check thread.
        """
        self.check = True
        self.check_thread = threading.Thread(target=PlayerList.checker,
                                             args=(self,))
        self.check_thread.start()

    def stop(self):
        """
        Stop check thread and delete all Player objects.
        """
        self.check = False
        self.check_thread.join()
        for i in range(len(self.players)):
            self.players[i].stop()
        self.players.clear()

    def acquire(self):
        """
        Acquire semaphore.
        """
        self.sem.acquire()

    def release(self):
        """
        Release semaphore.
        """
        self.sem.release()

    def add_player(self, is_master, res, sock, number):
        """
        Add player to PlayerList.
        """
        self.acquire()
        control_sem = threading.Semaphore(0)
        main_sem = threading.Semaphore(0)
        new_player = Player(sock, "MASTER" if is_master else "PLAYER",
                            control_sem, main_sem, res, self.game_st, self,
                            number, self.logger)
        new_player.start()
        self.players.append(new_player)
        self.release()

    def sync(self):
        """
        Synchronize with all Player objects.
        """
        for player in self:
            player.control_sem.release()
        for player in self:
            player.main_sem.acquire()
        for player in self:
            player.control_sem.release()

    def broadcast(self, data, info=None):
        """
        Send broadcast message.
        """
        if data == "#PLAYER_LIST":
            data = "PLAYER_LIST " + ",".join([str(i.number) + ";" + i.name
                                              for i in self])
        if data == "#SELF":
            data = "PLAYER " + str(info.number)
        for i in self:
            if i.get_broadcast:
                i.conn.send(data)


class GameServer:
    """
    Main game server class.
    """
    def __init__(self, listening_socket, logger):
        self.listening_socket = listening_socket
        self.logger = logger
        self.game_state = None
        self.players = None
        self.cards = None
        self.resource_server = None
        self.resources = None
        self.disconnector = None
        self.cli = None

    def main(self):
        """
        Game server main function.
        """
        self.game_state = GameState("PLAYER_CONN")
        self.cli = CLI(None, self.game_state)
        self.cli.start()

        while self.game_state.state != "SHUTDOWN":
            self.prepare()
            self.connect_players()

            self.disconnector.start()
            self.logger.info("Start game")

            try:
                self.begin_game()

                self.players.sync()
                self.players.sync()

                current_player = self.players.players[randrange(len(
                    self.players.players))]
                # game loop
                while self.game_state.state == "GAME":
                    # turn group 1
                    current_player = self.players.next_player(current_player)
                    if current_player is None:
                        raise GameException("No players left in game, exit")
                    for i in self.players:
                        if i is current_player:
                            i.has_turn = True
                        else:
                            i.has_turn = False
                    self.players.broadcast("TURN " +
                                           str(current_player.number))
                    get = current_player.conn.get().split(maxsplit=2)
                    if len(get) != 3 or get[0] != "TURN":
                        current_player.valid = False
                        continue
                    current_card = int(get[1])
                    current_player.current_card = current_card
                    current_player.selected_card = 0
                    self.players.broadcast("ASSOC " + get[2])
                    self.players.sync()  # sync 1
                    # turn group 2
                    self.players.sync()  # sync 2
                    # turn group 3
                    cards_list = [i.current_card for i in self.players]
                    self.players.acquire()
                    self.players.broadcast("VOTE " +
                                           ",".join(map(str, cards_list)))
                    self.players.release()
                    self.players.sync()  # sync 3
                    # turn group 4
                    self.players.sync()  # sync 4

                    self.players.acquire()

                    self.calculate_result(current_player, current_card)

                    player_cards_list = [str(i.number) + ";" +
                                         str(i.current_card) + ";" +
                                         str(i.selected_card)
                                         for i in self.players]
                    player_score_list = [str(i.number) + ";" +
                                         str(i.score) for i in self.players]
                    self.players.broadcast("STATUS " + str(current_card) +
                                           " " + ",".join(player_cards_list) +
                                           " " + ",".join(player_score_list))

                    self.players.sync()  # sync 5
                    # next turn group
                    self.players.sync()  # sync 6
                    for player in self.players:
                        player.cards = [i for i in player.cards
                                        if i != player.current_card]
                    if len(self.cards) >= len(self.players):
                        for player in self.players:
                            player.cards.append(self.cards[0])
                            self.cards = self.cards[1:]

                    self.players.release()

                    if len(self.players.players[0].cards) == 0:
                        self.game_state.state = "END"
                        self.players.acquire()
                        self.players.broadcast("END_GAME")
                        self.players.release()
                    self.players.sync()  # sync 7
                    if self.game_state.state != "GAME":
                        break
                    self.players.sync()  # sync 8

            except GameException as ex:
                self.logger.error(str(ex))

            self.cli.players = None
            self.players.stop()
            self.disconnector.stop()

        self.cli.stop()

    def prepare(self):
        """
        Create components before players connection.
        """
        self.game_state.state = "PLAYER_CONN"
        self.players = PlayerList(self.logger, self.game_state)
        self.players.start_check()
        self.cards = list(range(98))
        shuffle(self.cards)
        self.resources = Resources(env.get_res_name(), env.get_res_link())
        self.disconnector = Disconnector(self.listening_socket, self.logger)
        self.cli.players = self.players
        self.resource_server = ResourceServer(self.logger)

    def connect_players(self):
        """
        Connect players to the server.
        """
        self.resource_server.start()
        p_number = 0
        first_player = False
        self.logger.info("Waiting for players to connect")
        while self.game_state.state == "PLAYER_CONN":
            try:
                sock_info = self.listening_socket.accept()
            except socket.timeout:
                continue
            self.players.add_player(not first_player, self.resources,
                                    sock_info[0], p_number)
            first_player = True
            p_number += 1
        self.resource_server.stop()

    def begin_game(self):
        """
        Setup before game start.
        """
        if len(self.players) == 0:
            raise GameException("Game started without players, end game")
        if self.game_state.state != "GAME":
            raise GameException(self.game_state.state +
                                " state detected, end game")

        if len(self.players) == 4:
            self.cards = self.cards[:len(self.cards) - 2]
        elif len(self.players) == 5:
            self.cards = self.cards[:len(self.cards) - 23]
        elif len(self.players) == 6:
            self.cards = self.cards[:len(self.cards) - 26]

        for player in self.players:
            player.cards = self.cards[:6]
            self.cards = self.cards[6:]

    def calculate_result(self, current_player, current_card):
        """
        Update players' score.
        """
        result = {p: 0 for p in self.players}
        for i in self.players:
            for player in self.players:
                if player is not current_player:
                    if i.current_card == player.selected_card:
                        result[i] += 1
        if result[current_player] == len(self.players) - 1:
            for player in self.players:
                if player is not current_player:
                    player.score += 3
        else:
            if result[current_player] != 0:
                for player in self.players:
                    if player is not current_player:
                        if player.selected_card == current_card:
                            player.score += 3
                current_player.score += 3
            for i in self.players:
                i.score += result[i]
