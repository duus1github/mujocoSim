'''
@project : mujocoSim
@file    : motion.py
@author  : duways
@date    : 2026/3/18 15:46
@info    : 获取机器人的数据，这里目前主要是通lcm获取到关节数据
'''
import itertools
import queue
import logging
import threading
from copy import deepcopy

import lcm

from config import config
from config.config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class MotionData(object):
    def __init__(self,data_from_type):
        self.config = Config()
        self.queues = {
            queue_name: queue.Queue(self.config.QUEUE_MAX_SIZE)
            for queue_name in self.config.TARGET_QUEUES
        }
        self.motion_data = []
        self.motion_data_lock = threading.Lock()
        self.running  = False
        self.lc = lcm.LCM()
        self.queue_lock = threading.Lock()
        self.channel_joint_map = self.config.channel_joint_map
        self.data_from_type = data_from_type
    def load_motion_from_txt(self):
        self.running = True
        qpos_list = []
        with open("DataSet/txt/开合跳_qpos.txt", 'r', encoding='utf-8') as f:
            lines = f.readlines()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 只处理以 ref_qpos_: 开头的行
                if line.startswith('ref_qpos_:'):
                    # 去掉前缀，按空格分割
                    parts = line.replace('ref_qpos_:', '').split()
                    # 转成浮点数
                    qpos = [float(p) for p in parts]
                    self.motion_data.append(qpos)

        # 将数据格式化为curr_motion结构并放入motion_data
        # formatted_data = [
        #     [
        #         qpos[0:7],  # leg_l
        #         qpos[7:13],  # leg_r
        #         qpos[13:20],  # waist
        #         qpos[20:24],  # arm_l
        #         qpos[24:28],  # arm_r
        #     ] for qpos in qpos_list
        # ]
        # with self.motion_data_lock:
        #     self.motion_data.extend(formatted_data)

        # return qpos_list
    def handler_all_msg(self,channel,data):
        """
        订阅lcm，获取数据，并组装位电机的数据21个关节数据
        :param channel:
        :param data:
        :return:
        """
        try:
            if channel not in self.config.CHANNEL_MSG_MAP:
                logging.warning(f"未知频道: {channel}")
                return

            msg_cls = self.config.CHANNEL_MSG_MAP[channel]
            msg = msg_cls.decode(data)
            queue_name = self.config.CHANNEL_QUEUE_MAP[channel]
            target_queue = self.queues[queue_name]

            with self.queue_lock:
                if target_queue.full():
                    target_queue.get_nowait()
                self.queues[queue_name].put(msg, block=False)

        except Exception as e:
            logging.error(f"处理频道 {channel} 失败: {e}", exc_info=True)

    def start_lcm_sub(self):
        """
        通过订阅lcm画题获取关节数据信息
        :return:
        # """
        subscriptions = []

        for _channel in self.channel_joint_map.keys():
            sub = self.lc.subscribe(_channel,self.handler_all_msg)
            subscriptions.append(sub)

        self.running = True
        self.lcm_thread = threading.Thread(target=self._lcm_lister,daemon=True)
        self.lcm_thread.start()
        print(f"subscribe success")

    def _lcm_lister(self):
        while self.running:
            self.lc.handle()
            self._get_motion_data()
            if not self.running:
                break
    def _get_motion_data(self):

        with self.queue_lock:
            all_have_data = all(not q.empty() for q in self.queues.values())
            if not all_have_data:
                return

            #通知拼接数据
            curr_motion = [
                self.queues["leg_l_queue"].get().original_curPos[:6],
                self.queues["leg_r_queue"].get().original_curPos[:6],
                self.queues["waist_queue"].get().waist_pos[:1],
                self.queues["arm_l_queue"].get().joint_curPos[:4],
                self.queues["arm_r_queue"].get().joint_curPos[:4],

            ]

            with self.motion_data_lock:
                self.motion_data.append(curr_motion)

    def get_latest_motion(self,index):
        # 如果没有motion_data，且data_from_type是txt，则加载txt数据
        if self.data_from_type == "txt":
            return self.motion_data[index]
        else:
            with self.motion_data_lock:
                if not self.motion_data and self.data_from_type == 'txt':
                    self.load_motion_from_txt()
                if not self.motion_data:
                    return None
                return deepcopy(list(itertools.chain(*self.motion_data[index])))


    def clear_motion_data(self):
        """
        接口4：清空motion_data（可选，避免数据堆积）
        """
        with self.motion_data_lock:
            self.motion_data.clear()
        logging.info("已清空motion_data")
    def stop_lcm_subscribe(self):
        """停止LCM订阅"""
        self.running = False
        for sub in self.subscriptions:
            self.lc.unsubscribe(sub)
        self.lc.shutdown()
        if hasattr(self, "lcm_thread"):
            self.lc_thread.join(timeout=1)
        logging.info("LCM订阅停止")
def map_joint():
    curr_joint_order = [
        "left_shoulder_pitch","left_shoulder_roll","left_shoulder_yaw","left_elbow_roll",
        "right_shoulder_pitch","right_shoulder_roll","right_shoulder_yaw","right_elbow_roll",
        "left_hip_pitch","left_hip_roll","left_hip_yaw","left_knee","left_ankle_pitch","left_ankle_roll"
        "right_hip_pitch","right_hip_roll","right_hip_yaw","right_knee","right_ankle_pitch","right_ankle_roll"
        "torso"
    ]

