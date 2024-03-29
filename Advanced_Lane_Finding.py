# The goal of this pipeline is to read in a video, frame by frame,
# and output a video displaying the lane boundaries, lane curvature,
# and vehicle position
#
#Written by Collin Feight

import numpy as np
import cv2 as cv
import glob
import matplotlib.pyplot as plt

#constants used for script
nx = 9
ny = 6
ym = 30/720
xm = 3.7/700

#Images used for testing and calibration
test = cv.imread('camera_cal/calibration1.jpg')
test_image = cv.imread('Test_Inputs/test1.jpg')
chessboard_images = glob.glob('camera_cal/calibration*.jpg')

objp = np.zeros((ny*nx,3), np.float32)
objp[:,:2] = np.mgrid[0:nx,0:ny].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objectpoints = [] # 3d points in real world space
imagepoints = [] # 2d points in image plane.

# Make a list of calibration images and Calibrate Camera
for fname in chessboard_images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chessboard corners
    ret, corners = cv.findChessboardCorners(gray, (nx, ny), None)

    # If found, add object points, image points
    if ret:
        objectpoints.append(objp)
        imagepoints.append(corners)


def main():
    save_video()


#Input is Image or Individual Frame from Video
def all(input):
    objpoints, imgpoints = objectpoints, imagepoints

    corrected_image, mtx, dist = undistort_image(input, objpoints, imgpoints)

    combined_binary = pipeline(corrected_image)

    top_down = warping_funct(combined_binary)[0]

    out_img, left_poly, right_ploy, ploty, left_line, right_line = fit_polynomial(top_down, ym, xm)

    left_val_real, right_val_real = measure_curvature(left_poly, right_ploy, ploty, ym, xm)

    lanes_filled = drawLaneonimage(input, left_line, right_line, ym, xm, left_poly, right_ploy, left_val_real,
                                   right_val_real)

    #axis_display(top_down,out_img, lanes_filled)
    return lanes_filled


def undistort_image(image, objectpoints, imagepoints):
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objectpoints, imagepoints, image.shape[1:], None, None)
    undistorted_image = cv.undistort(image, mtx, dist, None, mtx)
    return undistorted_image, mtx, dist


# fit the image according to the source points
def warping_funct(img):

    img_size = (img.shape[1], img.shape[0])

    #Vehicle View hardcoded in
    src = np.float32([[580, 460], [205, 720], [1110, 720], [703, 460]])

    #Desired View hardcoded in
    dst = np.float32([[320, 0], [320, 720], [960, 720], [960, 0]])
    M = cv.getPerspectiveTransform(src, dst)  # The transformation matrix
    Minv = cv.getPerspectiveTransform(dst, src)  # Inverse transformation

    #Image warping
    warped_img = cv.warpPerspective(img, M, img_size)

    #Image Unwarped
    unwarp_img = cv.warpPerspective(img, Minv, img_size)
    # Return the resulting image and matrix
    return warped_img, unwarp_img


#Creates Binary Image of Top Down Image
def pipeline(img, s_thresh=(180, 255), b_thresh=(155, 200), l_thresh=(225, 255)):
    img = np.copy(img)
    s_channel = cv.cvtColor(img, cv.COLOR_BGR2HLS)[:, :, 2]

    l_channel = cv.cvtColor(img, cv.COLOR_BGR2LUV)[:, :, 0]

    b_channel = cv.cvtColor(img, cv.COLOR_BGR2Lab)[:, :, 2]

    # Threshold color channel

    s_binary = np.zeros_like(s_channel)
    s_binary[(s_channel >= s_thresh[0]) & (s_channel <= s_thresh[1])] = 1


    b_binary = np.zeros_like(b_channel)
    b_binary[(b_channel >= b_thresh[0]) & (b_channel <= b_thresh[1])] = 1


    l_binary = np.zeros_like(l_channel)
    l_binary[(l_channel >= l_thresh[0]) & (l_channel <= l_thresh[1])] = 1

    # color_binary = np.dstack((u_binary, s_binary, l_binary))

    combined_binary = np.zeros_like(s_binary)
    combined_binary[(l_binary == 1) | (b_binary == 1)] = 1

    return combined_binary


