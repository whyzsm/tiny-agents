# SMTP 预设配置参考
# 版本：v3.1 | 更新日期：2026-06-08
# 用途：send_email.py 和 setup_email.py 的权威 SMTP 配置表

## 使用说明

本文件是 SMTP 预设的 Markdown 权威文档，供 AI 读取后自动填充 SMTP 配置。
Python 脚本中另有内置 DICT，修改时请同步更新 `scripts/send_email.py` 和 `scripts/setup_email.py`。

---

## 网易系

### 163 邮箱 (@163.com)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.163.com` |
| 端口 | `465`（SSL）或 `25`（不使用） |
| 加密方式 | SSL |
| 认证类型 | 授权码（**必须**，不用邮箱密码） |
| 获取授权码 | 登录网页版 → 设置 → POP3/SMTP/IMAP → 开启 SMTP → 短信验证获取 |

### 126 邮箱 (@126.com)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.126.com` |
| 端口 | `465`（SSL） |
| 加密方式 | SSL |
| 认证类型 | 授权码 |
| 获取授权码 | 同 163 邮箱步骤 |

### Yeah 邮箱 (@yeah.net)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.yeah.net` |
| 端口 | `465`（SSL） |
| 加密方式 | SSL |
| 认证类型 | 授权码 |
| 获取授权码 | 同 163 邮箱步骤 |

---

## 腾讯系

### QQ 邮箱 (@qq.com)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.qq.com` |
| 端口 | `465`（SSL）或 `587`（STARTTLS） |
| 加密方式 | SSL（推荐）或 STARTTLS |
| 认证类型 | 授权码（**必须**） |
| 获取授权码 | 登录网页版 → 设置 → 账户 → 开启 IMAP/SMTP → 验证后生成授权码 |

### Foxmail (@foxmail.com)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.qq.com`（同 QQ 邮箱） |
| 端口 | `465`（SSL） |
| 加密方式 | SSL |
| 认证类型 | 授权码（同 QQ 邮箱） |
| 获取授权码 | 同 QQ 邮箱步骤 |

### 腾讯企业邮箱 (@自定义域名)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.exmail.qq.com` |
| 端口 | `465`（SSL） |
| 加密方式 | SSL |
| 认证类型 | **邮箱登录密码**（无需授权码） |
| 注意事项 | 需管理员在管理后台开启 SMTP 服务 |

---

## 微软系

### Outlook (@outlook.com)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp-mail.outlook.com` |
| 端口 | `587`（STARTTLS） |
| 加密方式 | STARTTLS（TLS） |
| 认证类型 | 应用密码（**建议开启两步验证后使用**） |
| 获取应用密码 | account.microsoft.com → 安全 → 高级安全选项 → 创建应用密码（16位） |

### Hotmail (@hotmail.com)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp-mail.outlook.com`（同 Outlook） |
| 端口 | `587`（STARTTLS） |
| 加密方式 | STARTTLS |
| 认证类型 | 应用密码 |
| 获取应用密码 | 同 Outlook 步骤 |

### Live (@live.com)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp-mail.outlook.com`（同 Outlook） |
| 端口 | `587`（STARTTLS） |
| 加密方式 | STARTTLS |
| 认证类型 | 应用密码 |
| 获取应用密码 | 同 Outlook 步骤 |

### Office 365 企业邮箱
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.office365.com` |
| 端口 | `587`（STARTTLS） |
| 加密方式 | STARTTLS |
| 认证类型 | 应用密码（或管理员开启直接认证） |
| 注意事项 | 管理员需在 Azure AD / Microsoft 365 管理中心确认允许 SMTP 认证 |

---

## 谷歌系

### Gmail (@gmail.com)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.gmail.com` |
| 端口 | `465`（SSL）或 `587`（STARTTLS） |
| 加密方式 | SSL 或 STARTTLS |
| 认证类型 | 应用专用密码（**必须**，不用登录密码） |
| 获取应用密码 | myaccount.google.com → 安全 → 两步验证（先开启）→ 应用专用密码 → 生成 16 位密码（不含空格）|
| ⚠️ 中国用户 | Gmail SMTP 在中国大陆可能被屏蔽，建议使用其他邮箱或配置代理 |

