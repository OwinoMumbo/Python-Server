import os
import pytest
import server
import configparser
import signal
import threading
import time
import requests
import socket
from server import start_server, server_setting, find_path
from client import string_query_search
from collections import Callable


stop_server_flag = threading.Event()


def test_find_path():

    config = configparser.ConfigParser()
    path = server.find_path()

    assert isinstance(path, str), " the path should be a string"

    assert path is not None and path != "", "The path must exist"

    assert "200K_FILE_PATH" not in config or \
        'linuxpath' not in config['200K_FILE_PATH'], "200K_FILE_PATH in configuration file"


def test_server_setting():

    config = server_setting()

    assert isinstance(config, dict), "server_setting returns a dictionary"
    assert 'host' in config, "host is in configuration file"
    assert 'port' in config, "port is in configuration file"
    assert 'REREAD_ON_QUERY' in config, "REREAD_ON_QUERY exists"
    assert 'USE_SSL' in config, "USE_SSL exists"
    assert isinstance(config['USE_SSL'], dict), "USE_SSL is a dictionary"
    assert 'ssl' in config['USE_SSL'], "ssl exist in USE_SSL dictionary"
    assert 'certfile' in config['USE_SSL']
    assert 'keyfile' in config['USE_SSL']
    assert isinstance(config['REREAD_ON_QUERY'], bool)
    assert type(config['port']) is int
    assert type(config['host']) is str


def test_start_server():
  
    started = None
    FILE_PATH = find_path()
    server = server_setting()
    try:
        server_thread = threading.Thread(
            target=start_server,
            args=(server['host'], server['port'], FILE_PATH,
                  server['REREAD_ON_QUERY'], server['USE_SSL']))
        server_thread.start()
        started = True
    except Exception:
        started = False
    # Wait for the server to start
    time.sleep(1)

    # Stop the server by setting the stop_server_flag
    stop_server_flag.set()

    # Stop the server
    server_thread.join(timeout=1)

    
    assert server_thread.is_alive(), "Assert that the server is alive"
    
    assert started, "Assert that the server started"
