
import socket
from threading import Thread
from Process import Process
from Utilities import replace_value_with_definition, readify_data, string_me

def do_some_stuffs_with_input(input_string):  
    """
    This is where all the processing happens.

    Let's just read the string backwards
    """
    import time
    millis = str(int(round(time.time() * 1000)))
    auth_string = '{"status":"ok", "utc":' + millis + '}'

    print("Processing that nasty input!")
    return auth_string

class Network:
    # DAQ DATA
    metadata = ""
    data = []

    # Routing Class
    process = None

    # Server Configs
    listen_address = "0.0.0.0"
    listen_port = 8080

    def __init__(self):
        self.process = Process()


    def start_server(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # this is for easy starting/killing the app
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('Socket created')

        try:
            soc.bind((self.listen_address, self.listen_port))
            print('Socket bind complete')
        except socket.error as msg:
            import sys
            print('Bind failed. Error : ' + str(sys.exc_info()))
            print(msg)
            sys.exit()

        #Start listening on socket
        soc.listen(10)
        print('Socket now listening')


        # this will make an infinite loop needed for 
        # not reseting server for every client
        while True:
            conn, addr = soc.accept()
            ip, port = str(addr[0]), str(addr[1])
            print('Accepting connection from ' + ip + ':' + port)
            try:
                Thread(target=self.client_thread, args=(conn, ip, port)).start()
            except:
                print("Terrible error!")
                import traceback
                traceback.print_exc()
        soc.close()
    
    def client_thread(self, conn, ip, port, MAX_BUFFER_SIZE = 4096):
        # the input is in bytes, so decode it
        input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)

        # MAX_BUFFER_SIZE is how big the message can be
        # this is test if it's sufficiently big
        import sys
        siz = sys.getsizeof(input_from_client_bytes)
        if  siz >= MAX_BUFFER_SIZE:
            print("The length of input is probably too long: {}".format(siz))

        # decode input and strip the end of line
        input_from_client = input_from_client_bytes.decode("utf8")

        res = do_some_stuffs_with_input(input_from_client)
        print("Result of processing {} is: {}".format(input_from_client, res))

        vysl = res.encode("utf8")  # encode the result string
        conn.sendall(vysl)  # send it to client    

#        self.authenticate_daq(conn, ip, port, MAX_BUFFER_SIZE)
        self.process_metadata_from_daq(conn, ip, port, MAX_BUFFER_SIZE)
        while True:
            # the input is in bytes, so decode it
            input_from_daq_bytes = conn.recv(MAX_BUFFER_SIZE)
            import sys
            siz = sys.getsizeof(input_from_daq_bytes)
            if  siz >= MAX_BUFFER_SIZE:
                print("The length of input is probably too long: {}".format(siz))
            # decode input
            input_from_daq = input_from_daq_bytes.decode("utf8")
            print(input_from_daq)
            self.process.get_data(input_from_daq)

    def authenticate_daq(self, conn, ip, port, max_buffer_size):
        # On first input, ignore it 
        input_from_client_bytes = conn.recv(max_buffer_size)
        print("Inside Auth: " + input_from_client_bytes.decode("utf8"))
        import sys
        siz = sys.getsizeof(input_from_client_bytes)
        if  siz >= max_buffer_size:
            print("The length of input is probably too long: {}".format(siz))

        input_from_client = input_from_client_bytes.decode("utf8")

        # Send authentication string back to DAQ (dw we the REAL Podium Connect)
        import time
        millis = str(int(round(time.time() * 1000)))
        auth = '{"status":"ok", "utc":' + millis + '}'
        auth_encoded = auth.encode("utf8")  # encode the result string
        conn.sendall(auth_encoded)  # send it to client

    def process_metadata_from_daq(self, conn, ip, port, max_buffer_size):
        print("Im trying to process metadata")
        statement = '{"getMeta":null}\r\n'
        while True:
            conn.sendall(statement.encode("utf-8"))
            meta = conn.recv(max_buffer_size).decode("utf-8")
            print("inside meta: " + meta)
            if meta is not None and b'{"meta"' in meta:
                try:
                    raw_data = string_me(meta)
                    self.metadata = raw_data
                except Exception as e:
                    print(e)
                finally:
                    print("Updated Channel Metadata")
                    break


    def get_metadata(self):
        return self.metadata
        