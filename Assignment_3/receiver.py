import time

frame_delays = []

def receiver(frame_queue):
    while True:
        if not frame_queue:
            time.sleep(0.01)
            continue
        frame, start_time = frame_queue.pop(0)
        print(f"\033[92mReceived frame {frame}\033[0m")
        end_time = time.time()
        frame_delays.append(end_time - start_time)
