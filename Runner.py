from Process import Process
from TestDAQ import DAQTester
if __name__ == "__main__":
    tester = DAQTester()
    processor = Process(tester)

    while True:
        data = processor.get_data()
        print(data)
        