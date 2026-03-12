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

# ==================== API 配置 ====================
# 和风天气 API Key
QWEATHER_API_KEY = os.getenv("QWEATHER_API_KEY", "")

# 天行数据 API Key
TIANXING_API_KEY = os.getenv("TIANXING_API_KEY", "")

# ==================== 信息搜集模块 ====================

class InfoCollector:
    """信息搜集器"""

    def fetch_weather(self, city: str = "北京") -> Dict:
        """获取天气信息（使用和风天气API）"""
        try:
            # 如果没有配置API Key，使用模拟数据
            if not QWEATHER_API_KEY:
                import random
                weathers = ["晴", "多云", "阴", "小雨", "中雨"]
                weather = random.choice(weathers)
                temp = random.randint(15, 30)
                return {
                    "type": "天气",
                    "content": f"{city}当前天气：{weather}，温度：{temp}℃（模拟数据，请配置API获取真实数据）"
                }

            # 使用真实 API
            # 先获取城市ID
            city_url = f"https://geoapi.qweather.com/v2/city/lookup?location={city}&key={QWEATHER_API_KEY}"
            city_response = requests.get(city_url)
            city_data = city_response.json()

            if not city_data.get('location'):
                return {"type": "天气", "content": f"未找到城市：{city}"}

            location_id = city_data['location'][0]['id']

            # 获取天气
            weather_url = f"https://devapi.qweather.com/v7/weather/now?location={location_id}&key={QWEATHER_API_KEY}"
            response = requests.get(weather_url)
            data = response.json()

            return {
                "type": "天气",
                "content": f"{city}当前天气：{data.get('now', {}).get('text', '未知')}，温度：{data.get('now', {}).get('temp', 'N/A')}℃"
            }
        except Exception as e:
            return {"type": "天气", "content": f"获取天气失败：{str(e)}"}

    def fetch_news(self, keyword: str = "") -> List[Dict]:
        """获取新闻信息（使用天行数据API）"""
        try:
            # 如果没有配置API Key，使用模拟数据
            if not TIANXING_API_KEY:
                import random
                titles = [
                    "人工智能技术在医疗领域取得突破",
                    "新能源汽车销量持续增长",
                    "科学家发现新的可再生能源技术",
                    "5G网络覆盖范围进一步扩大",
                    "全球气候变化问题受到关注"
                ]
                news_list = random.sample(titles, min(3, len(titles)))
                return {
                    "type": "新闻",
                    "content": "\n".join([f"• {title}" for title in news_list]) + "\n（模拟数据，请配置API获取真实数据）"
                }

            # 使用真实 API
            url = f"https://api.tianapi.com/topnews/index?key={TIANXING_API_KEY}&num=5"
            response = requests.get(url)
            data = response.json()

            if data.get('code') != 200:
                return {"type": "新闻", "content": f"获取新闻失败：{data.get('msg', '未知错误')}"}

            news_list = data.get('newslist', [])
            content = "\n".join([
                f"• {item['title']}"
                for item in news_list[:5]
            ])

            return {"type": "新闻", "content": content}
        except Exception as e:
            return {"type": "新闻", "content": f"获取新闻失败：{str(e)}"}

    def fetch_stock(self, symbol: str = "000001") -> Dict:
        """获取股票信息（使用腾讯财经API，免费）"""
        try:
            # 使用腾讯财经API（免费）
            # symbol格式：sh000001(上证指数) 或 sz000001(平安银行)
            url = f"https://qt.gtimg.cn/q={symbol}"
            response = requests.get(url)
            data = response.text

            # 腾讯API返回格式：v_sh000001="1~上证指数~3200.50~..."
            if data.startswith('v_'):
                content = data.split('"')[1]
                if content:
                    parts = content.split('~')
                    if len(parts) > 3:
                        name = parts[1]
                        price = parts[3]
                        change = parts[4]
                        change_percent = parts[5]
                        return {
                            "type": "股票",
                            "content": f"{name}({symbol}) 最新价：{price}，涨跌：{change}({change_percent}%)"
                        }

            return {"type": "股票", "content": "获取股票数据失败，请检查股票代码"}
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
