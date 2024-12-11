import os
from kaggle.api.kaggle_api_extended import KaggleApi

# Set the KAGGLE_CONFIG_DIR to the current directory (where kaggle.json is located)
os.environ['KAGGLE_CONFIG_DIR'] = os.getcwd()

def download_movielens():
    # Authenticate using the Kaggle API
    api = KaggleApi()
    api.authenticate()
    
    # Dataset details
    dataset = 'grouplens/movielens-latest-small'
    dest = './data/'  # Destination folder
    
    # Download and extract
    api.dataset_download_files(dataset, path=dest, unzip=True)
    print("Dataset downloaded and extracted to ./data/")

if __name__ == "__main__":
    download_movielens()
