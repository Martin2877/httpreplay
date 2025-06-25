# HTTP 请求回放工具

该工具可以从 Excel 文件中提取 HTTP 请求并转换为 GOR 格式进行回放。提供 Python 和 Go 两种实现版本。

## 功能特点

- 从 Excel 文件中提取 HTTP 请求
- 将请求转换为 GOR 格式进行回放
- 支持 Python 和 Go 两种实现
- 生成唯一的请求 ID 和时间戳
- 高效处理大型 Excel 文件

## 环境要求

### Python 版本
- Python 3.6+
- pandas
- openpyxl

### Go 版本
- Go 1.21+

## 安装指南

### Python 版本

#### 使用虚拟环境（推荐）

1. 创建虚拟环境：
```bash
python3 -m venv venv
source venv/bin/activate  # Windows 系统: venv\Scripts\activate
```

2. 安装依赖：
```bash
pip install -r requirements.txt
# 或者使用清华源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### Go 版本

1. 确保已安装 Go 1.21 或更高版本
2. 安装依赖：
```bash
go mod tidy
```
3. 构建可执行文件：
```bash
go build -o excel_to_gor.exe excel_to_gor.go
```

## 使用方法

### Python 版本
```bash
python excel_to_gor.py --input <excel文件> --output <gor文件> [--column <列名>]

# 选项：
#   -i, --input     输入 Excel 文件路径（必填）
#   -o, --output    输出 GOR 文件路径（必填）
#   -c, --column    包含 HTTP 请求的列名（默认：'http请求'）
```

### Go 版本
```bash
# 使用 go run 直接运行
go run excel_to_gor.go --input <excel文件> --output <gor文件> [--column <列名>]

# 使用编译后的可执行文件
./excel_to_gor --input <excel文件> --output <gor文件> [--column <列名>]

# 选项：
#   -i, --input     输入 Excel 文件路径（必填）
#   -o, --output    输出 GOR 文件路径（必填）
#   -c, --column    包含 HTTP 请求的列名（默认：'http请求'）
```

使用示例：
```bash
# Python 使用默认列名
python excel_to_gor.py --input report.xlsx --output output.gor

# Python 指定自定义列名
python excel_to_gor.py --input report.xlsx --output output.gor --column "custom_column"

# Go 使用默认列名
go run excel_to_gor.go --input report.xlsx --output output.gor

# Go 指定自定义列名
go run excel_to_gor.go --input report.xlsx --output output.gor --column "custom_column"
```

### 安装 GOR

#### Linux/macOS 系统
```bash
# 下载并安装
curl -L -o gor.tar.gz https://github.com/buger/goreplay/releases/download/1.3.3/gor_1.3.3_x64.tar.gz
tar -xzf gor.tar.gz
sudo mv gor /usr/local/bin/

# 验证安装
gor --version
```

#### Windows 系统
1. 从 [GOR 发布页面](https://github.com/buger/goreplay/releases) 下载最新版本
2. 解压下载的 ZIP 文件
3. 将解压目录添加到系统 PATH 环境变量
4. 打开新的命令提示符并验证安装：
   ```
   gor.exe --version
   ```

### 使用 GOR 回放 HTTP 请求

基本用法：
```bash
# 回放到目标主机
gor --input-file "output.gor" --output-http "http://目标主机"

# 回放到本地
gor --input-file "output.gor" --output-http "http://localhost:8000"

# 带速率限制的回放（例如：每秒10个请求）
gor --input-file "output.gor" --output-http "http://localhost:8000" --output-http-workers 10
```

## HTTP 流量回放与捕获

本工具提供从 PCAP 文件回放 HTTP 请求以及捕获网络流量到新 PCAP 文件的功能。

### 环境要求

- Python 3.6+
- Wireshark（包含 `tshark` 命令行工具）
- 所需 Python 包：`scapy`、`pandas`

安装所需 Python 包：

```bash
pip install scapy pandas
```

### 捕获 HTTP 流量

将 HTTP/HTTPS 流量捕获到 PCAP 文件：

```bash
# 基本捕获（30秒，默认网卡）
python http_replay.py capture -i eth0 -o capture.pcap

# 高级捕获（指定持续时间和过滤条件）
python http_replay.py capture -i eth0 -o capture.pcap -d 60 -f "tcp port 80 or tcp port 443"

# 列出可用网卡
# Windows 系统：
getmac
# Linux 系统：
ifconfig -a
```

### 回放 HTTP 请求

从 PCAP 文件回放 HTTP 请求到目标 URL：

```bash
# 基本回放
python http_replay.py replay -i input.pcap -t http://目标服务器

# 高级回放（带延迟和多次迭代）
python http_replay.py replay -i input.pcap -t http://目标服务器 -c 3 -d 0.5
```

### 启动 HTTP 服务器（API）

启动一个简单的 HTTP 服务器，通过 API 处理回放请求：

```bash
python http_replay.py server -p 8000
```

然后发送 POST 请求到 `http://localhost:8000/replay`，请求体为 JSON 格式：

```json
{
    "pcap_file": "path/to/input.pcap",
    "target_url": "http://目标服务器",
    "count": 1,
    "delay": 1
}
```

### 使用示例

1. 首先，捕获一些流量：
   ```bash
   python http_replay.py capture -i eth0 -o traffic.pcap -d 60
   ```

2. 然后回放捕获的流量：
   ```bash
   python http_replay.py replay -i traffic.pcap -t http://测试服务器:8080
   ```

### 注意事项

- 回放工具会从 PCAP 文件中提取 HTTP GET 请求并回放到目标 URL
- 对于 HTTPS 流量，您可能需要配置系统以拦截 SSL/TLS 流量
- 捕获工具需要管理员/root 权限来捕获网络流量
- 在 Windows 系统上，可能需要以管理员身份运行捕获命令