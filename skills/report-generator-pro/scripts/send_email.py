#!/usr/bin/env python3
"""
send_email.py - 发送邮件（支持 15+ 主流邮箱预设）
依赖: pip install secure-smtplib  (标准库 smtplib 即可)
"""
import argparse
import sys
import os
import json
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# ============================================================
# SMTP 预设配置（18 种主流邮箱）
# ============================================================
SMTP_PRESETS = {
    "163.com":      {"host": "smtp.163.com",      "port": 465, "ssl": True,  "auth_type": "authorization_code"},
    "126.com":      {"host": "smtp.126.com",      "port": 465, "ssl": True,  "auth_type": "authorization_code"},
    "yeah.net":     {"host": "smtp.yeah.net",     "port": 465, "ssl": True,  "auth_type": "authorization_code"},
    "qq.com":       {"host": "smtp.qq.com",        "port": 465, "ssl": True,  "auth_type": "authorization_code"},
    "foxmail.com":  {"host": "smtp.qq.com",        "port": 465, "ssl": True,  "auth_type": "authorization_code"},
    "exmail.qq.com": {"host": "smtp.exmail.qq.com", "port": 465, "ssl": True, "auth_type": "password"},
    "outlook.com":  {"host": "smtp-mail.outlook.com", "port": 587, "ssl": False, "tls": True, "auth_type": "app_password"},
    "hotmail.com":  {"host": "smtp-mail.outlook.com", "port": 587, "ssl": False, "tls": True, "auth_type": "app_password"},
    "live.com":     {"host": "smtp-mail.outlook.com", "port": 587, "ssl": False, "tls": True, "auth_type": "app_password"},
    "office365.com": {"host": "smtp.office365.com", "port": 587, "ssl": False, "tls": True, "auth_type": "app_password"},
    "gmail.com":    {"host": "smtp.gmail.com",    "port": 465, "ssl": True,  "auth_type": "app_password"},
    "aliyun.com":   {"host": "smtp.aliyun.com",   "port": 465, "ssl": True,  "auth_type": "authorization_code"},
    "qiye.aliyun.com": {"host": "smtp.qiye.aliyun.com", "port": 465, "ssl": True, "auth_type": "password"},
    "icloud.com":   {"host": "smtp.mail.me.com",  "port": 587, "ssl": False, "tls": True, "auth_type": "app_password"},
    "me.com":       {"host": "smtp.mail.me.com",  "port": 587, "ssl": False, "tls": True, "auth_type": "app_password"},
    "sina.com":     {"host": "smtp.sina.com",      "port": 465, "ssl": True,  "auth_type": "authorization_code"},
    "sina.cn":      {"host": "smtp.sina.com",      "port": 465, "ssl": True,  "auth_type": "authorization_code"},
    "sohu.com":     {"host": "smtp.sohu.com",      "port": 465, "ssl": True,  "auth_type": "authorization_code"},
    "189.cn":       {"host": "smtp.189.cn",        "port": 465, "ssl": True,  "auth_type": "authorization_code"},
    "139.com":      {"host": "smtp.139.com",       "port": 465, "ssl": True,  "auth_type": "authorization_code"},
}

def detect_smtp(email_address):
    """根据邮箱地址自动检测 SMTP 配置"""
    domain = email_address.split('@')[-1].lower()
    # 精确匹配
    if domain in SMTP_PRESETS:
        return SMTP_PRESETS[domain]
    # 企业邮箱：尝试腾讯企业邮
    if 'exmail' in domain or 'tencent' in domain:
        return {"host": "smtp.exmail.qq.com", "port": 465, "ssl": True, "auth_type": "password", "note": "腾讯企业邮箱（请使用邮箱密码）"}
    # 通用兜底
    return None

