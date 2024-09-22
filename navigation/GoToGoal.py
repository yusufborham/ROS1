#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist  
from turtlesim.msg import Pose
import math 
import time
#from std_srvs.srv import Empty
WIDTH = 0.2

def correctAngle(angle):
    if angle < 0 : 
        angle = angle + 360 
    return angle

def init_node():
    rospy.init_node("sender" ,anonymous=True)

def sender():
    sender = rospy.Publisher('/turtle1/cmd_vel' , Twist , queue_size = 10)
    rate = rospy.Rate(10)
    msg = Twist()
    while not rospy.is_shutdown() :
        rospy.loginfo("hello i am sending ")
        msg.linear.x = -0.5
        sender.publish(msg)
        rate.sleep()
def poseCallback(pose_message):
    global x
    global y, yaw
    x= pose_message.x
    y= pose_message.y
    yaw = pose_message.theta
    # print("x  " , x)
    # print("y  " , y)
    # print("theta  ", correctAngle(yaw*(180/3.14)))

def sub_for_pos():
    pose_sub = rospy.Subscriber('/turtle1/pose/',Pose ,poseCallback)
    #rospy.spin()

def move(distance,forward=True):
    
    distance_moved = 0.0 
    global x , y
    x0 = x
    y0 = y
    
    velocity = Twist()
    velocity.linear.x = 0
    velocity.linear.y = 0
    velocity.linear.z = 0  
    velocity.angular.x = 0
    velocity.angular.y = 0
    velocity.angular.z = 0
   
    sender = rospy.Publisher('/turtle1/cmd_vel' , Twist , queue_size = 10)
    rate = rospy.Rate(50)
    kp = 2
    while True :
        distance_moved = abs(math.sqrt(((x-x0) ** 2) + ((y-y0) ** 2)))
        e = distance - distance_moved 
        velocity.linear.x = kp * e
        sender.publish(velocity)
        print(distance_moved)
        rate.sleep()
        if (distance_moved >= distance):
            rospy.loginfo("reached")
            break
    
    velocity.linear.x = 0 
    sender.publish(velocity)

def rotateTo(angle):
        angle_now = correctAngle(yaw * (180/3.1415))

        if angle_now > angle :
            flag = 1 
        else :
            flag = 0 

        velocity = Twist()
        velocity.linear.x = 0
        velocity.linear.y = 0
        velocity.linear.z = 0  
        velocity.angular.x = 0
        velocity.angular.y = 0
        velocity.angular.z = 0

        sender = rospy.Publisher('/turtle1/cmd_vel' , Twist , queue_size = 10)
        rate = rospy.Rate(100)

        kp = 0.03
        while True :
            angle_now = correctAngle(yaw * (180/3.1415))
            e = abs(angle-angle_now)
            velocity.angular.z = e * kp
            sender.publish(velocity)
            print(angle_now)
            rate.sleep()
            if e <=0.01:
                rospy.loginfo("reached")
                break
        velocity.angular.z = 0 
        sender.publish(velocity)
def rotate(angle):
    angle_now = correctAngle(yaw * (180/3.1415))
    angle = angle_now + angle 
    rotateTo(angle)

def goToGoal(x_goal,y_goal):
    global x , y
    x0 = x
    y0 = y
    ed = abs(math.sqrt(((x_goal-x0) ** 2) + ((y_goal-y0) ** 2)))
    eA = math.atan2(y_goal - y0 , x_goal - x)
    kp_d = 0.4
    kp_A = 4

    velocity = Twist()

    velocity.linear.x = kp_d*ed
    velocity.linear.y = 0
    velocity.linear.z = 0  
    velocity.angular.x = 0
    velocity.angular.y = 0
    velocity.angular.z = kp_A*eA 

    sender = rospy.Publisher('/turtle1/cmd_vel' , Twist , queue_size = 10)
    rate = rospy.Rate(100)


    while True :
        sender.publish(velocity)
        ed = abs(math.sqrt(((x_goal-x) ** 2) + ((y_goal-y) ** 2)))
        eA = math.atan2(y_goal - y , x_goal - x) 

        velocity.linear.x = kp_d*ed
        velocity.angular.z = kp_A*(eA - yaw) 

        vel_R = 0.5*(velocity.angular.z*WIDTH + 2 * velocity.linear.x)
        vel_L = 2 * velocity.linear.x - vel_R

        print("velocity for right is ",vel_R , " velocity for left is " , vel_L ,"  --> x ", x , "y " ,y)

        rate.sleep()

        if (abs(ed) <= 0.01):
            rospy.loginfo("reached")
            break
    velocity.linear.x = 0
    velocity.angular.z = 0
    sender.publish(velocity)

def sweep():
    goToGoal(0,0)
    rotateTo(360)
    move(10)
    for i in range (4):
        rotateTo(90)
        move(8)
        rotateTo(180)
        move(1)
        rotateTo(270)
        move(8)
        rotateTo(180)
        move(1)


if __name__ == "__main__" :
    try :
       init_node()
       sub_for_pos()
       time.sleep(2)
       sweep()
    
    

    except rospy.ROSInterruptException :
        pass 
