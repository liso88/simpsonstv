
#!/usr/bin/python3
import evdev
import logging
import socket
import json
import os

# Screen is rotated; logical max
MAX_X = 480
MAX_Y = 640

X_MARGIN = 100           # side margin for seek
SEEK_SECS = 30           # seconds to seek
SOCKET_PATH = f"/run/user/{os.getuid()}/mpvsocket"  # MUST match player

def send_mpv(cmd_list):
    """Send a JSON IPC command list to MPV (e.g., ["cycle", "pause"])."""
    payload = json.dumps({"command": cmd_list}) + "\n"
    logging.info("MPV command: %s", cmd_list)
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(0.5)
        client.connect(SOCKET_PATH)
        client.sendall(payload.encode("utf-8"))
        # Best effort read (mpv may or may not reply depending on command)
        try:
            resp = client.recv(4096).decode("utf-8", errors="ignore").strip()
            if resp:
                logging.info("Received response: %s", resp)
        except socket.timeout:
            logging.debug("No response from MPV (timeout)")
    except (ConnectionRefusedError, FileNotFoundError) as e:
        logging.error("MPV IPC not available at %s: %s", SOCKET_PATH, e)
    finally:
        try:
            client.close()
        except Exception:
            pass

# Commands: https://mpv.io/manual/master/#json-ipc
def act(x: int, y: int, dx: int, dy: int):
    half = MAX_X / 2
    # Swipe left: previous in playlist
    if dx < -half:
        send_mpv(["playlist-prev"])
    # Swipe right: next in playlist
    elif dx > half:
        send_mpv(["playlist-next"])
    # Left margin: seek backward
    elif x < X_MARGIN:
        send_mpv(["seek", -SEEK_SECS, "relative"])
    # Right margin: seek forward
    elif x > MAX_X - X_MARGIN:
        send_mpv(["seek", SEEK_SECS, "relative"])
    # Middle tap: toggle pause
    else:
        send_mpv(["cycle", "pause"])

def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
    # Adjust this if your touchscreen is not event0 (use `sudo evtest` to check)
    device_path = os.environ.get("TOUCH_DEVICE", "/dev/input/event0")
    device = evdev.InputDevice(device_path)
    logging.info("Input device: %s", device)

    # Start with center position
    x = int(MAX_X / 2)
    y = int(MAX_Y / 2)
    down_x = None
    down_y = None

    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_TOUCH:
            if event.value == 0x0:  # touch up
                if down_x is not None and down_y is not None:
                    dx = x - down_x
                    dy = y - down_y
                    act(x, y, dx, dy)
                down_x = None
                down_y = None
            elif event.value == 0x1:  # touch down
                down_x = x
                down_y = y
        elif event.type == evdev.ecodes.EV_ABS:
            # Swap coordinates due to rotation
            if event.code == evdev.ecodes.ABS_MT_POSITION_X:
                y = MAX_Y - event.value
            elif event.code == evdev.ecodes.ABS_MT_POSITION_Y:
                x = MAX_X - event.value

if __name__ == "__main__":
    main()
