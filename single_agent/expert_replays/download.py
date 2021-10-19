import requests
import os


def download(replay_id):
  if os.path.isfile(f'{replay_id}.json'):
    return

  url = f'https://www.kaggleusercontent.com/episodes/{replay_id}.json'

  with open(f'{replay_id}.json', 'wb') as file:
    file.write(requests.get(url).content)



with open ("download.txt", "r") as file:
  for replay_id in file.readlines():
    download(replay_id.replace('\n', ''))