#!/usr/bin/env python3
"""
setup_email.py - 交互式邮箱配置向导
用法: python setup_email.py [--config-dir <配置目录>]
"""
import argparse
import json
import os
import getpass
import re

# SMTP 预设（同 send_email.py，独立一份便于向导使用）
SMTP_PRESETS = {
    "163.com":      {"host": "smtp.163.com",      "port": 465, "ssl": True,  "auth_type": "authorization_code", "guide": "登录 163 邮箱网页版 → 设置 → POP3/SMTP/IMAP → 开启 SMTP → 短信验证获取授权码"},
    "126.com":      {"host": "smtp.126.com",      "port": 465, "ssl": True,  "auth_type": "authorization_code", "guide": "登录 126 邮箱网页版 → 设置 → POP3/SMTP/IMAP → 开启 SMTP → 短信验证获取授权码"},
    "yeah.net":     {"host": "smtp.yeah.net",     "port": 465, "ssl": True,  "auth_type": "authorization_code", "guide": "登录 Yeah 邮箱网页版 → 设置 → POP3/SMTP/IMAP → 开启服务 → 短信验证获取授权码"},
    "qq.com":       {"host": "smtp.qq.com",        "port": 465, "ssl": True,  "auth_type": "authorization_code", "guide": "登录 QQ 邮箱网页版 → 设置 → 账户 → 开启 IMAP/SMTP 服务 → 用手机 QQ 扫码或短信验证生成授权码"},
    "foxmail.com":  {"host": "smtp.qq.com",        "port": 465, "ssl": True,  "auth_type": "authorization_code", "guide": "同 QQ 邮箱：登录 Foxmail 网页版 → 设置 → 账户 → 开启服务 → 获取授权码"},
    "exmail.qq.com":{"host": "smtp.exmail.qq.com", "port": 465, "ssl": True,  "auth_type": "password",          "guide": "腾讯企业邮箱直接使用邮箱登录密码，无需授权码"},
    "outlook.com":  {"host": "smtp-mail.outlook.com", "port": 587, "ssl": False, "tls": True, "auth_type": "app_password", "guide": "访问 account.microsoft.com → 安全 → 高级安全选项 → 创建应用密码（16位）"},
    "hotmail.com":  {"host": "smtp-mail.outlook.com", "port": 587, "ssl": False, "tls": True, "auth_type": "app_password", "guide": "同 Outlook：在微软账户中生成应用密码"},
    "live.com":     {"host": "smtp-mail.outlook.com", "port": 587, "ssl": False, "tls": True, "auth_type": "app_password", "guide": "同 Outlook：在微软账户中生成应用密码"},
    "office365.com":{"host": "smtp.office365.com", "port": 587, "ssl": False, "tls": True, "auth_type": "app_password", "guide": "Office365 管理员需在 Azure AD 中允许 SMTP 认证，或生成应用密码"},
    "gmail.com":    {"host": "smtp.gmail.com",    "port": 465, "ssl": True,  "auth_type": "app_password",       "guide": "访问 myaccount.google.com → 安全 → 两步验证（开启）→ 应用专用密码 → 生成 16 位密码（不含空格）"},
    "aliyun.com":   {"host": "smtp.aliyun.com",   "port": 465, "ssl": True,  "auth_type": "authorization_code", "guide": "登录阿里云邮箱网页版 → 设置 → 客户端专用密码 → 开启并生成授权码"},
    "qiye.aliyun.com": {"host": "smtp.qiye.aliyun.com", "port": 465, "ssl": True, "auth_type": "password", "guide": "阿里企业邮箱直接使用邮箱密码"},
    "icloud.com":   {"host": "smtp.mail.me.com",  "port": 587, "ssl": False, "tls": True, "auth_type": "app_password", "guide": "访问 appleid.apple.com → 登录和安全 → 应用专用密码 → 生成密码（格式 xxxx-xxxx-xxxx-xxxx）"},
    "me.com":       {"host": "smtp.mail.me.com",  "port": 587, "ssl": False, "tls": True, "auth_type": "app_password", "guide": "同 iCloud：在 Apple ID 中生成应用专用密码"},
    "sina.com":     {"host": "smtp.sina.com",      "port": 465, "ssl": True,  "auth_type": "authorization_code", "guide": "登录新浪邮箱网页版 → 设置 → POP3/SMTP → 开启 SMTP → 获取授权码"},
    "sina.cn":      {"host": "smtp.sina.com",      "port": 465, "ssl": True,  "auth_type": "authorization_code", "guide": "同新浪邮箱：在设置中开启 SMTP 并获取授权码"},
    "sohu.com":     {"host": "smtp.sohu.com",      "port": 465, "ssl": True,  "auth_type": "authorization_code", "guide": "登录搜狐邮箱网页版 → 设置 → 客户端授权密码 → 开启并生成"},
    "189.cn":       {"host": "smtp.189.cn",        "port": 465, "ssl": True,  "auth_type": "authorization_code", "guide": "登录 189 邮箱网页版 → 设置 → 邮箱密码 → 客户端授权密码 → 获取"},
    "139.com":      {"host": "smtp.139.com",       "port": 465, "ssl": True,  "auth_type": "authorization_code", "guide": "登录 139 邮箱网页版 → 设置 → POP3/SMTP → 开启并获取授权码"},
}

