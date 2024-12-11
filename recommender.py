import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import process, fuzz  # Import rapidfuzz and its components

class MovieRecommender:
    def __init__(self, movies_path='./data/movies.csv', links_path='./data/links.csv', ratings_path='./data/ratings.csv', tags_path='./data/tags.csv'):
        # Load datasets
        self.movies = pd.read_csv(movies_path)
        self.links = pd.read_csv(links_path)
        self.ratings = pd.read_csv(ratings_path)
        self.tags = pd.read_csv(tags_path)

        # Preprocess genres
        self.movies['genres'] = self.movies['genres'].apply(lambda x: x.replace('|', ' '))
        self.vectorizer = CountVectorizer()
        self.similarity_matrix = None

    def train(self):
        # Combine genres and tags for feature engineering
        self.movies = self.movies.merge(
            self.tags.groupby('movieId')['tag'].apply(lambda x: ' '.join(x)).reset_index(),
            on='movieId', how='left'
        )
        self.movies['combined_features'] = self.movies[['genres', 'tag']].fillna('').agg(' '.join, axis=1)

        # Vectorize combined features
        feature_matrix = self.vectorizer.fit_transform(self.movies['combined_features'])
        self.similarity_matrix = cosine_similarity(feature_matrix)
        print("Model trained on genres and tags!")

    def find_closest_match(self, movie_title):
        # Use rapidfuzz to find closest matching titles
        titles = self.movies['title'].tolist()
        closest_matches = process.extract(movie_title, titles, limit=5, scorer=fuzz.token_sort_ratio)
        return [match[0] for match in closest_matches]

    def recommend(self, movie_title, top_n=5):
        try:
            # Find the movie index
            movie_idx = self.movies[self.movies['title'].str.contains(movie_title, case=False, na=False, regex=False)].index[0]
        except IndexError:
            # If movie not found, suggest closest matches
            closest_matches = self.find_closest_match(movie_title)
            return [f"Did you mean: {', '.join(closest_matches)}?"]

        # Calculate similarity scores
        sim_scores = list(enumerate(self.similarity_matrix[movie_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get top N recommendations
        recommended_indices = [i[0] for i in sim_scores[1:top_n+1]]
        recommendations = self.movies.iloc[recommended_indices][['title', 'movieId']]

        # Include IMDb links in recommendations
        recommendations = recommendations.merge(self.links, on='movieId', how='left')
        recommendations['imdb_url'] = recommendations['imdbId'].apply(lambda x: f"https://www.imdb.com/title/tt{int(x):07d}/")

        return recommendations[['title', 'imdb_url']].to_dict('records')
