#!/usr/bin/env python3
import os 
import sys
from typedef import *
from ctypes import *
import time
import threading
import keyboard  # 需要安装 keyboard 库

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



# 创建数据类型
motor_s0_start = MOTOR_send()
motor_s0_stop = MOTOR_send()
motor_r = MOTOR_recv()

motor_s1_start = MOTOR_send()
motor_s1_stop = MOTOR_send()

# 设置电机 0 参数 (开启电机)
motor_s0_start.id = 0          #ID = 0 (可选ID为0,1,2)
motor_s0_start.mode = 10       #闭环模式 (可选模式 0=关闭,5=开环,10=闭环)
motor_s0_start.T = 0.0         #单位：Nm, T<255.9
motor_s0_start.W = 0.0         #单位：rad/s, W<511.9
motor_s0_start.Pos = 0.0         #单位：rad, Pos<131071.9
motor_s0_start.K_P = 0.0       #K_P<31.9
motor_s0_start.K_W = 3         #K_W<63.9

# 设置电机 0 参数 (关闭电机)
motor_s0_stop.id = 0
motor_s0_stop.mode = 0

# 设置电机 1 参数 (开启电机)
motor_s1_start.id = 1          #ID = 0 (可选ID为0,1,2)
motor_s1_start.mode = 10       #闭环模式 (可选模式 0=关闭,5=开环,10=闭环)
motor_s1_start.T = 0.0         #单位：Nm, T<255.9
motor_s1_start.W = 50.0        #单位：rad/s, W<511.9
motor_s1_start.Pos = 0         #单位：rad, Pos<131071.9
motor_s1_start.K_P = 0.0       #K_P<31.9
motor_s1_start.K_W = 3         #K_W<63.9

# 设置电机 1 参数 (关闭电机)
motor_s1_stop.id = 1
motor_s1_stop.mode = 0

c.modify_data(byref(motor_s0_start))
c.modify_data(byref(motor_s0_stop))
c.modify_data(byref(motor_s1_start))
c.modify_data(byref(motor_s1_stop))

c.send_recv(fd, byref(motor_s0_stop), byref(motor_r)) # 关闭 ID=0 电机
c.send_recv(fd, byref(motor_s1_stop), byref(motor_r)) # 关闭 ID=1 电机

# 测试日志：2024.3.18 使用示波器查看 RS485 信号
# 20:07 检测到RS485信号


# 循环发送信号函数
def send_commands():
    while not exit_event.is_set():  # 检查退出事件是否被设置
        c.send_recv(fd, byref(motor_s0_start), byref(motor_r))  # 开启 ID=0 电机
        c.send_recv(fd, byref(motor_s1_start), byref(motor_r))  # 开启 ID=1 电机
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

c.send_recv(fd, byref(motor_s0_stop), byref(motor_r)) # 关闭 ID=0 电机
c.send_recv(fd, byref(motor_s1_stop), byref(motor_r)) # 关闭 ID=1 电机
print('测试结束')