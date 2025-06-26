import streamlit as st
import pickle
import pandas as pd
import requests
import time
import io

# --------- Load Data ---------
# Load movie dict (local)
with open("movie_dict.pkl", "rb") as f:
    movies = pickle.load(f)

movies = pd.DataFrame(movies)

# Load similarity matrix from Hugging Face (not Google Drive)
@st.cache_data
def load_similarity():
    URL = "https://huggingface.co/dpk-sethiii/movie-files/resolve/main/similarity.pkl"  # replace with your raw link
    response = requests.get(URL)
    return pickle.load(io.BytesIO(response.content))

similarity = load_similarity()

# --------- Fetch Poster ---------
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
            else:
                return "https://via.placeholder.com/500x750?text=No+Poster"

        except requests.exceptions.RequestException as e:
            print(f"[Attempt {attempt + 1}] Error fetching poster for movie ID {movie_id}: {e}")
            time.sleep(1)

    return "https://via.placeholder.com/500x750?text=Failed+to+Fetch"

# --------- Recommendation Logic ---------
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_titles = []
    recommended_posters = []

    for idx in movie_list:
        movie_id = movies.iloc[idx[0]].movie_id
        recommended_titles.append(movies.iloc[idx[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_titles, recommended_posters

# --------- Streamlit App Layout ---------
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox("Select a movie you like:", movies['title'].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
