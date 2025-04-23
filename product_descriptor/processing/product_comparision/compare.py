from product_descriptor.processing.static.prompts import product_comparision_prompt
from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI
import streamlit as st
load_dotenv()
client = OpenAI(api_key=st.secrets['openai'])

class comparision(BaseModel):
    heading : str
    sidea : str
    sideb : str
    summary : str
    
class score(BaseModel):
    scorea: int
    scoreb: int
    reasona:str
    reasonb:str 

class table(BaseModel):
    rows : list[comparision]
    score : score
    
def generate_report(report1:str,report2:str):
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": product_comparision_prompt},
            {"role": "user", "content": f"PRODUCT 1 :\n{report1} \n\n\nPRODUCT 2 :\n{report2}"},
        ],
        response_format = table
    )
    return completion.choices[0].message.parsed