import socket
from connection import connection
import threading
import readline

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


class list_thr(list, monitor):
    def __init__(self, *args, **kwargs):
        monitor.__init__(self)
        list.__init__(self, *args, **kwargs)


class game_state(monitor):
    def __init__(self, initial_state):
        monitor.__init__(self)
        self.state = initial_state


class player(monitor):
    def __init__(self, sock, status, sem):
        monitor.__init__(self)
        self.player_socket = sock
        self.status = status
        self.control_sem = sem
        self.conn = connection(self.player_socket)
        self.valid = True
        self.name = "Player"

    def main(self):
        self.control_sem.acquire()
        self.check_version()

    def check_version(self):
        pass

    def start_game(self):
        pass

    def turn(self):
        pass

    def to_new_turn(self):
        pass

    def end_game(self):
        pass


class CLI:
    def __init__(self, players, game_st):
        self.players = players
        self.game_st = game_st
        readline.set_completer(self.completer)
        readline.set_completer_delims("")
        readline.parse_and_bind("tab: complete")

    def start(self):
        work = True
        print("CLI started")
        while work:
            try:
                cmdline = input("\x1b[1;32m>\x1b[0m$ ").split()
            except Exception as ex:
                print("CLI: error:", ex)
                continue

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
                print("CLI:", len(self.players), "players")
            elif cmdline[0] == "start":
                self.game_st.state = "START_GAME"
                print("CLI: Starting game")
            elif cmdline[0] == "stop":
                self.game_st.state = "STOPPING_SERVER"
                print("CLI: exit")
                work = False
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
    def __init__(self, sock):
        monitor.__init__(self)
        self.sock = sock
        self.active = False

    def main(self):
        while self.active:
            try:
                new_sock = self.sock.accept()
            except:
                continue
            conn = connection(new_sock[0])
            conn.send("DISCONNECT")
            conn.close()


def main(listening_socket):
    game_st = game_state("PLAYER_CONN")
    players = list_thr()
    semaphores = [ ]
    threads = [ ]

    disc = disconnector(listening_socket)

    cli = CLI(players, game_st)

    threads.append(threading.Thread(target=CLI.start, args=(cli,)))
    threads[-1].start()

    first_player = False
    while game_st.state == "PLAYER_CONN":
        try:
            sock_info = listening_socket.accept()
        except:
            continue

        control_sem = threading.Semaphore(0)

        new_player = player(sock_info[0],
                    "PLAYER" if first_player else "MASTER", control_sem)
        players.append(new_player)
        semaphores.append(control_sem)

        threads.append(threading.Thread(target=player.main, args=(new_player,)))
        threads[-1].start()
        first_player = True

    disc.active = True
    disc_thread = threading.Thread(target=disconnector.main, args=(disc,))
    disc_thread.start()

    for p in players:
        p.control_sem.release()

    while game_st.state == "START_GAME":
        pass

    disc.active = False
    disc_thread.join()

    print("Exiting")
    for thr in threads:
        thr.join()
