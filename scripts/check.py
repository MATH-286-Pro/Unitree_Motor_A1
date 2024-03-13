#!/usr/bin/env python3
import os 
import sys
from typedef import *
from ctypes import *
import time

def time_count(num):
    for i in range(num):
        time.sleep(1)
        print(str(i+1)+'s')

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
motor_s0_start.W = 50.0        #单位：rad/s, W<511.9
motor_s0_start.Pos = 0         #单位：rad, Pos<131071.9
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

# print(bin(motor_s0_start.mode))       # 二进制显示
# print(bin(motor_s0_stop.mode))        # 二进制显示
# print('ID =',(motor_s0_start.mode))   # 十进制显示
# print('ID =',(motor_s0_stop.mode))    # 十进制显示

c.modify_data(byref(motor_s0_start))
c.modify_data(byref(motor_s0_stop))
c.modify_data(byref(motor_s1_start))
c.modify_data(byref(motor_s1_stop))

# print(bin(motor_s0_start.motor_send_data.Mdata.mode))
# print((motor_s0_start.motor_send_data.Mdata.mode))



c.send_recv(fd, byref(motor_s0_stop), byref(motor_r)) # 关闭 ID=0 电机
c.send_recv(fd, byref(motor_s1_stop), byref(motor_r)) # 关闭 ID=1 电机
print('测试开始')

c.send_recv(fd, byref(motor_s0_start), byref(motor_r)) # 开启 ID=0 电机
c.send_recv(fd, byref(motor_s1_start), byref(motor_r)) # 开启 ID=1 电机
time_count(10)
##time.sleep(10) 

c.send_recv(fd, byref(motor_s0_stop), byref(motor_r)) # 关闭 ID=0 电机
c.send_recv(fd, byref(motor_s1_stop), byref(motor_r)) # 关闭 ID=1 电机
print('测试结束 :)')

# c.close_serial(fd) # 关闭程序 (会导致VSCode关闭 qwq)

# 前置要求：需要上级文件目录包含 lib 文件夹 (lib 文件夹中包含对应的动态链接库)
#
# 使用方法：1.修改对应 COM 口
#          2.cd scripts
#          3.python check.py 
#
# 任务日志：2024.3.13 使用宇树485转USB成功启动，打印出 end 说明正常运行