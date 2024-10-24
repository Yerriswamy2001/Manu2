import cv2
import numpy as np
import os

def process_image_for_anomaly(image,mydb,MEDIA_PATH, thresh_1=2.2000000000000e-05):
    # Function to remove background from an image
    def remove_background(image):
        center_x = 932
        center_y = 638
        radius = 420
        inr = 345
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
         # Create a mask
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), radius, 255, -1)
        cv2.circle(mask, (center_x, center_y), inr, 0, -1)
 
        # Apply the mask to the grayscale image (no need for 3 channels)
        img = cv2.bitwise_and(image, mask)
 
        # Define the region of interest (ROI)
        x1 = max(center_x - radius, 0)
        y1 = max(center_y - radius, 0)
        x2 = min(center_x + radius, image.shape[1])
        y2 = min(center_y + radius, image.shape[0])
 
        # Crop the image
        cropped_img = img[y1:y2, x1:x2]
 
        return cropped_img
    image=remove_background(image)
    output_folder = r"C:\Users\MicroApt\Desktop\Manu2\media\RAW IMAGES"
    output_image_path = os.path.join(output_folder, "processed_image.png")  # Specify the output filename

# Save the image
    cv2.imwrite(output_image_path, image)

# Print confirmation
    print(f"Processed image saved at: {output_image_path}")

    # Function to compute the 2D Fourier Transform and return magnitude and phase
    def fourier_transform(image):
        # Apply 2D Fourier Transform
        f_transform = np.fft.fft2(image)
        # Shift the zero frequency component to the center
        f_transform_shifted = np.fft.fftshift(f_transform)
        # Extract magnitude and phase
        magnitude = np.abs(f_transform_shifted)
        phase = np.angle(f_transform_shifted)
        return magnitude, phase, f_transform_shifted
   

    # Function to reconstruct the image using inverse Fourier Transform
    def inverse_fourier_transform(f_transform_shifted):
        # Inverse shift to return the zero frequency component to the origin
        f_ishift = np.fft.ifftshift(f_transform_shifted)
        # Apply the inverse Fourier Transform
        img_back = np.fft.ifft2(f_ishift)
        # Take the real part of the result (since the output is complex)
        img_back = np.abs(img_back)
        return img_back

    # Function to calculate Mean Squared Error (MSE) as the reconstruction loss
    def compute_normalized_mse(image,img_back):
        mse = np.mean((image.astype(np.float32) - img_back.astype(np.float32)) ** 2)
        normalized_mse = mse / image.size  # Normalize by the number of pixels
        return normalized_mse
    
    # Step 2: Fourier Transform (Magnitude and Phase)
    magnitude, phase, f_transform_shifted = fourier_transform(image)

    
    # Step 3: Reconstruct the image using the Inverse Fourier Transform
    reconstructed_image = inverse_fourier_transform(f_transform_shifted)
   
    
    
    # Step 4: Apply Gaussian Filter to the reconstructed image
    reconstructed_image_blurred = cv2.GaussianBlur(np.uint8(reconstructed_image), (5, 5), 0)
    
    
    # Step 5: Compute the reconstruction loss (MSE)
    mse_loss = compute_normalized_mse(image, reconstructed_image_blurred)
    print(f"Reconstruction Loss (MSE): {mse_loss}")
    
    # Step 6: Check if it's an anomaly or good based on the MSE loss and threshold
    if (mse_loss >= thresh_1):
        result=0
    else:
        result=1

    print(f"Image classified as {result}")

    # Return the classification result and reconstruction loss
    return result, mse_loss

