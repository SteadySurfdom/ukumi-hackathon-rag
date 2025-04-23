import pathlib
import os
import product_descriptor

PACKAGE_ROOT = pathlib.Path(product_descriptor.__file__).resolve().parent

DATA_PATH = os.path.join(PACKAGE_ROOT,"user_data")
AUDIO_DATA_PATH = os.path.join(DATA_PATH,"audio")
XML_DATA_PATH = os.path.join(DATA_PATH,"xml")
# MODEL_PATH = os.path.join(PACKAGE_ROOT,"models")

TARGET_LANG = "en"
MAX_K = 5             #max videos to process
MAX_LIMIT = 20        #max videos to fetch from youtube to check relivency 
REL_THRESH = 0.75     #threshold to consider relivent video

