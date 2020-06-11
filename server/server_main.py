"""
Imaginarium game server.
"""

import threading
import readline
from select import select
import socket
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from random import shuffle, randrange
import os
import sys
import gettext
import json
from monitor import Monitor
from connection import connection
import server.environment as env


class Resources(Monitor):
    """
    Information about game resources.

    Attributes:
    name (str): resources version name.
    link (str): new resources version address.
    configuration(dict): number if cards in each set.
    """
    def __init__(self, res_name, res_link, logger):
        Monitor.__init__(self)
        self.name = res_name
        self.link = res_link
        self.logger = logger
        self.configuration = None
        conf_path = os.path.dirname(sys.argv[0]) + "/resources/sets.json"
        try:
            with open(conf_path) as conf:
                self.configuration = json.load(conf)
        except Exception:
            self.logger.error("failed to load config file resources/sets.json.")


class HTTPHandler(SimpleHTTPRequestHandler):
    """
    Handler for HTTP requests.
    """
    def __init__(self, *args, **kwargs):
        SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)

    def log_message(self, format, *args):
        """
        Log message from request handler.

        format (str): format string.
        args (list): arguments for format string.
        """
        self.logger.info("HTTP: " + (format % args))

    log_error = log_message


class ResourceServer(Monitor):
    """
    Server for resource pack downloading.

    Attributes:
    logger (Logger): logger for handling log messages.
    server (HTTPServer): server object.
    thread (Thread): thread for main server function.
    active (bool): server state.
    """
    def __init__(self, logger):
        Monitor.__init__(self)
        self.logger = logger
        self.server = None
        self.thread = None
        self.active = False

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
        file_path = os.path.dirname(sys.argv[0]) + "/resources/cards"
        self.server = ThreadingHTTPServer((ip_addr, port),
                                          (lambda *args, **kwargs:
                                           handler(*args,
                                                   directory=file_path,
                                                   **kwargs)))
        self.server.serve_forever(poll_interval=0.5)
        self.server.server_close()

    def start(self):
        """
        Start main server function in new thread.
        """
        self.thread = threading.Thread(target=ResourceServer.main,
                                       args=(self,))
        self.thread.start()
        self.active = True

    def stop(self):
        """
        Stop server thread.
        """
        self.server.shutdown()
        self.thread.join()
        self.active = False


class GameState(Monitor):
    """
    Information about game state.

    Attributes:
    state (str): current game state.
    card_set (str): current card set number.
    """
    def __init__(self, initial_state):
        Monitor.__init__(self)
        self.state = initial_state
        self.card_set = "0"


