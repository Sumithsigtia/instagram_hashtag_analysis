import instaloader
from datetime import datetime, timedelta
import pandas as pd

def scrape_hashtag(hashtag, days=30):
    L = instaloader.Instaloader()

    # Define timeframe
    start_date = datetime.now() - timedelta(days=days)
    posts = instaloader.Hashtag.from_name(L.context, hashtag).get_posts()

    data = []
    for post in posts:
        if post.date_utc > start_date:
            data.append({
                'date': post.date_utc,
                'likes': post.likes,
                'comments': post.comments,
                'url': post.url,
            })
        else:
            break

    df = pd.DataFrame(data)
    df.to_csv(f'data/{hashtag}_data.csv', index=False)
    return df