#Sliding Windows Approach
def find_lane_pixels(top_down):
    # Take a histogram of the bottom half of the image
    histogram = np.sum(top_down[top_down.shape[0] // 2:, :], axis=0)
    # Create an output image to draw on and visualize the result
    out_img = np.dstack((top_down, top_down, top_down))*255
    # Find the peak of the left and right halves of the histogram
    # These will be the starting point for the left and right lines
    midpoint = np.int(histogram.shape[0] // 2)
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint

    # HYPERPARAMETERS
    # Choose the number of sliding windows
    nwindows = 10
    # Set the width of the windows +/- margin
    margin = 80
    # Set minimum number of pixels found to recenter window
    minpix = 40

    # Set height of windows - based on nwindows above and image shape
    window_height = np.int(top_down.shape[0] // nwindows)
    # Identify the x and y positions of all nonzero pixels in the image
    nonzero = top_down.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    # Current positions to be updated later for each window in nwindows
    leftx_current = leftx_base
    rightx_current = rightx_base

    # Create empty lists to receive left and right lane pixel indices
    left_lane_inds = []
    right_lane_inds = []

    # Step through the windows one by one
    for window in range(nwindows):
        # Identify window boundaries in x and y (and right and left)
        win_y_low = top_down.shape[0] - (window + 1) * window_height
        win_y_high = top_down.shape[0] - window * window_height
        win_xleft_low = leftx_current - margin
        win_xleft_high = leftx_current + margin
        win_xright_low = rightx_current - margin
        win_xright_high = rightx_current + margin

        # Draw the windows on the visualization image
        cv.rectangle(out_img, (win_xleft_low, win_y_low),
                      (win_xleft_high, win_y_high), (0, 255, 0), 2)
        cv.rectangle(out_img, (win_xright_low, win_y_low),
                      (win_xright_high, win_y_high), (0, 255, 0), 2)

        # Identify the nonzero pixels in x and y within the window #
        good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                          (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
        good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                           (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]

        # Append these indices to the lists
        left_lane_inds.append(good_left_inds)
        right_lane_inds.append(good_right_inds)

        # If you found > minpix pixels, recenter next window on their mean position
        if len(good_left_inds) > minpix:
            leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
        if len(good_right_inds) > minpix:
            rightx_current = np.int(np.mean(nonzerox[good_right_inds]))

    # Concatenate the arrays of indices (previously was a list of lists of pixels)
    try:
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)
    except ValueError:
        # Avoids an error if the above is not implemented fully
        pass

    # Extract left and right line pixel positions
    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds]
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]

    return leftx, lefty, rightx, righty, out_img


#Where Polynomial Lines are Created
def fit_polynomial(binary_warped, ym, xm):
    # Find our lane pixels first
    leftx, lefty, rightx, righty, out_img = find_lane_pixels(binary_warped)

    # Fit a second order polynomial to each using `np.polyfit`
    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)

    #For Real World Curve Values
    left_fit_c = np.polyfit(lefty*ym, leftx*xm, 2)
    right_fit_c = np.polyfit(righty*ym, rightx*xm, 2)

    # Generate x and y values for plotting
    ploty = np.linspace(0, binary_warped.shape[0] - 1, binary_warped.shape[0])
    try:
        left_fitx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
        right_fitx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]
    except TypeError:
        # Avoids an error if `left` and `right_fit` are still none or incorrect
        print('The function failed to fit a line!')
        left_fitx = 1 * ploty ** 2 + 1 * ploty
        right_fitx = 1 * ploty ** 2 + 1 * ploty

    ## Visualization ##
    # Colors in the left and right lane regions
    out_img[lefty, leftx] = [255, 0, 0]
    out_img[righty, rightx] = [0, 0, 255]
    plt.plot(left_fitx, ploty, color='yellow')
    plt.plot(right_fitx, ploty, color='yellow')

    # Plots the left and right polynomials on the lane lines
    return out_img, left_fit_c, right_fit_c, ploty, left_fit, right_fit


#Curvature measured using adjusted polynomial lines for real world values
def measure_curvature(left, right, ploty, ym, xm):
    y_eval = np.max(ploty)*ym
    left_curve = ((1 + (2*left[0]*y_eval*ym + left[1])**2)**1.5) / np.absolute(2*left[0])
    right_curve = ((1 + (2*right[0]*y_eval*ym + right[1])**2)**1.5) / np.absolute(2*right[0])
    return left_curve, right_curve


def drawLine(img, left_fit, right_fit):
    ymax = img.shape[0]
    ploty = np.linspace(0, ymax-1, ymax)
    color_warp = np.zeros_like(img).astype(np.uint8)
    left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
    right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]
    pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
    pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
    pts = np.hstack((pts_left, pts_right))
    cv.fillPoly(color_warp, np.int_([pts]), (0,255, 0))
    newwarp = warping_funct(color_warp)[1]
    return cv.addWeighted(img, 1, newwarp, 0.3, 0)


#Vehicle Position Calculated Here
def drawLaneonimage(img, left, right, ym, xm, left_c, right_c, left_curve, right_curve):
    output = drawLine(img, left, right)

    #calculate center distance
    xmax = img.shape[1] * xm
    ymax = img.shape[0] * ym
    center = xmax / 2
    lineL = left_c[0]*ymax**2 + left_c[1]*ymax + left_c[2]
    lineR = right_c[0]*ymax**2 + right_c[1]*ymax + right_c[2]
    lineM = lineL + (lineR-lineL)/2
    vehicle_diff = lineM-center
    if vehicle_diff > 0:
        message = '{:.2f} m right'.format(vehicle_diff)
    else:
        message = '{:.2f} m left'.format(-vehicle_diff)
    #plain text bad
    font = cv.FONT_HERSHEY_SIMPLEX
    fontcolor = (255, 255, 255)
    fontscale = 1
    cv.putText(output, 'Left Curve: {:.0f} m'.format(left_curve), (20, 50), font, fontscale, fontcolor, 2)
    cv.putText(output, 'Right Curve: {:.0f} m'.format(right_curve), (20, 130), font, fontscale, fontcolor, 2)
    cv.putText(output, 'Vehicle is {} of center'.format(message), (20, 210), font, fontscale, fontcolor, 2)


    return output


#Used to read in and save video
def save_video():
    video = cv.VideoCapture('Test_Inputs/project_video.mp4')

    frame_width = int(video.get(3))
    frame_height = int(video.get(4))

    # define codec, create VideoWriter
    out = cv.VideoWriter('Final_Output.avi', cv.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))

    # iterate through video and process frame by frame
    while video.isOpened():
        bool, frame = video.read()
        global count
        count = 0
        if bool:
            count +=1
            edited_frame = all(frame)
            out.write(edited_frame)

        else:
            break


    # Release everything if job is finished
    video.release()
    out.release()
    cv.destroyAllWindows()


#For Testing
def display(subject):
    plt.imshow(subject)
    plt.show()


#For Testing
def axis_display(im1, im2, im3):

    f, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(24, 9))
    f.tight_layout()
    ax1.imshow(im1)
    ax2.imshow(im2)
    ax3.imshow(im3)
    plt.subplots_adjust(left=0., right=1, top=0.9, bottom=0.)


if __name__ == '__main__':
    main()






