# sever_backend.py
import socket
import threading
import os

class FileServer:
    def __init__(self, host='0.0.0.0', port=12345, save_dir='./received_files'):
        self.host = host
        self.port = port
        self.save_dir = save_dir
        self.clients = {}
        self.client_lock = threading.Lock()
        os.makedirs(self.save_dir, exist_ok=True)

    def start(self):
        """启动服务器线程以监听客户端连接"""
        server_thread = threading.Thread(target=self._run_server, daemon=True)
        server_thread.start()

    def _run_server(self):
        """在后台运行的服务器线程"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 设置套接字选项以允许重用地址
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            connection, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")
            threading.Thread(target=self._handle_client, args=(connection, client_address)).start()

    def _handle_client(self, connection, client_address):
        """处理每个客户端的连接"""
        client_ip = client_address[0]
        with self.client_lock:
            if client_ip not in self.clients:
                self.clients[client_ip] = 0

        try:
            while True:
                # 接收文件名长度
                file_name_length_data = connection.recv(4)
                if not file_name_length_data:
                    break  # 如果没有数据，可能是客户端断开了连接

                file_name_length = int.from_bytes(file_name_length_data, 'big')

                # 接收文件名
                file_name = connection.recv(file_name_length).decode()
                file_path = os.path.join(self.save_dir, file_name)

                # 接收文件大小
                file_size_data = connection.recv(8)
                file_size = int.from_bytes(file_size_data, 'big')
                received_size = 0

                # 接收文件数据
                with open(file_path, 'wb') as f:
                    while received_size < file_size:
                        data = connection.recv(1024)
                        if not data:
                            break
                        f.write(data)
                        received_size += len(data)

                print(f"Received file '{file_name}' from {client_address}")

                # 更新客户端文件计数
                with self.client_lock:
                    self.clients[client_ip] += 1

        except Exception as e:
            print(f"Error handling client {client_address}: {e}")

        finally:
            print(f"Client {client_address} disconnected.")
            # with self.client_lock:
            #     if client_ip in self.clients:
            #         del self.clients[client_ip]
            connection.close()
import socket
import threading
import os

class FileServer:
    def __init__(self, host='0.0.0.0', port=12345, save_dir='./received_files'):
        self.host = host
        self.port = port
        self.save_dir = save_dir
        self.clients = {}
        self.client_lock = threading.Lock()
        self.server_socket = None
        self.is_running = False  # 新增的标志位
        os.makedirs(self.save_dir, exist_ok=True)

    def start(self):
        """启动服务器线程以监听客户端连接"""
        self.is_running = True
        server_thread = threading.Thread(target=self._run_server, daemon=True)
        server_thread.start()

    def stop(self):
        """停止服务器"""
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()

    def _run_server(self):
        """在后台运行的服务器线程"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        while self.is_running:
            try:
                connection, client_address = self.server_socket.accept()
                print(f"Accepted connection from {client_address}")
                threading.Thread(target=self._handle_client, args=(connection, client_address)).start()
            except OSError:
                break  # 当服务器 socket 关闭时会抛出 OSError 异常

        self.server_socket.close()

    def _handle_client(self, connection, client_address):
        """处理每个客户端的连接"""
        client_ip = client_address[0]
        with self.client_lock:
            if client_ip not in self.clients:
                self.clients[client_ip] = 0

        try:
            while True:
                file_name_length_data = connection.recv(4)
                if not file_name_length_data:
                    break

                file_name_length = int.from_bytes(file_name_length_data, 'big')

                file_name = connection.recv(file_name_length).decode()
                file_path = os.path.join(self.save_dir, file_name)

                file_size_data = connection.recv(8)
                file_size = int.from_bytes(file_size_data, 'big')
                received_size = 0

                with open(file_path, 'wb') as f:
                    while received_size < file_size:
                        data = connection.recv(1024)
                        if not data:
                            break
                        f.write(data)
                        received_size += len(data)

                print(f"Received file '{file_name}' from {client_address}")

                with self.client_lock:
                    self.clients[client_ip] += 1

        except Exception as e:
            print(f"Error handling client {client_address}: {e}")

        finally:
            print(f"Client {client_address} disconnected.")
            connection.close()
