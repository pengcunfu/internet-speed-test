# -*- coding: utf-8 -*-
"""
SpeedTest Controller
网速测试控制器
"""

from PySide6.QtCore import QObject, QThread, Signal
from ..models.speedtest_model import SpeedTestModel
from datetime import datetime


class SpeedTestWorker(QThread):
    """网速测试工作线程"""
    
    # 信号定义
    progress = Signal(str)  # 进度更新
    log = Signal(str)  # 日志信息
    finished = Signal(dict)  # 完成信号，传递结果字典
    error = Signal(str)  # 错误信号
    
    def __init__(self, test_type: str):
        """
        初始化工作线程
        
        Args:
            test_type: 测试类型 ('download', 'upload', 'both', 'ping')
        """
        super().__init__()
        self.test_type = test_type
        self.model = SpeedTestModel(log_callback=self._emit_log)
        self._is_running = True
        
    def _emit_log(self, message: str):
        """发送日志信号"""
        self.log.emit(message)
        
    def run(self):
        """线程运行函数"""
        try:
            # 初始化
            self.progress.emit("正在初始化测试服务...")
            if not self.model.initialize():
                self.error.emit("无法初始化网速测试服务")
                return
                
            if not self._is_running:
                return
                
            # 获取服务器列表
            self.progress.emit("正在获取服务器列表...")
            if not self.model.get_servers():
                self.error.emit("无法获取服务器列表，请检查网络连接")
                return
                
            if not self._is_running:
                return
                
            # 选择最佳服务器
            self.progress.emit("正在选择最佳服务器...")
            server_info = self.model.select_best_server()
            if not server_info:
                self.error.emit("无法找到合适的测试服务器")
                return
                
            server_name = server_info.get('sponsor', '测试服务器')
            server_country = server_info.get('country', '')
            self.progress.emit(f"已连接到: {server_name} ({server_country})")
            
            if not self._is_running:
                return
                
            # 执行测试
            result = {
                'server': server_info,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if self.test_type in ('download', 'both'):
                self.progress.emit("正在测试下载速度...")
                download_speed = self.model.test_download()
                if download_speed is None:
                    self.error.emit("下载速度测试失败")
                    return
                result['download'] = download_speed
                
                if not self._is_running:
                    return
                    
            if self.test_type in ('upload', 'both'):
                self.progress.emit("正在测试上传速度...")
                upload_speed = self.model.test_upload()
                if upload_speed is None:
                    self.error.emit("上传速度测试失败")
                    return
                result['upload'] = upload_speed
                
                if not self._is_running:
                    return
                    
            if self.test_type == 'ping':
                self.progress.emit("正在测试多个国内服务器的Ping...")
                ping_results = self.model.ping_multiple_hosts()
                if ping_results is None:
                    self.error.emit("Ping测试失败")
                    return
                result['ping'] = ping_results['average']
                result['ping_min'] = ping_results['min']
                result['ping_max'] = ping_results['max']
                result['ping_details'] = ping_results['results']
                result['ping_success_rate'] = f"{ping_results['success_count']}/{ping_results['total_count']}"
                
            # 发送完成信号
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(f"测试过程出错: {str(e)}")
            
    def stop(self):
        """停止线程"""
        self._is_running = False
        self.quit()
        self.wait()


class SpeedTestController(QObject):
    """网速测试控制器"""
    
    # 信号定义
    progress_updated = Signal(str)
    log_updated = Signal(str)  # 日志更新信号
    test_completed = Signal(dict)
    test_failed = Signal(str)
    
    def __init__(self):
        """初始化控制器"""
        super().__init__()
        self._worker: SpeedTestWorker = None
        
    def start_test(self, test_type: str):
        """
        开始测试
        
        Args:
            test_type: 测试类型 ('download', 'upload', 'both', 'ping')
        """
        # 如果有正在运行的测试，先停止
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            
        # 创建新的工作线程
        self._worker = SpeedTestWorker(test_type)
        
        # 连接信号
        self._worker.progress.connect(self.progress_updated.emit)
        self._worker.log.connect(self.log_updated.emit)  # 连接日志信号
        self._worker.finished.connect(self._on_test_finished)
        self._worker.error.connect(self._on_test_error)
        
        # 启动线程
        self._worker.start()
        
    def _on_test_finished(self, result: dict):
        """测试完成处理"""
        self.test_completed.emit(result)
        
    def _on_test_error(self, error_msg: str):
        """测试错误处理"""
        self.test_failed.emit(error_msg)
        
    def cancel_test(self):
        """取消测试"""
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            
    def is_testing(self) -> bool:
        """
        检查是否正在测试
        
        Returns:
            bool: 是否正在测试
        """
        return self._worker is not None and self._worker.isRunning()
