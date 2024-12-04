import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import json
import logging
from datetime import datetime, timezone
from get_config_info import get_config_info
import uuid
import os
from get_folder_abs_path import get_folder_abs_path


class xml_data_process(get_config_info,get_folder_abs_path):
    def __init__(self):
        super().__init__() 
        # self.logger = logging.getLogger(__name__)
        # logging.basicConfig(
        #         level=logging.INFO,
        #         format='%(asctime)s - %(levelname)s - %(message)s',
        #         filename=os.path.abspath(r'log\project_log.log'),
        #         filemode='a',
        #         encoding='utf-8'
        # )
        
        self.get_config_info()
        self.new_uuid = ''
    def generate_w3c_timestamp(self):
        """
        生成符合W3C标准的时间戳字符串。

        :return: 生成的时间戳字符串
        """
        try:
            now = datetime.now(timezone.utc)
            offset = now.astimezone().strftime('%z')
            offset = offset[:3] + ':' + offset[3:]
            return now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + offset
        except Exception as e:
            self.logger.error(f"生成W3C时间戳时出错: {e}", exc_info=False) 
    
    def generate_request_xml(self):
        """
        根据配置信息和读取的扫描仪信息生成特定结构的XML数据，并对其进行美化处理后记录到日志中。
        """
        

        # 创建XML根元素
        root = ET.Element("root")

        # 创建header元素并设置属性和子元素
        header = ET.SubElement(root, "header")
        header.set("eventId", str(self.config_dict["event_id"]))
        header.set("eventName", self.config_dict["event_name"])
        header.set("version", self.config_dict["version"])
        header.set("eventSwitch", self.config_dict["event_switch"])
        header.set("timeStamp", self.generate_w3c_timestamp())
        header.set("user", self.config_dict["user"])
        header.set("pwd", self.config_dict["password"])
        header.set("contentType", self.config_dict["content_type"])

        location = ET.SubElement(header, "location")
        location.set("lineNo", self.config_dict["line_no"])
        location.set("statNo", self.config_dict["stat_no"])
        location.set("statIdx", self.config_dict["stat_idx"])
        location.set("fuNo", self.config_dict["fu_no"])
        location.set("workPos", self.config_dict["work_pos"])
        location.set("toolPos", self.config_dict["tool_pos"])
        location.set("processNo", self.config_dict["process_no"])
        location.set("processName", self.config_dict["process_name"])
        location.set("application", self.config_dict["application"])

        # 创建event元素并添加partReceived子元素及属性
        event = ET.SubElement(root, "event")
        part_received = ET.SubElement(event, "partReceived")
        part_received.set("identifier", self.config_dict["bar_scanner_ID"])
        part_received.set("typeNo", self.config_dict["type_no"])
        part_received.set("typeVar", self.config_dict["type_var"])
        part_received.set("typeVersion", self.config_dict["type_version"])

        # 创建body元素（可根据需要添加更多应用特定数据）
        body = ET.SubElement(root, "body")

        # 创建XML树并转换为美化后的字符串形式
        tree = ET.ElementTree(root)
        self.logger.debug(f"生成的XML树: {tree}")
        xml_data = ET.tostring(root, encoding='utf-8').decode('utf-8')
        dom = minidom.parseString(xml_data)
        modified_xml_data = dom.toprettyxml(indent='    ')

        self.new_uuid = uuid.uuid4()
        xml_name = "Request_{ip}_{ID}.xml".format(ip=self.config_dict["mes_ip"],ID = self.new_uuid)
        write_path =self.get_folder_abs_path("message/{xml_name}".format(xml_name=xml_name))
        root = ET.fromstring(modified_xml_data)
        tree = ET.ElementTree(root)
        tree.write(write_path,encoding='utf-8',xml_declaration="True")
        self.logger.info(f"生成XML数据已存储在message文件夹:{xml_name}")
        self.logger.info(f"生成XML数据中的关键信息如下：")
        self.logger.info(f"生产线号(lineNo)：{self.config_dict["line_no"]}")
        self.logger.info(f"工位号(statNo)：{self.config_dict["stat_no"]}")
        self.logger.info(f"工位索引(statIdx)：{self.config_dict["stat_idx"]}")
        self.logger.info(f"功能单元索引(fuNo)：{self.config_dict["fu_no"]}")
        self.logger.info(f"工作位置(workPos)：{self.config_dict["work_pos"]}")
        self.logger.info(f"工具位置(toolPos)：{self.config_dict["tool_pos"]}")
        self.logger.info(f"工序号(processNo)：{self.config_dict["process_no"]}")
        self.logger.info(f"工序名称(processName)：{self.config_dict["process_name"]}")

        return modified_xml_data
    def extract_key_data(self,response_xml):
        """
        从接收到的响应XML数据中提取关键信息，包括'workPart'元素和'location'元素中的相关属性值，
        并将这些关键信息合并后保存到一个文本文件中。
        如果在解析XML数据时出现错误，将记录相应的错误日志。
        """
        try:
            try:
                wait_xml_data = ET.fromstring(response_xml.decode('utf-8','ignore'))
            except UnicodeDecodeError as e:
                self.logger.error(f"解码错误: {e}")
                self.logger.error(f"错误字节位置: {e.start}")
                self.logger.error(f"错误字节值: {hex(e.object[e.start])}")
           
            workPart_element = wait_xml_data.find(".//structs/workPart")
            if workPart_element is not None:
                workPart_info = {
                    "identifier":workPart_element.get("identifier"),
                    "partForStation": workPart_element.get("partForStation"),
                    "typeNo":workPart_element.get("typeNo"),
                    "nextProcessNo":workPart_element.get("nextProcessNo")
                }

            location_element = wait_xml_data.find(".//header/location")
            location_info = {
                "lineNo": location_element.get("lineNo"),
                "statNo": location_element.get("statNo"),
                "statIdx": location_element.get("statIdx"),
                "fuNo": location_element.get("fuNo"),
                "workPos": location_element.get("workPos"),
                "toolPos": location_element.get("toolPos"),
                "application": location_element.get("application"),
                "processName": location_element.get("processName"),
                "processNo": location_element.get("processNo")
                }

            combined_info = {**workPart_info, **location_info}

            self.logger.info("已解析接收XML数据中的关键信息。")
            self.logger.info("解析接收XML数据中的关键信息如下")
            self.logger.info(f"标识符（identifier）：{combined_info['identifier']}")
            self.logger.info(f"工位零件（partForStation）：{combined_info['partForStation']}")
            self.logger.info(f"类型号（typeNo）：{combined_info['typeNo']}")
            self.logger.info(f"下一个工序号（nextProcessNo）：{combined_info['nextProcessNo']}")
            self.logger.info(f"生产线号（lineNo）：{combined_info['lineNo']}")
            self.logger.info(f"工位号（statNo）：{combined_info['statNo']}")
            self.logger.info(f"工位索引（statIdx）：{combined_info['statIdx']}")
            self.logger.info(f"功能单元索引（fuNo）：{combined_info['fuNo']}")
            self.logger.info(f"工作位置（workPos）：{combined_info['workPos']}")
            self.logger.info(f"工具位置（toolPos）：{combined_info['toolPos']}")
            self.logger.info(f"应用（application）：{combined_info['application']}")
            self.logger.info(f"工序名称（processName）：{combined_info['processName']}")
            self.logger.info(f"工序号（processNo）：{combined_info['processNo']}")
            
            with open(self.config_dict["key_info_path"], "w", encoding="utf-8") as f:
                for key, value in combined_info.items():
                    f.write(f"{key}:{json.dumps(value, ensure_ascii=False)}\n")
        except ET.ParseError as e:
            self.logger.error(f"解析XML数据时出错: {e}", exc_info=True)
        return(combined_info)
    

