import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from hashtag_scraper import scrape_hashtag

# Streamlit app
st.title("Instagram Hashtag Popularity Analysis")

# Input for hashtag
hashtag = st.text_input("Enter a hashtag (without #):", value="your_hashtag")
days = st.slider("Number of days to analyze:", 7, 90, 30)

# Button to scrape data
if st.button("Analyze"):
    with st.spinner("Scraping Instagram data..."):
        df = scrape_hashtag(hashtag, days)
        st.success("Data scraped successfully!")

    # Load and analyze data
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Daily statistics
    daily_posts = df.resample('D').size()
    daily_engagement = df.resample('D').mean()[['likes', 'comments']]

    # Plot results
    st.subheader(f"Trend Analysis for #{hashtag}")

    fig, ax1 = plt.subplots(figsize=(10, 6))

    sns.lineplot(data=daily_posts, ax=ax1, label='Daily Posts', color='blue')
    ax2 = ax1.twinx()
    sns.lineplot(data=daily_engagement['likes'], ax=ax2, label='Average Likes', color='green')
    sns.lineplot(data=daily_engagement['comments'], ax=ax2, label='Average Comments', color='red')

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Number of Posts', color='blue')
    ax2.set_ylabel('Engagement', color='green')

    fig.tight_layout()
    st.pyplot(fig)

    # Display raw data
    st.subheader("Raw Data")
    st.write(df)

    # Option to download data
    st.download_button("Download Data as CSV", df.to_csv(), file_name=f"{hashtag}_data.csv")
