#!/usr/bin/python
# -*- coding: utf-8 -*-

from py4j.java_gateway import JavaGateway
from RobotController import RobotController
from threading import Thread
import time
import math
import config
import urllib
import collections
import sys
from copy import copy

__current_user_name = config.TORNADO_USER
__current_ip = config.TORNADO_IP
__current_ip_local = config.TORNADO_IP_LOCAL
__socket_port = config.TORNADO_PORT
__key = config.TORNADO_KEY
__socket_group_name = config.TORNADO_GROUP_ROBOT

direction = 0
position = (0,0)
gateway = JavaGateway()

angle_threshold = 13
small_angle_threshold = 4
distance_threshold = 0.25
small_distance_threshold = 0.25

lap_time = 4.4

rc = RobotController()

recursion_cutoff = 7



def current_status():
	position = __get_position()
	orientation = get_direction()
	x = position[0]
	y = position[1]
	return 'Position(' + str(x) + ',' + str(y) + '), Orientation(' + str(get_direction()) + ')'


def turn_to(angle, backwards):

	Thread(target=__call_turn_to, args=(angle, backwards)).start()
	# __turn_to(angle, backwards, 0)
	

def move_to(x, y, a, backwards):

	# retrieving current position
	curr_position = __get_position()
	c_x = curr_position[0]
	c_y = curr_position[1]
	# retrieving target position
	t_x = float(x)
	t_y = float(y)
	# final angle
	angle = None
	angle = int(a)
	# # moving robot
	Thread(target=__call_move_to, args=(t_x, t_y, angle, backwards)).start()
	# trigger next cognitive prompt if at beginning of new problem



def plot_point():
	__move_forward()
	time.sleep(0.4)
	__move_backward()
	time.sleep(0.5)
	__stop()

def __call_turn_to(angle, backwards):
	print("Starting turn to!")
	__turn_to(angle, backwards, 0)
	__set_auto(True)
	__stop()
	print("Finished turn to!")

def __call_move_to(x, y, angle, backwards):
	print("Starting move to!")
	__move_to(x,y,backwards,0)
	if angle != None:
		print(">>> STARTING TURN")
		__turn_to(angle, False, 0)
		print("FINISHING TURN <<<")
	print('angle! ' + str(angle))
	__set_auto(True)
	__stop()
	print("Finished move to!")

def __turn_to(angle, backwards, recursion):
	print("Turn (recursion #%d)" % (recursion))
	if __auto():
		if backwards: 
			angle = (angle + 180) % 360
		# print('%s' % str(angle))
		if not __within_threshold(angle, small_angle_threshold):
			direction = get_direction()
			print("- %f: Current " % (direction))
			small_turn = __within_threshold(angle, angle_threshold)		
			if __should_turn_left(direction, angle):
				print("- %d: Turning left" % (recursion))
				__turn_left(small_turn)
			else:
				print("- %d: Turning right" % (recursion))
				__turn_right(small_turn)
			while __auto():
				if __within_threshold(angle, small_angle_threshold if small_turn else angle_threshold):
					print("- %d: Within big threshold" % (recursion))
					__stop()
					break
			if (not __within_threshold(angle, small_angle_threshold)) and (recursion < recursion_cutoff):
				print("- %d: Out of small threshold" % (recursion))
				backwards = not backwards if backwards else backwards # read this expression outloud. Laugh. This sets backwards to False if it was True
				__turn_to(angle, backwards, recursion + 1)
			else:
				print("- %d: Within small threshold, angle: %f" % (recursion, get_direction()))
			print('- %d: Finished turn recursion' % (recursion))

def __should_turn_left(current, target):
	'''Determines if the shortest turn is through the left (true) or through the right (false)'''
	dist = __get_angle_distance(current, target) 
	if (current + dist) % 360 == target:
		return True
	else:
		return False

def __get_angle_distance(current, target):
	dist = math.fabs(target - current)
	dist = dist if dist <= 180 else 360 - dist
	return dist

def test():
	position = __get_position()
	c_x = position[0]
	c_y = position[1]
	print("Final threshold")
	print('X:' + str(math.fabs(c_x - 0)))
	print('Y:' + str(math.fabs(c_y - 0)))
	return small_distance_threshold

def __within_threshold(desired, th):
	current = get_direction()
	diff = math.fabs(current - desired)
	diff = diff if diff < 180 else 360 - diff
	# print('Within : ' + str(diff) + ' - ' + str(diff < th))
	return diff < th

