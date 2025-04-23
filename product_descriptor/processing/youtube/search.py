import concurrent.futures
from youtubesearchpython import Video,VideosSearch
from product_descriptor.config import config
import concurrent
 
 
def search_videos(title : str):
    videosSearch = VideosSearch(title,limit = config.MAX_LIMIT)
    return videosSearch.result()["result"]

def get_video_info(url):
    data = Video.getInfo(url)
    return data

def get_video_keywords(data):
    keywords = data["keywords"]
    if(keywords == None):
        keywords = []
    final = data["title"].split(" ")
    for keyword in keywords:
        final.extend(keyword.split(" "))
    final = set([i.lower() for i in final])
    return final

def relivency_score(video_data : dict,title:str):
    title_split_arr = title.split(" ")
    title_split_arr= [i.lower() for i in title_split_arr]
    data = get_video_info(video_data["link"])
    video_keywords = get_video_keywords(data)
    count = 0
    for key in title_split_arr:
        if key in video_keywords:
            count+=1
    return count/len(title_split_arr),{"link":video_data["link"],"description":data["description"],"id":data["id"],"channel":data["channel"]["name"]}

def get_videos(title:str):
    data = search_videos(title = title)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executer:
        results = list(executer.map(relivency_score,data,[title for i in range(len(data))]))
    
    relivent_videos = []    
    for score,data in results:
        if(score >= config.REL_THRESH):
            relivent_videos.append(data)
        if(len(relivent_videos) >= config.MAX_K):
            break
    return relivent_videos
        
    
    
    
    