from PIL import Image
import tflite_runtime.interpreter as tflite
import io
import numpy as np
import time
import math
import threading
import os
from dotenv import load_dotenv

load_dotenv()

class_labels = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']

_interpreter = None
_interpreter_lock = threading.Lock()

def get_interpreter():
    """Get a singleton interpreter instance."""
    global _interpreter
    if _interpreter is None:
        _interpreter = tflite.Interpreter(model_path="model_int8.tflite")
        _interpreter.allocate_tensors()
    return _interpreter

def preprocess(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
    img_array = np.array(img, dtype=np.uint8)
    batch_data = np.expand_dims(img_array, axis=0)
    
    img.close()
    del img_array
    
    return batch_data

def is_nsfw(image_bytes, threshold=0.5):
    if bool(os.getenv("DEBUG", False)):
        print("Processing image...")
        time.sleep(10)
        print("Done sleep...")

    with _interpreter_lock:
        interpreter = get_interpreter()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        batch_data = preprocess(image_bytes)
        
        try:
            interpreter.set_tensor(input_details[0]['index'], batch_data)
            interpreter.invoke()
            
            raw_output = interpreter.get_tensor(output_details[0]['index'])
            pred_list = [float(x) for x in raw_output[0]]
            
        finally:
            del batch_data

    exp_values = [math.exp(x/100.0) for x in pred_list]
    sum_exp = sum(exp_values)
    probs = {label: exp_val/sum_exp for label, exp_val in zip(class_labels, exp_values)}
    
    nsfw_categories = ['porn', 'hentai', 'sexy']
    nsfw_prob = sum(probs[cat] for cat in nsfw_categories)
    top_category = max(probs, key=probs.get)
    top_confidence = probs[top_category]
    
    return {
        'is_nsfw': nsfw_prob >= threshold,
        'nsfw_confidence': nsfw_prob,
        'top_category': top_category,
        'top_confidence': top_confidence,
        'all_probabilities': probs
    }