def send_email(smtp_config, from_email, password, to_list, subject, html_body,
               cc_list=None, bcc_list=None, attachments=None, max_retry=3):
    """
    发送邮件，支持重试
    返回: {"success": True} 或 {"error": "...", "error_code": "..."}
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ", ".join(to_list) if isinstance(to_list, list) else to_list
    if cc_list:
        msg['Cc'] = ", ".join(cc_list) if isinstance(cc_list, list) else cc_list

    # HTML 正文
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    # 附件
    if attachments:
        for filepath in (attachments if isinstance(attachments, list) else [attachments]):
            if os.path.exists(filepath):
                filename = os.path.basename(filepath)
                with open(filepath, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment', filename=filename)
                    msg.attach(part)

    all_recipients = (to_list if isinstance(to_list, list) else [to_list])
    if cc_list:
        all_recipients += (cc_list if isinstance(cc_list, list) else [cc_list])
    if bcc_list:
        all_recipients += (bcc_list if isinstance(bcc_list, list) else [bcc_list])

    # 重试逻辑（指数退避）
    for attempt in range(1, max_retry + 1):
        try:
            if smtp_config.get('ssl'):
                server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'], timeout=30)
            else:
                server = smtplib.SMTP(smtp_config['host'], smtp_config['port'], timeout=30)
                if smtp_config.get('tls'):
                    server.starttls()

            server.login(from_email, password)
            server.sendmail(from_email, all_recipients, msg.as_string())
            server.quit()

            return {
                "success": True,
                "attempt": attempt,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except smtplib.SMTPAuthenticationError:
            return {"error": "SMTP 认证失败：用户名或密码/授权码错误", "error_code": "AUTH_FAILED"}
        except smtplib.SMTPException as e:
            err_msg = str(e)
            if attempt < max_retry:
                wait = 2 ** attempt  # 指数退避：2s, 4s, 8s
                time.sleep(wait)
                continue
            return {"error": f"SMTP 错误（重试{max_retry}次后失败）: {err_msg}", "error_code": "SMTP_ERROR"}
        except Exception as e:
            if attempt < max_retry:
                wait = 2 ** attempt
                time.sleep(wait)
                continue
            return {"error": f"发送失败（重试{max_retry}次后失败）: {str(e)}", "error_code": "UNKNOWN_ERROR"}

    return {"error": "达到最大重试次数", "error_code": "MAX_RETRY"}

def main():
    parser = argparse.ArgumentParser(description='发送邮件')
    parser.add_argument('--from-account', required=True, help='发件人邮箱地址')
    parser.add_argument('--password', required=True, help='密码/授权码/应用密码')
    parser.add_argument('--to', required=True, help='收件人（逗号分隔）')
    parser.add_argument('--cc', default='', help='抄送（逗号分隔）')
    parser.add_argument('--bcc', default='', help='密送（逗号分隔）')
    parser.add_argument('--subject', required=True, help='邮件主题')
    parser.add_argument('--html', required=True, help='HTML 正文文件路径 或 HTML 字符串')
    parser.add_argument('--attach', default='', help='附件路径（逗号分隔）')
    parser.add_argument('--smtp-host', default='', help='自定义 SMTP 服务器（可选）')
    parser.add_argument('--smtp-port', type=int, default=0, help='自定义 SMTP 端口')
    parser.add_argument('--log', default='', help='日志文件路径')
    args = parser.parse_args()

    # 解析收件人
    to_list = [x.strip() for x in args.to.split(',') if x.strip()]
    cc_list = [x.strip() for x in args.cc.split(',') if x.strip()] if args.cc else None
    bcc_list = [x.strip() for x in args.bcc.split(',') if x.strip()] if args.bcc else None

    # SMTP 配置
    if args.smtp_host:
        smtp_config = {"host": args.smtp_host, "port": args.smtp_port or 465, "ssl": True}
    else:
        smtp_config = detect_smtp(args.from_account)
        if not smtp_config:
            result = {"error": f"无法识别邮箱域名 {args.from_account.split('@')[-1]}，请使用 --smtp-host 指定 SMTP 服务器", "error_code": "UNKNOWN_DOMAIN"}
            print(json.dumps(result, ensure_ascii=False))
            sys.exit(1)

    # 读取 HTML 正文
    if os.path.exists(args.html):
        with open(args.html, 'r', encoding='utf-8') as f:
            html_body = f.read()
    else:
        html_body = args.html

    # 附件
    attachments = [x.strip() for x in args.attach.split(',') if x.strip()] if args.attach else None

    # 发送
    result = send_email(
        smtp_config=smtp_config,
        from_email=args.from_account,
        password=args.password,
        to_list=to_list,
        subject=args.subject,
        html_body=html_body,
        cc_list=cc_list,
        bcc_list=bcc_list,
        attachments=attachments
    )

    # 写日志
    if args.log:
        os.makedirs(os.path.dirname(args.log), exist_ok=True)
        log_entry = f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```\n"
        with open(args.log, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get('success') else 1)

if __name__ == '__main__':
    main()
