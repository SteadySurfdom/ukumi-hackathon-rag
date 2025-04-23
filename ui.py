import streamlit as st
import pandas as pd
from colorama import Fore
from streamlit_echarts import st_echarts
import sys
# sys.path.append('C:\\Users\\gupta\\OneDrive\\Desktop\\Hackathon\\ukumi-hackathon\\')
from product_descriptor.processing.post_processing.extract import get_results
from product_descriptor.run import run
from product_descriptor.rag.chatbot import ask_question
from product_descriptor.processing.product_comparision.compare import generate_report
from colorama import Fore
import os

os.environ["OPENAI_API_KEY"] = st.secrets["openai"]
os.environ["deepgram_api_key"] = st.secrets["deepgram"]


def parserpros(obj):
    pros = obj.Pros
    returnable = []
    for pro in pros:
        # print(pro)
        returnable.append({'text':pro.FeatureName,'count':len(pro.VideoTimestamp),'videos':pro.VideoTimestamp,'summary':pro.ProsSummary})
    return returnable
# print(parser(pros_info))

def parsercons(obj):
    cons = obj.Cons
    returnable = []
    for con in cons:
        # print(pro)
        returnable.append({'text':con.FeatureName,'count':len(con.VideoTimestamp),'videos':con.VideoTimestamp,'summary':con.ConsSummary})
    return returnable
# print(parsercons(cons_info))

def parserspecs(obj):
    specs = obj.Specifications
    returnable = {}
    for spec in specs:
        returnable[spec.name] = spec.value
    return returnable
# print(parsespecs(specs_info))

def parseropinion(obj):
    returnable = []
    for review in obj:
        returnable.append(review.review)
    return returnable
# print(parseopinion(all_opinion))

def parsercomparison(obj):
    points = obj.rows
    returnable = []
    score = {}
    for point in points:
        returnable.append({'heading':point.heading,'left_spec':point.sidea,'right_spec':point.sideb})
    score['scorea'] = obj.score.scorea
    score['scoreb'] = obj.score.scoreb
    score['reasona'] = obj.score.reasona
    score['reasonb'] = obj.score.reasonb
    return returnable, score

def get_all_info(product_name):
    filenames,channels = run(product_name)
    pros_info, cons_info, specs_info, all_opinion = get_results(filenames)
    pros = parserpros(pros_info)
    cons = parsercons(cons_info)
    specs = parserspecs(specs_info)
    opinion = parseropinion(all_opinion)
    return pros,cons,specs,opinion,filenames,channels

def convert_to_seconds(timestamp: str):
  if ':' in timestamp:
    parts = timestamp.split(':')
    parts = list(filter(None, parts))
    if len(parts) == 2:
      return int(parts[0])*60 + int(parts[1])
    else:
      return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
  elif '.' in timestamp:
    parts = timestamp.split('.')
    for i in range(1,len(parts)):
        if len(parts[i]) == 1:
            parts[i] += '0'
    parts = list(filter(None, parts))
    if len(parts) == 2:
      # return int(parts[0])*60 + int(parts[1])
      return int(parts[0])
    else:
      print(parts)
      return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
  else:
      return int(timestamp)

def format_timestamps(timestamp):
    s,ms = timestamp.split('.')
    m,s = int(s)//60,int(s)%60
    if len(str(m)) == 1:
        m = f'0{m}'
    else:
        m = str(m)
    if len(str(s)) == 1:
        s = f'0{s}'
    else:
        s = str(s)
    return f'{m}:{s}'
    
    
@st.cache_data
def cached_get_all_info(product_name):
    return get_all_info(product_name)

def make_report(prod):
    pros,cons,specs,opinions,_,_ = get_all_info(prod)
    returnable = "Pros:\n"
    for pro in pros:
        returnable += f' - {pro["text"]}\n'
    returnable += "\nCons:\n"
    for con in cons:
        returnable += f' - {con["text"]}\n'
    returnable += "\nSpecifications:\n"
    for key,value in specs.items():
        returnable += f' - {key}: {value}\n'
    returnable += '\nKey Insights:\n'
    for op in opinions:
        returnable += f' - {op}\n'
    return returnable

def get_youtube_timestamp_url(video_url, start_time):
    # Convert start_time from "MM:SS" format to seconds
    # minutes, seconds = map(int, start_time.split(':'))
    # total_seconds = minutes * 60 + seconds
    return f"{video_url}&t={start_time}"



