#!/usr/bin/env python3
import os 
import sys
from typedef import *
from ctypes import *
import time
import threading
import keyboard  # 需要安装 keyboard 库

# 减速比
Gear_ratio = 9.1
PI = 3.1415926

# 寻找串口
system=platform.system()
if system == 'Windows':
    fd = c.open_set(b'\\\\.\\COM15')  #修改串口号
    libPath = os.path.dirname(os.getcwd()) + '/lib/libUnitree_motor_SDK_Win64.dll'
elif system == 'Linux':
    fd = c.open_set(b'/dev/ttyUSB0')
    maxbit=sys.maxsize
    if maxbit>2**32:
        libPath = os.path.dirname(os.getcwd()) + '/lib/libUnitree_motor_SDK_Linux64.so'
        print('Linux 64 bits')
    else:
        libPath = os.path.dirname(os.getcwd()) + '/lib/libUnitree_motor_SDK_Linux32.so'
        print('Linux 32 bits')

c = cdll.LoadLibrary(libPath)


# 创建结构体 数据类型
motor_s0_start = MOTOR_send()
motor_s0_stop = MOTOR_send()
motor_r0 = MOTOR_recv()

motor_s1_start = MOTOR_send() # 速度模式
motor_p1_start = MOTOR_send() # 位置模式
motor_s1_stop = MOTOR_send()  # 关闭电机
motor_r1 = MOTOR_recv()

# 设置电机 0 参数 (开启电机)
motor_s0_start.id = 0             #ID = 0 (可选ID为0,1,2)
motor_s0_start.mode = 10          #闭环模式 (可选模式 0=关闭,5=开环,10=闭环)
motor_s0_start.T = 0.0            #单位：Nm, T<255.9                        # float
motor_s0_start.W = -5.0*Gear_ratio #单位：rad/s, W<511.9                    # float
motor_s0_start.Pos = 0.0          #单位：rad, Pos<131071.9                  # float
motor_s0_start.K_P = 0.0          #K_P<31.9                                # float
motor_s0_start.K_W = 3            #K_W<63.9                                # Literal[3]

# 设置电机 0 参数 (关闭电机)
motor_s0_stop.id = 0
motor_s0_stop.mode = 0

# 设置电机 1 速度模式参数 (开启电机)
motor_s1_start.id = 1               #ID = 0 (可选ID为0,1,2)
motor_s1_start.mode = 10            #闭环模式 (可选模式 0=关闭,5=开环,10=闭环)
motor_s1_start.T = 0.0              #单位：Nm, T<255.9
motor_s1_start.W = 5.0*Gear_ratio   #单位：rad/s, W<511.9
motor_s1_start.Pos = 0              #单位：rad, Pos<131071.9
motor_s1_start.K_P = 0.0            #K_P<31.9
motor_s1_start.K_W = 3              #K_W<63.9

# 设置电机 1 位置模式参数 (开启电机)
motor_p1_start.id = 1               #ID = 0 (可选ID为0,1,2)
motor_p1_start.mode = 10            #闭环模式 (可选模式 0=关闭,5=开环,10=闭环)
motor_p1_start.T = 0.0              #单位：Nm, T<255.9
motor_p1_start.W = 0.0              #单位：rad/s, W<511.9
motor_p1_start.Pos = PI*Gear_ratio  #单位：rad, Pos<131071.9
motor_p1_start.K_P = 0.2            #位置刚度 K_P<31.9
motor_p1_start.K_W = 3.0            #速度刚度 K_W<63.9

# 设置电机 1 参数 (关闭电机)
motor_s1_stop.id = 1
motor_s1_stop.mode = 0

c.modify_data(byref(motor_s0_start))
c.modify_data(byref(motor_s0_stop))
c.modify_data(byref(motor_s1_start))
c.modify_data(byref(motor_s1_stop))

c.send_recv(fd, byref(motor_s0_stop), byref(motor_r0)) # 关闭 ID=0 电机
c.send_recv(fd, byref(motor_s1_stop), byref(motor_r1)) # 关闭 ID=1 电机


# 循环发送接收信号函数
def send_commands():
    while not exit_event.is_set():  # 检查退出事件是否被设置
        c.send_recv(fd, byref(motor_s0_start), byref(motor_r0))  # 开启 ID=0 电机
        c.send_recv(fd, byref(motor_s1_start), byref(motor_r1))  # 开启 ID=1 电机

        c.extract_data(byref(motor_r1)) # 解码回传数据
        print('ID=1 角速度='+str(motor_r1.W)+' rad/s '+'力矩='+str(motor_r1.T))
        time.sleep(0.1)  # 每 0.1 秒运行一次

# 检测空格键函数
def on_space_press(event):
    exit_event.set()  # 当按下空格键时，设置退出事件




# 测试部分
print('测试开始')
exit_event = threading.Event()
keyboard.on_press_key("space", on_space_press)  # 监听空格键按下事件

send_commands_thread = threading.Thread(target=send_commands)
send_commands_thread.start()

send_commands_thread.join()  # 等待发送指令的线程结束

c.send_recv(fd, byref(motor_s0_stop), byref(motor_r0)) # 关闭 ID=0 电机
c.send_recv(fd, byref(motor_s1_stop), byref(motor_r1)) # 关闭 ID=1 电机
print('测试结束')