def __move_to(x, y, backwards, recursion):
	print("Move (recursion #%d)" % (recursion))
	if __auto():
		# print('Move to #' + str(recursion))
		
		m = __move_forward if not backwards else __move_backward # based on the backwards variable, determine function for robot movement
		
		if recursion < recursion_cutoff:
			# retrieving current position
			curr_position = __get_position()
			c_x, c_y = curr_position[0], curr_position[1]
			# retrieving target position
			t_x, t_y = x, y
			# calculating deltas
			d_x, d_y = t_x - c_x, t_y - c_y
			# calculatin angle
			new_angle = int(math.atan2(d_y,d_x) * 180 / math.pi)
			if new_angle < 0:
				new_angle += 360

			# determining if it'll be moving in x, y or both
			position = __get_position()
			c_x = position[0]
			c_y = position[1]
			move_x = math.fabs(c_x - x) > distance_threshold
			move_y = math.fabs(c_y - y) > distance_threshold

			# print('Move X: ' + str(move_x) + ', Move Y: ' + str(move_y))

			if move_x or move_y:
				# turning robot
				# angle_delta = math.fabs(get_direction() - new_angle)
				if not __within_threshold(new_angle, small_angle_threshold):
					# print("change angle")
					print(">>> STARTING TURN")
					__turn_to(new_angle, backwards, 0)	
					print("FINISHING TURN <<<")
				# moving robot
				m() # either __move_forward or __move_backward
				prev = sys.maxint
				progress = 0
				while __auto():
					position = __get_position()
					c_x = position[0]
					c_y = position[1]
					# determine progress metric
					curr = math.sqrt(math.pow(c_x - t_x, 2) + math.pow(c_y - t_y, 2))
					# print('Curr: ' + str(curr))
					# print('Prev: ' + str(prev))
					if curr < prev:
						progress = 0
					else:
						progress = progress + 1
					prev = curr
					# determine if it's time to stop
					if (False and progress > 100) or ((move_x and math.fabs(x - c_x) < small_distance_threshold)  or (move_y and math.fabs(c_y - y) < small_distance_threshold)): # TODO cases where x is + and c_x is -. Same for y
						if progress > 100:
							print('Progress: ' + str(progress))
						__stop()
						break
			# Obtaining position again
			position = __get_position()
			c_x = position[0]
			c_y = position[1]
			if math.fabs(c_x - x) > distance_threshold or math.fabs(c_y - y) > distance_threshold:
				__move_to(x, y, backwards, recursion + 1)
			else:
				print("Final threshold")
				print('X:' + str(math.fabs(c_x - x)))
				print('Y:' + str(math.fabs(c_y - y)))

		else:
			print("Recursion DONE")
			make_attribution()


def move_forward():
	__move_forward()

def move_backward():
	__move_backward()

def stop():
	__stop()

def turn_left():
	__turn_left(False)

def turn_right():
	__turn_right(False)

def connect():
	try:
		robot = rc.get_robot()
		return 'yes'
	except Exception as ex:
		return 'no'

def toggle_auto_control():
	return rc.set_auto(not rc.auto)

def test_d():
	return RobotController.d

def get_direction():
	return gateway.getCurrentOrientation()
	# if not RobotController.d:
		# info from iPod not available
		# return gateway.getCurrentOrientation()
	
	#info from iPod available. Using it.
	# h = float(RobotController.d) # Info from secondary orientation source
	# o1 = gateway.getCurrentOrientation() # Info from primary orientation source (may be flipped 180º)
	# o2 = (o1 + 180) % 360 # flipped o1
	
	# # Calculating orientation based on two sources.
	# # The primary source is precise(ish), but it may be flipped 180 degrees. So we check the secondary source for the closest point.
	# d1 = math.fabs(o1 - h)
	# d2 = math.fabs(o2 - h)
	# # Calculating the distance
	# h1 = d1 if d1 <= 180 else 360 - d1
	# h2 = d2 if d2 <= 180 else 360 - d2

	# if h1 < h2:
	# 	return o1
	# else:
	# 	return o2


## private functions
def __auto():
	return rc.auto

def __set_auto(auto):
	rc.set_auto(auto)

def __move_forward():
	rc.get_robot().forwardArrow()

def __move_backward():
	rc.get_robot().backwardArrow()

def __turn_left(low_speed):
	rc.get_robot().leftArrow(low_speed)

def __turn_right(low_speed):
	rc.get_robot().rightArrow(low_speed)

def __stop():
	rc.get_robot().stop()

def __get_position():
	return gateway.getCurrentPositionAsArray()

if __name__ == "__main__":
	print(1)