### Google Workspace / G Suite（企业域名）
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.gmail.com`（同 Gmail） |
| 端口 | `465`（SSL） |
| 加密方式 | SSL |
| 认证类型 | 应用专用密码 |
| 获取应用密码 | 同 Gmail 步骤 |

---

## 阿里系

### 阿里云邮箱 (@aliyun.com)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.aliyun.com` |
| 端口 | `465`（SSL） |
| 加密方式 | SSL |
| 认证类型 | 授权码 |
| 获取授权码 | 登录阿里云邮箱网页版 → 设置 → 客户端授权密码 → 开启并生成 |

### 阿里企业邮箱 (@自定义域名)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.qiye.aliyun.com` |
| 端口 | `465`（SSL） |
| 加密方式 | SSL |
| 认证类型 | **邮箱登录密码**（无需授权码） |

---

## 苹果系

### iCloud / me.com (@icloud.com / @me.com)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.mail.me.com` |
| 端口 | `587`（STARTTLS） |
| 加密方式 | STARTTLS（TLS） |
| 认证类型 | 应用专用密码（**必须**） |
| 获取应用密码 | appleid.apple.com → 登录和安全 → 应用专用密码 → 生成（格式：xxxx-xxxx-xxxx-xxxx）|

---

## 其他国内邮箱

### 新浪邮箱 (@sina.com / @sina.cn)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.sina.com` |
| 端口 | `465`（SSL） |
| 加密方式 | SSL |
| 认证类型 | 授权码 |
| 获取授权码 | 登录新浪邮箱网页版 → 设置 → POP3/SMTP → 开启 SMTP → 获取授权码 |

### 搜狐邮箱 (@sohu.com)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.sohu.com` |
| 端口 | `465`（SSL） |
| 加密方式 | SSL |
| 认证类型 | 授权码 |
| 获取授权码 | 登录搜狐邮箱网页版 → 设置 → 客户端授权密码 → 开启并生成 |

### 189 邮箱 (@189.cn)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.189.cn` |
| 端口 | `465`（SSL） |
| 加密方式 | SSL |
| 认证类型 | 授权码 |
| 获取授权码 | 登录 189 邮箱网页版 → 设置 → 邮箱密码 → 客户端授权密码 → 获取 |

### 139 邮箱 (@139.com)
| 字段 | 值 |
|------|-----|
| SMTP 服务器 | `smtp.139.com` |
| 端口 | `465`（SSL） |
| 加密方式 | SSL |
| 认证类型 | 授权码 |
| 获取授权码 | 登录 139 邮箱网页版 → 设置 → POP3/SMTP → 开启并获取授权码 |

---

## 自定义 SMTP

当用户邮箱域名未在以上列表中时，引导用户手动填写：
- SMTP 服务器地址（host）
- 端口（常用：465/587/25）
- 加密方式（SSL / STARTTLS / 无加密）
- 认证类型（password / authorization_code / app_password）
- 用户名（通常为完整邮箱地址）
- 密码/授权码/应用密码

---

## 快速速查表

| 邮箱 | SMTP 服务器 | 端口 | 加密 | 密码类型 |
|------|-------------|------|------|----------|
| 163 | `smtp.163.com` | 465 | SSL | 授权码 |
| 126 | `smtp.126.com` | 465 | SSL | 授权码 |
| yeah | `smtp.yeah.net` | 465 | SSL | 授权码 |
| QQ | `smtp.qq.com` | 465 | SSL | 授权码 |
| Foxmail | `smtp.qq.com` | 465 | SSL | 授权码 |
| 腾讯企业 | `smtp.exmail.qq.com` | 465 | SSL | 登录密码 |
| Outlook | `smtp-mail.outlook.com` | 587 | STARTTLS | 应用密码 |
| Hotmail | `smtp-mail.outlook.com` | 587 | STARTTLS | 应用密码 |
| Office365 | `smtp.office365.com` | 587 | STARTTLS | 应用密码 |
| Gmail | `smtp.gmail.com` | 465 | SSL | 应用密码 |
| 阿里云 | `smtp.aliyun.com` | 465 | SSL | 授权码 |
| 阿里企业 | `smtp.qiye.aliyun.com` | 465 | SSL | 登录密码 |
| iCloud | `smtp.mail.me.com` | 587 | STARTTLS | 应用密码 |
| 新浪 | `smtp.sina.com` | 465 | SSL | 授权码 |
| 搜狐 | `smtp.sohu.com` | 465 | SSL | 授权码 |
| 189 | `smtp.189.cn` | 465 | SSL | 授权码 |
| 139 | `smtp.139.com` | 465 | SSL | 授权码 |
