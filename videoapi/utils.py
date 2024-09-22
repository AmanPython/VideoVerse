import time
import hashlib

def generate_unique_filename(original_filename, video_id):
    timestamp = int(time.time())
    hash_input = f"{video_id}_{timestamp}_{original_filename}"
    hash_object = hashlib.md5(hash_input.encode())
    return f"{hash_object.hexdigest()}_{original_filename}"