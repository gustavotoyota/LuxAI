import compress_pickle




def save_lz4_pickle(obj, file_path):
  compress_pickle.dump(obj, file_path, compression='lz4')

def load_lz4_pickle(file_path):
  return compress_pickle.load(file_path, compression='lz4')