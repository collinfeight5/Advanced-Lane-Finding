[image1]: ./Output_Images/Calibration.png "Chessboard"
[image2]: ./Output_Images/Calibration2.png "Undistorted Road Image"
[image3]: ./Output_Images/BinaryStraight.png "Straight Line Binary"
[image4]: ./Output_Images/BinaryTest3.png "Curved Line Binary"
[image5]: ./Output_Images/TopDownStraight.png "Output"
[image6]: ./Output_Images/TopDownTest3.png "Output"
[image7]: ./Output_Images/LanePixelsStraight.png "Output"
[image8]: ./Output_Images/LanePixelsTest3.png "Output"
[image9]: ./Output_Images/FinalStraight.png "Output"
[image10]: ./Output_Images/FinalTest2.png "Output"
[image11]: ./Test_Inputs/Curvature.png "Curve"



[//]: # (Image References)


[video1]: ./project_video.mp4 "Video"

## Overview of steps that were taken to complete this project: Detailed descriptions seen below
### 1. Get array of object points and image points from calibration chessboard images
### 2. Undistort an image, or in the case of a video, a frame
### 3. Apply a Binary Threshold to the unidsorted image or frame
### 4. Warp the Binary image to reflect a "top-down" view of the image or frame
### 5. Fit a polynomial line to the lane lines
### 6. Measure the curvature of the road 
### 7. Create function to transform the image/frame back to the original view from TopDown and color fill lines;  
### 8. Formats and creates text on image/frame for curvature; also calculates vehicle position
### 9. Creates function to call input video and process each frame individually. 
### 10. Create "all" function that takes individual image/frame and runs it through steps above.


### Step 1. 
The code for this step is contained in lines 17-36. 
I start by preparing "object points", which will be the (x, y, z) coordinates of the chessboard corners in the world. Here I am assuming the chessboard is fixed on the (x, y) plane at z=0, such that the object points are the same for each calibration image.  Thus, `objp` is just a replicated array of coordinates, and `objpoints` will be appended with a copy of it every time I successfully detect all chessboard corners in a test image.  `imgpoints` will be appended with the (x, y) pixel position of each of the corners in the image plane with each successful chessboard detection.  





### Step 2. 
The code for the following step is contained in lines 63-66.
I then use the output `objpoints` and `imgpoints` to compute the camera calibration and distortion coefficients using the `cv2.calibrateCamera()` function.  I applied this distortion correction to the test image using the `cv2.undistort()` function and obtained this result for a calibration image: 



![alt text][image1]

and this for an image of the car on the road: Note the circled locations compared to the inital image

![alt text][image2]

### Step 3.
The code for the following step is contained in lines 92-118.
Once the image had been corrected for distortion, I then passed it to my function called "pipeline". This function took the corrected image and created a binary threshold using 3 different color spaces: HLS, LUV, and Lab, and S Channel, L, Channel, and B Channel for each of these color channels respectively. I then combined the thresholds all the thresholds and returned a "combined threshold" I could apply to images and frames of the video. 

![alt text][image3]

![alt text][image4]


### Step 4.
The code for the following step is contained in lines 70-88.
After the image/frame had been converted to a binary image, I then used the cv.warpPerspective function to warp the binary image/frame to a top-down aspect. The inputs for this function was a transform matrix, which was created with hard-coded source and destination values along with the cv.getPerspectiveTransform function.

![alt text][image5]

![alt text][image6]

### Step 5.
The code for the following step is contained in lines 122-236
Once I had a top-down binary image, The next step was to create windows encompasing the lane lines and draw a best-fit polynomial line where the lane lines should be. This was accomplished by splitting the top-down view of the road and lane lines into two parts, a left and a right divided in the middle of the image. A histogram was used to find the "peaks", or concentrated color areas of the image produced from the binary threshold, which represented the start of the lane lanes in our image. Once a beginning point had been found, the "sliding windows" approach was used to move up the lane lines and track the changing lane lines, or curvature, of the road. The active pixels in the areas of the windows were then saved, and a best fit polynomial line was created to represent the lanes lines.


![alt text][image7]

![alt text][image8]

### Step 6. 
The code for the following step is contained in lines 240-244.
The radius of curvature of the lane lines was calculated using the following equation:

![alt text][image11]

This equation corresponded to the following equations for the left and right lanes respectively. 
   left_curve = ((1 + (2*left[0]*y_eval*ym + left[1])**2)**1.5) / np.absolute(2*left[0])
   right_curve = ((1 + (2*right[0]*y_eval*ym + right[1])**2)**1.5) / np.absolute(2*right[0])
    
These equations use corrected polynomial lines to account for the conversion from pixel space to real world space. There was some assumptions that went along with this, such as that the area that we were viewing was rougly 700 pixels wide, and the width of our road was roughly 3.7 meters across. The output of this function was to return the radius of curvature of the left and right lane lines. 

### Step 7.
The code for the following step is contained in lines 247-258, along with the warping function described in step 4. 
This is where I create a function that is later called in step 8 to fill the area between the polynomial, or road lines. Along with this, I unwarp the top-down view back to the original image using the inverse matrix found using the source and destination points described in step 4. Once the inverse matrix had been found, I used the same cv.warpPerspective function to transform the image from top-down to the original view. 

### Step 8. 
The code for the following step is contained in lines 262-286.
The code here calls the function described in step 7, and also calculates the vehicle position in regard to the right and left lane lines. This is also where the text formatting occurs for writing the radius of curvature and vheicle position on the image/frame. 

### Step 9.
The code for the following step is contained in lines 290-310. 
This is where I read in the input video, and break it into individual frames that I can then pass to my all function described in step 10. This is also where I write the output video for the final output. 

### Step 10.
The code for the following step is contained in lines 43-60.
The Final step. Pass an image or frame into this function and it will run it through each step described above in the right order and output the correct and final result. 

![alt text][image9]

![alt text][image10]



### Pipeline (video)

#### Link to the pipeline output video. 

Here's a [link to my video result](./project_video.mp4)

---

### Discussion

#### 1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  


