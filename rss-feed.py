import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import pytz

# RSS feed sources
RSS_FEEDS = {
    "매일경제 AI": "https://www.mk.co.kr/rss/50200011/",
    "Machine Learning Mastery": "https://machinelearningmastery.com/blog/feed/",
    "AI Business": "https://aibusiness.com/rss.xml",
    "AI News" : "https://www.artificialintelligence-news.com/feed/rss/",
    "AI Tech Park": "https://ai-techpark.com/category/ai/feed/",
    "AI Ahead": "https://magazine.sebastianraschka.com/feed",
    "AI Models": "https://aimodels.substack.com/feed",
}

def format_date(date_str):
    try:
        # Parse the date string to datetime object
        # Replace GMT with +0000 for proper timezone parsing
        date_str = date_str.replace('GMT', '+0000')
        date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        
        # Convert to KST (Korea Standard Time)
        kst = pytz.timezone('Asia/Seoul')
        date_obj = date_obj.astimezone(kst)
        
        # Format the date
        return date_obj.strftime('%Y-%m-%d %H:%M')
    except ValueError as e:
        # Fallback for any parsing errors
        st.warning(f"Date parsing error: {date_str}")
        return date_str

def fetch_rss_feed(feed_url):
    # Fetch RSS feed
    feed = feedparser.parse(feed_url)
    
    # Extract relevant information
    articles = []
    for entry in feed.entries:
        article = {
            'title': entry.title,
            'link': entry.link,
            'published': format_date(entry.published),
            'summary': entry.summary
        }
        articles.append(article)
    
    return articles

def main():
    st.title('Feed Aggregator')
    
    # Initialize session state for custom feeds if not exists
    if 'custom_feeds' not in st.session_state:
        st.session_state.custom_feeds = {}

    # Setup sidebar
    with st.sidebar:
        # Combine default and custom feeds
        all_feeds = {**RSS_FEEDS, **st.session_state.custom_feeds}
        
        # Add feed selector
        st.subheader("Select Feed")
        selected_feed = st.selectbox(
            "Choose a news source",
            list(all_feeds.keys())
        )
        
        # Add refresh button
        if st.button('🔄 Refresh Feed'):
            st.rerun()
        
        # Add remove feed button (only for custom feeds)
        if selected_feed in st.session_state.custom_feeds:
            if st.button('❌ Remove Feed'):
                del st.session_state.custom_feeds[selected_feed]
                st.rerun()
        
        # Add separator
        st.divider()
        
        # Add new feed section
        st.subheader("Add Custom Feed")
        new_feed_name = st.text_input("Feed Name")
        new_feed_url = st.text_input("Feed URL")
        
        if st.button("Add Feed"):
            if new_feed_name and new_feed_url:
                try:
                    test_feed = feedparser.parse(new_feed_url)
                    if test_feed.entries:
                        st.session_state.custom_feeds[new_feed_name] = new_feed_url
                        st.success(f"Added: {new_feed_name}")
                    else:
                        st.error("Invalid RSS feed URL")
                except:
                    st.error("Invalid URL")

    st.subheader(f'Latest articles from {selected_feed}')
    
    # Fetch articles from selected feed
    articles = fetch_rss_feed(all_feeds[selected_feed])
    
    # Convert to DataFrame and display articles
    df = pd.DataFrame(articles)
    
    for idx, row in df.iterrows():
        with st.container():
            st.subheader(row['title'])
            st.write(f"📅 Published: {row['published']}")
            st.write(row['summary'])
            st.markdown(f"[Read more]({row['link']})")
            st.divider()

if __name__ == '__main__':
    main()
