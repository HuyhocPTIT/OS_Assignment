import psutil
from flask import Flask, jsonify, render_template
import time

app = Flask(__name__)

# --- Hàm Thu thập Dữ liệu Tổng quan ---
def get_system_metrics():
    """Thu thập CPU và RAM utilization."""
    
    # Lấy % sử dụng CPU trong khoảng thời gian ngắn
    cpu_percent = psutil.cpu_percent(interval=0.5) 
    
    # Lấy thông tin bộ nhớ ảo (RAM)
    memory_info = psutil.virtual_memory()
    ram_percent = memory_info.percent
    
    # Lấy thông tin I/O (ví dụ: Disk Read/Write)
    # Lấy I/O counter trước và sau để tính tốc độ
    io_before = psutil.disk_io_counters()
    time.sleep(0.5)
    io_after = psutil.disk_io_counters()
    
    disk_read_mb = round((io_after.read_bytes - io_before.read_bytes) / (1024 * 1024), 2)
    disk_write_mb = round((io_after.write_bytes - io_before.write_bytes) / (1024 * 1024), 2)

    return {
        "timestamp": time.time(),
        "cpu_percent": cpu_percent,
        "ram_percent": ram_percent,
        "disk_read_mb": disk_read_mb,
        "disk_write_mb": disk_write_mb,
    }

# --- Hàm Thu thập Process Tree/List ---
def get_process_list():
    """Thu thập danh sách 10 tiến trình tốn tài nguyên nhất."""
    processes = []
    
    # Lặp qua tất cả các tiến trình
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            # Lấy thông tin chi tiết
            pinfo = proc.info
            
            # Gán thêm PID cha để tạo Process Tree
            try:
                pinfo['ppid'] = proc.ppid() 
            except psutil.Error:
                pinfo['ppid'] = None
                
            processes.append(pinfo)
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    # Sắp xếp theo %CPU và lấy 10 tiến trình hàng đầu
    sorted_processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)
    return sorted_processes[:10]


@app.route('/')
def index():
    """Route chính hiển thị giao diện dashboard."""
    return render_template('index.html')


@app.route('/api/metrics')
def api_metrics():
    """API endpoint trả về chỉ số CPU, RAM, I/O."""
    return jsonify(get_system_metrics())

@app.route('/api/processes')
def api_processes():
    """API endpoint trả về danh sách tiến trình."""
    return jsonify(get_process_list())

if __name__ == '__main__':
    # Chạy ứng dụng Flask
    app.run(debug=True)