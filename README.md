# 每日信息自动推送系统

一个基于 GitHub Actions 的自动化信息搜集与通知系统，可定时搜集网络信息并推送到指定渠道。

## 功能特性

- ✅ **多种信息源**：天气、新闻、股票、自定义API
- ✅ **多种通知方式**：邮件、企业微信、钉钉、飞书
- ✅ **定时自动执行**：支持自定义时间
- ✅ **完全免费**：基于 GitHub Actions 免费额度
- ✅ **无需服务器**：云端自动运行

## 快速开始

### 第一步：创建 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 创建一个新的公开仓库（推荐公开，免费额度更多）
3. 上传本项目的所有文件到仓库

### 第二步：配置 GitHub Secrets

进入仓库：`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

添加以下 Secrets（根据你的通知方式选择配置）：

#### 邮件通知
| Secret Name | 说明 | 示例 |
|-------------|------|------|
| `NOTIFICATION_TYPE` | 通知方式 | `email` |
| `EMAIL_SMTP_HOST` | SMTP服务器地址 | `smtp.gmail.com` |
| `EMAIL_SMTP_PORT` | SMTP端口 | `587` |
| `EMAIL_FROM` | 发件邮箱 | `your@gmail.com` |
| `EMAIL_PASSWORD` | 邮箱密码/应用密码 | `xxxxx` |
| `EMAIL_TO` | 收件邮箱 | `recipient@example.com` |

#### 企业微信通知
| Secret Name | 说明 | 示例 |
|-------------|------|------|
| `NOTIFICATION_TYPE` | 通知方式 | `wechat` |
| `WECHAT_WEBHOOK` | Webhook地址 | `https://qyapi.weixin.qq.com/...` |

#### 钉钉通知
| Secret Name | 说明 | 示例 |
|-------------|------|------|
| `NOTIFICATION_TYPE` | 通知方式 | `dingtalk` |
| `DINGTALK_WEBHOOK` | Webhook地址 | `https://oapi.dingtalk.com/...` |
| `DINGTALK_SECRET` | 加密密钥 | `SECxxxxx` |

#### 飞书通知
| Secret Name | 说明 | 示例 |
|-------------|------|------|
| `NOTIFICATION_TYPE` | 通知方式 | `feishu` |
| `FEISHU_WEBHOOK` | Webhook地址 | `https://open.feishu.cn/...` |

#### 信息搜集配置（可选）
| Secret Name | 说明 | 示例 |
|-------------|------|------|
| `WEATHER_CITY` | 天气城市 | `北京` |
| `NEWS_KEYWORD` | 新闻关键词 | `科技` |
| `STOCK_SYMBOL` | 股票代码 | `000001` |

### 第三步：修改定时时间

编辑 `.github/workflows/daily-report.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # UTC时间0点 = 北京时间8点
```

常用时间参考：
- 早上8点：`0 0 * * *`
- 早上9点：`0 1 * * *`
- 中午12点：`0 4 * * *`
- 晚上18点：`0 10 * * *`
- 晚上20点：`0 12 * * *`

> 💡 注意：cron 使用 UTC 时间，北京时间 = UTC + 8 小时

### 第四步：启用工作流

1. 提交代码到 GitHub 仓库
2. 进入 `Actions` 标签页
3. 确认工作流已启用

### 第五步：测试运行

方法一：手动触发
- 进入 `Actions` → 选择工作流 → 点击 `Run workflow`

方法二：等待定时执行
- 等待设置的时间到达，会自动执行

## 自定义功能

### 修改信息源

编辑 `fetch_and_notify.py` 中的 `InfoCollector` 类：

```python
# 添加自定义信息搜集方法
def fetch_custom_info(self):
    # 调用你的API或爬取网页
    url = "your_api_url"
    response = requests.get(url)
    data = response.json()

    return {
        "type": "自定义",
        "content": f"数据：{data}"
    }
```

### 修改报告格式

编辑 `format_report()` 函数自定义输出格式：

```python
def format_report(info_list: List[Dict]) -> str:
    # 自定义你的报告格式
    pass
```

## 通知方式详细配置

### 邮件配置

#### Gmail 配置
1. 开启两步验证
2. 生成应用专用密码：Google 账号 → 安全性 → 应用专用密码
3. 使用应用密码作为 `EMAIL_PASSWORD`

#### QQ邮箱配置
- SMTP服务器：`smtp.qq.com`
- 端口：`587`
- 需要开启 SMTP 服务并获取授权码

#### 企业微信配置
1. 企业微信管理后台 → 应用管理 → 创建应用
2. 获取 Webhook 地址
3. 复制到 `WECHAT_WEBHOOK`

#### 钉钉配置
1. 钉钉群 → 群设置 → 机器人 → 添加机器人
2. 选择「自定义」机器人
3. 获取 Webhook 地址和密钥
4. 复制到对应的 Secret

#### 飞书配置
1. 飞书群 → 设置 → 机器人 → 添加机器人
2. 选择「自定义机器人」
3. 获取 Webhook 地址
4. 复制到 `FEISHU_WEBHOOK`

## 本地测试

在本地运行前，先安装依赖：

```bash
pip install -r requirements.txt
```

然后设置环境变量或创建 `.env` 文件：

```bash
cp .env.example .env
# 编辑 .env 文件，填入真实值
```

运行测试：

```bash
python fetch_and_notify.py
```

## 免费额度说明

### GitHub Actions 免费额度

- **公开仓库**：无限免费
- **私有仓库**：每月 2000 分钟
- Ubuntu 环境计为 1 倍时间

对于每日一次的定时任务，完全在免费额度范围内。

## 常见问题

### Q1: 如何验证是否运行成功？
A: 查看 Actions 页面的执行日志，成功会显示 ✅，失败会显示 ❌

### Q2: 如何查看错误原因？
A: 点击失败的运行记录，查看详细日志输出

### Q3: 可以修改为多次执行吗？
A: 可以，在 cron 表达式中添加多个时间，例如：
```yaml
schedule:
  - cron: '0 0 * * *'   # 早上8点
  - cron: '0 12 * * *'  # 晚上20点
```

### Q4: 如何支持更多通知方式？
A: 在 `NotificationSender` 类中添加新方法，参考现有实现

### Q5: 为什么收不到邮件？
A: 检查以下几点：
- Gmail 需要使用应用专用密码，不是登录密码
- 检查垃圾邮件文件夹
- 确认 SMTP 服务器地址和端口正确

### Q6: 如何获取真实的天气API？
A: 推荐使用和风天气（免费版足够使用）：
1. 注册 https://dev.qweather.com/
2. 创建应用获取 API Key
3. 替换代码中的 `YOUR_API_KEY`

## 文件结构

```
.
├── .github/
│   └── workflows/
│       └── daily-report.yml    # GitHub Actions 工作流配置
├── fetch_and_notify.py          # 主脚本
├── requirements.txt             # Python 依赖
├── config.json                  # 配置文件
├── .env.example                 # 环境变量示例
└── README.md                    # 使用文档
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
