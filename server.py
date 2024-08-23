import socket
import os

def start_server(save_directory, host='0.0.0.0', port=12345):
    # 创建一个 TCP/IP 套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 绑定套接字到地址和端口
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server is running. Waiting for connection on port {port}...")

    while True:
        # 等待并接受客户端连接
        connection, client_address = server_socket.accept()
        print(f"Client connected from {client_address}!")

        try:
            while True:
                # 接收文件名长度
                file_name_length = int.from_bytes(connection.recv(4), 'big')
                if not file_name_length:
                    break
                # 接收文件名
                file_name = connection.recv(file_name_length).decode()
                file_path = os.path.join(save_directory, file_name)

                # 接收文件大小
                file_size = int.from_bytes(connection.recv(8), 'big')
                received_size = 0
                
                # 接收文件数据
                with open(file_path, 'wb') as f:
                    while received_size < file_size:
                        data = connection.recv(1024)
                        if not data:
                            break
                        f.write(data)
                        received_size += len(data)

                print(f"File '{file_name}' received and saved to '{file_path}'.")

        finally:
            connection.close()

if __name__ == "__main__":
    # 设置保存文件的目录
    save_directory = "./received_files"
    os.makedirs(save_directory, exist_ok=True)
    start_server(save_directory)