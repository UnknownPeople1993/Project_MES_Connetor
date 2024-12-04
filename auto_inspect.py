import socket
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import logging
from xml_data_process import xml_data_process
import select
import os
from get_folder_abs_path import get_folder_abs_path

class xml_request_and_response(xml_data_process,get_folder_abs_path):
    def __init__(self):
        super().__init__() 
        
        # 创建一个以当前模块名命名的日志记录器
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # 创建第一个文件处理器并设置相关参数
        project_file_handler = logging.FileHandler(self.get_folder_abs_path(r'log\project_log.log'), mode='a', encoding='utf-8')
        project_file_handler.setLevel(logging.INFO)
        project_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        project_file_handler.setFormatter(project_formatter)

        # 创建第二个文件处理器并设置相关参数
        show_file_handler = logging.FileHandler(self.get_folder_abs_path(r'log\show_log.log'), mode='w', encoding='utf-16')
        show_file_handler.setLevel(logging.INFO)
        show_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        show_file_handler.setFormatter(show_formatter)

        # 将两个文件处理器添加到日志记录器
        self.logger.addHandler(project_file_handler)
        self.logger.addHandler(show_file_handler)

        self.server_address = (self.config_dict["mes_ip"], int(self.config_dict["mes_port"]))
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setblocking(0)
        self.client_socket.settimeout(15)

    def connect_to_mes(self):
        self.logger.info("")
        self.logger.info("")
        self.logger.info("")
        self.logger.info("#################################日志记录信息############################################")
        try:
            self.client_socket.connect(self.server_address)
        except BlockingIOError:
            self.logger.info("正在进行连接...")
        except socket.gaierror as e:
            self.logger.error(f"域名服务器无法正确解析给定的主机名: {e}", exc_info=False)
            if hasattr(self, 'client_socket'):
                self.client_socket.close()
                self.logger.info("MES服务器已关闭")
        except ConnectionRefusedError as e:
            self.logger.error(f"连接被拒绝: {e}", exc_info=False)
            if hasattr(self, 'client_socket'):
                self.client_socket.close()
                self.logger.info("MES服务器已关闭")
        except socket.error as e:
            self.logger.error(f"连接MES系统失败: {e}", exc_info=False)
            if hasattr(self, 'client_socket'): 
                self.client_socket.close() 
                self.logger.info("MES服务器已关闭")  
        except socket.timeout as e:
            self.logger.error(f"与MES系统通信超时: {e}", exc_info=False)
            if hasattr(self, 'client_socket'):
                self.client_socket.close()
                self.logger.info("MES服务器已关闭")
        except Exception as e:
            self.logger.error(f"发生其他异常: {e}", exc_info=False)
            if hasattr(self, 'client_socket'):
                self.client_socket.close()
                self.logger.info("MES服务器已关闭")    
            
        if not self.client_socket.getsockopt(socket.SOL_SOCKET,socket.SO_ERROR):
            self.logger.info("连接到MES服务器")
            

            
    def request_xml_send(self):

        request_xml_data =self.generate_request_xml()

        
        request_xml_data_bytes = request_xml_data.encode('utf-8')
        total_size = len(request_xml_data_bytes) + 4
        size_header = total_size.to_bytes(4, byteorder='big')
        packet = size_header + request_xml_data_bytes
        try:
            # 先发送消息头和XML数据
            self.client_socket.sendall(packet)
            self.logger.info("消息已成功发送给服务器")
        except socket.error as e:
            self.logger.error(f"发送消息时出现错误: {e}")

    
    def response_xml_get(self):
        try:
            while True:
                ready_to_read,_,_ =select.select([self.client_socket], [], [],10)
                if ready_to_read:
                    # 接收消息头（4字节）
                    size_header = self.client_socket.recv(4)
                    if size_header:
                        self.logger.info(f"接收到消息头: {size_header}")
                        break
                    else:
                        self.logger.info("服务器关闭连接，未接收到消息头")
                        break
                else:
                    self.logger.info("等待服务器发送消息头...")
                    break
            # 将消息头字节数据转换为整数，获取后续消息体总长度
            
            total_size = int.from_bytes(size_header, byteorder='big')
            print(total_size)
            self.logger.info(f"从服务器获取到消息体总长度为: {total_size} 字节")
            received_data = b""

            while len(received_data) < total_size:
                remaining_size = total_size - len(received_data)
                data = self.client_socket.recv(remaining_size)
                if not data:
                    self.logger.info("XML数据接收完成。")
                    break
                received_data += data
                self.logger.info("正在接收XML返回数据！")
            root = ET.fromstring(received_data)
            ET.indent(root)
            formatted_xml = ET.tostring(root, encoding='unicode')

            
            xml_name = "Response_{ip}_{ID}_IO.xml".format(ip=self.config_dict["mes_ip"],ID = self.new_uuid)
            write_path = self.get_folder_abs_path("message/{xml_name}".format(xml_name=xml_name))
            tree = ET.ElementTree(root)
            tree.write(write_path,encoding='utf-8',xml_declaration="True")
            self.logger.info(f"服务器接收到的XML数据已存储在message文件夹（{xml_name}）")
            #self.logger.info(f"服务器接收到的XML数据为：\n{formatted_xml}")
            return received_data
        except socket.error as e:
            self.logger.error(f"接收消息时出现错误: {e}")
            return None
    
if __name__ == "__main__":
    Myxml = xml_request_and_response()
    Myxml.connect_to_mes()
    Myxml.request_xml_send()
    response_xml = Myxml.response_xml_get()
    Myxml.extract_key_data(response_xml)