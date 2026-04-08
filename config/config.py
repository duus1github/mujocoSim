'''
@project : mujocoSim
@file    : config.py
@author  : duways
@date    : 2026/3/18 15:48
@info    : 整体项目的配置
'''
from lcm_msg.ecat_debug_cmd_lcmt import ecat_debug_cmd_lcmt as leg_joint_cmd
from lcm_msg.ecat_debug_data_lcmt import ecat_debug_data_lcmt as leg_joint_data
from lcm_msg.arm_control_data_lcmt import arm_control_data_lcmt as arm_joint_data
from lcm_msg.arm_control_cmd_lcmt import arm_control_cmd_lcmt as arm_joint_cmd
from lcm_msg.waist_control_data_lcmt import waist_control_data_lcmt as waist_data
from lcm_msg.waist_control_command_lcmt import waist_control_command_lcmt as waist_cmd
class Config:
    QUEUE_MAX_SIZE = 10

    CHANNEL_MSG_MAP = {
        "ecat_debug_dataLEG_L": leg_joint_data,
        "ecat_debug_dataLEG_R": leg_joint_data,
        "ecat_debug_data_ARM_R": arm_joint_data,
        "ecat_debug_data_ARM_L": arm_joint_data,
        "ecat_debug_data_WAIST": waist_data
    }
    CHANNEL_QUEUE_MAP = {
        "ecat_debug_dataLEG_L": "leg_l_queue",
        "ecat_debug_dataLEG_R": "leg_r_queue",
        "ecat_debug_data_ARM_L": "arm_l_queue",
        "ecat_debug_data_ARM_R": "arm_r_queue",
        "ecat_debug_data_WAIST": "waist_queue"
    }
    TARGET_QUEUES = list(CHANNEL_QUEUE_MAP.values())

    channel_joint_map = {
        # "ecat_debug_cmdLEG_L": leg_joint_cmd, "ecat_debug_cmdLEG_R": leg_joint_cmd,
        # "ecat_debug_cmd_ARM_L": arm_joint_cmd,
        # "ecat_debug_cmd_ARM_R": arm_joint_cmd, "ecat_debug_cmd_WAIST": waist_joint_cmd,
        "ecat_debug_dataLEG_L": leg_joint_data, "ecat_debug_dataLEG_R": leg_joint_data,
        "ecat_debug_data_ARM_R": arm_joint_data, "ecat_debug_data_ARM_L": arm_joint_data,
        "ecat_debug_data_WAIST": waist_data
    }