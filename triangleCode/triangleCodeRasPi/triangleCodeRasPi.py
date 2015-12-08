#!/usr/bin/python
# Triangle detection code adapted from Keying '17
# written by Kayla Nguyen'18

# NumPy adds support for large, multi-dimensional arrays and matrices
# and a large library of high-level mathematical functions
# cv2 supports images
import math
import numpy as np
import cv2

# import servo driver
from Adafruit_PWM_Servo_Driver import PWM
import time

# variables
# number of vertices
vertex_num = 3
# object size (base edge length of triangle) is 50mm
object_size = 60
# focal length of MacBook Air camera is 50mm
# 1mm = 3.779527559 pixels
focal_length = 600 # * 3.779527559
# goal distance to maintain (in mm)
goal_distance = 150

# declare threshold var
global thresh
thresh = None

# display flag to check whether or not show the display with camera data
# set to true to see the display to debug
# set to false to omit the display to run on RasPi without monitor
global displayOn
displayOn = False

# Initialise the PWM device using the default address
pwm = PWM(0x40)
# Note if you'd like more debug output you can instead run:
# pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(60)                        # Set frequency to 60 Hz

forwardPulse = 150  # Min pulse length out of 4096
backwardPulse = 600  # Max pulse length out of 4096
stopValue = 0

# main method
def main():
	# global displayOn

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

            # check number of vertices
            if len(vertices) == vertex_num:
                # get the contour area
                area = cv2.contourArea(cnt)
                # get the equivalent diameter
                # (the diameter of the circle whose area is same as the contour area)
                equi_d = np.sqrt(4 * area / np.pi)
                # if the diameter is larger than 100 pixels (3 vertices are separate)
                if equi_d > 100:
                    # give color to the detected shape
                    cv2.drawContours(frame, [cnt], 0, (0, 0, 225), -1)

                    # Calculates the image moments of the triangle.
                    moment = cv2.moments(cnt)
                    # extract centroid coordinates
                    cx = int(moment['m10'] / moment['m00'])
                    cy = int(moment['m01'] / moment['m00'])

                    # check parallel
                    check_parallel(vertices, cx)
                    # check distance
                    check_distance(vertices)
                    # check center
                    # check_center(cap, cx, cy)
        if displayOn:
        	# display image in the specified window
        	cv2.imshow('binary', thresh)
        	cv2.imshow('contours', frame)
        # displays the image for specified milliseconds.
        if cv2.waitKey(1) & 0xff == 27:
            break

    # when everything done, release the capture
    cap.release()
    if displayOn:
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
def compute_distance(vertices):
    # get the coordinates of 2 base vertices
    cx1 = vertices[1][0][0]
    cy1 = vertices[1][0][1]

    cx2 = vertices[2][0][0]
    cy2 = vertices[2][0][1]

    # # get the coordinates of mid point of triangle base edge
    # cx_mid = (cx1 + cx2)/2
    # cy_mid = (cy1 + cy2)/2

    # compute the image size of the triangle base edge (in pixels)
    image_size = math.sqrt((cx1 - cx2) ** 2 + (cy1 - cy2) ** 2)
    print "image size is %s" %image_size
    # compute the distance by multiply the object size by focal length
    # then divide all by image size
    current_distance = (object_size * focal_length) / image_size
    print "Current distance is %s mm" % current_distance
    return current_distance


# method to maintain distance
def check_distance(vertices):
    # compute current distance
    current_distance = compute_distance(vertices)
    # if distance is too close
    if current_distance < goal_distance - 20:
        print "Move back!"
        moveBackward()
    # if distance is too far
    elif current_distance > goal_distance + 20:
        print "Move forward!"
        moveForward()
    # if distance is met
    else:
        print "Right distance"
        stopMoving()


# method to maintain center
# determine the center of the triangle
# by comparing the centroid coordinates with the screen's size
def check_center(cap, cx, cy):
    # get the screen's size
    video_width = cap.get(3)
    video_height = cap.get(4)

    if cx > video_width / 2 + 20:
        print "Move left!"
        # turnLeft()
    elif cx < video_width / 2 - 20:
        print "Move right!"
        # turnRight()
    else:
        print "Horizontally center!"
        # stopMoving()

    if cy > video_height / 2 + 10:
        print "Move up!"
        # fly up
    elif cy < video_height / 2 - 10:
        print "Move down!"
        # fly down
    else:
        print "Vertically center!"
        # stop 


