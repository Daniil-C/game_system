"""
Environment variables handling.
"""

import os

def get_ip():
    """
    Get host ip address.
    """
    return os.getenv("HOST_IP", "127.0.0.1")

def get_port():
    """
    Get game server port.
    """
    return int(os.getenv("PORT", "7840"))

def get_res_name():
    """
    Get resourcepack version name.
    """
    return os.getenv("RESOURCES_VERSION", "res_0.0")

def get_res_port():
    """
    Get resource server port
    """
    return get_port() + 1

def get_res_link():
    """
    Get resourcepack link.
    """
    res = os.getenv("RESOURCEPACK", "")
    if res == "":
        res = "http://" + get_ip() + ":" + str(get_res_port()) + "/resources.zip"
    return res

def get_log_file():
    """
    Get log file name.
    """
    return os.getenv("LOG_FILE", "log.txt")
