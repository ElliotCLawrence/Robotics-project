#Des Marks
#Teammate 1: Russ Vick
#Teammate 2: Elliot Lawrence
#Teammate 3: John Choi
#Teammate 4: Ryan Taylor

#!/usr/bin/env python

import math
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
import cv2
import numpy as np
from image_converter import ToOpenCV, depthToOpenCV

turning = 0

#this function does our image processing
#returns the location and "size" of the detected object
def process_image(image):
    #convert color space from BGR to HSV
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #create bounds for our color filter
    #lower_bound = np.array([160, 30, 30])
    #upper_bound = np.array([200, 100, 100])

    lower_bound = np.array([0, 140, 140]) #THIS WORKS IN THE FRONT OF THE CLASSROOM
    upper_bound = np.array([192, 200, 200]) #THIS WORKS IN THE FRONT OF THE CLASSROOM


    #0, 140, 140



    #lower_bound = np.array([0, 145, 145])
    #upper_bound = np.array([192, 200, 200])
    #192 52 51

    #execute the color filter, returns a binary black/white image
    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

    #display the results of the color filter
    cv2.imshow("image_mask", mask)

    #calculate the centroid of the results of the color filer
    M = cv2.moments(mask)
    location = None
    magnitude = 0
    if M['m00'] > 0:
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        magnitude = M['m00']
        location = (cx-320, cy-240) #scale so that 0,0 is center of screen
        #draw a circle image where we detected the centroid of the object
        cv2.circle(image, (cx,cy), 3, (0,0,255), -1)

    #display the original image with the centroid drawn on the image
    cv2.imshow("processing result", image)

    #waitKey() is necessary for making all the cv2.imshow() commands work
    cv2.waitKey(1)
    return location, magnitude


class Node:


    def __init__(self):
        #register a subscriber callback that receives images
        self.image_sub = rospy.Subscriber('/camera/rgb/image_raw', Image, self.image_callback, queue_size=1)

        #create a publisher for sending commands to turtlebot
        self.movement_pub = rospy.Publisher('cmd_vel_mux/input/teleop', Twist, queue_size=1)

    #this function wll get called every time a new image comes in
    #all logic occurs in this function
    def image_callback(self, ros_image):
        # convert the ros image to a format openCV can use
        cv_image = np.asarray(ToOpenCV(ros_image))

        #run our vision processing algorithm to pick out the object
        #returns the location (x,y) of the object on the screen, and the
        #"size" of the discovered object. Size can be used to estimate
        #distance
        #None/0 is returned if no object is seen
        location, magnitude = process_image(cv_image)

        #log the processing results
        rospy.logdebug("image location: {}\tmagnitude: {}".format(location, magnitude))

        ###########
        # Insert turtlebot controlling logic here!
        ###########
        cmd = Twist()

        global turning


        #case 1: No target so just turn until you find target
        #case 2: The turtle bot has stopped and is tracking target
        #case 3: Turtle bot is moving and tracking target
        #turtle bot has stopped
        r = rospy.Rate(5)
        r.sleep()


        if magnitude < 1000000: #Scan for new target
            print("First!")
            turning = 1

            #case 1: No target so just turn until you find target
            #case 2: The turtle bot has stopped and is tracking target

            print "Magnitude small!"

            cmd.angular.z =  0.45
            cmd.linear.x = 0.0

            self.movement_pub.publish(cmd)
            #r.sleep()
        elif magnitude > 5000000: #Track your target, without moving forward
            print("Second!")
            print(magnitude)
            if location is not None:
                if location[0] < -100:
                    cmd.angular.z = 0.4
                    cmd.linear.x = 0.0;
                    self.movement_pub.publish(cmd)
                    #r.sleep()
                elif location[0] > 100:
                    cmd.angular.z = -0.4
                    cmd.linear.x = 0.0;
                    self.movement_pub.publish(cmd)
                    #r.sleep()

        else: #move forward and track
            #print(magnitude)
            if location is not None:
                if location[0] < -10:
                    cmd.angular.z = 0.4
                elif location[0] > 10:
                    cmd.angular.z = -0.4

            cmd.linear.x = 0.1
            self.movement_pub.publish(cmd)

            #case 3: Turtle bot is moving and tracking target
        #publish command to the turtlebot
#self.movement_pub.publish(cmd)




if __name__ == "__main__":
    #print("snarf")
    rospy.init_node("lab2_example")
    node = Node()

    #this function loops and returns when the node shuts down
    #all logic should occur in the callback function
rospy.spin()
