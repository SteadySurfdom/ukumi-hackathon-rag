from product_descriptor.config import config
from pytubefix import YouTube
import os
import concurrent

def download_audio(url:str,id:str):
    print(url)
    yt = YouTube(url)
    yt.streams.filter(only_audio=True).first().download(output_path=config.AUDIO_DATA_PATH,filename = f"{id}.mp3")
    return True

def download_async(url:list,id:list):
    with concurrent.futures.ThreadPoolExecutor(max_workers = 5) as executer:
        results = list(executer.map(download_audio,url,id))
    return results

def delete_audio(id):
    if(type(id) == str):
        id = [id]
    for i in id:
        os.remove(os.path.join(config.AUDIO_DATA_PATH,f"{i}.mp3"))