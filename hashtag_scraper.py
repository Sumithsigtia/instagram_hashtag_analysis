import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_hashtag(hashtag, days=30):
    url = f"https://www.instagram.com/explore/tags/{hashtag}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find script tag containing JSON data
    script_tag = soup.find('script', text=lambda t: t and 'window._sharedData' in t).string
    start = script_tag.find('{')
    end = script_tag.rfind('}') + 1
    json_data = script_tag[start:end]
    
    import json
    data = json.loads(json_data)
    
    posts_data = data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']
    
    data = []
    for post in posts_data:
        node = post['node']
        date = datetime.fromtimestamp(node['taken_at_timestamp'])
        likes = node['edge_liked_by']['count']
        comments = node['edge_media_to_comment']['count']
        
        data.append({
            'date': date,
            'likes': likes,
            'comments': comments,
            'url': f"https://www.instagram.com/p/{node['shortcode']}/",
        })
    
    df = pd.DataFrame(data)
    return df
