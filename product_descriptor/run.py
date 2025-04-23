from product_descriptor.processing.youtube.search import get_videos
from product_descriptor.processing.youtube.download import download_async
from product_descriptor.processing.transcribe.deepgram import transcribe_async
from product_descriptor.processing.post_processing.extract import get_results
from product_descriptor.config import config
from product_descriptor.rag.chatbot import create_chatbot
from dotenv import load_dotenv
import json
import os

load_dotenv()

def run(title:str):
    videos = get_videos(title)
    links = [i["link"] for i in videos]
    channel_names = {links[i]:videos[i]["channel"] for i in range(len(links))}
    ids = [i["id"] for i in videos]
    download_async(links,ids)
    transcriptions = transcribe_async(ids)
    filenames = []
    new_ids = []
    for i,video in enumerate(videos):
        if ((transcriptions[i] == {}) or (len(transcriptions[i]['transcript']) < 200)):
            continue
        new_ids.append(ids[i])
        videos[i]["transcription"] = transcriptions[i]
        path = f"{ids[i]}.json"
        filenames.append(path)
        with open(os.path.join(config.XML_DATA_PATH,path),"w") as f:
            json.dump(videos[i],f)
    create_chatbot(new_ids)
    return filenames, channel_names
        

