from detect import is_nsfw

def classify_with_verdict(image_path, nsfw_threshold=0.5):
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    result = is_nsfw(image_bytes, nsfw_threshold)

    print(f"Image: {image_path}")
    print(f"Verdict: {'🔞 NSFW' if result['is_nsfw'] else '✅ Safe'}")
    print(f"NSFW Confidence: {result['nsfw_confidence']:.1%}")
    print(f"Top Category: {result['top_category']} ({result['top_confidence']:.1%})")
    print("All probabilities:")
    for category, prob in result['all_probabilities'].items():
        print(f"  {category}: {prob:.1%}")
    print("-" * 40)

    return result

# Example usage
if __name__ == "__main__":
    image_files = ['test1.jpg', 'test2.jpg', 'test3.jpg', 'test4.jpg', 'test5.jpg']

    for filename in image_files:
        result = classify_with_verdict(filename, nsfw_threshold=0.5)