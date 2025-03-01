import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import pytz

# RSS feed sources organized by category
RSS_FEEDS = {
    # Machine Learning
    "Cube Dev Blog": "https://blog.statsbot.co/feed",
    "Machine Learning Mastery": "https://machinelearningmastery.com/feed/",
    "AWS Machine Learning": "https://aws.amazon.com/blogs/machine-learning/feed/",
    "ML Reddit": "https://www.reddit.com/r/MachineLearning/.rss",
    "ML in Production": "https://mlinproduction.com/rss/",
    "Jay Alammar Blog": "http://jalammar.github.io/feed.xml",
    "JMLR Papers": "http://www.jmlr.org/jmlr.xml",
    "Distill Blog": "https://distill.pub/rss.xml",
    
    # Artificial Intelligence
    "매일경제 AI": "https://www.mk.co.kr/rss/50200011/",
    "AI Trends": "https://www.aitrends.com/feed/",
    "AI Weirdness": "https://aiweirdness.com/rss",
    "BAIR Blog": "https://bair.berkeley.edu/blog/feed.xml",
    "MIT AI News": "https://news.mit.edu/rss/topic/artificial-intelligence-ai",
    "NVIDIA AI Blog": "https://blogs.nvidia.com/feed/",
    "David Stutz AI": "https://davidstutz.de/feed/",
    "AI Reddit": "https://www.reddit.com/r/artificial/.rss",
    "Neural Networks Reddit": "https://www.reddit.com/r/neuralnetworks/.rss",
    "Science Daily AI": "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
    "Seita's Place": "https://danieltakeshi.github.io/feed.xml",
    "VitalAI Lab": "https://vitalab.github.io/feed.xml",
    "Andrej Karpathy": "https://medium.com/feed/@karpathy",
    "Microsoft Research": "https://www.microsoft.com/en-us/research/feed/",
    "Google AI": "https://blog.google/technology/ai/rss/",
    
    # Reinforcement Learning
    "RL Reddit": "https://www.reddit.com/r/reinforcementlearning/.rss",
    "RL Paper Review": "https://dtransposed.github.io/feed.xml",
    
    # Data Science
    "Data Science Central": "https://www.datasciencecentral.com/feed/",
    "John Cook Blog": "https://www.johndcook.com/blog/feed/"
}

# Category mappings
CATEGORY_MAPPING = {
    "Machine Learning": [
        "Cube Dev Blog", "Machine Learning Mastery", "ML Uber Engineering",
        "AWS Machine Learning", "arXiv ML", "arXiv Stats ML", "ML Reddit",
        "ML in Production", "Jay Alammar Blog", "JMLR Papers", "Distill Blog"
    ],
    "Artificial Intelligence": [
        "매일경제 AI", "AI Trends", "AI Weirdness", "BAIR Blog", "MIT AI News",
        "NVIDIA AI Blog", "David Stutz AI", "AI Reddit", "Neural Networks Reddit",
        "Science Daily AI", "Seita's Place", "VitalAI Lab", "Andrej Karpathy",
        "OpenAI Blog", "Microsoft Research", "Google AI", "Fast AI"
    ],
    "Reinforcement Learning": [
        "RL Reddit", "RL Weekly", "RL Paper Review"
    ],
    "Data Science": [
        "Data Science Central", "John Cook Blog"
    ]
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
        # Add category filter
        categories = ["All", "Machine Learning", "Artificial Intelligence", "Reinforcement Learning", "Data Science"]
        selected_category = st.radio("Filter by Category", categories)
        
        # Filter feeds by category
        if selected_category == "All":
            filtered_feeds = {**RSS_FEEDS, **st.session_state.custom_feeds}
        else:
            # You'll need to add category mapping logic here
            filtered_feeds = {k: v for k, v in RSS_FEEDS.items() if k in CATEGORY_MAPPING.get(selected_category, [])}
            filtered_feeds.update(st.session_state.custom_feeds)
        
        # Add feed selector with filtered feeds
        st.subheader("Select Feed")
        selected_feed = st.selectbox(
            "Choose a news source",
            list(filtered_feeds.keys())
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
    
    # Fetch articles from selected feed using filtered_feeds instead of all_feeds
    articles = fetch_rss_feed(filtered_feeds[selected_feed])
    
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
