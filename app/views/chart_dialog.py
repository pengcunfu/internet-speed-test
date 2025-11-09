# -*- coding: utf-8 -*-
"""
Chart Dialog View
图表展示对话框
"""

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class SpeedChartCanvas(FigureCanvas):
    """速度图表画布"""
    
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
        plt.rcParams['axes.unicode_minus'] = False
        
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        
    def plot_speed_comparison(self, download_speed, upload_speed):
        """
        绘制下载上传速度对比图
        
        Args:
            download_speed: 下载速度(Mbps)
            upload_speed: 上传速度(Mbps)
        """
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        # 数据
        categories = ['下载速度', '上传速度']
        speeds = [download_speed, upload_speed]
        colors = ['#4CAF50', '#2196F3']
        
        # 绘制柱状图
        bars = ax.bar(categories, speeds, color=colors, alpha=0.8, width=0.6)
        
        # 添加数值标签
        for bar, speed in zip(bars, speeds):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{speed/8:.2f} MB/s',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # 设置标题和标签
        ax.set_title('网速测试结果', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('速度 (MB/s)', fontsize=12)
        ax.set_ylim(0, max(speeds) * 1.3)
        
        # 网格
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # 美化
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        self.fig.tight_layout()
        self.draw()
        
    def plot_ping_details(self, ping_details):
        """
        绘制Ping延迟详情图
        
        Args:
            ping_details: Ping详情字典 {名称: 延迟}
        """
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        # 过滤有效数据
        valid_data = {k: v for k, v in ping_details.items() if v is not None}
        
        if not valid_data:
            ax.text(0.5, 0.5, '暂无Ping数据', 
                   ha='center', va='center', fontsize=14)
            self.draw()
            return
        
        # 排序
        sorted_items = sorted(valid_data.items(), key=lambda x: x[1])
        names = [item[0] for item in sorted_items]
        pings = [item[1] for item in sorted_items]
        
        # 颜色映射（根据延迟高低）
        colors = []
        for ping in pings:
            if ping < 50:
                colors.append('#4CAF50')  # 绿色 - 优秀
            elif ping < 100:
                colors.append('#FFC107')  # 黄色 - 良好
            elif ping < 200:
                colors.append('#FF9800')  # 橙色 - 一般
            else:
                colors.append('#F44336')  # 红色 - 较差
        
        # 绘制水平柱状图
        y_pos = range(len(names))
        bars = ax.barh(y_pos, pings, color=colors, alpha=0.8, height=0.6)
        
        # 添加数值标签
        for i, (bar, ping) in enumerate(zip(bars, pings)):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f' {ping:.1f} ms',
                   ha='left', va='center', fontsize=10, fontweight='bold')
        
        # 设置标题和标签
        ax.set_title('Ping延迟测试结果', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('延迟 (ms)', fontsize=12)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=10)
        
        # 网格
        ax.grid(True, alpha=0.3, linestyle='--', axis='x')
        ax.set_axisbelow(True)
        
        # 美化
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        self.fig.tight_layout()
        self.draw()
        
    def plot_speed_gauge(self, speed, max_speed=1000, title='网速'):
        """
        绘制速度仪表盘
        
        Args:
            speed: 当前速度(Mbps)
            max_speed: 最大速度(Mbps)
            title: 标题
        """
        self.fig.clear()
        ax = self.fig.add_subplot(111, projection='polar')
        
        # 角度范围：-120度到120度
        theta = np.linspace(-2*np.pi/3, 2*np.pi/3, 100)
        
        # 背景扇形
        ax.fill_between(theta, 0, 1, alpha=0.1, color='gray')
        
        # 当前速度角度
        speed_ratio = min(speed / max_speed, 1.0)
        speed_angle = -2*np.pi/3 + speed_ratio * 4*np.pi/3
        
        # 绘制指针
        ax.plot([0, speed_angle], [0, 0.9], 'r-', linewidth=3)
        ax.plot(speed_angle, 0.9, 'ro', markersize=10)
        
        # 刻度
        for i, ratio in enumerate([0, 0.25, 0.5, 0.75, 1.0]):
            angle = -2*np.pi/3 + ratio * 4*np.pi/3
            value = ratio * max_speed
            ax.text(angle, 1.1, f'{value:.0f}', 
                   ha='center', va='center', fontsize=10)
        
        # 中心文字
        ax.text(0, 0, f'{speed/8:.1f}\nMB/s', 
               ha='center', va='center', fontsize=16, fontweight='bold')
        
        ax.set_ylim(0, 1.2)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.axis('off')
        
        self.fig.tight_layout()
        self.draw()


class ChartDialog(QDialog):
    """图表展示对话框"""
    
    def __init__(self, parent, result_data):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            result_data: 测速结果数据
        """
        super().__init__(parent)
        
        self.result_data = result_data
        self.setWindowTitle("测速结果图表")
        self.setMinimumSize(900, 700)
        self.setModal(False)
        
        self._init_ui()
        self._show_chart()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("📊 测速结果可视化")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 图表画布
        self.canvas = SpeedChartCanvas(self, width=8, height=5, dpi=100)
        layout.addWidget(self.canvas)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 切换图表按钮
        if 'download' in self.result_data and 'upload' in self.result_data:
            self.speed_btn = QPushButton("📈 速度对比")
            self.speed_btn.clicked.connect(self._show_speed_chart)
            self.speed_btn.setMinimumHeight(40)
            button_layout.addWidget(self.speed_btn)
        
        if 'ping_details' in self.result_data:
            self.ping_btn = QPushButton("📊 Ping详情")
            self.ping_btn.clicked.connect(self._show_ping_chart)
            self.ping_btn.setMinimumHeight(40)
            button_layout.addWidget(self.ping_btn)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        close_btn.setMinimumHeight(40)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
    def _show_chart(self):
        """显示图表"""
        if 'download' in self.result_data and 'upload' in self.result_data:
            self._show_speed_chart()
        elif 'ping_details' in self.result_data:
            self._show_ping_chart()
            
    def _show_speed_chart(self):
        """显示速度对比图"""
        download = self.result_data.get('download', 0)
        upload = self.result_data.get('upload', 0)
        self.canvas.plot_speed_comparison(download, upload)
        
    def _show_ping_chart(self):
        """显示Ping详情图"""
        ping_details = self.result_data.get('ping_details', {})
        self.canvas.plot_ping_details(ping_details)
