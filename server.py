import socket

def start_server():
    # 创建一个 TCP/IP 套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 绑定套接字到地址和端口
    server_socket.bind(('0.0.0.0', 12345))
    
    # 监听传入连接
    server_socket.listen(5)
    print("Server is running. Waiting for connection on port 12345...")

    # 等待并接受客户端连接
    connection, client_address = server_socket.accept()
    print(f"Client connected from {client_address}!")

    try:
        while True:
            # 接收客户端发送的数据
            data = connection.recv(128)
            if data:
                print(f"Received data: {data.decode()}")
            else:
                print("No more data from client. Closing connection.")
                break
    finally:
        # 关闭连接
        connection.close()

if __name__ == "__main__":
    start_server()