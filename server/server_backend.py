# server_backend.py
import socket
import threading
import os
import time

class FileServer:
    def __init__(self, host='0.0.0.0', port=12345, save_dir='./data/received_files', log_signal=None):
        self.host = host
        self.port = port
        self.save_dir = save_dir
        self.clients = {}
        self.client_lock = threading.Lock()
        self.server_socket = None
        self.is_running = False
        self.log_signal = log_signal  # 添加 log_signal 参数
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
                command = connection.recv(4)
                if not command:
                    break

                if command == b'LIST':
                    self.check_files(connection)
                elif command == b'SEND':
                    self.receive_file(connection, client_ip)
                else:
                    print(f"Unknown command received: {command}")

        except Exception as e:
            print(f"Error handling client {client_address}: {e}")

        finally:
            print(f"Client {client_address} disconnected.")
            connection.close()

    def check_files(self, connection):
        """检查客户端发送的文件列表，返回需要的文件列表"""
        try:
            # 接收文件列表长度
            files_length_data = connection.recv(4)
            if not files_length_data:
                return
            files_length = int.from_bytes(files_length_data, 'big')

            # 接收文件列表
            files_data = connection.recv(files_length).decode()
            client_files = files_data.split('\n')

            # 服务器已有的文件
            server_files = set(os.listdir(self.save_dir))

            # 计算需要发送的文件列表
            files_to_request = [file for file in client_files if file not in server_files]
            files_to_request_data = '\n'.join(files_to_request).encode()

            # 发送需要发送的文件列表长度和数据
            connection.send(len(files_to_request_data).to_bytes(4, 'big'))
            connection.send(files_to_request_data)

        except Exception as e:
            print(f"Error checking files: {e}")

    def receive_file(self, connection, client_ip):
        """接收并保存文件"""
        try:
            while True:
                # 接收文件名长度
                file_name_length_data = connection.recv(4)
                if not file_name_length_data:
                    break

                file_name_length = int.from_bytes(file_name_length_data, 'big')

                # 接收文件名
                file_name = connection.recv(file_name_length).decode()
                file_path = os.path.join(self.save_dir, file_name)

                # 接收文件大小
                file_size_data = connection.recv(8)
                if not file_size_data:
                    break
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
                        message = f"Receiving file '{file_name}': {received_size}/{file_size} bytes"
                        print(message)

                        # # 使用日志信号发送更新到GUI
                        # if self.log_signal:
                        #     self.log_signal.emit(message)

                completion_message = f"Received file '{file_name}' from {client_ip}"
                print(completion_message)
                
                # 使用日志信号发送文件接收完成的消息到GUI
                if self.log_signal:
                    self.log_signal.emit(completion_message)

                with self.client_lock:
                    self.clients[client_ip] += 1

        except Exception as e:
            error_message = f"Error handling client {client_ip}: {e}"
            print(error_message)
            
            # 使用日志信号发送错误消息到GUI
            if self.log_signal:
                self.log_signal.emit(error_message)
