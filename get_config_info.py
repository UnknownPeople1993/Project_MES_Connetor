
import logging
import os
from get_folder_abs_path import get_folder_abs_path

class get_config_info(get_folder_abs_path):
    def __init__(self):
        self.received_data = b""
        # 获取日志记录器对象并进行基本配置
        # self.logger = logging.getLogger(__name__)
        # logging.basicConfig(
        #     level=logging.INFO,
        #     format='%(asctime)s - %(levelname)s - %(message)s',
        #     filename=r'log\project_log.log',
        #     filemode='a',
        #     encoding='utf-8'
        # )
        
        self.config_path = self.get_folder_abs_path(r"config\config.ini")
        self.config_dict = {}
        

    def get_config_info(self):
        # try:
        #     with open(self.config_path, "r", encoding='utf-8') as f:
        #         self.config_dict = json.load(f)
        #     self.logger.info("加载配置字典")
        # except FileNotFoundError as e:
        #     self.logger.error(f"配置文件 {self.config_path} 不存在: {e}", exc_info=False)
        # except json.JSONDecodeError as e:
        #     self.logger.error(f"配置文件 {self.config_path} 内容不是有效的JSON格式: {e}", exc_info=False)
        # return(self.config_dict)
        with open( self.config_path, 'r',encoding='Ascii') as file:
            for line in file.readlines():
                line = line.strip()  # 去除每行两端的空白字符（如换行符、空格等）
                if line:  # 跳过空行
                    key, value = line.split('@')  # 以冒号加空格作为分隔符拆分每行
                    self.config_dict[key.strip()] = value.strip()
        return (self.config_dict)
if __name__ == "__main__":
    Myxml = get_config_info()
    x = Myxml.get_config_info()