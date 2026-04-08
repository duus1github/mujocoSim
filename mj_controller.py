'''
@project : mujocoSim
@file    : mj_controller.py
@author  : duways
@date    : 2026/3/18 15:55
@info    : 初始化mujoco类，然后控制仿真界面
'''
import time
import threading

import numpy as np
from motion import MotionData
from mujoco import viewer
import mujoco

import matplotlib.pyplot as plt
class MjController(object):
    def __init__(self,data_from_type):
        self.model = mujoco.MjModel.from_xml_path("./robots/nix2/mjcf/nix2_default.xml")
        self.data = mujoco.MjData(self.model)
        self.step = 0
        self.viewer = None
        self.data_from_type = data_from_type
        self.motion = MotionData(self.data_from_type) # lcm or txt
        self.motion_history = []  # 存储每一帧的电机数据
        self.plot_lock = threading.Lock()  # 线程锁，保护绘图数据
        self.plot_thread = None
        self.plot_running = False

        self.data.qpos[0] = 0.0
        self.data.qpos[1] = 0.0
        self.data.qpos[2] = 0.435

        self.data.qpos[3] = 1.0
        self.data.qpos[4] = 0.0
        self.data.qpos[5] = 0.0
        self.data.qpos[6] = 0.0
        self.paused = False

    def change_mj_config(self):
        # todo:set 重力投影
        self.model.opt.gravity = np.array([0, 0, -1.62])
        # todo:修改地面摩擦力
        ground_geom_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_GEOM, "ground")
        self.model.geom_friction[ground_geom_id] = np.array([0.05, 0.001, 0.001])

    def _plot_thread_worker(self):
        """后台线程：实时绘制每个关节的位置随时间的变化"""
        plt.ion()  # 打开交互模式
        fig = None
        axes = None
        num_joints = None

        while self.plot_running:
            with self.plot_lock:
                if not self.motion_history:
                    time.sleep(0.1)
                    continue

                motion_array = np.array(self.motion_history)  # shape: (num_frames, num_joints)
                if num_joints is None:
                    num_joints = motion_array.shape[1]
                    # 第一次创建图表
                    cols = 3
                    rows = (num_joints-7 + cols - 1) // cols
                    fig, axes = plt.subplots(rows, cols, figsize=(15, 3*rows))
                    axes = axes.flatten()
                    fig.suptitle('Real-time Joint Position Monitoring')

                # 更新每个关节的曲线
                time_steps = np.arange(motion_array.shape[0])
                for joint_idx in range(num_joints-7):
                    ax = axes[joint_idx]
                    # ax.clear()
                    ax.plot(time_steps, motion_array[:, joint_idx+7], linewidth=1, color='blue')
                    # ax.set_xlabel('Frame')
                    ax.set_ylabel('Position (rad)')
                    ax.set_title(f'Joint {joint_idx}')
                    ax.grid(True, alpha=0.1)

                # 隐藏多余的子图
                for idx in range(num_joints, len(axes)):
                    axes[idx].axis('off')

            plt.tight_layout()
            plt.pause(0.1)  # 每100ms更新一次

        if fig:
            plt.close(fig)

    def start_plot_thread(self):
        """启动实时绘图线程"""
        self.plot_running = True
        self.plot_thread = threading.Thread(target=self._plot_thread_worker, daemon=True)
        self.plot_thread.start()
        print("实时绘图线程已启动")

    def stop_plot_thread(self):
        """停止实时绘图线程"""
        self.plot_running = False
        if self.plot_thread:
            self.plot_thread.join(timeout=2)

    def _simulation_step(self):
        """仿真步进函数，每帧调用一次"""
        if not self.paused:
            try:
                motion_data = self.motion.get_latest_motion(self.step)
                
                # 保存当前帧数据
                with self.plot_lock:
                    self.motion_history.append(motion_data)
                
                self.data.qpos[0] = motion_data[0]
                self.data.qpos[1] = motion_data[1]
                self.data.qpos[2] = motion_data[2]+0.086

                self.data.qpos[3] = motion_data[3]
                self.data.qpos[4] = motion_data[4]
                self.data.qpos[5] = motion_data[5]
                self.data.qpos[6] = motion_data[6]
                self.data.qpos[7:] = motion_data[7:]
                mujoco.mj_forward(self.model, self.data)
                self.step += 1
                
                if self.step > len(self.motion.motion_data):
                    self.motion.running = False
            except Exception as e:
                print(f"仿真步进错误: {e}")
                self.motion.running = False

    def key_callback(self,keycode):
        if chr(keycode) == ' ':
            # nonlocal self.paused
            self.paused = not self.paused

    def run_step(self):
        # 使用被动 viewer
        self.viewer = mujoco.viewer.launch_passive(
            self.model,
            self.data,
            key_callback=self.key_callback
        )

        if self.data_from_type != "txt":
            self.motion.start_lcm_sub()
        else:
            self.motion.load_motion_from_txt()

        self.start_plot_thread()

        while self.viewer.is_running() and self.motion.running:
            if not self.paused:
                self._simulation_step()
            self.viewer.sync()
            time.sleep(1 / 60)

        self.stop_plot_thread()