# method to maintain parallel
# determine the parallelism of the triangle
# by comparing the centroid x coordinates
# with the top vertex's x coordinate
def check_parallel(vertices, cx):
    # a is an array storing 3 vertices of the triangle
    a = [vertices[0][0][0], vertices[1][0][0], vertices[2][0][0]]
    # sort vertices' coordinates from smallest to biggest
    a.sort()

    if cx < a[1] - 5:
        print "Rotate clockwise!"
        turnLeft()
    elif cx > a[1] + 5:
        print "Rotate counterclockwise!"
        turnRight()
    else:
        print "You are now parallel with object ahead"
        stopMoving()

# method to check if the triangle is tilted forward or backward
# by using distance formula
def checkRotationOx(vertices):
    # get the coordinates of 1 base vertex
    cx1 = vertices[1][0][0]
    cy1 = vertices[1][0][1]

    cx2 = vertices[2][0][0]
    cy2 = vertices[2][0][1]

    # get the coordinates of top vertex
    cx_top = vertices[0][0][0]
    cy_top = vertices[0][0][1]

    # compute the image size of the triangle base edge and side edge (in pixels)
    baseSize = math.sqrt((cx1 - cx2) ** 2 + (cy1 - cy2) ** 2)
    sideSize = math.sqrt((cx1 - cx_top) ** 2 + (cy1 - cy_top) ** 2)
    print "side size is %s" %sideSize
    print "base size is %s" %baseSize
    # if side edge is longer than base edge
    # the triangle is tilted toward the camera
    if sideSize > baseSize + 10:
    	print "Tilt backward!"
    elif sideSize < baseSize - 10:
    	print "Tilt toward camera!"
    else:
    	print "You are not tilted"

# method to check if the triangle is rotating around Oz vector
# by comparing coordinates
# NOTE: the result is not accurate
def checkRotationOz(vertices):
    # get the coordinates of 2 base vertices
    cx1 = vertices[1][0][0]
    cx2 = vertices[2][0][0]

    # get the coordinates of mid point of triangle base edge
    cx_mid = (cx1 + cx2)/2

    # get the coordinates of top vertex
    cx_top = vertices[0][0][0]

    # if the top vertex and mid point is aligned
    # the triangle is standing up straight
    # if cx of mid point is on the right of cx of top vertex
    # the triangle is tilted to the right
    if cx_mid > cx_top + 3:
    	print "Tilt to the right"
    elif cx_mid < cx_top - 3:
    	print "Tilt to the left"
    else:
    	print "You are up straight"

# pin 0 is left servo, pin 1 is right servo
# method to move the robot forward
# pwm.setPWM(channel, 0, pulse)
def moveForward():
    # move forward
    pwm.setPWM(0, 0, backwardPulse)
    pwm.setPWM(1, 0, forwardPulse)

# method to move the robot backward
# pwm.setPWM(channel, 0, pulse)
def moveBackward():
    # move backward
    pwm.setPWM(0, 0, forwardPulse)
    pwm.setPWM(1, 0, backwardPulse)

# method to stop the robot
# pwm.setPWM(channel, 0, pulse)
def stopMoving():
    # stop
    pwm.setPWM(0, 0, stopValue)
    pwm.setPWM(1, 0, stopValue)

# method to turn left
# pwm.setPWM(channel, 0, pulse)
def turnLeft():
    # move right servo, stop left servo
    pwm.setPWM(0, 0, stopValue)
    pwm.setPWM(1, 0, forwardPulse)

# method to turn right
# pwm.setPWM(channel, 0, pulse)
def turnRight():
    # move left servo, stop right servo
    pwm.setPWM(0, 0, backwardPulse)
    pwm.setPWM(1, 0, stopValue)

# run the main method
if __name__ == '__main__':
    main()