import socket
import ssl
import argparse
from server import server_setting

# Server configuration.

HOST = '0.0.0.0' #Random Address
PORT = 54321 #Unused port number 

#Request a string search from the server.
def string_query_search(str_query: str) -> str:
    
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        with socket.create_connection((HOST, PORT)) as soc:
            with context.wrap_socket(soc, server_hostname=HOST) as secure_socket:

                secure_socket.send(str_query.encode())
                response = secure_socket.recv(1024).decode()
                #check the response and print to terminal
                if response == 'STRING EXISTS':
                    print(f'{response}')
                    return response
                else:
                    print(f'{response}')
                    return response

    #Handle Socket Error
    except socket.error as e:
        print(f'{e}')
    #Handle AuthenticatiOn error from SSL
    except ssl.SSLError as e:
        print(f"SSL error occurred: {str(e)}")
    #Handle other errors. 
    except Exception as e:
        print(f"An error occurred: {str(e)}")
   

if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--search", type=str, help="Search string")

    # Parse the arguments
    args = parser.parse_args()
    search = args.search

    # Search string
    string_query_search(search)
