import time
import threading
from execution.robot_testbed import IBapiTest
from utils.params import *


app = None


def run_loop():
    app.run()


def execution_main():
    global app

    app = IBapiTest()

    app.connect(IBIP, PORT, 555)

    # Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    app.reqAccountUpdates(True, ACCOUNT)

    time.sleep(10)  # give some time for the system to fill the orders


    orderid = app.nextValidOrderId
    print(f"now next orderid is {orderid}")
    app.nextValidId(orderid)
    print(f"after method, now next orderid is {app.nextValidOrderId}")



    app.disconnect()


if __name__ == "__main__":
    execution_main()