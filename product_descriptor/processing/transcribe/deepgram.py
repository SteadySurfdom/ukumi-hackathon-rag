import concurrent.futures
from product_descriptor.processing.youtube.download import delete_audio
from product_descriptor.config import config
from dotenv import load_dotenv
import concurrent
import os
load_dotenv()

from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)

load_dotenv()
API_KEY = os.getenv("deepgram_api_key")

def transcribe_audio(id:str):
    try:
        AUDIO_FILE = os.path.join(config.AUDIO_DATA_PATH,f"{id}.mp3")
        deepgram = DeepgramClient(API_KEY)
        with open(AUDIO_FILE, "rb") as file:
            buffer_data = file.read()
        payload: FileSource = {
            "buffer": buffer_data,
        }
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        data = response.results.channels[0].alternatives[0].to_dict()
    except Exception as e:
        print(f"Exception: {e}")
        data = {}
        
    # finally:
    try:
        delete_audio(id)
    except:
        pass
    return data

def transcribe_async(id:list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(transcribe_audio,id))
    return results