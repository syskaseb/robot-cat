"""Retry Windows sharing violations without losing or truncating a receipt."""
import json
import time


def save_json(destination,value,attempts=12,delay=.05):
    temp=destination.with_suffix('.writing.json')
    temp.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
    for attempt in range(attempts):
        try:
            temp.replace(destination)
            return
        except PermissionError:
            if attempt+1==attempts:raise
            time.sleep(delay)
