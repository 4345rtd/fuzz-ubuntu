import xml.etree.ElementTree as ET
import yaml

class SVDToYAMLConverter:
    def __init__(self):
        self.peripherals = []

    def parse_svd(self, svd_file_path):
        # 解析SVD文件
        tree = ET.parse(svd_file_path)
        root = tree.getroot()

        # 遍历SVD文件中的所有外设
        for peripheral in root.findall('.//peripheral'):
            peripheral_dict = {
                'name': peripheral.find('name').text,
                'description': peripheral.find('description').text if peripheral.find('description') is not None else None,
                'base_address': int(peripheral.find('baseAddress').text, 0) if peripheral.find('baseAddress') is not None else None,
                'registers': []
            }

            # 遍历外设中的寄存器
            if peripheral.find('registers') is not None:
                for register in peripheral.find('registers').findall('register'):
                    register_dict = {
                        'name': register.find('name').text,
                        'description': register.find('description').text if register.find('description') is not None else None,
                        'address_offset': int(register.find('addressOffset').text, 0) if register.find('addressOffset') is not None else None,
                        'size': int(register.find('size').text, 0) if register.find('size') is not None else None,
                        'access': register.find('access').text if register.find('access') is not None else None,
                        'fields': []
                    }

                    # 遍历寄存器中的字段
                    if register.find('fields') is not None:
                        for field in register.find('fields').findall('field'):
                            field_dict = {
                                'name': field.find('name').text,
                                'description': field.find('description').text if field.find('description') is not None else None,
                                'bit_offset': int(field.find('bitOffset').text) if field.find('bitOffset') is not None else None,
                                'bit_width': int(field.find('bitWidth').text) if field.find('bitWidth') is not None else None,
                                'access': field.find('access').text if field.find('access') is not None else None
                            }
                            register_dict['fields'].append(field_dict)

                    peripheral_dict['registers'].append(register_dict)

            self.peripherals.append(peripheral_dict)

    def write_to_yaml(self, yaml_file_path):
        # 将数据写入YAML文件
        with open(yaml_file_path, 'w') as yaml_file:
            yaml.dump({'peripherals': self.peripherals}, yaml_file, default_flow_style=False)

    def convert(self, svd_file_path, yaml_file_path):
        self.parse_svd(svd_file_path)
        self.write_to_yaml(yaml_file_path)
        return yaml_file_path


if __name__ == '__main__':
    # 示例用法
    svd_file = '/home/zqh/fuzzware/pipeline/fuzzware_pipeline/parser/CMSDK_CM3.svd'  # 替换为你的SVD文件路径
    yaml_file = '/home/zqh/fuzzware/pipeline/fuzzware_pipeline/parser/CMSDK_CM3.yml'  # 替换为你想要保存的YAML文件路径
    converter = SVDToYAMLConverter(svd_file, yaml_file)
    converter.convert()