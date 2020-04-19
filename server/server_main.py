"""
Imaginarium game server.
"""

import threading
import readline
from select import select
from http.server import HTTPServer, SimpleHTTPRequestHandler
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
    Server for resource pack downloading.
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
    def __init__(self, sock, status, res, game_st, plist, number,
                 logger):
        Monitor.__init__(self)
        self.player_socket = sock
        self.status = status
        self.state = "VER_CHECK"
        self.conn = connection(self.player_socket)
        self.valid = True
        self.name = "Player"
        self.res = res
        self.game_st = game_st
        self.score = 0
        self.plist = plist
        self.get_broadcast = False
        self.cards = list()
        self.number = number
        self.logger = logger
        self.current_card = None
        self.selected_card = None
        self.buffer = list()
        self.has_buffer = False
        self.has_turn = False

    def __hash__(self):
        return self.number

    def stop(self):
        """
        Disconnect.
        """
        self.valid = False
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def send_message(self, data):
        """
        Put message into send buffer.
        """
        self.buffer.append(data)
        self.has_buffer = True

    # Player states:
    # VER_CHECK
    #    v  [Send version info]
    # VER_WAIT
    #    v  [Get OK <name>]
    # START_WAIT
    #    v  [game_state -> GAME]
    # BEGIN_SYNC
    #    v  [All reached sync]
    # READY_WAIT
    #    v  [Get READY]
    # TURN_SYNC <----------------------\
    #    v  [All reached sync]         |
    # WAIT_ASSOC                       |
    #    v  [Get assoc, sent to all]   |
    # WAIT_SELF_CARD                   |
    #    v  [Get self card]            |
    # SELF_SYNC                        |
    #    v  [All reached sync]         |
    # WAIT_VOTE                        |
    #    v  [Get vote card]            |
    # VOTE_SYNC                        |
    #    v  [All reached sync]         |
    # WAIT_NEXT_TURN                   |
    #    v  [Get NEXT_TURN]            |
    # SYNC_NEXT_TURN                   |
    #    |  [All reached sync]         |
    #    |-----------------------------/
    # END

    def handle_message(self):
        """
        Receive and handle a message.
        """
        res = self.conn.get().split()
        if self.state == "VER_WAIT":
            if len(res) != 2 or res[0] != "OK":
                self.valid = False
                self.log_message("version check failed")
                return
            self.name = res[1]
            self.get_broadcast = True
            self.plist.broadcast("#PLAYER_LIST")
            self.state = "START_WAIT"
        elif self.state == "START_WAIT":
            if self.status != "MASTER":
                self.valid = False
                self.log_message("receive START_GAME message")
                return
            if (len(res) != 2 or res[0] != "START_GAME" or
                    not res[1].isnumeric()):
                self.valid = False
                return
            self.game_st.state = "GAME"
            self.game_st.card_set = int(res[1])
            self.state = "BEGIN_SYNC"
        elif self.state == "READY_WAIT":
            if len(res) != 1 or res[0] != "READY":
                self.valid = False
                self.log_message("did not receive READY")
                return
            self.state = "TURN_SYNC"
        elif self.state == "WAIT_ASSOC":
            if not self.has_turn:
                self.valid = False
                return
            if len(res) < 3 or res[0] != "TURN" or not res[1].isnumeric():
                self.valid = False
                for player in self.plist:
                    player.state = "TURN_SYNC"
                return
            self.current_card = int(res[1])
            self.selected_card = 0
            for player in self.plist:
                player.state = "WAIT_SELF_CARD"
            self.plist.broadcast("ASSOC " + " ".join(res[2:]))
        elif self.state == "WAIT_SELF_CARD":
            if not self.has_turn:
                if len(res) < 2 or res[0] != "CARD" or not res[1].isnumeric():
                    self.valid = False
                    return
                self.current_card = int(res[1])
                self.plist.broadcast("#SELF", self)
                self.state = "SELF_SYNC"
            else:
                self.valid = False
        elif self.state == "WAIT_VOTE":
            if not self.has_turn:
                if len(res) < 2 or res[0] != "CARD" or not res[1].isnumeric():
                    self.valid = False
                    return
                self.selected_card = int(res[1])
                self.state = "VOTE_SYNC"
            else:
                self.valid = False
        elif self.state == "WAIT_NEXT_TURN":
            if len(res) != 1 or res[0] != "NEXT_TURN":
                self.valid = False
                return
            self.state = "SYNC_NEXT_TURN"
        else:
            self.log_message("error state reached: " + self.state)
            self.valid = False

    def handle_state(self):
        """
        Check and do state transition.
        """
        if self.state == "VER_CHECK":
            self.send_message("VERSION " + str(self.number) + " " +
                              self.status + " " + self.res.name + " " +
                              self.res.link)
            self.state = "VER_WAIT"
        if self.state == "START_WAIT" and self.game_st.state == "GAME":
            self.state = "BEGIN_SYNC"
        if self.state == "WAIT_SELF_CARD" and self.has_turn:
            self.state = "SELF_SYNC"
            self.plist.broadcast("#SELF", self)
        if self.state == "WAIT_VOTE" and self.has_turn:
            self.state = "VOTE_SYNC"

    def log_message(self, message):
        """
        Print message into log file.
        """
        self.logger.info("Player %d: %s.", self.number, message)


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


