import threading
from app.init import get_env, get_path

import websocket
import _thread as thread
import time

websockets_url = get_env('WebSockets_Url')
websockets_api_key = get_env('WebSockets_Api_Key')

def create_websockets_client(message, callback):
    def on_message(ws, message):

        print('calling callback')
        callback(message)

    def on_error(ws, error):
        print(error)

    def on_close(ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(ws):
        #def run(*args):
        ws.send(message)
            # for i in range(3):
            #     time.sleep(1)
            #     ws.send('2')
            # time.sleep(1)
            #ws.close()
        #     print("thread terminating...")
        # def ping():            
        # thread.start_new_thread(ping, ())


    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f'{websockets_url}?token={websockets_api_key}',
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever()
    # ws._send_ping(30, , '2')
    # ws._send_ping(30, threading.Event(), '2')