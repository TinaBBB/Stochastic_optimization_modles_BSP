import pickle
import json

def pickle_load(file_dir):
  with open(file_dir, "rb") as fp:   # Unpickling
    return pickle.load(fp)

def json_load(file_dir):
    with open(file_dir) as f:
        return json.load(f)

def pickle_dump(file_to_dump, file_dir):
    with open(file_dir, "wb") as fp:  # Pickling
        pickle.dump(file_to_dump, fp)

def json_dump(file_to_dump, file_dir):
    with open(file_dir, 'w') as fp:
        json.dump(file_to_dump, fp)
