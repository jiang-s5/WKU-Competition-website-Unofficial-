# WKU Platform Backend

这是温州肯恩大学AI社团竞赛平台的 Flask 后端项目。

## 目录结构

- `app/`: 应用包，包含路由、数据库、模板和静态资源
- `run.py`: 本地开发入口
- `serve.py`: Windows 服务器生产启动入口
- `wku_backend_app.py`: 兼容旧入口
- `scripts/start-local.ps1`: 本地一键启动脚本
- `scripts/build-deploy.ps1`: 重新生成部署压缩包
- `instance/`: SQLite 数据目录，首次运行后自动生成

## 本地开发

在 `F:\backend` 目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-local.ps1
```

默认会：

1. 创建 `.venv`
2. 安装依赖
3. 初始化数据库
4. 在 `http://127.0.0.1:8000` 启动本地开发站

## 本地管理员账号

- 用户名：`admin`
- 密码：`Admin@123456`

## 重新打包部署包

本地改完代码后，在 `F:\backend` 执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-deploy.ps1
```

会重新生成：

```text
F:\backend-deploy.zip
```

## Windows 服务器启动

把新版本解压到服务器后，在服务器目录执行：

```powershell
cd C:\wku-platform\site
py -m pip install -r wku_backend_requirements.txt
py -m flask --app run.py init-db
py serve.py
```

默认会监听：

```text
http://0.0.0.0:8000
```

## 推荐上线补充

- 将 `WKU_SECRET_KEY` 换成随机强密钥
- 后续把 SQLite 升级为 MySQL 或 PostgreSQL
- 对接真实短信服务
- 配置域名和 HTTPS
- 将 `py serve.py` 配成开机自启

## 接入阿里云真实短信

当前项目已经支持阿里云短信服务。要启用真实短信，需要同时完成控制台配置和环境变量配置。

### 1. 阿里云控制台需要准备的内容

你需要在阿里云短信服务中准备：

1. 已开通短信服务
2. 已审核通过的短信签名
3. 已审核通过的短信模板
4. 一个具备短信发送权限的 AccessKey

建议至少准备两个模板：

- 注册验证码模板
- 找回密码验证码模板

模板变量请统一使用：

```text
${code}
```

### 2. 环境变量

在服务器上设置这些环境变量后，系统就会自动从演示短信切换到真实短信：

```text
WKU_DEMO_SMS=0
WKU_SMS_PROVIDER=aliyun
WKU_SMS_ENDPOINT=dysmsapi.aliyuncs.com
WKU_SMS_SIGN_NAME=你的短信签名
WKU_SMS_TEMPLATE_PARAM_KEY=code
WKU_SMS_TEMPLATE_CODE_REGISTER=你的注册模板CODE
WKU_SMS_TEMPLATE_CODE_RESET=你的找回密码模板CODE
WKU_SMS_RESEND_SECONDS=60
WKU_SMS_EXPIRE_MINUTES=10
ALIBABA_CLOUD_ACCESS_KEY_ID=你的AccessKeyId
ALIBABA_CLOUD_ACCESS_KEY_SECRET=你的AccessKeySecret
```

### 3. Windows 服务器临时设置示例

```powershell
set WKU_DEMO_SMS=0
set WKU_SMS_PROVIDER=aliyun
set WKU_SMS_ENDPOINT=dysmsapi.aliyuncs.com
set WKU_SMS_SIGN_NAME=你的短信签名
set WKU_SMS_TEMPLATE_PARAM_KEY=code
set WKU_SMS_TEMPLATE_CODE_REGISTER=SMS_xxxxxxxx
set WKU_SMS_TEMPLATE_CODE_RESET=SMS_xxxxxxxx
set ALIBABA_CLOUD_ACCESS_KEY_ID=你的AccessKeyId
set ALIBABA_CLOUD_ACCESS_KEY_SECRET=你的AccessKeySecret
```

设置完成后重新启动：

```powershell
.\.venv\Scripts\python -m pip install -r wku_backend_requirements.txt
.\.venv\Scripts\python -m flask --app run.py init-db
.\.venv\Scripts\python serve.py
```

### 4. 当前逻辑说明

- 如果 `WKU_SMS_PROVIDER=aliyun` 且签名、模板、AccessKey 完整，系统会发送真实短信
- 如果没有配置完整并且 `WKU_DEMO_SMS=1`，系统会继续走演示短信模式
- 验证码默认 10 分钟有效
- 同一手机号同一用途默认 60 秒内不能重复发送
- 验证成功后验证码会立即作废，只能使用一次