class PlayerList(Monitor):
    """
    Player objects container.
    """
    def __init__(self, logger, game_st):
        Monitor.__init__(self)
        self.players = list()
        self.sockets = dict()
        self.logger = logger
        self.game_st = game_st
        self.sem = threading.Semaphore(1)
        self.have_master = False
        self.seq_number = 0

    def __iter__(self):
        for player in self.players:
            if player.valid:
                yield player

    def __len__(self):
        return len(tuple(iter(self)))

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

    def check(self):
        """
        Check for Player objects to be removed.
        """
        for player in self.players:
            if not player.valid or not player.conn.status:
                player.stop()
                self.sockets.pop(player.player_socket)
                if (player.status == "MASTER" and
                        self.game_st.state == "PLAYER_CONN"):
                    self.game_st.state = "ERROR"
                self.players.remove(player)
                break

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

    def stop(self):
        """
        Delete all Player objects.
        """
        for i in range(len(self.players)):
            self.players[i].stop()
        self.players.clear()
        self.sockets.clear()

    def add_player(self, res, sock):
        """
        Add player to PlayerList.
        """
        new_player = Player(sock, "PLAYER" if self.have_master else "MASTER",
                            res, self.game_st, self,
                            self.seq_number, self.logger)
        self.players.append(new_player)
        self.sockets[sock] = new_player
        self.have_master = True
        self.seq_number += 1

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
                i.send_message(data)


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
            work = True
            res_serv = False
            while work:
                if (self.game_state.state != "PLAYER_CONN" and
                        self.game_state.state != "GAME"):
                    self.logger.info("Detected state %s, exit.",
                                     self.game_state.state)
                    work = False

                if self.game_state.state == "PLAYER_CONN" and not res_serv:
                    self.resource_server.start()
                    res_serv = True
                if self.game_state.state != "PLAYER_CONN" and res_serv:
                    self.resource_server.stop()
                    res_serv = False
                if (len(self.players) == 0 and
                        self.game_state.state != "PLAYER_CONN"):
                    self.logger.info("No players left in game, exit")
                    work = False
                    continue

                rlist = [player.player_socket for player in self.players]
                rlist.append(self.listening_socket)
                wlist = [player.player_socket for player in self.players
                         if player.has_buffer]
                flows = select(rlist, wlist, list(), 0.5)

                self.players.acquire()
                # Push buffers
                for flow in flows[1]:
                    player = self.players.sockets[flow]
                    player.conn.send(player.buffer.pop(0))
                    player.has_buffer = len(player.buffer) > 0

                # Handle input
                for flow in flows[0]:
                    if flow is self.listening_socket:
                        self.accept_connection()
                    else:
                        self.players.sockets[flow].handle_message()

                # Do player events according to state
                for player in self.players:
                    player.handle_state()

                # Global operations
                cond = self.get_sync_state()
                if cond == "BEGIN_SYNC":
                    if len(self.players) > 0:
                        self.begin_game()
                        for player in self.players:
                            player.state = "READY_WAIT"
                            player.send_message("BEGIN " +
                                                str(self.game_state.card_set) +
                                                " " +
                                                ",".join(map(str,
                                                             player.cards)))
                        current_player = self.players.next_player(
                            self.players.players[randrange(len(
                                self.players.players))])
                    else:
                        self.logger.info("Started game without players, exit")
                        self.game_state.state = "ERROR"
                elif cond == "TURN_SYNC":
                    current_player = self.players.next_player(current_player)
                    for player in self.players:
                        player.has_turn = player is current_player
                        player.state = "WAIT_ASSOC"
                    self.players.broadcast("TURN " +
                                           str(current_player.number))
                elif cond == "SELF_SYNC":
                    card_list = [player.current_card
                                 for player in self.players]
                    self.players.broadcast("VOTE " +
                                           ",".join(map(str, card_list)))
                    for player in self.players:
                        player.state = "WAIT_VOTE"
                elif cond == "VOTE_SYNC":
                    self.calculate_result(current_player)
                    card_list = [str(player.number) + ";" +
                                 str(player.current_card) + ";" +
                                 str(player.selected_card)
                                 for player in self.players]
                    score_list = [str(player.number) + ";" +
                                  str(player.score)
                                  for player in self.players]
                    self.players.broadcast("STATUS " +
                                           str(current_player.current_card) +
                                           " " + ",".join(card_list) + " " +
                                           ",".join(score_list))
                    for player in self.players:
                        player.state = "WAIT_NEXT_TURN"
                elif cond == "SYNC_NEXT_TURN":
                    for player in self.players:
                        for card in player.cards:
                            if card == player.current_card:
                                player.cards.remove(card)
                                break
                    if len(self.cards) >= len(self.players):
                        for player in self.players:
                            player.cards.append(self.cards.pop(0))
                    if len(tuple(self.players)[0].cards) > 0:
                        for player in self.players:
                            player.send_message("CARDS " +
                                                ",".join(map(str,
                                                             player.cards)))
                            player.state = "TURN_SYNC"
                    else:
                        self.players.broadcast("END_GAME")
                        for player in self.players:
                            player.valid = False
                        self.game_state.state = "END"

                self.players.check()
                self.players.release()

            self.players.stop()

        self.cli.stop()

    def get_sync_state(self):
        """
        Check if all players have the same state.
        """
        st = None
        for player in self.players:
            if st is None:
                st = player.state
            else:
                if player.state != st:
                    return None
        return st

    def prepare(self):
        """
        Create components before players connection.
        """
        self.game_state.state = "PLAYER_CONN"
        self.players = PlayerList(self.logger, self.game_state)
        self.cards = list(range(98))
        shuffle(self.cards)
        self.resources = Resources(env.get_res_name(), env.get_res_link())
        self.cli.players = self.players
        self.resource_server = ResourceServer(self.logger)
        self.current_player = None

    def accept_connection(self):
        """
        Accept a new connection and create Player object.
        """
        new_conn = self.listening_socket.accept()
        if self.game_state.state == "PLAYER_CONN":
            self.players.add_player(self.resources, new_conn[0])
        else:
            self.logger.info("Disconnected: " + str(new_conn[1]))

    def begin_game(self):
        """
        Setup before game start.
        """
        if len(self.players) == 4:
            self.cards = self.cards[:len(self.cards) - 2]
        elif len(self.players) == 5:
            self.cards = self.cards[:len(self.cards) - 23]
        elif len(self.players) == 6:
            self.cards = self.cards[:len(self.cards) - 26]

        for player in self.players:
            player.cards = self.cards[:6]
            self.cards = self.cards[6:]

    def calculate_result(self, current_player):
        """
        Update players' score.
        """
        current_card = current_player.current_card
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
