#### 2ShapesCode
2 lines detection code written by Kayla Nguyen'18

* patterns: a triangle and a quadrilateral

* detects distance from camera to object

* fixes object center

* determines rotation of object

#### triangleCode
Triangle detection code adapted from Keying Gu'17, written by Kayla Nguyen'18

* patterns: an equilateral triangle

* detects distance from camera to object

* fixes object center

* determines 3D rotations of object

#### In triangleCode folder
* triangle.png is an image file, example of the triangle pattern
* triangleCode3D.py is file that handles 3D CAD constraints
* triangleCode.py is file that hangles 2D CAD constraints
* Inside triangleCodeRasPi is
  * Adafruit_I2C.py, Adafruit_PWM_Servo_Driver.py are 2 servo module
  * servoTest.py is file to test servo (go straight, go back, turn left, turn right)
  * triangleCodeRasPi.py is file to be run on RasPi Bot to detect and follow triangle
  * launcher.sh is a bash script file which is run in crontab everytime RasPi Bot is rebooted. In this file, triangleCodeRasPi.py is called. So RasPi bot automatically run python code on start.

*Summer Research 2015*

*CS395 Independent Study Fall 2015*

Website: https://sites.google.com/a/mtholyoke.edu/robotics-summer-2015/kayla
