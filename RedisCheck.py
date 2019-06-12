import redis
import time
import traceback


def RedisCheck():
    try:
        r = redis.StrictRedis(host='localhost', port=6379)                          # Connect to local Redis instance

        p = r.pubsub()                                                              # See https://github.com/andymccurdy/redis-py/#publish--subscribe
        p.subscribe('streaming')                                                 # Subscribe to startScripts channel
        PAUSE = True
        print("Waiting For DAQ...")
        while True:                                                                # Will stay in loop until START message received
            message = p.get_message()                                               # Checks for message
            if message:
                data = message['data']                                           # Get data from message
                print(data)
                
        print("Permission to start...")

    except Exception as e:
        print("!!!!!!!!!! EXCEPTION !!!!!!!!!")
        print(str(e))
        print(traceback.format_exc())

RedisCheck()