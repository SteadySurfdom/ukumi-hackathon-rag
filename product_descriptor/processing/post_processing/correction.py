from product_descriptor.processing.static.prompts import correction_prompt
from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI
import json
load_dotenv()

class output_format(BaseModel):
  corrected_transcript: str
  percentage_improved: int

def clean_transcript(transcript: str):
  '''
    Arguments:
      transcript: A dictionary that should contain 2 keys, named "words" and "transcript" where:
        "words": points to a list of dictionaries where each word has an associated confidence score.
        "transcript": points to a string that contains the entire transcript in human readable format.
      
    Returns:
      An object of the `output_format` class where the corrected_transcript contains the human readable corrected transcript and 
      percentage_improved contains integer value of by how much the model thinks it improved the transcript.
  '''
  words = transcript['words']
  low_conf_words = []
  for word in words:
      if word['confidence'] < 0.8:
          low_conf_words.append(word['word'])
  low_conf_words = list(set(low_conf_words))
  

  client = OpenAI()

  response = client.beta.chat.completions.parse(
    model="gpt-4o-mini-2024-07-18",
    messages=[
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": correction_prompt.format(transcript = transcript["transcript"],words=low_conf_words)},
    ],
    response_format=output_format
  )
  return response.choices[0].message.parsed

# Example Usage:
# dic = json.load(open('ukumi-hackathon\\product_descriptor\\user_data\\xml\\3mH46NdkO2A.json'))
# a = clean_transcript(dic['transcription'])