
class DAQTester:
    metadata = b'{"meta": [{"nm": "Interval", "ut": "ms", "min": 0, "max": 0, "prec": 0, "sr": 1}, {"nm": "Utc", "ut": "ms", "min": 0, "max": 0, "prec": 0, "sr": 1}, {"nm": "Battery", "ut": "Volts", "min": 0.0, "max": 20.0, "prec": 2, "sr": 1}, {"nm": "AccelX", "ut": "G", "min": -3.0, "max": 3.0, "prec": 2, "sr": 25}, {"nm": "AccelY", "ut": "G", "min": -3.0, "max": 3.0, "prec": 2, "sr": 25}, {"nm": "AccelZ", "ut": "G", "min": -3.0, "max": 3.0, "prec": 2, "sr": 25}, {"nm": "Yaw", "ut": "Deg/Sec", "min": -120, "max": 120, "prec": 0, "sr": 25}, {"nm": "Pitch", "ut": "Deg/Sec", "min": -120, "max": 120, "prec": 0, "sr": 25}, {"nm": "Roll", "ut": "Deg/Sec", "min": -120, "max": 120, "prec": 0, "sr": 25}, {"nm": "Latitude", "ut": "Degrees", "min": -180.0, "max": 180.0, "prec": 6, "sr": 10}, {"nm": "Longitude", "ut": "Degrees", "min": -180.0, "max": 180.0, "prec": 6, "sr": 10}, {"nm": "Speed", "ut": "MPH", "min": 0.0, "max": 150.0, "prec": 2, "sr": 10}, {"nm": "Altitude", "ut": "ft", "min": 0.0, "max": 4000.0, "prec": 1, "sr": 10}, {"nm": "GPSSats", "ut": "", "min": 0, "max": 20, "prec": 0, "sr": 10}, {"nm": "GPSQual", "ut": "", "min": 0, "max": 5, "prec": 0, "sr": 10}, {"nm": "GPSDOP", "ut": "", "min": 0.0, "max": 20.0, "prec": 1, "sr": 10}, {"nm": "Distance", "ut": "mi", "min": 0.0, "max": 0.0, "prec": 3, "sr": 10}, {"nm": "LapCount", "ut": "", "min": 0, "max": 0, "prec": 0, "sr": 10}, {"nm": "LapTime", "ut": "Min", "min": 0.0, "max": 0.0, "prec": 4, "sr": 10}, {"nm": "Sector", "ut": "", "min": 0, "max": 0, "prec": 0, "sr": 10}, {"nm": "SectorTime", "ut": "Min", "min": 0.0, "max": 0.0, "prec": 4, "sr": 10}, {"nm": "PredTime", "ut": "Min", "min": 0.0, "max": 0.0, "prec": 4, "sr": 5}, {"nm": "ElapsedTime", "ut": "Min", "min": 0.0, "max": 0.0, "prec": 4, "sr": 10}, {"nm": "CurrentLap", "ut": "", "min": 0, "max": 0, "prec": 0, "sr": 10}]}'
    filename = "sampleLog.txt"
    counter = 0
    ROW_COUNT = 0
    data = []


    def __init__(self):
        print("Initializing Test...")
        self.data = [line.rstrip('\n') for line in open(self.filename)]
        self.ROW_COUNT = len(self.data)



    def get_metadata(self):
        return self.metadata

    def get_data(self):
        self.counter = self.counter + 1
        if (self.counter >= self.ROW_COUNT):
            self.counter = 0
        return self.data[self.counter].encode("utf-8")
