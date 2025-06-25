
# HTTP Request Replay Tool

This tool extracts HTTP requests from an Excel file and converts them to GOR format for replay. It's available in both Python and Go implementations.

## Features

- Extract HTTP requests from Excel files
- Convert requests to GOR format for replay
- Support for both Python and Go implementations
- Generate unique request IDs and timestamps
- Handle large Excel files efficiently

## Prerequisites

### For Python Version
- Python 3.6+
- pandas
- openpyxl

### For Go Version
- Go 1.21+

## Installation

### Python Version

#### Using Virtual Environment (Recommended)

You can install the required packages globally, but this is not recommended:

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
# or
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### Go Version

1. Ensure Go is installed (1.21 or later)
2. Install dependencies:
```bash
go mod tidy
```
3. Build the binary:
```bash
go build -o excel_to_gor.exe excel_to_gor.go
```

## Usage

### Python Version
```bash
python excel_to_gor.py --input <excel_file> --output <gor_file> [--column <column_name>]

# Options:
#   -i, --input     Path to the input Excel file (required)
#   -o, --output    Path to the output GOR file (required)
#   -c, --column    Name of the column containing HTTP requests (default: 'http请求')
```

### Go Version
```bash
# Using go run
go run excel_to_gor.go --input <excel_file> --output <gor_file> [--column <column_name>]

# Using compiled binary
./excel_to_gor --input <excel_file> --output <gor_file> [--column <column_name>]

# Options:
#   -i, --input     Path to the input Excel file (required)
#   -o, --output    Path to the output GOR file (required)
#   -c, --column    Name of the column containing HTTP requests (default: 'http请求')
```

Example:
```bash
# Python with default column
python excel_to_gor.py --input report.xlsx --output output.gor

# Python with custom column
python excel_to_gor.py --input report.xlsx --output output.gor --column "custom_column"

# Go with default column
go run excel_to_gor.go --input report.xlsx --output output.gor

# Go with custom column
go run excel_to_gor.go --input report.xlsx --output output.gor --column "custom_column"
```

### Install GOR

#### Linux/macOS
```bash
# Download and install
curl -L -o gor.tar.gz https://github.com/buger/goreplay/releases/download/1.3.3/gor_1.3.3_x64.tar.gz
tar -xzf gor.tar.gz
sudo mv gor /usr/local/bin/

# Verify installation
gor --version
```

#### Windows
1. Download the latest release from [GOR releases page](https://github.com/buger/goreplay/releases)
2. Extract the downloaded ZIP file
3. Add the extracted directory to your system's PATH
4. Open a new command prompt and verify installation:
   ```
   gor.exe --version
   ```

### Replay HTTP Requests using GOR

Basic usage:
```bash
# Replay to a target host
gor --input-file "output.gor" --output-http "http://target-host"

# Replay to localhost
gor --input-file "output.gor" --output-http "http://localhost:8000"

# Replay with rate limiting (e.g., 10 requests per second)
gor --input-file "output.gor" --output-http "http://localhost:8000" --output-http-workers 10
```


## HTTP Traffic Replay and Capture

This tool provides functionality to replay HTTP requests from a PCAP file and capture network traffic to a new PCAP file.

### Prerequisites

- Python 3.6+
- Wireshark (includes `tshark` command-line tool)
- Required Python packages: `scapy`, `pandas`

Install the required Python packages:

```bash
pip install scapy pandas
```

### Capture HTTP Traffic

To capture HTTP/HTTPS traffic to a PCAP file:

```bash
# Basic capture (30 seconds, default interface)
python http_replay.py capture -i eth0 -o capture.pcap

# Advanced capture (specific duration and filter)
python http_replay.py capture -i eth0 -o capture.pcap -d 60 -f "tcp port 80 or tcp port 443"

# List available interfaces
# On Windows:
getmac
# On Linux:
ifconfig -a
```

### Replay HTTP Requests

To replay HTTP requests from a PCAP file to a target URL:

```bash
# Basic replay
python http_replay.py replay -i input.pcap -t http://target-server

# Advanced replay (with delay and multiple iterations)
python http_replay.py replay -i input.pcap -t http://target-server -c 3 -d 0.5
```

### Start HTTP Server (API)

Start a simple HTTP server to handle replay requests via API:

```bash
python http_replay.py server -p 8000
```

Then send a POST request to `http://localhost:8000/replay` with a JSON body:

```json
{
    "pcap_file": "path/to/input.pcap",
    "target_url": "http://target-server",
    "count": 1,
    "delay": 1
}
```

### Example Workflow

1. First, capture some traffic:
   ```bash
   python http_replay.py capture -i eth0 -o traffic.pcap -d 60
   ```

2. Then replay the captured traffic:
   ```bash
   python http_replay.py replay -i traffic.pcap -t http://test-server:8080
   ```

### Notes

- The replay tool extracts HTTP GET requests from the PCAP file and replays them to the target URL.
- For HTTPS traffic, you may need to configure your system to intercept SSL/TLS traffic.
- The capture tool requires administrative/root privileges to capture network traffic.
- For Windows, you may need to run the capture command as Administrator.