def main():
        

    st.set_page_config(page_title="Tech Review Analyzer", layout="wide")
    
    # Custom CSS for background gradient (Dark Blue -> Black -> Dark Purple)
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #00005b, #000000, #4b0041);
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Sidebar
    # st.sidebar.title("Navigation")
    # page = st.sidebar.radio("Go to", ["Product Analysis", "Product Comparison"])
    
    # Sidebar
# Sidebar
    with st.sidebar:
        st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            min-width: 250px;
            max-width: 250px;
        }
        .sidebar .sidebar-content {
            background-color: #1e1e1e;
            color: white;
        }
        .sidebar .sidebar-content .block-container {
            padding-top: 0;
        }
        .sidebar .sidebar-content .stButton > button {
            width: 100%;
            background-color: #2c2c2c;
            color: white;
            border: none;
            padding: 15px 10px;
            text-align: left;
            margin-bottom: 10px;
            font-size: 16px;
            line-height: 1.2;
        }
        .sidebar .sidebar-content .stButton > button:hover {
            background-color: #3a3a3a;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3 style='font-size: 20px; margin-bottom: 20px; font-family: Arial;'>NAVIGATION</h3>", unsafe_allow_html=True)        

        if st.button("Product Analyzer", key="analyzer_btn"):
            st.session_state.page = "analyzer"
        
        if st.button("Product Comparison", key="comparison_btn"):
            st.session_state.page = "comparison"
    
    # if page == "Product Analysis":
    #     product_analysis_page()
    # else:
    #     product_comparison_page()
    if 'page' not in st.session_state:
        st.session_state.page = "analyzer"
        
    if st.session_state.page == "analyzer":
        product_analysis_page()
    else:
        product_comparison_page()

def product_analysis_page():
    st.title("RECAP: Review Extraction and Consolidated Analysis Platform")
    
    # User input
    product = st.text_input("Enter the product name (e.g., 's22 ultra samsung phone'):")
    
    if product:
        
        # Dummy data for demonstration
        # pros = [
        #     {"text": "Excellent camera quality", "count": 4, "videos": ["Video 1", "Video 2", "Video 3", "Video 4"]},
        #     {"text": "Long battery life", "count": 3, "videos": ["Video 1", "Video 3", "Video 5"]},
        #     {"text": "Sleek design", "count": 5, "videos": ["Video 1", "Video 2", "Video 3", "Video 4", "Video 5"]}
        # ]
        
        # cons = [
        #     {"text": "Expensive", "count": 4, "videos": ["Video 1", "Video 2", "Video 4", "Video 5"]},
        #     {"text": "Limited storage options", "count": 2, "videos": ["Video 2", "Video 3"]}
        # ]
        
        # specs = {
        #     "Display": "6.8-inch Dynamic AMOLED 2X",
        #     "Processor": "Exynos 2200",
        #     "RAM": "8GB/12GB",
        #     "Storage": "128GB/256GB/512GB",
        #     "Battery": "5000mAh"
        # }
        
        # opinions = [
        #     "Overall, reviewers praised the camera system and build quality.",
        #     "Many found the price to be high but justified for the features offered.",
        #     "Battery life received mixed reviews, with some praising it and others finding it average."
        # ]
        pros,cons,specs,opinions,filenames,channels=cached_get_all_info(product)
        # print(Fore.GREEN + f'{channels}')
        st.header(f"Analysis Results for: {product}")
        
        # Display pros and cons
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Pros")
            for pro in pros:
                with st.expander(f"{pro['text']} ({pro['count']} out of 5 videos mention this)"):
                    st.write(f'{pro["summary"]}')
                    for video in pro['videos']:
                        print(Fore.RED + f'The channels dict is: {channels}\n\n\nThe key used is: {video.VideoSource}' + Fore.WHITE)
                        st.markdown(f"{channels[video.VideoSource]} - [Go to Video]({get_youtube_timestamp_url(video.VideoSource,convert_to_seconds(video.StartTimeStamp))})",unsafe_allow_html=True)
        
        with col2:
            st.subheader("Cons")
            for con in cons:
                with st.expander(f"{con['text']} ({con['count']} out of 5 videos mention this)"):
                    st.write(f'{con["summary"]}')
                    for video in con['videos']:
                        st.markdown(f"{channels[video.VideoSource]} - [Go to Video]({get_youtube_timestamp_url(video.VideoSource,convert_to_seconds(video.StartTimeStamp))})",unsafe_allow_html=True)
        
        # Display specifications
        st.subheader("Specifications")
        specs_df = pd.DataFrame.from_dict(specs, orient='index', columns=['Value'])
        st.table(specs_df)
        
        # Display reviewer opinions
        st.subheader("Reviewer Opinions")
        for opinion in opinions:
            st.write("• " + opinion)
        
        # Visualization: Pros and Cons comparison
        st.subheader("Pros vs Cons Comparison")
        pros_cons_data = [
            {"value": len(pros), "name": "Pros"},
            {"value": len(cons), "name": "Cons"}
        ]
        options = {
            "tooltip": {"trigger": "item"}, 
            "legend": {"top": "5%", "left": "center", 'textStyle': {'color':'white'}},
            "series": [
                {
                    "name": "Pros vs Cons",
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "avoidLabelOverlap": False,
                    "itemStyle": {
                        "borderRadius": 10,
                        "borderColor": "#fff",
                        "borderWidth": 2
                    },
                    "label": {"show": False},
                    "emphasis": {
                        'scale': False
                    },
                    "labelLine": {"show": False},
                    "data": pros_cons_data
                }
            ]
        }
        st_echarts(options=options, height="400px")

        st.subheader("Still have a question? Ask away.")
        user_question = st.text_input("Enter your question here:")
        if user_question:
            # Placeholder for response
            response = ask_question(user_question,[ids.split('.')[0] for ids in filenames])
            st.write(response)
            # You can replace this with actual backend processing later
            # response = process_question(user_question, product)
            # st.write(response)
                    
def product_comparison_page():
    st.markdown("<h2 style='font-size: 37px;'>Product Comparison</h2>",unsafe_allow_html=True)
    
    # User input for two products
    product1 = st.text_input("Enter the first product name:",)
    product2 = st.text_input("Enter the second product name:")
    
    if product1 and product2:
        
        # Dummy data for demonstration
        # comparison_data = [
        #     {"heading": "Display", "left_spec": "6.8-inch Dynamic AMOLED 2X", "right_spec": "6.7-inch Super Retina XDR OLED"},
        #     {"heading": "Processor", "left_spec": "Exynos 2200", "right_spec": "A15 Bionic"},
        #     {"heading": "RAM", "left_spec": "8GB/12GB", "right_spec": "6GB"},
        #     {"heading": "Storage", "left_spec": "128GB/256GB/512GB", "right_spec": "128GB/256GB/512GB/1TB"},
        #     {"heading": "Battery", "left_spec": "5000mAh", "right_spec": "4352mAh"},
        #     {"heading": "Main Camera", "left_spec": "108 MP, f/1.8, 24mm", "right_spec": "12 MP, f/1.5, 26mm"},
        #     {"heading": "Price", "left_spec": "$1199", "right_spec": "$1099"}
        # ]
        # score_data = {
        #     'scorea': 10,
        #     'scoreb': 9,
        #     'reasona': "reason is that you ...",
        #     'reasonb': 'my name is moulik'
        # }
        
        report1 = make_report(product1)
        report2 = make_report(product2)
        comparison_report = generate_report(report1,report2)
        comparison_data,score_data = parsercomparison(comparison_report)
        st.markdown(f"<h2 style='font-size: 32px;'>Comparison: {product1} vs {product2}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='font-size: 30px;'>RECAP RATING</h2>", unsafe_allow_html=True)
        col1,col2 = st.columns(2)
        with col1:
            st.write(f"<p style='font-size: 22px;'>{product1}: {score_data['scorea']}/10</p>", unsafe_allow_html=True)
            st.write(f"<p style='font-size: 22px;'>{score_data['reasona']}</p>", unsafe_allow_html=True)
        with col2:
            st.write(f"<p style='font-size: 22px;'>{product2}: {score_data['scoreb']}/10</p>", unsafe_allow_html=True)
            st.write(f"<p style='font-size: 22px;'>{score_data['reasonb']}</p>", unsafe_allow_html=True)
        st.markdown("---")  # Horizontal line for separation

        for item in comparison_data:
            st.markdown(f"<h2 style='font-size: 30px;'>{item['heading']}</h2>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"<p style='font-size: 22px;'>{product1}: {item['left_spec']}</p>", unsafe_allow_html=True)
            with col2:
                st.write(f"<p style='font-size: 22px; '>{product2}: {item['right_spec']}</p>", unsafe_allow_html=True)
            st.markdown("---")  # Horizontal line for separation
            
if __name__ == "__main__":
    main()