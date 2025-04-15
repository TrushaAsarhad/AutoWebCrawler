import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import networkx as nx
import matplotlib.pyplot as plt


# Helper to check if a link belongs to the same domain
def is_valid(url, domain):
    parsed = urlparse(url)
    return parsed.netloc == domain or parsed.netloc == ""


# Crawler function
def crawl(seed_url, max_pages=10):
    visited = set()
    queue = deque([seed_url])
    domain = urlparse(seed_url).netloc
    structure = {}

    while queue and len(visited) < max_pages:
        current_url = queue.popleft()
        if current_url in visited:
            continue
        try:
            response = requests.get(current_url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = set()

            for a in soup.find_all('a', href=True):
                href = urljoin(current_url, a['href'])
                if is_valid(href, domain):
                    links.add(href)
                    if href not in visited and href not in queue:
                        queue.append(href)

            structure[current_url] = list(links)
            visited.add(current_url)

        except Exception as e:
            structure[current_url] = [f"Error: {e}"]

    return structure


# Visualization function with labeled nodes
def visualize_graph(structure):
    G = nx.DiGraph()
    label_map = {}

    for page, links in structure.items():
        for link in links:
            G.add_edge(page, link)

    for node in G.nodes():
        parsed = urlparse(node)
        label = parsed.netloc + parsed.path
        if len(label) > 30:
            label = label[:27] + "..."
        label_map[node] = label

    pos = nx.spring_layout(G, k=0.5, seed=42)
    fig, ax = plt.subplots(figsize=(12, 8))

    nx.draw(
        G, pos, ax=ax, labels=label_map,
        node_size=500, font_size=8, arrows=True,
        node_color="skyblue", edge_color="gray",
        with_labels=True
    )
    ax.set_title("Web Structure Graph", fontsize=14)
    return fig


# Streamlit App UI
st.set_page_config(page_title="Web Crawler with Structure Mining", layout="wide")
st.title("🕷️ Web Crawler + Structure Miner")
st.markdown("Built with **BeautifulSoup + Streamlit + NetworkX**")

# User input
seed_url = st.text_input("Enter Seed URL", "https://example.com")
max_pages = st.slider("Max Pages to Crawl", 1, 50, 10)

# Trigger crawl
if st.button("Start Crawling"):
    with st.spinner("Crawling in progress..."):
        structure = crawl(seed_url, max_pages)

    st.success(f"Crawled {len(structure)} pages!")

    st.subheader("🔗 Crawled Structure")
    for page, links in structure.items():
        st.markdown(f"**{page}**")
        for link in links:
            st.markdown(f"- {link}")

    st.subheader("📊 Web Structure Graph")
    fig = visualize_graph(structure)
    st.pyplot(fig)
