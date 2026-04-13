# 项目名称 MUJOCOSIM
    通过输入人型机器人整机关节数据，在mujoco中复现机器人的全身运动，同时呈现各个关节位置变化曲线图
# 目录结构
│   ├── config              配置信息，包含lcm相关的配置        
│   ├── config.py
│   ├── __init__.py
│   └── __pycache__
├── DataSet                 存放数据，包含txt关节数据，lcm的关节数据
│   └── txt
├── lcm_msg                 lcm通信的消息类型
│
├── main.py                 主函数
├── mj_controller.py        mujoco控制函数
├── motion.py               关节数据解析函数
├── __pycache__
│   ├── mj_controller.cpython-310.pyc
│   └── motion.cpython-310.pyc
├── README.md
├── requirements.txt        包管理
└── robots                  机器人模型

# 依赖
    python==3.10
    mujoco==3.6.0
    matplotlib==3.10.8
# 安装
    pip install -r requirements.txt
# 使用
    python main.py




