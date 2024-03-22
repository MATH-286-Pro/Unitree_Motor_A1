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

# 广播所有电机
ID = 0xBB

# 创建结构体 数据类型
motor_s1_start = MOTOR_send() # 正常模式
motor_p1_start = MOTOR_send() # ID模式
motor_s1_stop  = MOTOR_send() # 关闭电机
motor_r1 = MOTOR_recv()


# 设置电机 1 速度模式参数 
motor_s1_start.id = ID               
motor_s1_start.mode = 10            
motor_s1_start.T   = 0.0            
motor_s1_start.W   = 0.0           
motor_s1_start.Pos = 0.0             
motor_s1_start.K_P = 0.0           
motor_s1_start.K_W = 0     

# 设置电机 1 ID模式参数
motor_p1_start.id  = ID               
motor_p1_start.mode = 11         
motor_p1_start.T   = 0.0           
motor_p1_start.W   = 0.0            
motor_p1_start.Pos = 0.0            
motor_p1_start.K_P = 0.0            
motor_p1_start.K_W = 0.0            

# 设置电机 1 参数 (关闭电机)
motor_s1_stop.id   = ID
motor_s1_stop.mode = 0




# 主程序--------------------------------------------------

# 数据处理
c.modify_data(byref(motor_s1_start))
c.modify_data(byref(motor_p1_start))
c.modify_data(byref(motor_s1_stop))

# 关闭所有电机
c.send_recv(fd, byref(motor_s1_stop), byref(motor_r1))
time.sleep(0.5)

# 开启所有电机
c.send_recv(fd, byref(motor_s1_start), byref(motor_r1))
time.sleep(0.5)

c.send_recv(fd, byref(motor_p1_start), byref(motor_r1))
time.sleep(0.5)
print('修改ID模式')

running = True

# 检测空格键函数
def on_space_press(event):
    global running
    c.send_recv(fd, byref(motor_s1_stop), byref(motor_r1))  # 关闭所有电机
    running = False  # 更改循环条件以退出程序

# 监听空格键按下事件
keyboard.on_press_key("space", on_space_press)

# 使用循环保持程序运行，直到按下空格键
while running:
    time.sleep(0.5)  # 稍微延时以避免过高的CPU占用

print('修改ID结束')


