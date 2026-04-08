"""
播放的关节顺序为上半身，下半身，先左后右，最后腰
"""

import logging

from mj_controller import MjController

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    mj_controller = MjController(data_from_type = "txt")
    mj_controller.run_step()


if __name__ == '__main__':
    main()


