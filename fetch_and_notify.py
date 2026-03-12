#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动信息搜集与通知脚本
支持：网页抓取、API调用、数据处理、发送通知
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any
import os
import sys

# ==================== 配置区域 ====================

# 通知方式配置（选择一种启用）
NOTIFICATION_TYPE = os.getenv("NOTIFICATION_TYPE", "email")  # email, wechat, dingtalk, feishu

# 邮件配置
EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")

# 企业微信配置
WECHAT_WEBHOOK = os.getenv("WECHAT_WEBHOOK", "")

# 钉钉配置
DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK", "")
DINGTALK_SECRET = os.getenv("DINGTALK_SECRET", "")

# 飞书配置
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")

# ==================== 信息搜集模块 ====================

class InfoCollector:
    """信息搜集器"""

    def fetch_weather(self, city: str = "北京") -> Dict:
        """获取天气信息（示例使用免费API）"""
        try:
            # 这里使用和风天气API作为示例，需要替换为您的API Key
            url = f"https://devapi.qweather.com/v7/weather/now?location={city}&key=YOUR_API_KEY"
            response = requests.get(url)
            data = response.json()

            return {
                "type": "天气",
                "content": f"{city}当前天气：{data.get('now', {}).get('text', '未知')}，温度：{data.get('now', {}).get('temp', 'N/A')}℃"
            }
        except Exception as e:
            return {"type": "天气", "content": f"获取天气失败：{str(e)}"}

    def fetch_news(self, keyword: str = "") -> List[Dict]:
        """获取新闻信息（示例）"""
        try:
            # 这里可以使用各大新闻API，如：天行数据、聚合数据等
            # 示例：使用RSS或自定义API
            news_list = [
                {"title": "示例新闻1", "url": "https://example.com/1"},
                {"title": "示例新闻2", "url": "https://example.com/2"}
            ]

            return {
                "type": "新闻",
                "content": "\n".join([f"• {item['title']}" for item in news_list])
            }
        except Exception as e:
            return {"type": "新闻", "content": f"获取新闻失败：{str(e)}"}

    def fetch_stock(self, symbol: str = "000001") -> Dict:
        """获取股票信息（示例）"""
        try:
            # 可以使用腾讯财经、新浪财经等API
            url = f"https://qt.gtimg.cn/q={symbol}"
            response = requests.get(url)
            data = response.text

            # 解析返回的数据
            if '~' in data:
                parts = data.split('~')
                return {
                    "type": "股票",
                    "content": f"{symbol} 最新价：{parts[3]}，涨跌：{parts[4]}%"
                }

            return {"type": "股票", "content": "获取股票数据失败"}
        except Exception as e:
            return {"type": "股票", "content": f"获取股票失败：{str(e)}"}

    def fetch_custom_api(self, url: str, **params) -> Dict:
        """调用自定义API"""
        try:
            response = requests.get(url, params=params)
            return {
                "type": "自定义API",
                "content": json.dumps(response.json(), ensure_ascii=False, indent=2)
            }
        except Exception as e:
            return {"type": "自定义API", "content": f"调用失败：{str(e)}"}

# ==================== 通知发送模块 ====================

class NotificationSender:
    """通知发送器"""

    def send_email(self, subject: str, content: str) -> bool:
        """发送邮件"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.header import Header

            msg = MIMEText(content, 'plain', 'utf-8')
            msg['From'] = Header(EMAIL_FROM)
            msg['To'] = Header(EMAIL_TO)
            msg['Subject'] = Header(subject, 'utf-8')

            with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_FROM, EMAIL_PASSWORD)
                server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())

            return True
        except Exception as e:
            print(f"邮件发送失败：{str(e)}")
            return False

    def send_wechat(self, content: str) -> bool:
        """发送企业微信通知"""
        try:
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            response = requests.post(WECHAT_WEBHOOK, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"企业微信发送失败：{str(e)}")
            return False

    def send_dingtalk(self, content: str) -> bool:
        """发送钉钉通知"""
        try:
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            response = requests.post(DINGTALK_WEBHOOK, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"钉钉发送失败：{str(e)}")
            return False

    def send_feishu(self, content: str) -> bool:
        """发送飞书通知"""
        try:
            data = {
                "msg_type": "text",
                "content": {
                    "text": content
                }
            }
            response = requests.post(FEISHU_WEBHOOK, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"飞书发送失败：{str(e)}")
            return False

    def send_notification(self, subject: str, content: str) -> bool:
        """根据配置发送通知"""
        print(f"准备发送通知（方式：{NOTIFICATION_TYPE}）")

        if NOTIFICATION_TYPE == "email":
            return self.send_email(subject, content)
        elif NOTIFICATION_TYPE == "wechat":
            return self.send_wechat(content)
        elif NOTIFICATION_TYPE == "dingtalk":
            return self.send_dingtalk(content)
        elif NOTIFICATION_TYPE == "feishu":
            return self.send_feishu(content)
        else:
            print(f"不支持的通知方式：{NOTIFICATION_TYPE}")
            return False

# ==================== 主程序 ====================

def collect_all_info() -> List[Dict]:
    """搜集所有信息"""
    collector = InfoCollector()
    results = []

    # 收集天气信息
    city = os.getenv("WEATHER_CITY", "北京")
    results.append(collector.fetch_weather(city))

    # 收集新闻信息
    keyword = os.getenv("NEWS_KEYWORD", "")
    results.append(collector.fetch_news(keyword))

    # 收集股票信息
    symbol = os.getenv("STOCK_SYMBOL", "000001")
    results.append(collector.fetch_stock(symbol))

    return results

def format_report(info_list: List[Dict]) -> str:
    """格式化报告"""
    report = []
    report.append("=" * 50)
    report.append(f"📅 每日信息报告")
    report.append(f"⏰ 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 50)
    report.append("")

    for info in info_list:
        report.append(f"【{info['type']}】")
        report.append(info['content'])
        report.append("")

    report.append("=" * 50)
    report.append("💡 本报告由自动化脚本生成")

    return "\n".join(report)

def main():
    """主函数"""
    print("开始执行信息搜集任务...")

    # 1. 搜集信息
    print("正在搜集信息...")
    info_list = collect_all_info()

    # 2. 格式化报告
    report = format_report(info_list)
    print(f"生成的报告：\n{report}")

    # 3. 发送通知
    print("正在发送通知...")
    sender = NotificationSender()
    success = sender.send_notification("每日信息报告", report)

    if success:
        print("✅ 通知发送成功！")
    else:
        print("❌ 通知发送失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
