# -*- coding: utf-8 -*-
"""
IP Controller
IP信息查询控制器
"""

from PySide6.QtCore import QObject, QThread, Signal
from ..models.ip_model import IPModel
from typing import Optional


class IPWorker(QThread):
    """IP信息查询工作线程"""
    
    # 信号定义
    progress = Signal(str)  # 进度更新
    finished = Signal(dict)  # 完成信号
    error = Signal(str)  # 错误信号
    
    def __init__(self, query_type: str, ip: Optional[str] = None):
        """
        初始化工作线程
        
        Args:
            query_type: 查询类型 ('get_ip', 'ip_info', 'external_ip_info')
            ip: IP地址（用于外部IP查询）
        """
        super().__init__()
        self.query_type = query_type
        self.ip = ip
        self.model = IPModel()
        self._is_running = True
        
    def run(self):
        """线程运行函数"""
        try:
            if self.query_type == 'get_ip':
                self._get_current_ip()
            elif self.query_type == 'ip_info':
                self._get_current_ip_info()
            elif self.query_type == 'external_ip_info':
                self._get_external_ip_info()
                
        except Exception as e:
            self.error.emit(f"查询过程出错: {str(e)}")
            
    def _get_current_ip(self):
        """获取当前IP"""
        self.progress.emit("正在获取IP地址...")
        
        ip = self.model.get_current_ip()
        if not ip:
            self.error.emit("获取IP地址失败")
            return
            
        result = {'ip': ip}
        self.finished.emit(result)
        
    def _get_current_ip_info(self):
        """获取当前IP详细信息"""
        self.progress.emit("正在获取IP地址...")
        
        ip = self.model.get_current_ip()
        if not ip:
            self.error.emit("获取IP地址失败")
            return
            
        if not self._is_running:
            return
            
        self.progress.emit("正在查询IP信息...")
        
        info = self.model.get_ip_info(ip)
        if not info:
            self.error.emit("获取IP信息失败")
            return
            
        self.finished.emit(info)
        
    def _get_external_ip_info(self):
        """获取外部IP信息"""
        if not self.ip:
            self.error.emit("未提供IP地址")
            return
            
        self.progress.emit(f"正在查询IP {self.ip} 的信息...")
        
        info = self.model.get_ip_info(self.ip)
        if not info:
            self.error.emit("查询IP信息失败")
            return
            
        self.finished.emit(info)
        
    def stop(self):
        """停止线程"""
        self._is_running = False
        self.quit()
        self.wait()


class IPController(QObject):
    """IP信息查询控制器"""
    
    # 信号定义
    progress_updated = Signal(str)
    query_completed = Signal(dict)
    query_failed = Signal(str)
    
    def __init__(self):
        """初始化控制器"""
        super().__init__()
        self._worker: IPWorker = None
        
    def get_current_ip(self):
        """获取当前IP"""
        self._start_query('get_ip')
        
    def get_current_ip_info(self):
        """获取当前IP详细信息"""
        self._start_query('ip_info')
        
    def get_external_ip_info(self, ip: str):
        """
        获取外部IP信息
        
        Args:
            ip: 要查询的IP地址
        """
        self._start_query('external_ip_info', ip)
        
    def _start_query(self, query_type: str, ip: Optional[str] = None):
        """
        开始查询
        
        Args:
            query_type: 查询类型
            ip: IP地址（可选）
        """
        # 如果有正在运行的查询，先停止
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            
        # 创建新的工作线程
        self._worker = IPWorker(query_type, ip)
        
        # 连接信号
        self._worker.progress.connect(self.progress_updated.emit)
        self._worker.finished.connect(self._on_query_finished)
        self._worker.error.connect(self._on_query_error)
        
        # 启动线程
        self._worker.start()
        
    def _on_query_finished(self, result: dict):
        """查询完成处理"""
        self.query_completed.emit(result)
        
    def _on_query_error(self, error_msg: str):
        """查询错误处理"""
        self.query_failed.emit(error_msg)
        
    def cancel_query(self):
        """取消查询"""
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            
    def is_querying(self) -> bool:
        """
        检查是否正在查询
        
        Returns:
            bool: 是否正在查询
        """
        return self._worker is not None and self._worker.isRunning()
