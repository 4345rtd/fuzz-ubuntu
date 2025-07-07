import logging
from unicorn import *
from unicorn.x86_const import *

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('emulator.log'),  # 将日志写入文件
        logging.StreamHandler()  # 同时输出到控制台
    ]
)
logger = logging.getLogger('unicorn_emulator')

# 读取机器码
with open('draw.bin', 'rb') as f:
    X86_CODE32 = f.read()

# 要模拟的x86代码（32位）
# X86_CODE32 = b"\x41\x4a"  # inc ecx; dec edx
ADDRESS = 0x1000000


def emulate_instance(instance_id):
    logger.info(f"Starting emulation for instance {instance_id}")
    try:
        # 初始化模拟器，架构为x86，模式为32位
        mu = Uc(UC_ARCH_X86, UC_MODE_32)

        # 映射2MB内存
        mu.mem_map(ADDRESS, 2 * 1024 * 1024)
        logger.debug(f"Instance {instance_id} mapped 2MB memory at address 0x{ADDRESS:x}")

        # 将代码写入内存
        mu.mem_write(ADDRESS, X86_CODE32)
        logger.debug(f"Instance {instance_id} wrote {len(X86_CODE32)} bytes of code to memory")

        # 设置寄存器初始值
        mu.reg_write(UC_X86_REG_ECX, 0x1234)
        mu.reg_write(UC_X86_REG_EDX, 0x7890)
        logger.debug(f"Instance {instance_id} set initial register values: ECX=0x1234, EDX=0x7890")

        # 开始模拟，从ADDRESS地址开始，到ADDRESS + len(X86_CODE32)结束
        logger.info(f"Instance {instance_id} starting emulation from 0x{ADDRESS:x} to 0x{ADDRESS + len(X86_CODE32):x}")
        mu.emu_start(ADDRESS, ADDRESS + len(X86_CODE32))

        # 读取寄存器的值
        r_ecx = mu.reg_read(UC_X86_REG_ECX)
        r_edx = mu.reg_read(UC_X86_REG_EDX)
        logger.info(f'Instance {instance_id} finished emulation. ECX = 0x{r_ecx:x}, EDX = 0x{r_edx:x}')

    except UcError as e:
        logger.error(f"Instance {instance_id} encountered an error: {e}")


# 模拟运行多个实例
num_instances = 3  # 运行3个实例
for i in range(num_instances):
    emulate_instance(i + 1)
