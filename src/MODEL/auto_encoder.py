import numpy as np
import cv2
import time
# from keras.models import load_model
import matplotlib.pyplot as plt
 
def process_image_for_anomaly1(image, model, cycle_no,mydb,file_raw,MEDIA_PATH,format_date_db,threshold=0.004952204937580973, center_x=929, center_y=638, radius=430, inr=350):
    # Function to remove background from an image
    def remove_background(image, center_x, center_y, radius, inr):
        # Create a mask
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), radius, 255, -1)
        cv2.circle(mask, (center_x, center_y), inr, 0, -1)
        # Create a 3-channel mask
        mask_3ch = cv2.merge([mask, mask, mask])
        # Apply the mask to the image
        img = cv2.bitwise_and(image, mask_3ch)
        # Define the region of interest (ROI)
        x1 = max(center_x - radius, 0)
        y1 = max(center_y - radius, 0)
        x2 = min(center_x + radius, image.shape[1])
        y2 = min(center_y + radius, image.shape[0])
        # Crop the image
        cropped_img = img[y1:y2, x1:x2]
        return cropped_img
 
    # Function to preprocess a single image
    def preprocess_image(image):
        # Convert to grayscale
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Resize image to 512x512
        image = cv2.resize(image, (512, 512))
        # Normalize image to the range [0, 1]
        image = image.astype('float32') / 255.0
        # Reshape to (1, height, width, channels)
        image = np.reshape(image, (1, 512, 512, 1))
        return image
 
    # Function to calculate reconstruction error
    def calculate_reconstruction_error(original, reconstructed):
        mse = np.mean(np.square(original - reconstructed))  # Mean squared error
        return mse
 
    # Function for inference
    def infer_image(model, image, threshold):
        # Reconstruct the image
        reconstructed_image = model.predict(image)  # Reconstruct the image
        # Calculate reconstruction error
        error = calculate_reconstruction_error(image, reconstructed_image)
        # Determine if the image is anomalous
        is_anomalous = error > threshold
        return image.squeeze(), reconstructed_image.squeeze(), error, is_anomalous
 
    # Start the process
    start_time = time.time()
 
    # Remove the background from the image
    image = remove_background(image, center_x, center_y, radius, inr)
   
    # Preprocess the image
    image = preprocess_image(image)
   
    # Run inference
    original_image, reconstructed_image, error, is_anomalous = infer_image(model, image, threshold)
   
    # Print results
    print(f"Error: {error}, Anomalous: {is_anomalous}")
   
    # Capture the time taken
    end_time = time.time()
    print("Time taken:", end_time - start_time)
   
    # Return anomaly result
    return is_anomalous, error