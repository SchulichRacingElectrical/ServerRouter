import random
import re
import time
import datetime
import platform
import json

from Utilities import replace_value_with_definition, readify_data, string_me

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


class Process:
    samples = []
    timeout = 1
    metas = ChannelMetaCollection()
    writeTimeout = 3
    data = {}
    last_called = None
    cumulative_fuel_usage = 0
    


    def __init__(self):
        self.last_called = time.time()



    def updateMeta(self, raw_metadata):
        while True:
            ### CHANGE TO SUPPORT STREAMING ###
            meta = raw_metadata
            #### END CHANGE ###
            if meta is not None and b'{"meta"' in meta:
                try:
                    raw_data = string_me(meta)
                    self.metas = ChannelMetaCollection()
                    self.metas.fromJson(raw_data["meta"])
                except Exception as e:
                    print(e)
                finally:
                    print("Updated Channel Metadata")
                    break

    def processData(self, data_json):
        metas = self.metas.channel_metas
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

        samples = self.samples
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

    def readify_samples(self):
        d = {}
        samples = self.samples

        for sample in samples:
            d[sample.channelMeta.name] = sample.value

        #d = self.calculate_fuel_usage(d)

        # Convert into JSON Object and convert into bytes
        return readify_data(d)

    def get_data(self, row):
        if row is not None and b'{\"s\":{' in row:
            try:
                # Decode binary and convert into list
                raw_data_decoded = row.decode("utf-8")
                raw_data = json.loads(raw_data_decoded)
                # Process data using channels - converting into dict
                self.processData(raw_data['s']['d'])
            except Exception as e:
                print(e)
        # Make ready for transmission
        return self.readify_samples()

    # def calculate_fuel_usage(self, data):
    #     time_elapsed = time.time() - self.last_called
    #     self.last_called = time.time()
    #     correction = 1
    #     x = ((correction * (data["injectorPW"] - 0.5) * data["rpm"]) / 120)
    #     self.cumulative_fuel_usage = (self.cumulative_fuel_usage + x * (time_elapsed / 60 / 1000))
    #     data = replace_value_with_definition(data, "fuelRate", round(x, 2))

    #     data = replace_value_with_definition(data, "fuelUsage", round(self.cumulative_fuel_usage, 3))
    #     return data
    