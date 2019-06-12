
import time
import json
import re


CHANNEL_TYPE_UNKNOWN = 0
CHANNEL_TYPE_SENSOR = 1
CHANNEL_TYPE_IMU = 2
CHANNEL_TYPE_GPS = 3
CHANNEL_TYPE_TIME = 4
CHANNEL_TYPE_STATS = 5


class SampleMetaException(Exception):
    pass


class SampleValue(object):
    def __init__(self, value, channelMeta):
        self.value = value
        self.channelMeta = channelMeta


STARTING_BITMAP = 1


class ChannelMeta(object):
    DEFAULT_NAME = ''
    DEFAULT_UNITS = ''
    DEFAULT_MIN = 0
    DEFAULT_MAX = 100
    DEFAULT_SAMPLE_RATE = 1
    DEFAULT_PRECISION = 0
    DEFAULT_TYPE = 0

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', ChannelMeta.DEFAULT_NAME)
        self.units = kwargs.get('units', ChannelMeta.DEFAULT_UNITS)
        self.min = kwargs.get('min', ChannelMeta.DEFAULT_MIN)
        self.max = kwargs.get('max', ChannelMeta.DEFAULT_MAX)
        self.precision = kwargs.get('prec', ChannelMeta.DEFAULT_PRECISION)
        self.sampleRate = kwargs.get(
            'sampleRate', ChannelMeta.DEFAULT_SAMPLE_RATE)
        self.type = kwargs.get('type', ChannelMeta.DEFAULT_TYPE)

    @staticmethod
    def filter_name(name):
        return ''.join([char for char in name if char.isalnum() or char == ' ' or char == '_'])

    def fromJson(self, json):
        self.name = json.get('nm', self.name)
        self.units = json.get('ut', self.units)
        self.min = json.get('min', self.min)
        self.max = json.get('max', self.max)
        self.precision = json.get('prec', self.precision)
        self.sampleRate = int(json.get('sr', self.sampleRate))
        self.type = int(json.get('type', self.type))


class ChannelMetaCollection(object):
    channel_metas = []

    def fromJson(self, metaJson):
        channel_metas = self.channel_metas
        del channel_metas[:]
        for ch in metaJson:
            channel_meta = ChannelMeta()
            channel_meta.fromJson(ch)
            channel_metas.append(channel_meta)


def do_some_stuffs_with_input(input_string):  
    """
    This is where all the processing happens.

    Let's just read the string backwards
    """
    import time
    millis = str(int(round(time.time() * 1000)))
    auth_string = '{"status":"ok", "utc":' + millis + '}'

    return auth_string

def client_thread(conn, ip, port, MAX_BUFFER_SIZE = 16384):

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
    vysl = res.encode("utf8")  # encode the result string
    conn.sendall(vysl)  # send it to client
    counter = 0
    last_token = ""
    token = ""
    metas = ChannelMetaCollection()
    samples = []

    while True:
        data = conn.recv(MAX_BUFFER_SIZE)
        import sys
        siz = sys.getsizeof(data)
        if  siz >= MAX_BUFFER_SIZE:
            print("The length of input is probably too long: {}".format(siz))

        data_decoded = data.decode("utf8")
        if data_decoded.startswith('{"s"'):
            last_token = token
            token = data_decoded
        else:
            token = token + data_decoded
        
        if '"meta"' in last_token:
            full_token_json = json.loads(last_token.split("}}", 1)[0] + "}}")
            metas.fromJson(full_token_json['s']['meta'])
            print(metas)
            break
    while True:
        data = conn.recv(MAX_BUFFER_SIZE)
        import sys
        siz = sys.getsizeof(data)
        if  siz >= MAX_BUFFER_SIZE:
            print("The length of input is probably too long: {}".format(siz))

        data_decoded = data.decode("utf8")
        if data_decoded.startswith('{"s"'):
            last_token = token
            token = data_decoded
        else:
            token = token + data_decoded
        
        if last_token != "":
            processed_data = get_data(last_token, metas, samples)
            print(processed_data)
            last_token = ""
    
     
def get_data(row, metas, samples):
        if row is not None and b'{\"s\":{' in row:
            try:
                # Decode binary and convert into list
                raw_data_decoded = row.decode("utf-8")
                raw_data = json.loads(raw_data_decoded)
                # Process data using channels - converting into dict
                processData(raw_data['s']['d'], samples, metas)
            except Exception as e:
                print(e)
        # Make ready for transmission
        return readify_samples(samples)

def processData(data_json, samples, metas):
    metas = metas.channel_metas
    channel_config_count = len(metas)
    bitmask_field_count = max(0, int((channel_config_count - 1) / 32)) + 1

    max_field_count = channel_config_count + bitmask_field_count

    field_data = data_json
    field_data_size = len(field_data)
    if field_data_size > max_field_count or field_data_size < bitmask_field_count:
        raise Exception(
            'Unexpected data packet count {}; channel meta expects between {} and {} channels'.format(field_data_size,
                                                                                                        bitmask_field_count,
                                                                                                        max_field_count))

    bitmask_fields = []
    for i in range(field_data_size - bitmask_field_count, field_data_size):
        bitmask_fields.append(int(field_data[i]))

    del samples[:]

    channel_config_index = 0
    bitmap_index = 0
    field_index = 0
    mask_index = 0
    channel_config_count = len(metas)
    while channel_config_index < channel_config_count:
        if mask_index >= 32:
            mask_index = 0
            bitmap_index += 1
            if bitmap_index > len(bitmask_fields):
                print("channel count overflowed number of bitmap fields available")

        mask = 1 << mask_index
        if (bitmask_fields[bitmap_index] & mask) != 0:
            value = float(field_data[field_index])
            field_index += 1
            sample = SampleValue(value, metas[channel_config_index])
            samples.append(sample)
        channel_config_index += 1
        mask_index += 1
    return samples

def readify_samples(samples):
    d = {}
    for sample in samples:
        d[sample.channelMeta.name] = sample.value

    #d = self.calculate_fuel_usage(d)

    # Convert into JSON Object and convert into bytes
    return readify_data(d)



def start_server():

    import socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this is for easy starting/killing the app
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Socket created')

    try:
        soc.bind(("0.0.0.0", 8080))
        print('Socket bind complete')
    except socket.error as msg:
        import sys
        print('Bind failed. Error : ' + str(sys.exc_info()))
        print(msg)
        sys.exit()

    #Start listening on socket
    soc.listen(10)
    print('Socket now listening')

    # for handling task in separate jobs we need threading
    from threading import Thread

    # this will make an infinite loop needed for 
    # not reseting server for every client
    while True:
        conn, addr = soc.accept()
        ip, port = str(addr[0]), str(addr[1])
        print('Accepting connection from ' + ip + ':' + port)
        try:
            Thread(target=client_thread, args=(conn, ip, port)).start()
        except:
            print("Terrible error!")
            import traceback
            traceback.print_exc()
    soc.close()

start_server()  