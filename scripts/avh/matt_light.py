#!/usr/bin/env python3
import asyncio
import re
from websockets import client as ws
import sys

#import avh_api_async as AvhAPIAsync
from pprint import pprint

url = sys.argv[1]

# Initialize global state variables
stage = 1
done = False
async def configureInstance():
  global done
  text = ''

  # Give the VM time to finish booting
  console = await ws.connect(url)

  async def handleText(text):
    global done, stage

    if stage == 1:
      # Log in
      match = re.match(r'(?:(raspberrypi login:)|(Password:)|.*(pi\@raspberrypi:~\$))', text) 
      if (match):
        pprint(match)
        if match[1]:
          await console.send('pi\n')
        elif match[2]:
          await console.send('raspberry\n')
        elif match[3]:
          print('== Logged in ==')
          # Hit enter to let the network code continue
          await console.send('\n')
          stage += 1
        return True
    elif stage == 2:
      # Set light up to receive pairing
      match = re.match(r'(?:.*(pi\@raspberrypi:~\$))', text)         #On/Off set value: 1 0
      if (match):
        if (match[1]):
          await asyncio.sleep(1)
          await console.send('./chip-lighting-app\n')
          stage += 1
    else:
        done = True
    return False
  try:
    async for message in console:

      data = message.decode('UTF-8', errors='ignore')
      text += data

      while '\n' in text:
        offset = text.find('\n')
        line, text = text[:offset], text[offset+1:]
        print('%s' % line)
        await handleText(line)
      
      if await handleText(text):
        # Clear partial lines that were matched
        print('%s' % text, end='')
        text = ''
      
      if done:
        break

  finally:
    console.close_timeout = 1
    await console.close()

exitStatus = 0

async def main():
  global exitStatus
  global api_instance

  await configureInstance()

asyncio.run(main())
exit(0)