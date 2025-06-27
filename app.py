import streamlit as st
import pickle
import pandas as pd
import requests
import time
import io
import numpy as np

# --------- Load Movie Data ---------
with open("movie_dict.pkl", "rb") as f:
    movies = pickle.load(f)

movies = pd.DataFrame(movies)

if 'movie_id' not in movies.columns:
    st.error("❌ 'movie_id' column is missing from movies dataset.")
    st.stop()

# --------- Load Similarity Matrix ---------
@st.cache_data
def load_similarity():
    URL = "https://huggingface.co/dpk-sethiii/movie-files/resolve/main/similarity.pkl"
    response = requests.get(URL)
    if response.status_code == 200:
        return pickle.load(io.BytesIO(response.content))
    else:
        st.error(f"❌ Failed to fetch similarity matrix. HTTP {response.status_code}")
        st.stop()

similarity = load_similarity()

# --------- Fetch Poster from TMDB ---------
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=2df6c26978584da17778ced554a54939&language=en-US"
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
        except requests.exceptions.RequestException as e:
            print(f"[Attempt {attempt + 1}] Poster fetch error: {e}")
            time.sleep(1)
    return "https://via.placeholder.com/500x750?text=No+Poster"

# --------- Recommend Movies ---------
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("❌ Movie not found in dataset.")
        return [], []

distances = np.array(similarity[movie_index])  # Ensure numeric indexing

movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

recommended_titles = []
recommended_posters = []

for idx, _ in movie_list:
    try:
        row = movies.iloc[idx]
        movie_id = row['movie_id']
        title = row['title']
    except (KeyError, IndexError):
        continue

    recommended_titles.append(title)
    recommended_posters.append(fetch_poster(movie_id))
    return recommended_titles, recommended_posters
    






# --------- Streamlit UI ---------
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox("Select a movie you like:", movies['title'].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)
    if names:
        cols = st.columns(len(names))
        for i in range(len(names)):
            with cols[i]:
                st.text(names[i])
                st.image(posters[i])
