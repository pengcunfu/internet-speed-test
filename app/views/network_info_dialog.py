# -*- coding: utf-8 -*-
"""
Network Info Dialog View
网络信息查看对话框
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QTextEdit, QPushButton, QLabel, QWidget, QTableWidget,
                               QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ..models.network_info_model import NetworkInfoModel


class NetworkInfoDialog(QDialog):
    """网络信息查看对话框"""
    
    def __init__(self, parent):
        """初始化对话框"""
        super().__init__(parent)
        
        self.model = NetworkInfoModel()
        self.setWindowTitle("网络信息查看")
        self.setMinimumSize(800, 600)
        self.setModal(False)
        
        self._init_ui()
        self._load_data()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("🌐 网络信息")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 标签页
        self.tab_widget = QTabWidget()
        
        # 网络适配器标签页
        self.adapter_widget = QWidget()
        self._init_adapter_tab()
        self.tab_widget.addTab(self.adapter_widget, "🔌 网络适配器")
        
        # 代理设置标签页
        self.proxy_widget = QWidget()
        self._init_proxy_tab()
        self.tab_widget.addTab(self.proxy_widget, "🔐 代理设置")
        
        # 网络统计标签页
        self.stats_widget = QWidget()
        self._init_stats_tab()
        self.tab_widget.addTab(self.stats_widget, "📊 网络统计")
        
        # DNS服务器标签页
        self.dns_widget = QWidget()
        self._init_dns_tab()
        self.tab_widget.addTab(self.dns_widget, "🌍 DNS服务器")
        
        layout.addWidget(self.tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self._load_data)
        refresh_btn.setMinimumHeight(40)
        button_layout.addWidget(refresh_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        close_btn.setMinimumHeight(40)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
    def _init_adapter_tab(self):
        """初始化网络适配器标签页"""
        layout = QVBoxLayout(self.adapter_widget)
        
        self.adapter_table = QTableWidget()
        self.adapter_table.setColumnCount(5)
        self.adapter_table.setHorizontalHeaderLabels(['名称', '状态', '速度', 'IP地址', 'MAC地址'])
        
        # 设置列宽
        header = self.adapter_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.adapter_table)
        
    def _init_proxy_tab(self):
        """初始化代理设置标签页"""
        layout = QVBoxLayout(self.proxy_widget)
        
        self.proxy_text = QTextEdit()
        self.proxy_text.setReadOnly(True)
        self.proxy_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.proxy_text)
        
    def _init_stats_tab(self):
        """初始化网络统计标签页"""
        layout = QVBoxLayout(self.stats_widget)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.stats_text)
        
    def _init_dns_tab(self):
        """初始化DNS服务器标签页"""
        layout = QVBoxLayout(self.dns_widget)
        
        self.dns_text = QTextEdit()
        self.dns_text.setReadOnly(True)
        self.dns_text.setFont(QFont("Consolas", 11))
        layout.addWidget(self.dns_text)
        
    def _load_data(self):
        """加载数据"""
        self._load_adapters()
        self._load_proxy()
        self._load_stats()
        self._load_dns()
        
    def _load_adapters(self):
        """加载网络适配器信息"""
        adapters = self.model.get_network_adapters()
        
        self.adapter_table.setRowCount(len(adapters))
        
        for i, adapter in enumerate(adapters):
            # 名称
            self.adapter_table.setItem(i, 0, QTableWidgetItem(adapter['name']))
            
            # 状态
            status = '🟢 启用' if adapter['status'] == 'up' else '🔴 禁用'
            self.adapter_table.setItem(i, 1, QTableWidgetItem(status))
            
            # 速度
            speed = f"{adapter['speed']} Mbps" if adapter['speed'] > 0 else 'N/A'
            self.adapter_table.setItem(i, 2, QTableWidgetItem(speed))
            
            # IP地址和MAC地址
            ipv4 = ''
            mac = ''
            for addr in adapter['addresses']:
                if addr['type'] == 'IPv4':
                    ipv4 = addr['address']
                elif addr['type'] == 'MAC':
                    mac = addr['address']
            
            self.adapter_table.setItem(i, 3, QTableWidgetItem(ipv4))
            self.adapter_table.setItem(i, 4, QTableWidgetItem(mac))
            
    def _load_proxy(self):
        """加载代理设置"""
        proxy = self.model.get_proxy_settings()
        
        text = "系统代理设置\n"
        text += "=" * 50 + "\n\n"
        
        text += f"代理状态: {'✅ 已启用' if proxy['enabled'] else '❌ 未启用'}\n\n"
        
        if proxy['enabled']:
            if proxy['http_proxy']:
                text += f"HTTP代理:  {proxy['http_proxy']}\n"
            if proxy['https_proxy']:
                text += f"HTTPS代理: {proxy['https_proxy']}\n"
            if proxy['ftp_proxy']:
                text += f"FTP代理:   {proxy['ftp_proxy']}\n"
            if proxy['socks_proxy']:
                text += f"SOCKS代理: {proxy['socks_proxy']}\n"
            
            if proxy['bypass_list']:
                text += f"\n绕过代理的地址:\n"
                for addr in proxy['bypass_list']:
                    text += f"  - {addr}\n"
        else:
            text += "当前未配置代理服务器\n"
        
        self.proxy_text.setText(text)
        
    def _load_stats(self):
        """加载网络统计"""
        stats = self.model.get_network_stats()
        
        text = "网络流量统计\n"
        text += "=" * 50 + "\n\n"
        
        # 转换字节为GB/MB
        bytes_sent_gb = stats['bytes_sent'] / (1024**3)
        bytes_recv_gb = stats['bytes_recv'] / (1024**3)
        
        text += f"📤 发送数据:\n"
        text += f"   总量: {bytes_sent_gb:.2f} GB ({stats['bytes_sent']:,} 字节)\n"
        text += f"   数据包: {stats['packets_sent']:,} 个\n"
        text += f"   错误: {stats['errout']:,} 个\n"
        text += f"   丢弃: {stats['dropout']:,} 个\n\n"
        
        text += f"📥 接收数据:\n"
        text += f"   总量: {bytes_recv_gb:.2f} GB ({stats['bytes_recv']:,} 字节)\n"
        text += f"   数据包: {stats['packets_recv']:,} 个\n"
        text += f"   错误: {stats['errin']:,} 个\n"
        text += f"   丢弃: {stats['dropin']:,} 个\n\n"
        
        text += f"📊 总计:\n"
        text += f"   总流量: {bytes_sent_gb + bytes_recv_gb:.2f} GB\n"
        text += f"   总数据包: {stats['packets_sent'] + stats['packets_recv']:,} 个\n"
        
        self.stats_text.setText(text)
        
    def _load_dns(self):
        """加载DNS服务器"""
        dns_servers = self.model.get_dns_servers()
        
        text = "DNS服务器列表\n"
        text += "=" * 50 + "\n\n"
        
        if dns_servers:
            for i, dns in enumerate(dns_servers, 1):
                text += f"{i}. {dns}\n"
        else:
            text += "未找到DNS服务器配置\n"
        
        self.dns_text.setText(text)
