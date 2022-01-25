# -*- coding: utf-8 -*-
import sys
import win32api
import win32con
import win32gui
import win32process
import subprocess


class HandleSet:
    def __init__(self, handle_title=''):
        super(HandleSet, self).__init__()
        self.handle_pos = None
        self.handle_title = handle_title
        self.handle_num = None
        # self.handle_num = self.get_handle_num(self.handle_title)  # 静态方法才能这么用
        self.handle_pid = None

    @property
    def get_handle_num(self):
        """通过句柄标题获取句柄编号"""
        self.handle_num = win32gui.FindWindow(None, self.handle_title)  # 搜索句柄标题，获取句柄编号
        if self.handle_num == 0:
            print("目标程序未启动,即将中止！")
            sys.exit(0)  # 脚本结束
        else:
            return self.handle_num

    @staticmethod
    def get_handle_title(handle_num=None):
        """
        通过句柄编号获取句柄标题
        :param handle_num: 句柄编号
        :returns: 句柄标题
        """
        handle_title = win32gui.GetWindowText(handle_num)  # 获取句柄标题
        return handle_title

    @property
    def get_handle_pid(self):
        """通过句柄标题获取句柄进程id"""
        self.handle_pid = win32process.GetWindowThreadProcessId(self.get_handle_num)  # 获取进程Pid
        return self.handle_pid[1]

    @property
    def get_handle_pos(self):
        """
        获取句柄的坐标
        :returns: 坐标，左上角（x1，y1），右下角（x2，y2）
        """
        self.handle_pos = win32gui.GetWindowRect(self.get_handle_num)
        return self.handle_pos

    def handle_is_active(self):
        """检测句柄是否停止"""
        hwnd = self.get_handle_num
        if hwnd == 0:  # 检测目标窗口是否存在
            print("目标程序未启动,即将中止！")
            sys.exit(0)  # 脚本结束
        # else:
        #     print("目标程序正常运行中！")

    def set_priority(self, priority=4):
        """
        设置程序的优先级,需要管理员模式运行
        :param priority: 0-5,(0-最低，5-最高)
        """
        pid = self.get_handle_pid
        priority_classes = [win32process.IDLE_PRIORITY_CLASS,
                            win32process.BELOW_NORMAL_PRIORITY_CLASS,
                            win32process.NORMAL_PRIORITY_CLASS,
                            win32process.ABOVE_NORMAL_PRIORITY_CLASS,
                            win32process.HIGH_PRIORITY_CLASS,
                            win32process.REALTIME_PRIORITY_CLASS]
        if pid is None:
            # pid = win32api.GetCurrentProcessId()  # 获取当前进程pid
            print("进程pid查找失败,即将中止！")
            sys.exit(0)  # 脚本结束
        else:
            # print(pid)
            handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
            win32process.SetPriorityClass(handle, priority_classes[priority])

            handle_title = self.handle_title
            priority_name = None
            if priority == 0:
                priority_name = "最低"
            if priority == 1:
                priority_name = "低于正常"
            if priority == 2:
                priority_name = "正常"
            if priority == 3:
                priority_name = "高于正常"
            if priority == 4:
                priority_name = "高"
            if priority == 5:
                priority_name = "最高"
            print(f"已设置进程 [{handle_title}] 的优先级为 [{priority_name}] ")
            print("------------------------------------------------------------")

    @staticmethod
    def deal_cmd(cmd):
        pi = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        return pi.stdout.read()

    @staticmethod
    def adb_device_status():
        result = HandleSet.deal_cmd('adb devices')
        result = result.decode("utf-8")
        if result.startswith('List of devices attached'):
            # 查看连接设备
            result = result.strip().splitlines()
            # 查看连接设备数量
            device_size = len(result)
            if device_size > 1:
                device_list = []
                for i in range(1, device_size):
                    device_detail = result[1].split('\t')
                    if device_detail[1] == 'device':
                        device_list.append(device_detail[0])
                    elif device_detail[1] == 'offline':
                        print(device_detail[0])
                        return False, '连接出现异常，设备无响应'
                    elif device_detail[1] == 'unknown':
                        print(device_detail[0])
                        return False, '设备不在线，请重新连接，或打开安卓调试模式'
                return True, device_list
            else:
                return False, "设备不在线，请重新连接，或打开安卓调试模式"