""" Interface for main menu """
import tkinter as tk
PLAYERS = 0
SERVER_IP = ""
SERVER_PORT = 0

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
    return (ip_flg and port_flg)

class App(tk.Frame):
    """ App Class"""
    def __init__(self, master=None):
        tk.Frame.__init__(self, master, borderwidth=2, relief="ridge",
                          cursor="dot", height=1080, width=1920)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.master.title("IMAGINARIUM")
        self.grid_propagate(0)
        self.grid(sticky="NEWS")
        self.widgets = [ ]
        self.main_menu()

    def settings_menu(self):
        """game settings"""
        def save(*arg):
            """Save ip and port"""
            if checker(server_ip_entry.get(), server_port_entry.get()):
                SERVER_IP = server_ip_entry.get()
                SERVER_PORT = server_port_entry.get()
                message["text"] = "SAVED!"
                message.grid(sticky="NEWS", column=1, row=3)
                server_port_entry.delete(0, tk.END)
                server_ip_entry.delete(0, tk.END)
            else:
                message["text"] = "Incorrect data. Try again."
                message.grid(sticky="NEWS", column=1, row=3)

        for i in self.widgets:
            i.grid_forget()
        self.widgets.clear()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.rowconfigure(6, weight=1)

        server_ip_label = tk.Label(master=self, text="Server IP")
        server_ip_label.grid(sticky="NEWS", column=1, row=1)
        self.widgets.append(server_ip_label)

        server_ip_entry = tk.Entry(master=self)
        server_ip_entry.grid(sticky="NEW", column=1, row=2)
        self.widgets.append(server_ip_entry)

        server_port_label = tk.Label(master=self, text="Server port")
        server_port_label.grid(sticky="NEWS", column=1, row=4)
        self.widgets.append(server_port_label)

        server_port_entry = tk.Entry(master=self)
        server_port_entry.grid(sticky="NEW", column=1, row=5)
        self.widgets.append(server_port_entry) 

        self.back = tk.PhotoImage(file="back.png")
        back_button = tk.Button(master=self, image=self.back, command=self.main_menu)
        back_button.grid(sticky="W", column=0, row=6)
        self.widgets.append(back_button)	

        save_button = tk.Button(master=self, text="Save", height=3, width=10, command=save)
        save_button.grid(sticky="N", column=1, row=6)
        self.widgets.append(save_button)

        message = tk.Label(master=self, text="")
        message.grid(sticky="NEWS", column=1, row=3)
        self.widgets.append(message)

    def rule_menu(self):
        """RULES"""
        for i in self.widgets:
            i.grid_forget()
        self.widgets.clear()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        rule_lable = tk.Label(master=self, text="RULE")
        rule_lable.grid(sticky="NEWS", column=1, row=0)
        self.widgets.append(rule_label)

        rules = tk.Label(master=self, text="")
        rules.grid(sticky="NEWS", column=1, row=0)
        self.widgets.append(rules)


    def main_menu(self):
        """Main menu interface loader"""
        for i in self.widgets:
            i.grid_forget()
        self.widgets.clear()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.rowconfigure(6, weight=1)

        game_name = tk.Label(master=self, text="IMAGINARIUM")
        game_name.grid(sticky="NEWS", column=1, row=0)
        self.widgets.append(game_name)

        play_button = tk.Button(master=self, text="Play")#, command=self.play_menu)
        play_button.grid(sticky="NEWS", column=1, row=2)
        self.widgets.append(play_button)

        exit_button = tk.Button(self, text="Exit", command=self.quit)
        exit_button.grid(sticky="NEWS", column=1, row=4)
        self.widgets.append(exit_button)

        self.gear = tk.PhotoImage(file="settings.png")
        settings_button = tk.Button(master=self, image=self.gear, command=self.settings_menu)
        settings_button.grid(sticky="W", column=0, row=6)
        self.widgets.append(settings_button)

        self.rule = tk.PhotoImage(file="rule.png")
        rule_button = tk.Button(master=self, image=self.rule)
        rule_button.grid(sticky="E", column=2, row=6)
        self.widgets.append(rule_button)



APP = App()
APP.mainloop()
