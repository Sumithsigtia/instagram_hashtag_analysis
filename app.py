import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import plotly.express as px
import re
import logging

logging.basicConfig(level=logging.INFO)

st.title("Instagram Hashtag Analysis")

def get_count(tag):
    try:
        url = f"https://www.instagram.com/explore/tags/{tag}/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        s = requests.get(url, headers=headers)
        soup = BeautifulSoup(s.content, 'html.parser')
        
        meta_tag = soup.find('meta', {'property': 'og:description'})
        if meta_tag and 'content' in meta_tag.attrs:
            content = meta_tag['content']
            match = re.search(r'([\d,.]+)([KMB]?)', content)
            if match:
                number = match.group(1).replace(",", "")
                suffix = match.group(2)
                if suffix == 'K':
                    count = int(float(number) * 1_000)
                elif suffix == 'M':
                    count = int(float(number) * 1_000_000)
                elif suffix == 'B':
                    count = int(float(number) * 1_000_000_000)
                else:
                    count = int(number)
                
                logging.info(f"Fetched count for #{tag}: {count}")
                return count
        
        logging.warning(f"Count not found for #{tag}")
        return None
    except Exception as e:
        logging.error(f"Error fetching data for tag '{tag}': {e}")
        return None

def get_best(tag, topn):
    try:
        url = f"https://best-hashtags.com/hashtag/{tag}/"
        s = requests.get(url)
        soup = BeautifulSoup(s.content, 'html.parser')
        
        tag_box = soup.find("div", {"class": "tag-box tag-box-v3 margin-bottom-40"})
        if tag_box:
            tags = tag_box.text.split()[:topn]
            return tags
        
        return []  # Return an empty list if no tags are found
    except Exception as e:
        logging.error(f"Error fetching best hashtags for '{tag}': {e}")
        return []

@st.cache_data
def load_data():
    # Try to load from session state if it exists
    if 'data' not in st.session_state:
        with open("database.json", "r") as f:
            st.session_state.data = json.load(f)
    return st.session_state.data

data = load_data()

num_tags = st.sidebar.number_input("Select number of tags", 1, 30)
tags = []
sizes = []
st.sidebar.header("Tags")
col1, col2 = st.sidebar.columns(2)

for i in range(num_tags):
    tag = col1.text_input(f"Tag {i}", key=f"tag_{i}")
    size = col2.number_input(f"Top-N {i}", 1, 10, key=f"size_{i}")
    tags.append(tag)
    sizes.append(size)

if st.sidebar.button("Create Hashtags"):
    tab_names = ["all"]
    tab_names = tab_names + [tags[i] for i in range(num_tags)]
    tag_tabs = st.tabs(tab_names)
    all_hashtags = []
    hashtag_data = []
    for i in range(num_tags):
        hashtags = get_best(tags[i], sizes[i])
        for hashtag in hashtags:
            if hashtag in data["hashtag_data"]:
                hashtag_count = data["hashtag_data"][hashtag]
            else:
                hashtag_count = get_count(hashtag.replace("#", ""))
                if hashtag_count is None:
                    hashtag_count = 0  # Default to 0 if count fetching fails
                data["hashtag_data"][hashtag] = hashtag_count
            hashtag_data.append((f"{hashtag}<br>{hashtag_count:,}", hashtag_count))
        
        tag_tabs[i+1].text_area(f"Tags for {tags[i]}", " ".join(hashtags))
        all_hashtags = all_hashtags + hashtags
    
    tag_tabs[0].text_area("All Hashtags", " ".join(all_hashtags))

    st.header("Hashtag Count Data")
    df = pd.DataFrame(hashtag_data, columns=["hashtag", "count"])
    df = df.sort_values("count")

    # Save back to session state instead of file
    st.session_state.data = data

    fig = px.bar(df, x='hashtag', y='count')
    st.plotly_chart(fig, use_container_width=True)
