#Author: Elliott Rees (C) 2014
#Github: www.github.com/elliottpaulrees
#Email: elliottpaulrees@gmail.com
#Website: www.elliottpaulrees.biz
#Liscence: Free for academic and personnel use!

import os
import e_pythonLibrary
import sys
import gc
from time import sleep
import timeit

#TODO:

#	find a way to time the runtime of the program, using python

###########################
#	Stand Variables
##########################

oneLoopVar = 0
twoLoopVar = 0
temp = 0.0
addr = 0
anint = 0
clr = 0x00000000
SHM_OFFSET = 0x01000000
anint = 0
pointerHolder = gc.get_rpy_referents(clr)
size = e_pythonLibrary.get_sizeof("int")


##########################
#	e Variables
#########################

e_pythonLibrary.e_init("/opt/adapteva/esdk/bsps/current/platform.hdf")
e_pythonLibrary.e_reset_system();
platform = e_pythonLibrary.e_get_platform_info()
dev = e_pythonLibrary.e_epiphany_create()
mem = e_pythonLibrary.e_mem_create()
e_pythonLibrary.e_open(dev, 0, 0, platform.rows, platform.cols)

###########################
# Clear flag data
##########################
print "Clearing flag data!"

for oneLoopVar in range(0, platform.rows):

	for twoLoopVar in range(0, platform.cols):


		e_pythonLibrary.e_write(dev, oneLoopVar, twoLoopVar, 0x7000, gc.get_rpy_referents(clr), size)

###########################
# allocate memory
##########################

shm = e_pythonLibrary.createStruct() 

shm.naught = 0
shm.one = 0
shm.two = 0
shm.three = 0
shm.four = 0
shm.five = 0
shm.six = 0
shm.seven = 0
shm.eight = 0
shm.nine = 0

size = e_pythonLibrary.get_sizeof("shm_t")
e_pythonLibrary.e_alloc(mem, SHM_OFFSET, size) 

###################################
# Write datastruct to shared memory
###################################


e_pythonLibrary.e_write(mem, 0, 0, 0, shm, size)

###################################
# load groups to test cores!
###################################

print "Loading groups to test cores..."


start_time = timeit.default_timer()

e_pythonLibrary.e_load("testCore_mutex.srec", dev, 0, 0)
sleep(1)
e_pythonLibrary.e_load_group("testCore.srec", dev, 0, 1, 1, 3)
e_pythonLibrary.e_load_group("testCore.srec", dev, 1, 0, 3, 4)
   
print "loaded!"

size = e_pythonLibrary.get_sizeof("int")

while 1:
	all_done = 0

	for oneLoopVar in range(0, platform.rows):

		for twoLoopVar in range (0, platform.cols):

			num = e_pythonLibrary.e_read(dev, oneLoopVar, twoLoopVar, 0x7000, size)
			all_done = all_done + num
				
	if all_done == 16:
		break
			

print "All cores completed loading programme!"


print "l       QT \n----------\n"




for oneLoopVar in range (0, 10):

	if oneLoopVar == 0:

	
		addr = e_pythonLibrary.get_offset("shm_t", "naught")
		anint = e_pythonLibrary.e_read(mem, 0, 0, addr, size)

	if oneLoopVar == 1:

                addr = e_pythonLibrary.get_offset("shm_t", "one")
                anint = e_pythonLibrary.e_read(mem, 0, 0, addr, size)

	if oneLoopVar == 2:

		addr = e_pythonLibrary.get_offset("shm_t", "two")
		anint = e_pythonLibrary.e_read(mem, 0, 0, addr, size)
		
	if oneLoopVar == 3:

		addr = e_pythonLibrary.get_offset("shm_t", "three")
		anint = e_pythonLibrary.e_read(mem, 0, 0, addr, size)

	if oneLoopVar == 4:
      
		addr = e_pythonLibrary.get_offset("shm_t", "four")
		anint = e_pythonLibrary.e_read(mem, 0, 0, addr, size)

	if oneLoopVar == 5:

		addr = e_pythonLibrary.get_offset("shm_t", "five")
		anint = e_pythonLibrary.e_read(mem, 0, 0, addr, size)

	if oneLoopVar == 6:

		addr = e_pythonLibrary.get_offset("shm_t", "six")
		anint = e_pythonLibrary.e_read(mem, 0, 0, addr, size)

	if oneLoopVar == 7:

		addr = e_pythonLibrary.get_offset("shm_t", "seven")
		anint = e_pythonLibrary.e_read(mem, 0, 0, addr, size)

	if oneLoopVar == 8:

		addr = e_pythonLibrary.get_offset("shm_t", "eight")
		anint = e_pythonLibrary.e_read(mem, 0, 0, addr, size)

	if oneLoopVar == 9:

		addr = e_pythonLibrary.get_offset("shm_t", "nine")
		anint = e_pythonLibrary.e_read(mem, 0, 0, addr, size)


	print oneLoopVar, "	", anint

elapsed = timeit.default_timer() - start_time
print "Time:", elapsed, "seconds."
e_pythonLibrary.e_close(dev)
e_pythonLibrary.e_finalize()










