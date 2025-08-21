from PIL import Image
import tflite_runtime.interpreter as tflite
import io
import numpy as np

# Load TFLite model
interpreter = tflite.Interpreter(model_path="model_int8.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

class_labels = ['drawings',
                'hentai',
                'neutral',
                'porn',
                'sexy']

def preprocess(image_bytes):
    # Open the image directly from bytes
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))

    # Convert the image into a numpy-like array structure for TFLite
    img_array = np.array(img, dtype=np.uint8)
    
    # Add batch dimension: shape becomes [1, 224, 224, 3]
    batch_data = np.expand_dims(img_array, axis=0)
    
    # Clean up image object after processing
    del img

    return batch_data

def is_nsfw(image_bytes, threshold=0.5):
    """
    Check if image is NSFW based on threshold
    
    Args:
        image_path: Path to the image file
        threshold: Minimum probability to consider NSFW (default: 0.5 = 50%)
    
    Returns:
        dict: {
            'is_nsfw': bool,
            'confidence': float,
            'category': str,
            'all_probabilities': dict
        }
    """
    batch_data = preprocess(image_bytes)
    
    interpreter.set_tensor(input_details[0]['index'], batch_data)
    interpreter.invoke()
    pred = interpreter.get_tensor(output_details[0]['index'])[0]
    
    # Apply softmax to get proper probabilities
    import math
    exp_values = [math.exp(x/100.0) for x in pred]  # Scale down for numerical stability
    sum_exp = sum(exp_values)
    probs = {label: exp_val/sum_exp for label, exp_val in zip(class_labels, exp_values)}
    
    
    # Define NSFW categories
    nsfw_categories = ['porn', 'hentai', 'sexy']
    safe_categories = ['neutral', 'drawings']
    
    # Calculate total NSFW probability
    nsfw_prob = sum(probs[cat] for cat in nsfw_categories)
    
    # Find the highest probability category
    top_category = max(probs, key=probs.get)
    top_confidence = probs[top_category]
    
    return {
        'is_nsfw': nsfw_prob >= threshold,
        'nsfw_confidence': nsfw_prob,
        'top_category': top_category,
        'top_confidence': top_confidence,
        'all_probabilities': probs
    }
