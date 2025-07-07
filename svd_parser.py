import xml.etree.ElementTree as ET

def parse_svd(file_path):
    """
    解析SVD文件并返回外设、寄存器和字段的信息。
    :param file_path: SVD文件的路径
    :return: 包含解析信息的字典
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    svd_info = {
        'peripherals': []
    }

    # 解析外设
    for peripheral in root.findall('.//peripheral'):
        peripheral_info = {
            'name': peripheral.find('name').text,
            'base_address': int(peripheral.find('baseAddress').text, 16),
            'registers': []
        }

        # 解析寄存器
        for register in peripheral.findall('.//register'):
            register_info = {
                'name': register.find('name').text,
                'description': register.find('description').text,
                'address_offset': int(register.find('addressOffset').text, 16),
                'size': int(register.find('size').text, 16) if register.find('size') is not None else None,
                'access': register.find('access').text if register.find('access') is not None else None,
                'fields': []
            }

            # 解析字段
            for field in register.findall('.//field'):
                field_info = {
                    'name': field.find('name').text,
                    'description': field.find('description').text,
                    'bit_offset': int(field.find('bitOffset').text),
                    'bit_width': int(field.find('bitWidth').text),
                }
                register_info['fields'].append(field_info)

            peripheral_info['registers'].append(register_info)

        svd_info['peripherals'].append(peripheral_info)

    return svd_info