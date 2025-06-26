import streamlit as st
import pickle
import pandas as pd
import requests
import time


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=2df6c26978584da17778ced554a54939&language=en-US"

    for attempt in range(3):  # Retry logic
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            poster_path = data.get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
            else:
                # Poster path missing — use placeholder
                return "https://via.placeholder.com/500x750?text=No+Poster"

        except requests.exceptions.RequestException as e:
            print(f"[Attempt {attempt + 1}] Error fetching poster for movie ID {movie_id}: {e}")
            time.sleep(1)

    # Fallback if all retries fail
    return "https://via.placeholder.com/500x750?text=Failed+to+Fetch"

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []
    recommended_movies_posters = []
    for idx in movies_list:
        movie_id = movies.iloc[idx[0]].movie_id
        recommended_movies.append(movies.iloc[idx[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies,recommended_movies_posters



movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))

movies = pd.DataFrame(movies_dict)

st.title("Movie Recommender System")

import streamlit as st

selected_movie_name = st.selectbox(
    "How would you like to be contacted?",
    movies['title'].values)
if st.button('Recommend'):
    names,posters = recommend(selected_movie_name)



    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0])

    with col2:
        st.text(names[1])
        st.image(posters[1])

    with col3:
        st.text(names[2])
        st.image(posters[2])

    with col4:
        st.text(names[3])
        st.image(posters[3])

    with col5:
        st.text(names[4])
        st.image(posters[4])
        

import streamlit as st
import pandas as pd
import pickle
import requests
import io

# Load movies dict (still local)
with open("movie_dict.pkl", "rb") as f:
    movies = pickle.load(f)

# Load similarity.pkl from Google Drive using raw download
@st.cache_data
def load_similarity():
    FILE_ID = "1-f24GkjPaZbGG7aC6vJcwm9bkR9Tifcp"  # Replace with your actual file ID
    URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
    response = requests.get(URL)
    return pickle.load(io.BytesIO(response.content))

similarity = load_similarity()