class Player(Monitor):
    """
    Player class is used for player information handling.

    Attributes:
    player_socket (socket): socket, connected to player.
    status (str): player status: MASTER or PLAYER.
    state (str): current player state.
    conn (connection): connection object, containing player_socket.
    valid (bool): error indicator.
    name (str): player name.
    res (Resources): resource pack container.
    game_st (GameState): game state container.
    score (int): current player score.
    plist (PlayerList): PlayerList object, containing this Player object.
    get_broadcast (bool): will this player receive broadcast messages.
    cards (list(int)): list of player's cards.
    number (int): player number.
    current_card (int): current player card.
    selected_card (int): current selected card.
    buffer (list(str)): list of messages waiting to be sent.
    has_buffer (bool): is True if buffer is not empty.
    has_turn (bool): is True if player is leader now.
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
        Disconnect player.
        """
        self.valid = False
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def verify(self):
        """
        Check if there is no errors in Player object.
        """
        return self.valid and self.conn.status

    def send_message(self, data):
        """
        Put message into send buffer.

        data (str): message.
        """
        self.buffer.append(data)
        self.has_buffer = True

    # Player states:
    #
    #    |
    #    v
    # VER_CHECK
    #    v  [Send version info][hndl]
    # VER_WAIT
    #    v  [Get OK <name>][msg]
    # START_WAIT
    #    v  [game_state -> GAME][hndl][msg]
    # BEGIN_SYNC
    #    v  [All reached sync][main]
    # READY_WAIT
    #    v  [Get READY][msg]
    # TURN_SYNC <---------------------------------\
    #    v  [All reached sync][main]              |
    # WAIT_ASSOC                                  |
    #    v  [Get assoc, sent to all][msg]         |
    # WAIT_SELF_CARD                              |
    #    v  [Get self card][hndl][msg]            |
    # SELF_SYNC                                   |
    #    v  [All reached sync][main]              |
    # WAIT_VOTE                                   |
    #    v  [Get vote card][hndl][msg]            |
    # VOTE_SYNC                                   |
    #    v  [All reached sync][main]              |
    # WAIT_NEXT_TURN                              |
    #    v  [Get NEXT_TURN][msg]                  |
    # SYNC_NEXT_TURN                              |
    #    |  [All reached sync][main]              |
    #    |----------------------------------------/
    #    v

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
            if len(res) != 2 or res[0] != "START_GAME":
                self.valid = False
                self.log_message("expected START_GAME message")
                return
            self.game_st.state = "GAME"
            self.game_st.card_set = res[1]
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
                self.log_message("receive association from wrong player")
                return
            if len(res) < 3 or res[0] != "TURN" or not res[1].isnumeric():
                self.valid = False
                for player in self.plist:
                    player.state = "TURN_SYNC"
                self.log_message("expected association message")
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
                    self.log_message("expected CARD message")
                    return
                self.current_card = int(res[1])
                self.plist.broadcast("#SELF", self)
                self.state = "SELF_SYNC"
            else:
                self.valid = False
                self.log_message("received unexpected message")
        elif self.state == "WAIT_VOTE":
            if not self.has_turn:
                if len(res) < 2 or res[0] != "CARD" or not res[1].isnumeric():
                    self.valid = False
                    self.log_message("expected CARD message")
                    return
                self.selected_card = int(res[1])
                self.state = "VOTE_SYNC"
            else:
                self.valid = False
                self.log_message("received unexpected message")
        elif self.state == "WAIT_NEXT_TURN":
            if len(res) != 1 or res[0] != "NEXT_TURN":
                self.valid = False
                self.log_message("expected NEXT_TURN message")
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
        if self.state == "VER_WAIT" and self.game_st.state == "GAME":
            self.valid = False
        if self.state == "WAIT_SELF_CARD" and self.has_turn:
            self.state = "SELF_SYNC"
            self.plist.broadcast("#SELF", self)
        if self.state == "WAIT_VOTE" and self.has_turn:
            self.state = "VOTE_SYNC"

    def log_message(self, message):
        """
        Print message into log file.

        message (str): printed message.
        """
        self.logger.info("Player %d,%s: %s.", self.number, self.name, message)


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
        gettext.install("server", os.path.dirname(sys.argv[0]),
                        names=("ngettext",))
        readline.parse_and_bind("tab: complete")
        self.thread = None
        self.work = False

    def start(self):
        """
        Start thread for command line interface.
        """
        self.thread = threading.Thread(target=CLI.main, args=(self,))
        self.thread.start()

    def stop(self):
        """
        Stop command line interface thread.
        """
        self.work = False
        self.thread.join()

    def main(self):
        """
        Main command line interface function.
        """
        self.work = True
        print("CLI started")
        while self.work:
            try:
                cmdline = input("\x1b[1;32m[%s]\x1b[0m$ " %
                                self.game_st.state).split()
            except Exception as ex:
                print("error:", str(ex))
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
                else:
                    print("error: unknown command")
            except Exception as ex:
                print("error: " + str(ex))

    def completer(self, text, state):
        """
        Function for command completion.

        text (str): current input buffer.
        state (int): match number.
        """
        commands = ["help", "players", "start ", "stop"]
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
        print(_("commands") + ":\n\nhelp\nplayers\nstart <card set>\nstop")

    def comm_players(self):
        """
        Execute 'players' command.
        """
        if self.players is not None:
            self.players.acquire()
            print(len(self.players), ngettext("player", "players",
                                              int(len(self.players))))
            out = list()
            str_num, str_name, str_score = _("number"), _("name"), _("score")
            m_len = [len(str_num), len(str_name), len(str_score)]
            for i in self.players:
                out.append((str(i.number), i.name, str(i.score),
                            i.status == "MASTER"))
                m_len = [max(m_len[0], len(str(i.number))),
                         max(m_len[1], len(i.name)),
                         max(m_len[2], len(str(i.score)))]
            if len(out) > 0:
                print(str_num + " "*(m_len[0] - len(str_num)),
                      str_name + " "*(m_len[1] - len(str_name)),
                      str_score + " "*(m_len[2] - len(str_score)))
                for i in out:
                    string = ""
                    for idx in range(3):
                        string += i[idx] + " "*(m_len[idx] - len(i[idx]) + 1)
                    if i[3]:
                        string += _("master")
                    print(string.strip())
            self.players.release()
        else:
            print(_("error: player list is not available"))

    def comm_start(self, cmdline):
        """
        Execute 'start' command.
        """
        if len(cmdline) == 2:
            self.game_st.card_set = cmdline[1]
            self.game_st.state = "GAME"
            print(_("Starting game."))
        else:
            print(_("error: expected start <card set>"))

    def comm_stop(self):
        """
        Execute 'stop' command.
        """
        self.game_st.state = "SHUTDOWN"
        print(_("exit"))
        self.work = False


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
            if not player.verify():
                player.stop()
                self.sockets.pop(player.player_socket)
                if (player.status == "MASTER" and
                        self.game_st.state == "PLAYER_CONN"):
                    self.game_st.state = "ERROR"
                self.players.remove(player)
                if self.game_st.state == "PLAYER_CONN":
                    self.broadcast("#PLAYER_LIST")
                break

    def next_player(self, player):
        """
        Get next player in player sequence.

        player (Player): current player.
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
        Disconnect all players and delete all Player objects.
        """
        for i in range(len(self.players)):
            self.players[i].stop()
        self.players.clear()
        self.sockets.clear()

    def add_player(self, res, sock):
        """
        Add player to PlayerList.

        res (Resources): resource pack information.
        sock (socket): player socket.
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

        data (str): message text.
        info (Player): additional info for #SELF message.
        """
        if data == "#PLAYER_LIST":
            data = "PLAYER_LIST " + ",".join([str(i.number) + ";" + i.name
                                              for i in self
                                              if i.get_broadcast])
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
        self.current_player = None
        self.session_id = 0

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
            self.logger.info("Starting session %d." % self.session_id)
            while work:
                self.check_resource_server()
                if (self.game_state.state != "PLAYER_CONN" and
                        self.game_state.state != "GAME"):
                    self.logger.info("Detected state %s, exit.",
                                     self.game_state.state)
                    work = False
                    continue

                if (len(self.players) == 0 and
                        self.game_state.state != "PLAYER_CONN"):
                    self.logger.info("No players left in game, exit.")
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
                self.global_operations()

                self.players.check()
                self.players.release()

            self.players.stop()
            self.logger.info("Closing session %d." % self.session_id)
            self.session_id += 1

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
        self.resources = Resources(env.get_res_name(), env.get_res_link(),
                                   self.logger)
        self.cli.players = self.players
        self.resource_server = ResourceServer(self.logger)
        self.current_player = None

    def accept_connection(self):
        """
        Accept a new connection and create Player object.
        """
        new_conn = self.listening_socket.accept()
        if self.game_state.state == "PLAYER_CONN":
            if len(self.players) < 7:
                self.players.add_player(self.resources, new_conn[0])
                return
        self.logger.info("Disconnected: %s.", str(new_conn[1]))
        new_conn[0].shutdown(socket.SHUT_RDWR)
        new_conn[0].close()

    def begin_game(self):
        """
        Setup before game start.
        """
        try:
            card_num = self.resources.configuration[self.game_state.card_set]
        except Exception:
            card_num = 50
            self.logger.error("no configuration entry for '%s'." %
                              self.game_state.card_set)
        self.cards = list(range(card_num))
        shuffle(self.cards)
        self.logger.info("Card set: %s, number of cards: %s." %
                         (self.game_state.card_set, str(card_num)))
        if len(self.players) == 4:
            self.cards = self.cards[:len(self.cards) - 2]
        elif len(self.players) == 5:
            self.cards = self.cards[:len(self.cards) - 23]
        elif len(self.players) == 6:
            self.cards = self.cards[:len(self.cards) - 26]

        for player in self.players:
            player.cards = self.cards[:6]
            self.cards = self.cards[6:]

    def calculate_result(self):
        """
        Update players' score.
        """
        current_card = self.current_player.current_card
        result = {p: 0 for p in self.players}
        for i in self.players:
            for player in self.players:
                if player is not self.current_player:
                    if i.current_card == player.selected_card:
                        result[i] += 1
        if result[self.current_player] == len(self.players) - 1:
            for player in self.players:
                if player is not self.current_player:
                    player.score += 3
        else:
            if result[self.current_player] != 0:
                for player in self.players:
                    if player is not self.current_player:
                        if player.selected_card == current_card:
                            player.score += 3
                self.current_player.score += 3
            for i in self.players:
                i.score += result[i]

    def global_operations(self):
        """
        Check state transitions in player synchronization points.
        """
        if self.current_player is not None:
            if not self.current_player.verify():
                for player in self.players:
                    player.state = "TURN_SYNC"
        cond = self.get_sync_state()
        if cond == "BEGIN_SYNC":
            if len(self.players) > 0:
                self.begin_game()
                player_lst = ",".join([str(i.number) + ";" + i.name
                                       for i in self.players
                                       if i.get_broadcast])
                for player in self.players:
                    player.state = "READY_WAIT"
                    player.send_message("BEGIN " +
                                        self.game_state.card_set + " " +
                                        ",".join(map(str, player.cards)) +
                                        " " + player_lst)
                self.current_player = self.players.next_player(
                    self.players.players[randrange(len(
                        self.players.players))])
            else:
                self.logger.info("Started game without players, exit.")
                self.game_state.state = "ERROR"
        elif cond == "TURN_SYNC":
            self.current_player = self.players.next_player(self.current_player)
            for player in self.players:
                player.has_turn = player is self.current_player
                player.state = "WAIT_ASSOC"
            self.players.broadcast("TURN " +
                                   str(self.current_player.number))
        elif cond == "SELF_SYNC":
            card_list = [player.current_card
                         for player in self.players]
            shuffle(card_list)
            self.players.broadcast("VOTE " +
                                   ",".join(map(str, card_list)))
            for player in self.players:
                player.state = "WAIT_VOTE"
        elif cond == "VOTE_SYNC":
            self.calculate_result()
            card_list = [str(player.number) + ";" +
                         str(player.current_card) + ";" +
                         str(player.selected_card)
                         for player in self.players]
            score_list = [str(player.number) + ";" +
                          str(player.score)
                          for player in self.players]
            self.players.broadcast("STATUS " +
                                   str(self.current_player.current_card) +
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
                                        ",".join(map(str, player.cards)))
                    player.state = "TURN_SYNC"
            else:
                self.players.broadcast("END_GAME")
                for player in self.players:
                    player.valid = False
                self.game_state.state = "END"

    def check_resource_server(self):
        """
        Check game state and start or stop resource server if necessary.
        """
        if (self.game_state.state == "PLAYER_CONN" and
                not self.resource_server.active):
            self.logger.info("Start resource server.")
            self.resource_server.start()
        if (self.game_state.state != "PLAYER_CONN" and
                self.resource_server.active):
            self.logger.info("Stop resource server.")
            self.resource_server.stop()
