import socket
from connection import connection
import threading
import readline
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import server.environment as env
import time


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


class player(monitor):
    def __init__(self, sock, status, sem, res, game_st):
        monitor.__init__(self)
        self.player_socket = sock
        self.status = status
        self.control_sem = sem
        self.conn = connection(self.player_socket)
        self.valid = True
        self.name = "Player"
        self.res = res
        self.game_st = game_st

    def main(self):
        self.check_version()
        if not self.valid:
            return
        if self.status == "MASTER":
            self.master_wait()
            if self.game_st == "PLAYER_CONN":
                self.game_st = "START_GAME"
        self.control_sem.acquire()
        self.valid = False

    def check_version(self):
        self.conn.send("VERSION_REQUEST " + self.res.name)
        resp = self.conn.get().split()
        if resp[0] != "VERSION_RESPONSE":
            self.valid = False
            return
        self.name = resp[2]
        if resp[1] == "OK":
            self.conn.send(self.status)
            return
        elif resp[1] == "UPDATE":
            self.conn.send("VERSION_LINK " + self.res.link)
            r = self.conn.get().split()
            if r[0] == "UPDATE_OK":
                self.conn.send(self.status)
                return
            else:
                self.conn.send("DISCONNECT")
                self.valid = False
                return
        else:
            self.conn.send("DISCONNECT")
            self.valid = False
            return

    def master_wait(self):
        resp = self.conn.get()
        if resp[0] != "START_GAME":
            self.valid = False

    def start_game(self):
        pass

    def turn(self):
        pass

    def to_new_turn(self):
        pass

    def end_game(self):
        pass


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
                print("CLI: error:", ex)
                continue

            if not self.work:
                break

            if len(cmdline) == 0:
                continue

            if cmdline[0] == "help":
                print("CLI commands:")
                print("\thelp")
                print("\tplayers")
                print("\tstart")
                print("\tstatus")
                print("\tstop")
            elif cmdline[0] == "players":
                self.players.acquire()
                print("CLI:", len(self.players.players), "players")
                for i in self.players.players:
                    print(i.name)
                self.players.release()
            elif cmdline[0] == "start":
                self.game_st.state = "START_GAME"
                print("CLI: Starting game")
            elif cmdline[0] == "stop":
                self.game_st.state = "STOPPING_SERVER"
                print("CLI: exit")
                self.work = False
            elif cmdline[0] == "status":
                print(self.game_st.state)
            else:
                print("CLI: error: unknown command")

    def completer(self, text, state):
        commands = ["help", "players", "start", "status", "stop"]
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
            conn.send("DISCONNECT")
            conn.close()


class player_list(monitor):
    def __init__(self, logger, game_st):
        monitor.__init__(self)
        self.players = [ ]
        self.semaphores = [ ]
        self.threads = [ ]
        self.sem = threading.Semaphore(1)
        self.locked = False
        self.check = False
        self.logger = logger
        self.game_st = game_st

    def checker(self):
        while self.check:
            self.acquire()
            for i in range(len(self.players)):
                if not self.players[i].valid:
                    self.threads[i].join()
                    if self.players[i].status == "MASTER":
                        fl = True
                    else:
                        fl = False
                    del self.semaphores[i]
                    del self.players[i]
                    del self.threads[i]
                    if fl and len(self.players) > 0:
                        self.players[0].status = "MASTER"
                    break
            self.release()
            time.sleep(1)

    def start_check(self):
        self.check = True
        self.check_thread = threading.Thread(target=player_list.checker,
                    args=(self,))
        self.check_thread.start()

    def stop_check(self):
        self.check = False
        self.check_thread.join()
        for i in range(len(self.players)):
            self.players[i].valid = False
            self.threads[i].join()
        self.players.clear()
        self.threads.clear()
        self.semaphores.clear()

    def acquire(self):
        self.sem.acquire()
        self.locked = True

    def release(self):
        self.locked = False
        self.sem.release()

    def add_player(self, is_master, res, sock):
        self.acquire()
        control_sem = threading.Semaphore(0)
        new_player = player(sock, "MASTER" if is_master else "PLAYER",
                    control_sem, res, self.game_st)
        self.players.append(new_player)
        self.semaphores.append(control_sem)

        self.threads.append(threading.Thread(target=player.main,
                    args=(new_player,)))
        self.threads[-1].start()
        self.release()


def main(listening_socket, logger):
    game_st = game_state("PLAYER_CONN")
    players = player_list(logger, game_st)
    players.start_check()

    res = resources("res", env.get_res_link())

    disc = disconnector(listening_socket, logger)

    cli = CLI(players, game_st)
    cli.start()

    first_player = False

    # player connection and version check
    res_server = resource_server(logger)
    res_server.start()

    while game_st.state == "PLAYER_CONN":
        try:
            sock_info = listening_socket.accept()
        except:
            continue

        players.add_player(not first_player, res, sock_info[0])
        first_player = True

    disc.start()

    res_server.stop()

    players.acquire()
    for p in players.players:
        p.control_sem.release()
    players.release()

    # starting game
    while game_st.state == "START_GAME":
        pass

    players.stop_check()
    disc.stop()
    cli.stop()

    print("Exiting")