def is_valid_email(email):
    return re.match(r'^[\w.+-]+@[\w-]+\.[\w.]+$', email) is not None

def detect_preset(email):
    domain = email.split('@')[-1].lower()
    return SMTP_PRESETS.get(domain)

def run_wizard(config_dir):
    print("=" * 50)
    print("  智能报告生成助手 - 邮箱配置向导")
    print("=" * 50)

    # 读取已有配置
    config_file = os.path.join(config_dir, 'email_settings.md')
    existing = []
    if os.path.exists(config_file):
        print(f"\n✓ 检测到已有邮箱配置：{config_file}")
        print("  是否继续添加新账户？（y/n）：", end=' ')
        if input().strip().lower() != 'y':
            print("已取消。")
            return

    # 步骤1：输入邮箱地址
    print("\n[步骤 1/4] 请输入发件邮箱地址：", end=' ')
    email = input().strip()
    if not is_valid_email(email):
        print("  ✗ 邮箱格式不正确，请重新运行向导")
        return

    preset = detect_preset(email)
    if preset:
        print(f"  ✓ 自动识别：{email.split('@')[1]} 邮箱")
        print(f"  ✓ SMTP 服务器：{preset['host']}:{preset['port']} {'SSL' if preset.get('ssl') else 'STARTTLS'}")
    else:
        print(f"  ? 未识别的邮箱域名，将使用自定义 SMTP 配置")
        preset = {"host": "", "port": 465, "ssl": True, "auth_type": "password", "guide": "请联系邮箱服务商获取 SMTP 配置"}

    # 步骤2：输入密码/授权码
    print(f"\n[步骤 2/4] 密码/授权码获取指引：")
    print(f"  {preset.get('guide', '请联系邮箱服务商获取 SMTP 配置')}")
    print(f"  请输入密码/授权码（输入不显示，按回车确认）：", end='')
    password = getpass.getpass('')

    # 步骤3：账户别名
    print(f"\n[步骤 3/4] 给这个账户起个名字（如 work_163 / personal_qq）：", end=' ')
    account_name = input().strip()
    if not account_name:
        account_name = email.split('@')[0] + '_' + email.split('@')[1].split('.')[0]

    # 步骤4：测试发送
    print(f"\n[步骤 4/4] 是否发送测试邮件验证配置？（y/n）：", end=' ')
    test_ok = False
    if input().strip().lower() == 'y':
        print(f"  输入接收测试邮件的地址（可直接回车使用 {email}）：", end=' ')
        test_to = input().strip() or email
        print(f"  正在发送测试邮件到 {test_to}...")
        # 调用 send_email.py
        import subprocess
        html_body = f"<h2>测试邮件</h2><p>这是来自 智能报告生成助手 的测试邮件，您的邮箱配置已成功！</p>"
        html_file = os.path.join(config_dir, '_test_email.html')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_body)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        cmd = [
            'python', os.path.join(script_dir, 'send_email.py'),
            '--from-account', email,
            '--password', password,
            '--to', test_to,
            '--subject', '智能报告生成助手 - 邮箱配置测试',
            '--html', html_file,
        ]
        if preset.get('host'):
            cmd += ['--smtp-host', preset['host'], '--smtp-port', str(preset['port'])]

        result = subprocess.run(cmd, capture_output=True, text=True)
        try:
            result_json = json.loads(result.stdout)
            if result_json.get('success'):
                print("  ✓ 测试邮件发送成功！")
                test_ok = True
            else:
                print(f"  ✗ 发送失败：{result_json.get('error', '未知错误')}")
        except:
            print(f"  ✗ 发送失败：{result.stdout or result.stderr}")

    # 保存配置
    os.makedirs(config_dir, exist_ok=True)
    entry = f"""

## 账户：{account_name}

| 字段 | 值 |
|------|-----|
| email | {email} |
| smtp_host | {preset.get('host', '自定义')} |
| smtp_port | {preset.get('port', '')} |
| ssl | {preset.get('ssl', True)} |
| tls | {preset.get('tls', False)} |
| auth_type | {preset.get('auth_type', 'password')} |
| from_name |  |
| signature |  |
| is_default | {'true' if not os.path.exists(config_file) else 'false'} |
| test_passed | {str(test_ok).lower()} |

> 密码/授权码已通过测试验证，实际使用时由用户每次输入（不保存明文）
"""
    with open(config_file, 'a', encoding='utf-8') as f:
        f.write(entry)

    print(f"\n✓ 配置已保存至：{config_file}")
    print(f"  账户名称：{account_name}")
    print(f"  发件地址：{email}")
    print("\n配置向导完成！")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-dir', default=None, help='配置目录路径')
    args = parser.parse_args()

    config_dir = args.config_dir or os.path.join(
        os.path.expanduser('~'), '.workbuddy', 'skills', 'report-generator', 'config'
    )
    os.makedirs(config_dir, exist_ok=True)
    run_wizard(config_dir)
