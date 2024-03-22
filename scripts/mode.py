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


# 设定 ID
ID = 1

#  创建结构体 数据类型 
motor_s1_start = MOTOR_send() # 速度模式
motor_p1_start = MOTOR_send() # 位置模式
motor_t1_start = MOTOR_send() # 力矩模式``
motor_s1_stop = MOTOR_send()  # 关闭电机
motor_r1 = MOTOR_recv()

# 设置电机 1 速度模式参数 
motor_s1_start.id = ID              #ID = 0 (可选ID为0,1,2)
motor_s1_start.mode = 10            #闭环模式 (可选模式 0=关闭,5=开环,10=闭环)
motor_s1_start.T = 0.0              #单位：Nm, T<255.9
motor_s1_start.W = 10.0*Gear_ratio  #单位：rad/s, W<511.9
motor_s1_start.Pos = 0              #单位：rad, Pos<131071.9
motor_s1_start.K_P = 0.0            #K_P<31.9
motor_s1_start.K_W = 3              #K_W<63.9

# 设置电机 1 位置模式参数 
motor_p1_start.id = ID              #ID = 0 (可选ID为0,1 ,2)
motor_p1_start.mode = 10            #闭环模式 (可选模式 0=关闭,5=开环,10=闭环)
motor_p1_start.T = 0.0              #单位：Nm, T<255.9
motor_p1_start.W = 0.0              #单位：rad/s, W<511.9
motor_p1_start.Pos = 0 #PI          #单位：rad, Pos<131071.9
motor_p1_start.K_P = 0.005  # 0.2      #位置刚度 K_P<31.9
motor_p1_start.K_W = 0.1    # 3.0         #速度刚度 K_W<63.9

# 设置电机 1 力矩模式参数 
motor_t1_start.id = ID               #ID = 0 (可选ID为0,1,2)
motor_t1_start.mode = 10            #闭环模式 (可选模式 0=关闭,5=开环,10=闭环)
motor_t1_start.T = 0.0              #单位：Nm, T<255.9
motor_t1_start.W = 0.0              #单位：rad/s, W<511.9
motor_t1_start.Pos = 0.0            #单位：rad, Pos<131071.9
motor_t1_start.K_P = 0.0            #K_P<31.9
motor_t1_start.K_W = 0.0            #K_W<63.9

# 设置电机 1 参数 (关闭电机)
motor_s1_stop.id = ID
motor_s1_stop.mode = 0

# 数据处理
c.modify_data(byref(motor_s1_start))
c.modify_data(byref(motor_p1_start))
c.modify_data(byref(motor_t1_start))
c.modify_data(byref(motor_s1_stop))

c.send_recv(fd, byref(motor_s1_stop), byref(motor_r1)) # 关闭 ID=1 电机









# 键盘代码 -------------------------------------------------------

# 添加全局变量以存储位置调整 
DGR2RAD = PI/180

pos_adjustment = 0.0
pos_increment = 360*Gear_ratio*DGR2RAD  # 外圈 360°

# 空格检测函数
def on_space_press(event):
    exit_event.set()  # 当按下空格键时，设置退出事件

# 上箭头键按下时增加位置
def increase_position(event):
    global pos_adjustment
    pos_adjustment += pos_increment

# 下箭头键按下时减少位置
def decrease_position(event):
    global pos_adjustment
    pos_adjustment -= pos_increment


# 修改 send_commands 函数
def send_commands():
    global pos_adjustment
    while not exit_event.is_set():  # 检查退出事件是否被设置
        if pos_adjustment != 0.0:
            motor_p1_start.Pos += pos_adjustment  # 根据调整值更新位置
            pos_adjustment = 0.0  # 重置调整值
            c.modify_data(byref(motor_p1_start))  # 应用新的位置值

        # 开启 ? 模式
        c.send_recv(fd, byref(motor_s1_start), byref(motor_r1))  

        # 解码回传数据
        c.extract_data(byref(motor_r1)) 

        print('ID='+str(ID)+' 键盘'+str(motor_p1_start.Pos)+' 角速度='+str(motor_r1.W)+' rad/s '+'力矩='+str(motor_r1.T))
        time.sleep(0.1)  # 每 0.1 秒运行一次


# 测试部分
print('测试开始')
exit_event = threading.Event()

keyboard.on_press_key("space", on_space_press)  # 监听空格键按下事件
keyboard.on_press_key("left", increase_position)
keyboard.on_press_key("right", decrease_position)

send_commands_thread = threading.Thread(target=send_commands)
send_commands_thread.start()

send_commands_thread.join()  # 等待发送指令的线程结束

c.send_recv(fd, byref(motor_s1_stop), byref(motor_r1)) # 关闭 ID=1 电机
print('测试结束')