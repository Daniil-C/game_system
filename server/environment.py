import os

def get_ip():
    return os.getenv("HOST_IP", "127.0.0.1")

def get_port():
    return int(os.getenv("PORT", "7840"))

def get_res_port():
    return get_port() + 1

def get_res_link():
    res = os.getenv("RESOURCEPACK", "")
    if res == "":
        res = "http://" + get_ip() + ":" + str(get_res_port()) + "/resources.zip"
