import socket

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('8.8.8.8', 1))  
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

def is_office_network(ip_address):
    # Define the office network IP range (for example: 192.168.1.0/24)
    office_ip_range_start = '172.16.2.100'
    office_ip_range_end = '172.16.2.300'

    ip_num = int(''.join([f"{int(part):02x}" for part in ip_address.split('.')]), 16)
    start_num = int(''.join([f"{int(part):02x}" for part in office_ip_range_start.split('.')]), 16)
    end_num = int(''.join([f"{int(part):02x}" for part in office_ip_range_end.split('.')]), 16)

    return start_num <= ip_num <= end_num

