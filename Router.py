from Process import Process

class Router:
    network = None
    processor = None
    metadata = ""

    def __init(self, network):
        self.network = network
        self.network.start_server()
        self.metadata = self.network.get_metadata()
        self.processor = Process(self.network)
        

    def process_data(self, data_to_process):
        self.processor.get_data(data_to_process)