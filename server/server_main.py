import socket
import connection
import threading


class game_state:
    def __init__(self):
        self.state = "PLAYER_CONN"
        self.sem = threading.Semaphore()


class player:
    def __init__(self, sock, status, semaphore):
        self.player_socket = sock
        self.status = status
        self.semaphore = semaphore

    def main(self):
        pass

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

    def start(self):
        work = True
        print("CLI: Welcome")
        while work:
            cmdline = input("\x1b[1;32m>\x1b[0m$ ").split()
            if len(cmdline) == 0:
                continue

            if cmdline[0] == "help":
                print("Commands:")
                print("\thelp")
                print("\tplayers")
                print("\tstart")
                print("\tstatus")
                print("\tstop")
            elif cmdline[0] == "players":
                print(len(self.players), "players")
            elif cmdline[0] == "start":
                self.game_st.sem.acquire()
                self.game_st.state = "START_GAME"
                self.game_st.sem.release()
                print("Starting game")
            elif cmdline[0] == "stop":
                self.game_st.sem.acquire()
                self.game_st.state = "STOPPING_SERVER"
                self.game_st.sem.release()
                print("Exiting CLI")
                work = False
            elif cmdline[0] == "status":
                self.game_st.sem.acquire()
                print(self.game_st.state)
                self.game_st.sem.release()


def start(listening_socket):
    print("Starting")
    game_st = game_state()
    players = [ ]
    semaphores = [ ]
    threads = [ ]

    cli = CLI(players, game_st)
    print("CLI init")

    threads.append(threading.Thread(target=CLI.start, args=(cli,)))
    print("CLI start")
    threads[-1].start()

    first_player = False
    game_st.sem.acquire()
    while game_st.state == "PLAYER_CONN":
        game_st.sem.release()
        try:
            sock_info = listening_socket.accept()
        except:
            continue

        new_player = Player(sock_info[0],
                    "PLAYER" if first_player else "MASTER", control_sem)
        control_sem = threading.Semaphore()
        control_sem.acquire()
        players.append(new_player)
        semaphores.append(control_sem)

        threads.append(threading.Thread(target=player.main, args=(new_player,)))
        threads[-1].start()
        first_player = True
        game_st.sem.acquire()

    game_st.sem.release()

    print("Exiting")
    for thr in threads:
        thr.join()
