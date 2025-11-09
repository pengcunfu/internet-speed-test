# -*- coding: utf-8 -*-
"""
Simple SpeedTest Implementation
简单的网速测试实现 - 不依赖speedtest-cli
"""

import time
import requests
import threading
from typing import Optional, Dict
from datetime import datetime


class SimpleSpeedTest:
    """简单的网速测试类"""
    
    # 国内测速文件URL（使用CDN和大文件）
    TEST_URLS = {
        'download': [
            # 阿里云CDN
            ('https://mirrors.aliyun.com/centos/7/isos/x86_64/CentOS-7-x86_64-DVD-2009.iso', '100MB', '阿里云镜像站'),
            # 腾讯云CDN
            ('https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe', '200MB', '腾讯QQ下载'),
            # 网易云CDN
            ('https://mirrors.163.com/centos/7/isos/x86_64/CentOS-7-x86_64-DVD-2009.iso', '100MB', '网易镜像站'),
            # 华为云CDN
            ('https://mirrors.huaweicloud.com/centos/7/isos/x86_64/CentOS-7-x86_64-DVD-2009.iso', '100MB', '华为云镜像站'),
            # 清华大学镜像站
            ('https://mirrors.tuna.tsinghua.edu.cn/centos/7/isos/x86_64/CentOS-7-x86_64-DVD-2009.iso', '100MB', '清华大学镜像站'),
            # 中国科技大学镜像站
            ('https://mirrors.ustc.edu.cn/centos/7/isos/x86_64/CentOS-7-x86_64-DVD-2009.iso', '100MB', '中科大镜像站'),
            # 搜狐CDN
            ('http://mirrors.sohu.com/centos/7/isos/x86_64/CentOS-7-x86_64-DVD-2009.iso', '100MB', '搜狐镜像站'),
            # 百度云盘分享（公开文件）
            ('https://issuecdn.baidupcs.com/issue/netdisk/yunguanjia/BaiduNetdisk_7.17.0.12.exe', '100MB', '百度网盘客户端'),
        ],
        'upload': [
            # 使用国内测试接口
            ('https://httpbin.org/post', 'httpbin'),
            ('https://postman-echo.com/post', 'postman-echo'),
            ('http://httpbin.org/post', 'httpbin-http'),
        ]
    }
    
    def __init__(self, log_callback=None):
        """初始化"""
        self.download_speed = 0.0
        self.upload_speed = 0.0
        self.ping_time = 0.0
        self._log_callback = log_callback
        
    def _log(self, message: str):
        """输出日志"""
        print(message)
        if self._log_callback:
            self._log_callback(message)
        
    def test_download(self, test_duration: int = 10) -> Optional[float]:
        """
        测试下载速度
        
        Args:
            test_duration: 测试持续时间（秒）
            
        Returns:
            Optional[float]: 下载速度(Mbps)
        """
        self._log(f"[下载测试] 开始测试下载速度...")
        
        # 使用多个URL测试
        speeds = []
        
        for url, size, name in self.TEST_URLS['download'][:3]:  # 使用前3个URL
            try:
                self._log(f"[下载测试] 正在从 {name} 下载测试...")
                speed = self._test_download_single(url, test_duration)
                if speed > 0:
                    speeds.append(speed)
                    self._log(f"[下载测试] {name}: {speed:.2f} Mbps")
            except Exception as e:
                self._log(f"[下载测试] {name} 测试失败: {e}")
                continue
        
        if speeds:
            # 取平均值
            avg_speed = sum(speeds) / len(speeds)
            self.download_speed = round(avg_speed, 3)
            self._log(f"[下载测试] 平均下载速度: {self.download_speed} Mbps ({self.download_speed / 8:.2f} MB/s)")
            return self.download_speed
        else:
            self._log(f"[下载测试] 所有测试都失败")
            return None
            
    def _test_download_single(self, url: str, duration: int = 10) -> float:
        """
        单个URL下载测试
        
        Args:
            url: 测试URL
            duration: 测试持续时间
            
        Returns:
            float: 下载速度(Mbps)
        """
        start_time = time.time()
        downloaded = 0
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    downloaded += len(chunk)
                    
                # 检查是否超时
                elapsed = time.time() - start_time
                if elapsed >= duration:
                    break
            
            elapsed = time.time() - start_time
            if elapsed > 0:
                # 计算速度: (字节数 * 8) / 时间 / 1,000,000 = Mbps
                speed_mbps = (downloaded * 8) / elapsed / 1_000_000
                return speed_mbps
            
        except Exception as e:
            print(f"[下载测试] 下载出错: {e}")
            
        return 0.0
        
    def test_upload(self, test_size_mb: int = 5) -> Optional[float]:
        """
        测试上传速度
        
        Args:
            test_size_mb: 测试数据大小(MB)
            
        Returns:
            Optional[float]: 上传速度(Mbps)
        """
        print(f"[上传测试] 开始测试上传速度...")
        
        # 生成测试数据
        test_data = b'0' * (test_size_mb * 1024 * 1024)
        
        speeds = []
        
        for url, name in self.TEST_URLS['upload'][:1]:  # 只使用第一个URL
            try:
                print(f"[上传测试] 正在向 {name} 上传测试...")
                
                start_time = time.time()
                response = requests.post(url, data=test_data, timeout=30)
                elapsed = time.time() - start_time
                
                if response.status_code == 200 and elapsed > 0:
                    # 计算速度
                    speed_mbps = (len(test_data) * 8) / elapsed / 1_000_000
                    speeds.append(speed_mbps)
                    print(f"[上传测试] {name}: {speed_mbps:.2f} Mbps")
                    
            except Exception as e:
                print(f"[上传测试] {name} 测试失败: {e}")
                continue
        
        if speeds:
            avg_speed = sum(speeds) / len(speeds)
            self.upload_speed = round(avg_speed, 3)
            print(f"[上传测试] 平均上传速度: {self.upload_speed} Mbps ({self.upload_speed / 8:.2f} MB/s)")
            return self.upload_speed
        else:
            print(f"[上传测试] 所有测试都失败")
            return None
            
    def test_ping(self, hosts: list = None) -> Optional[Dict]:
        """
        测试Ping延迟
        
        Args:
            hosts: 要测试的主机列表
            
        Returns:
            Optional[Dict]: Ping结果字典
        """
        if hosts is None:
            # 使用国内常用服务和CDN
            hosts = [
                ('www.baidu.com', '百度'),
                ('www.qq.com', '腾讯'),
                ('www.taobao.com', '淘宝'),
                ('www.163.com', '网易'),
                ('www.jd.com', '京东'),
                ('www.aliyun.com', '阿里云'),
                ('cloud.tencent.com', '腾讯云'),
                ('www.huaweicloud.com', '华为云'),
                ('www.bilibili.com', '哔哩哔哩'),
                ('www.douyin.com', '抖音'),
            ]
        
        self._log(f"[Ping测试] 开始测试 {len(hosts)} 个网站的延迟...")
        
        results = {}
        valid_pings = []
        
        for host, name in hosts:
            ping_time = self._ping_http(host)
            results[name] = ping_time
            
            if ping_time is not None:
                valid_pings.append(ping_time)
                self._log(f"[Ping测试] {name} ({host}): {ping_time:.1f} ms")
            else:
                self._log(f"[Ping测试] {name} ({host}): 超时")
        
        if valid_pings:
            avg_ping = round(sum(valid_pings) / len(valid_pings), 1)
            min_ping = round(min(valid_pings), 1)
            max_ping = round(max(valid_pings), 1)
            
            self._log(f"[Ping测试] 统计结果:")
            self._log(f"  - 平均延迟: {avg_ping} ms")
            self._log(f"  - 最小延迟: {min_ping} ms")
            self._log(f"  - 最大延迟: {max_ping} ms")
            self._log(f"  - 成功率: {len(valid_pings)}/{len(hosts)}")
            
            self.ping_time = avg_ping
            
            return {
                'results': results,
                'average': avg_ping,
                'min': min_ping,
                'max': max_ping,
                'success_count': len(valid_pings),
                'total_count': len(hosts)
            }
        else:
            self._log(f"[Ping测试] 所有主机都无法访问")
            return None
            
    def _ping_http(self, host: str) -> Optional[float]:
        """
        使用HTTP请求测试延迟
        
        Args:
            host: 主机地址
            
        Returns:
            Optional[float]: 延迟时间(ms)
        """
        url = f"http://{host}" if not host.startswith('http') else host
        
        try:
            start_time = time.time()
            response = requests.head(url, timeout=5, allow_redirects=True)
            elapsed = (time.time() - start_time) * 1000  # 转换为毫秒
            
            if response.status_code < 500:  # 只要不是服务器错误就算成功
                return elapsed
                
        except Exception as e:
            pass
            
        return None
        
    def get_results(self) -> Dict:
        """
        获取测试结果
        
        Returns:
            Dict: 测试结果字典
        """
        return {
            'download': self.download_speed,
            'upload': self.upload_speed,
            'ping': self.ping_time,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
