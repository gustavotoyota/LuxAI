import pickle
import gzip
import compress_pickle




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




def save_lz4_pickle(obj, file_path):
  compress_pickle.dump(obj, file_path, compression='lz4')

def load_lz4_pickle(file_path):
  return compress_pickle.load(file_path, compression='lz4')