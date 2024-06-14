import socket
from threading import Thread
import os
import ssl
import configparser #ini
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from logging import basicConfig, DEBUG, debug, info
from time import time

#function to read and get paths from configuration file "myc"
def find_path() -> str:
    
    # configparser object
    config = configparser.ConfigParser()
    config.read('myconfig.conf')

    if '200K_FILE_PATH' in config:
        if 'linuxpath' in config['200K_FILE_PATH']:
            # obtain the relative path 
            file_path = config['200K_FILE_PATH']['linuxpath']
            return file_path
    raise ValueError('path not found in configuration file')


def handle_client(
        client_socket: object, file_path: str, reread_on_query: bool):

    start = time()

    # log information
    debug(f"Requesting IP: {client_socket.getpeername()[0]}")
    debug(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # process the data from the client
    while True:
        data = client_socket.recv(1024)
        if not data:
            break

        # decode the received string from the client and strip null characters
        the_string = data.decode('utf-8').strip('\x00')

        if reread_on_query:
            # checks whether the query string is in the file and read ones
            # file_content = read_file(file_path)
            with open(file_path.lstrip(
                    'linuxpath=/').rstrip('\n'), 'r') as file:
                if the_string in file.read():
                    resp = "STRING EXISTS\n"
                else:
                    resp = "STRING DOES NOT EXIST\n"
        else:
            # goes through the file to look for a match
            with open(file_path.lstrip('linuxpath=/').rstrip('\n'),
                      'r') as file:

                for line in file:
                    if line.strip() == the_string:
                        resp = "STRING EXISTS\n"
                        break
                else:
                    resp = 'STRING DOES NOT EXIST\n'

        # the search query log information
        debug(f"Search query: {the_string}")
        client_socket.send(resp.encode('utf-8'))

        # the execution time of the program
        execution_time = time() - start
        debug(f"Execution time: {execution_time} seconds")

    # Close the client socket
    client_socket.close()


def start_server(host: str, port: int, file_path: str,
                 reread_on_query: bool, openssl: dict
                 ):
 

    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if openssl['ssl']:
        # Create SSL context
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

        # Load server-side certificate and key
        context.load_cert_chain(certfile=openssl['certfile'],
                                keyfile=openssl['keyfile'])

        # Wrap the socket with SSL/TLS
        server_socket = context.wrap_socket(server_socket, server_side=True)

    # Bind the socket to a specific host and port
    server_socket.bind((host, port))

    # Listen for incoming connections
    server_socket.listen(5)
    info(f"Server listening on {host} : {port}")

    # create threadpoolexecutor with 10 max_workers
    executor = ThreadPoolExecutor(max_workers=10)

    while True:
        # Accept a client connection
        client_sock, client_addr = server_socket.accept()
        info(f"New connection from {client_addr[0]} : {client_addr[1]}")

        # submit client handling task to the executor
        executor.submit(handle_client,
                        client_sock, file_path, reread_on_query)



def find_config_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, 'myconfig.conf')


def server_setting() -> dict:
 
    config_path = find_config_path()
    config = configparser.ConfigParser()
    config.read(config_path)
    server_section = config['Server']
    ssl_section = config['SSL']
    reread_section = config['REREAD']
    server_setting = {
            'host': server_section.get('host'),
            'port': server_section.getint('port'),
            'REREAD_ON_QUERY': reread_section.getboolean('REREAD_ON_QUERY'),
            'USE_SSL': {
                'ssl': ssl_section.getboolean('ssl_status'),
                'certfile': ssl_section.get('certfile'),
                'keyfile': ssl_section.get('keyfile')
                }

            }

    return server_setting


if __name__ == '__main__':

    # Read the server configuration
    server = server_setting()

    file_path = find_path()
    basicConfig(
            level=DEBUG, format='%(asctime)s - %(levelname)s - %(message)s'
            )
    # start the server
    start_server(server['host'], server['port'],
                 file_path, server['REREAD_ON_QUERY'], server['USE_SSL'])
