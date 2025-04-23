from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from product_descriptor.processing.static.prompts import report_generation_prompt, system_prompt, system_prompt_cons, system_prompt_pros, system_prompt_specs
from product_descriptor.config import config
import os
import pathlib
import json
from colorama import Fore
import streamlit as st

load_dotenv()
client = OpenAI(api_key=st.secrets['openai'])

class Specification(BaseModel):
    PropertyName: str
    Value: str
    StartTimestamp: str
    EndTimeStamp: str

class Point(BaseModel):
    Point: str
    StartTimestamp: str
    EndTimeStamp: str

class ProductInformation(BaseModel):
    Pros: list[Point]
    Cons: list[Point]
    Specifications: list[Specification]
    KeyInsights: list[Point]
    ReviewerOpinion: str

# classes for pros
class Citation(BaseModel):
    VideoSource: str
    StartTimeStamp: str
    EndTimeStamp: str

class ProsInformation(BaseModel):
    FeatureName: str
    ProsSummary: str
    VideoTimestamp: list[Citation]

class AllPros(BaseModel):
    Pros: list[ProsInformation]

# classes for cons
class ConsInformation(BaseModel):
    FeatureName: str
    ConsSummary: str
    VideoTimestamp: list[Citation]

class AllCons(BaseModel):
    Cons: list[ConsInformation]

# classes for Specification
class Specs(BaseModel):
    name: str
    value: str

class ProductSpecifications(BaseModel):
    Specifications: list[Specs]


# call llm
def call(system_prompt, user_prompt, response_format):
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format=response_format,
    )
    info = completion.choices[0].message.parsed
    return info

# extract_info
def extract_transcript(filename):
    filepath = pathlib.Path(__file__).parent.parent.parent.as_posix() + "/user_data/xml/" + filename
    transcript = ""

    with open(filepath) as f:
        paragraphs = json.load(f)["transcription"]["paragraphs"]["paragraphs"]
        for paragraph in paragraphs:
            transcript += f"Timestamp: {paragraph['start']} - {paragraph['end']}\n"+ "".join(sentence["text"] + "\n" for sentence in paragraph["sentences"]) +"\n"

    return transcript

def get_product_info(transcript):
    product_info = call(system_prompt, transcript, ProductInformation)
    return product_info

def get_pros_info(all_pros):
    pros_info = call(system_prompt, all_pros, AllPros)
    return pros_info

def get_cons_info(all_cons):
    cons_info = call(system_prompt, all_cons, AllCons)
    return cons_info

def get_specs_info(all_specs):
    specs_info = call(system_prompt, all_specs, ProductSpecifications)
    return specs_info

#  format the outputs
def format_timestamp(video_num, start_time, end_time):
    return f"Video {video_num} - [{start_time} to {end_time}]"

def expand_pros_info(all_pros: AllPros):
    expanded_info = []
    for pros_info in all_pros.Pros:
        # Count the number of videos mentioning this feature
        num_videos = len(pros_info.VideoTimestamp)
        info = f"{pros_info.FeatureName} ({num_videos} {'video mentions' if num_videos > 1 else 'video mentions this'})\n"
        
        # Add timestamps for each video
        for citation in pros_info.VideoTimestamp:
            info += format_timestamp(citation.VideoNum, citation.StartTimeStamp, citation.EndTimeStamp) + "\n"
        
        expanded_info.append(info)
    
    return "\n".join(expanded_info)


def expand_prod_info(product_info: ProductInformation) -> str:
    pros_text = "Pros:\n" + "\n".join([f"- {point.Point} (Timestamp: {point.StartTimestamp} - {point.EndTimeStamp})" for point in product_info.Pros]) + "\n"
    cons_text = "Cons:\n" + "\n".join([f"- {point.Point} (Timestamp: {point.StartTimestamp} - {point.EndTimeStamp})" for point in product_info.Cons]) + "\n"
    specifications_text = "Specifications:\n" + "\n".join([
        f"{spec.PropertyName}: {spec.Value} (Timestamp: {spec.StartTimestamp} - {spec.EndTimeStamp})" for spec in product_info.Specifications
    ]) + "\n"
    key_insights_text = "Key Insights:\n" + "\n".join([f"- {point.Point} (Timestamp: {point.StartTimestamp} - {point.EndTimeStamp})" for point in product_info.KeyInsights]) + "\n"
    reviewer_opinion_text = f"Reviewer Opinion:\n{product_info.ReviewerOpinion}\n"
    expanded_text = f"{pros_text}\n{cons_text}\n{specifications_text}\n{key_insights_text}\n{reviewer_opinion_text}"

    return expanded_text


class Reviews(BaseModel):
    url: str
    review: str

def get_results(filenames):
    all_product_info = []
    all_pros = []
    all_cons = []
    all_specs = []
    all_opinion = []
    
    for i, filename in enumerate(filenames):
        transcript = extract_transcript(filename)
        product_info = get_product_info(transcript)
        url = f"https://www.youtube.com/watch?v={filename.split('.')[0]}"
        all_opinion.append(Reviews(url=url, review=product_info.ReviewerOpinion))
        format_product_info = expand_prod_info(product_info)
        pros_text = f"Source: {url}\n" + "Pros:\n" + "\n".join([f"- {point.Point} (Timestamp: {point.StartTimestamp} - {point.EndTimeStamp})" for point in product_info.Pros]) + "\n"
        cons_text = f"Source: {url}\n" + "\n".join([f"- {point.Point} (Timestamp: {point.StartTimestamp} - {point.EndTimeStamp})" for point in product_info.Cons]) + "\n"
        specifications_text = f"Video {i}\n" + "Specifications:\n" + "\n".join([
                f"{spec.PropertyName}: {spec.Value}" for spec in product_info.Specifications
            ]) + "\n"
    
        all_pros.append(pros_text)
        all_cons.append(cons_text)
        all_specs.append(specifications_text)
        all_product_info.append(format_product_info)

    pros_info = get_pros_info(("-"*80).join(all_pros))
    cons_info = get_cons_info(("-"*80).join(all_cons))
    specs_info = get_specs_info(("-"*80).join(all_specs))
    return pros_info, cons_info, specs_info, all_opinion


    
