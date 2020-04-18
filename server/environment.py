import os

def get_ip():
    return os.getenv("HOST_IP", "127.0.0.1")

def get_port():
    return int(os.getenv("PORT", "7840"))

def get_res_name():
    return os.getenv("RESOURCES_VERSION", "res_0.0")

def get_res_port():
    return get_port() + 1

def get_res_link():
    res = os.getenv("RESOURCEPACK", "")
    if res == "":
        res = "http://" + get_ip() + ":" + str(get_res_port()) + "/resources.zip"
    return res

def get_log_file():
    return os.getenv("LOG_FILE", "log.txt")
