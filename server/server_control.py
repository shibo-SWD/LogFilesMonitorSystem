from server.server_backend import FileServer

class ServerController:
    def __init__(self):
        self.file_server = None

    def start_server(self):
        self.file_server = FileServer()
        self.file_server.start()

    def stop_server(self):
        if self.file_server:
            self.file_server.stop()
