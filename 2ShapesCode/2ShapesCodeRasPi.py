# 2 lines detection code works with RasPi
# written by Kayla Nguyen'18

# NumPy adds support for large, multi-dimensional arrays and matrices
# and a large library of high-level mathematical functions
# cv2 supports images
import math
import numpy as np
import cv2
#import RPi.GPIO as GPIO
# from Adafruit_PWM_Servo_Driver import PWM

# variables
# number of vertices of closer shape
vertex_num_close = 4
# number of vertices of further shape
vertex_num_far = 3
# object size (length of the line) is 50mm
object_size = 60
# focal length of MacBook Air camera is 50mm
# 1mm = 3.779527559 pixels
focal_length = 6450 # * 3.779527559
# goal distance to maintain (in mm)
goal_distance = 150

# declare threshold var
global thresh
thresh = None

# coordinates for closer line
global cx1
cx1 = 0
global cy1
cy1 = 0
global cx2
cx2 = 0
global cy2
cy2 = 0

# coordinates for further line
global cx3
cx3 = 0
global cy3
cy3 = 0
global cx4
cx4 = 0
global cy4
cy4 = 0

# pmw for RasPi
global pmw
pmw = None

# main method
def main():
    # initialize RasPi
    # initRasPi()

    # capture a video
    cap = cv2.VideoCapture(0)

    # repeatedly find the shape
    while True:
        # capture frame-by-frame
        _, frame = cap.read()
        # find the shape/contours
        contours = find_shape(frame)
        # for each contour
        for cnt in contours:
            # smooth the edges of contour
            # counts the number of edges
            # vertices is an array store coordinates of each vertex
            # cv2.approxPolyDP(curve, epsilon, closed[, approxCurve])
            vertices = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)

                        # further shape
            if len(vertices) == vertex_num_far:
                # get the contour area
                area = cv2.contourArea(cnt)
                # get the equivalent diameter
                # (the diameter of the circle whose area is same as the contour area)
                equi_d = np.sqrt(4 * area / np.pi)
                # if the diameter is larger than 100 pixels (shape is big enough)
                if equi_d > 100:
                    print "Further shape"
                    # give color to the detected shape
                    cv2.drawContours(frame, [cnt], 0, (0, 255, 225), -1)

                    # get the coordinates of the targeted line
                    # using the topmost and bottommost points
                    topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
                    global cx3
                    cx3 = topmost[0]
                    global cy3
                    cy3 = topmost[1]
                    bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])
                    global cx4
                    cx4 = bottommost[0]
                    global cy4
                    cy4 = bottommost[1]

            # check number of vertices
            # closer shape
            if len(vertices) == vertex_num_close:
                # get the contour area
                area = cv2.contourArea(cnt)
                # get the equivalent diameter
                # (the diameter of the circle whose area is same as the contour area)
                equi_d = np.sqrt(4 * area / np.pi)
                # if the diameter is larger than 100 pixels (shape is big enough)
                if equi_d > 100:
                    print "Closer shape"
                    # give color to the detected shape
                    cv2.drawContours(frame, [cnt], 0, (0, 0, 225), -1)

                    # get the coordinates of the targeted line
                    # using the topmost and bottommost points
                    topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
                    global cx1
                    cx1 = topmost[0]
                    global cy1
                    cy1 = topmost[1]
                    bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])
                    global cx2
                    cx2 = bottommost[0]
                    global cy2
                    cy2 = bottommost[1]

                    # check distance
                    check_distance()
                    # if the coordinates of closer shape are now updated
                    if cx1 != 0:
                        # check center
                        check_center(cap)
                        # check parallel
                        check_parallel()

        # display image in the specified window
        cv2.imshow('binary', thresh)
        cv2.imshow('contours', frame)
        # displays the image for specified milliseconds.
        if cv2.waitKey(1) & 0xff == 27:
            break

    # when everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


# method to find shape
def find_shape(frame):
    # operations on the frame aka image
    imgray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # detect edge
    # Canny(image, threshold1, threshold2)
    edges = cv2.Canny(imgray, 130, 200)
    # set threshold
    # threshold(src, thresh(used to classify the pixel values) , maxval, type)
    global thresh
    _, thresh = cv2.threshold(edges, 127, 255, 0)
    # find the shape/contours
    contours, _ = cv2.findContours(thresh, 2, 1)
    return contours


# method to compute distance from camera to object
# by using distance formula
# NOTE: the result is not accurate
def compute_distance():
    print "got here"
    # compute the image size of the triangle base edge (in pixels)
    image_size = math.sqrt((cx2 - cx1) ** 2 + (cy2 - cy1) ** 2)
    # print "image size is %s" %image_size
    # compute the distance by multiply the object size by focal length
    # then divide all by image size
    print object_size
    print focal_length
    print image_size
    current_distance = (object_size * focal_length) / image_size
    print "Current distance is %s mm" % current_distance
    return current_distance


# method to maintain distance
def check_distance():
    # compute current distance
    current_distance = compute_distance()
    # if distance is too close
    if current_distance < goal_distance - 10:
        print "Move back!"
    # if distance is too far
    elif current_distance > goal_distance + 10:
        print "Move forward!"
    # if distance is met
    else:
        print "Right distance"


# method to maintain center
# determine the center of the triangle
# by comparing the centroid coordinates with the screen's size
def check_center(cap):
    # get the screen's size
    video_width = cap.get(3)
    video_height = cap.get(4)

    # get the mid point of the closer line
    cx_mid = (cx1 + cx2)/2
    cy_mid = (cy1 + cy2)/2

    if cx_mid > video_width / 2 + 20:
        print "Move left!"
    elif cx_mid < video_width / 2 - 20:
        print "Move right!"
    else:
        print "Horizontally center!"

    if cy_mid > video_height / 2 + 10:
        print "Move up!"
    elif cy_mid < video_height / 2 - 10:
        print "Move down!"
    else:
        print "Vertically center!"


# method to maintain parallel
# determine the parallelism of the leader robot
# by comparing the bottom x coordinate of closer shape
# with the top x coordinate of further shape
def check_parallel():
    if cx2 < cx4 - 3:
        print "Rotate clockwise!"
    elif cx2 > cx4 + 3:
        print "Rotate counterclockwise!"
    else:
        print "You are now parallel with object ahead"

def initRasPi():
    # Initialise the PWM device using the default address
    global pwm
    pwm = PWM(0x40,)
    # Note if you'd like more debug output you can instead run:
    # pwm = PWM(0x40, debug=True)
    # set the PWM frequency to the minimum value of 0Hz
    pwm.setPWMFreq(40)

# run the main method
if __name__ == '__main__':
    pressedKey = raw_input("Press enter to start")
    if pressedKey is not None:
        main()