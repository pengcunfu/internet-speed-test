# -*- coding: utf-8 -*-
"""
Result Dialog View
结果显示对话框视图
"""

import pyperclip
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QTextEdit, QPushButton, QMessageBox)
from PySide6.QtCore import Qt, Signal


class ResultDialog(QDialog):
    """结果显示对话框"""
    
    # 定义关闭信号
    dialog_closed = Signal()
    
    def __init__(self, parent, title: str):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
        """
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setFixedSize(450, 500)
        self.setModal(True)
        
        # 居中显示
        if parent:
            parent_geometry = parent.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
        
        self._init_ui()
        
    def _init_ui(self):
        """初始化用户界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        self.title_label = QLabel("正在加载，请稍候...")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        # 信息显示区域
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("复制信息")
        self.close_btn = QPushButton("关闭")
        
        button_layout.addWidget(self.copy_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        # 添加到主布局
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.info_text)
        main_layout.addLayout(button_layout)
        
        # 绑定事件
        self.copy_btn.clicked.connect(self._copy_info)
        self.close_btn.clicked.connect(self._force_close)
        
    def update_progress(self, message: str):
        """
        更新进度信息
        
        Args:
            message: 进度消息
        """
        self.title_label.setText(message)
        
    def append_log(self, log_message: str):
        """
        追加日志信息
        
        Args:
            log_message: 日志消息
        """
        current_text = self.info_text.toPlainText()
        if current_text:
            self.info_text.setText(current_text + "\n" + log_message)
        else:
            self.info_text.setText(log_message)
        
        # 滚动到底部
        scrollbar = self.info_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def show_result(self, result: str):
        """
        显示结果
        
        Args:
            result: 结果文本
        """
        self.title_label.setText("操作完成")
        self.info_text.setText(result)
        
    def show_error(self, error_msg: str):
        """
        显示错误
        
        Args:
            error_msg: 错误消息
        """
        self.title_label.setText("发生错误")
        self.info_text.setText(f"错误: {error_msg}")
        
    def _copy_info(self):
        """复制信息到剪贴板"""
        try:
            text = self.info_text.toPlainText()
            pyperclip.copy(text)
            QMessageBox.information(self, "提示", "信息已复制到剪贴板")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"复制失败: {str(e)}")
            
    def _force_close(self):
        """强制关闭对话框"""
        # 发送关闭信号
        self.dialog_closed.emit()
        # 立即关闭
        self.close()
            
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 发送关闭信号
        self.dialog_closed.emit()
        event.accept()
