# -*- coding: utf-8 -*-
"""
Result Dialog View
结果显示对话框视图
"""

import pyperclip
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QTextEdit, QPushButton, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor


class ResultDialog(QDialog):
    """结果显示对话框"""
    
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
        # 设置背景色
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(250, 250, 250))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        self.title_label = QLabel("正在加载，请稍候...")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #323296;")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        # 信息显示区域
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("复制信息")
        self.close_btn = QPushButton("关闭")
        
        # 设置按钮样式
        button_style = """
        QPushButton {
            font-size: 11px;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
        """
        
        self.copy_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #64b464;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #5aa45a;
            }
        """)
        
        self.close_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border: 1px solid #c0c0c0;
            }
        """)
        
        button_layout.addWidget(self.copy_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        # 添加到主布局
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.info_text)
        main_layout.addLayout(button_layout)
        
        # 绑定事件
        self.copy_btn.clicked.connect(self._copy_info)
        self.close_btn.clicked.connect(self.accept)
        
    def update_progress(self, message: str):
        """
        更新进度信息
        
        Args:
            message: 进度消息
        """
        self.title_label.setText(message)
        self.info_text.setText(f"{message}\n\n请耐心等待...")
        
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
