import pickle
import gzip




def save_pickle(obj, file_path):
  with open(file_path, 'wb') as file:
    return pickle.dump(obj, file)

def load_pickle(file_path):
  with open(file_path, 'rb') as file:
    return pickle.load(file)




def save_gzip_pickle(obj, file_path):
  with gzip.open(file_path, 'wb') as file:
    return pickle.dump(obj, file)

def load_gzip_pickle(file_path):
  with gzip.open(file_path, 'rb') as file:
    return pickle.load(file)