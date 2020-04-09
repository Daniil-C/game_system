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
                          cursor="dot") #, height=master.winfo_screenheight(), width=master.winfo_screenwidth())
        self["height"] = self.master.winfo_screenheight()
        self["width"] = self.master.winfo_screenwidth()
        self.master.attributes("-fullscreen", True)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.master.title("IMAGINARIUM")
        self.grid_propagate(0)
        self.grid(sticky="NEWS")
        self.master.resizable(False, False)
        self.widgets = [ ]
        self.main_menu()

    def settings_menu(self):
        """game settings"""
        def save(*arg):
            """Save ip and port"""
            if checker(server_ip_entry.get(), server_port_entry.get()):
                SERVER_IP = server_ip_entry.get()
                SERVER_PORT = server_port_entry.get()
                self.BG_settings = tk.PhotoImage(file="BG_settings_saved.png")
                bg_settings["image"] = self.BG_settings
                bg_settings.grid(sticky="NEWS", column=0, row=0, columnspan = 3, rowspan = 7)
                server_port_entry.delete(0, tk.END)
                server_ip_entry.delete(0, tk.END)
            else:
                self.BG_settings = tk.PhotoImage(file="BG_settings_not_saved.png")
                bg_settings["image"] = self.BG_settings
                bg_settings.grid(sticky="NEWS", column=0, row=0, columnspan = 3, rowspan = 7)

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

        self.BG_settings = tk.PhotoImage(file="BG_settings.png")
        bg_settings = tk.Label(master=self, image=self.BG_settings)
        bg_settings.grid(sticky="NEWS", column=0, row=0, columnspan = 3, rowspan = 7)
        self.widgets.append(bg_settings)

        server_ip_entry = tk.Entry(master=self)
        server_ip_entry.grid(sticky="NEW", column=1, row=2)
        self.widgets.append(server_ip_entry)

        server_port_entry = tk.Entry(master=self)
        server_port_entry.grid(sticky="NEW", column=1, row=5)
        self.widgets.append(server_port_entry) 

        self.back = tk.PhotoImage(file="back.png")
        back_button = tk.Button(master=self, image=self.back, command=self.main_menu, borderwidth=0, relief=tk.FLAT)
        back_button.grid(sticky="W", column=0, row=6)
        self.widgets.append(back_button)	

        self.save = tk.PhotoImage(file="save.png")
        save_button = tk.Button(master=self, image=self.save, command=save, borderwidth=0, relief=tk.FLAT)
        save_button.grid(sticky="N", column=1, row=6)
        self.widgets.append(save_button)

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

        self.bg = tk.PhotoImage(file="BG.png")
        bg = tk.Label(master=self, image=self.bg)
        bg.grid(sticky="NEWS", column=0, row=0, columnspan = 3, rowspan = 7)
        self.widgets.append(bg)

        self.play = tk.PhotoImage(file="play.png")
        play_button = tk.Button(master=self, image=self.play, borderwidth=0, relief=tk.FLAT)#, command=self.play_menu)
        play_button.grid(column=1, row=3)
        self.widgets.append(play_button)

        self.exit = tk.PhotoImage(file="exit.png")
        exit_button = tk.Button(self, image=self.exit, command=self.quit, borderwidth=0, relief=tk.FLAT)
        exit_button.grid(column=1, row=5)
        self.widgets.append(exit_button)

        self.gear = tk.PhotoImage(file="settings.png")
        settings_button = tk.Button(master=self, image=self.gear, command=self.settings_menu, borderwidth=0, relief=tk.FLAT)
        settings_button.grid(sticky="W", column=0, row=6)
        self.widgets.append(settings_button)

        self.rule = tk.PhotoImage(file="rule.png")
        rule_button = tk.Button(master=self, image=self.rule, borderwidth=0, relief=tk.FLAT)
        rule_button.grid(sticky="E", column=2, row=6)
        self.widgets.append(rule_button)


APP = App()
APP.mainloop()
