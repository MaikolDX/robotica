# main.py
import os
from concurrent.futures import ThreadPoolExecutor
import signal
import sys
from threading import Thread
import time
from factory.led_manager import LEDDevice
from helpers.led_helper import led_device_manager
import uvicorn
from factory.db_connector import SQLiteConnector
from helpers.db_helper import DBTableHelper
from app_apis import app, run_websocket_image_scan, run_websocket_image_scan2
from fastapi.middleware.cors import CORSMiddleware
import RPi.GPIO as GPIO

from helpers.threads_exit_flag import set_exit_flag
from dotenv import load_dotenv

from lcd_logic import update_message, start_lcd_thread, stop_lcd_thread

# load environment variables
load_dotenv()

# Enable CORS for all routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend's URL or use "*" to allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # You can specify specific HTTP methods (e.g., ["GET", "POST"])
    allow_headers=["*"],  # You can specify specific HTTP headers
)


'''
    ---------------------------------
    START DATABASE CONNECTION 
    ---------------------------------
'''

#connect to database.
db_connector = SQLiteConnector("app_db.db")

# create DB tables if they do not exist
db_table_helper = DBTableHelper(db_connector=db_connector)
db_table_helper.create_db_tables()


'''
    ---------------------------------
    HANDLE THREADS
    ---------------------------------
'''


def cleanup_gpio():
    # Cleanup GPIO resources
    GPIO.cleanup()

def handle_shutdown(signum, frame):
    print("Received shutdown signal. Cleaning up...")
    try:
        set_exit_flag()
        time.sleep(0.5)
        sys.exit(0)
    except Exception as e:
        sys.exit(1)
    finally:
        stop_lcd_thread()
        cleanup_gpio()

def run_app_main():
    print("main application thread")
    update_message("Hola a todos!", "Iniciando...")
    start_lcd_thread()
    stop_lcd_thread()
    led_device_manager.print_devices()
    led_device_manager.start_manager_thread()
    

def run_http():
    uvicorn.run(app, host="0.0.0.0", port=8050)

def run_https():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="./localhost-ssl_keyfile.pem",
        ssl_certfile="./localhost-ssl_certfile.pem"
    )

def run_fast_api_app(executor):
    USE_HTTPS = True if os.environ.get("USE_HTTPS").lower() == "true" else False
    if USE_HTTPS:
        executor.submit(run_https)
    else:
        executor.submit(run_http)

# Bandera para controlar qué modo se está ejecutando
#modo_deteccion = True  # Iniciar con modo detección
#################################################################################
if __name__ == "__main__":
    # Set up a signal handler for KeyboardInterrupt (Ctrl+C)
    signal.signal(signal.SIGINT, handle_shutdown)

    # Use ThreadPoolExecutor to run both HTTP and HTTPS instances concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(run_app_main)
        run_fast_api_app(executor)
        executor.submit(run_websocket_image_scan)
        executor.submit(run_websocket_image_scan2)

###################################################################################