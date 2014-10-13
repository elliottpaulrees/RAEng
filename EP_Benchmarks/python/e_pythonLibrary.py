##############################################################
#
#
#Author: Elliot Rees (C) 2014
#Website: elliottpaulrees.biz
#Email: elliottpaulrees@gmail.com
#Github: www.github.com/elliottpaulrees
#Version: 1.0
#Liscence: Free for academic and personnel use!

############################################################
from cffi import FFI
import os
import time
import datetime

ffi = FFI()

ffi.cdef("""

typedef long int __OFF_T_TYPE;

typedef __OFF_T_TYPE __off_t;

typedef __off_t off_t;

typedef unsigned long size_t;

typedef enum {
        E_FALSE = 0,
        E_TRUE  = 1,
} e_bool_t;

//typedef enum {
//        E_FALSE = false,
//        E_TRUE  = true,
//} e_bool_t;


typedef enum {
        E_RD   = 1,
        E_WR   = 2,
        E_RDWR = 3,
} e_memtype_t;

typedef enum {
        E_NULL         = 0,
        E_EPI_PLATFORM = 1,
        E_EPI_CHIP     = 2,
        E_EPI_GROUP    = 3,
        E_EPI_CORE     = 4,
        E_EXT_MEM      = 5,
        E_MAPPING      = 6,
} e_objtype_t;


typedef enum {
        E_E16G301 = 0,
        E_E64G401 = 1,
} e_chiptype_t;


typedef enum {
        E_GENERIC        = 0,
        E_EMEK301        = 1,
        E_EMEK401        = 2,
        E_ZEDBOARD1601   = 3,
        E_ZEDBOARD6401   = 4,
        E_PARALLELLA1601 = 5,
        E_PARALLELLA6401 = 6,
} e_platformtype_t;


typedef struct {
        e_objtype_t      objtype;     // object type identifier
        off_t            phy_base;    // physical global base address of memory region
        off_t            page_base;   // physical base address of memory page
        off_t            page_offset; // offset of memory region base to memory page base
        size_t           map_size;    // size of mapped region
        void            *mapped_base; // for mmap
        void            *base;        // application space base address of memory region
} e_mmap_t;

typedef struct {
        e_objtype_t      objtype;     // object type identifier
        unsigned int     id;          // core ID
        unsigned int     row;         // core absolute row number
        unsigned int     col;         // core absolute col number
        e_mmap_t         mems;        // core's SRAM data structure
        e_mmap_t         regs;        // core's e-regs data structure
} e_core_t;

typedef struct {
        e_objtype_t      objtype;     // object type identifier
        e_chiptype_t     type;        // Epiphany chip part number
        unsigned int     num_cores;   // number of cores group
        unsigned int     base_coreid; // group base core ID
        unsigned int     row;         // group absolute row number
        unsigned int     col;         // group absolute col number
        unsigned int     rows;        // number of rows group
        unsigned int     cols;        // number of cols group
        e_core_t       **core;        // e-cores data structures array
        int              memfd;       // for mmap
} e_epiphany_t;


typedef struct {
        e_objtype_t      objtype;     // object type identifier
        off_t            phy_base;    // physical global base address of external memory buffer as seen by host side
        off_t            page_base;   // physical base address of memory page
        off_t            page_offset; // offset of memory region base to memory page base
        size_t           map_size;    // size of eDRAM allocated buffer for host side
        off_t            ephy_base;   // physical global base address of external memory buffer as seen by device side
        size_t           emap_size;   // size of eDRAM allocated buffer for device side
        void            *mapped_base; // for mmap
        void            *base;        // application (virtual) space base address of external memory buffer
        int              memfd;       // for mmap
} e_mem_t;


typedef struct {
        e_objtype_t      objtype;     // object type identifier
        e_chiptype_t     type;        // Epiphany chip part number
        char             version[32]; // version number of Epiphany chip
        unsigned int     arch;        // architecture generation
        unsigned int     base_coreid; // chip base core ID
        unsigned int     row;         // chip absolute row number
        unsigned int     col;         // chip absolute col number
        unsigned int     rows;        // number of rows in chip
        unsigned int     cols;        // number of cols in chip
        unsigned int     num_cores;   // number of cores in chip
        unsigned int     sram_base;   // base offset of core SRAM
        unsigned int     sram_size;   // size of core SRAM
        unsigned int     regs_base;   // base offset of core registers
        unsigned int     regs_size;   // size of core registers segment
        off_t            ioregs_n;    // base address of north IO register
        off_t            ioregs_e;    // base address of east IO register
        off_t            ioregs_s;    // base address of south IO register
        off_t            ioregs_w;    // base address of west IO register
} e_chip_t;


typedef struct {
        e_objtype_t      objtype;     // object type identifier
        off_t            phy_base;    // physical global base address of external memory segment as seen by host side
        off_t            ephy_base;   // physical global base address of external memory segment as seen by device side
        size_t           size;        // size of eDRAM allocated buffer for host side
        e_memtype_t      type;        // type of memory RD/WR/RW
} e_memseg_t;


typedef struct {
        e_objtype_t      objtype;     // object type identifier
        e_platformtype_t type;        // platform part number
        char             version[32]; // version number of platform
        unsigned int     hal_ver;     // version number of the E-HAL
        int              initialized; // platform initialized?

        unsigned int     regs_base;   // base address of platform registers

        int              num_chips;   // number of Epiphany chips in platform
        e_chip_t        *chip;        // array of Epiphany chip objects
        unsigned int     row;         // platform absolute minimum row number
        unsigned int     col;         // platform absolute minimum col number
        unsigned int     rows;        // number of rows in platform
        unsigned int     cols;        // number of cols in platform

        int              num_emems;   // number of external memory segments in platform
        e_memseg_t      *emem;        // array of external memory segments
} e_platform_t;


typedef unsigned int e_coreid_t;

typedef struct {
        int naught;
        int one;
        int two;
        int three;
        int four;
        int five;
        int six;
        int seven;
        int eight;
        int nine;
} shm_t;

	/*===============
	Epiphany Includes
	================*/
	
	int e_init(char *hdf);	
	int e_reset_system();
        int e_get_platform_info(e_platform_t *platform);
        int e_open(e_epiphany_t *dev, unsigned row, unsigned col, unsigned rows, unsigned cols);
        int e_reset_group(e_epiphany_t *dev);
        int e_load(char *executable, e_epiphany_t *dev, unsigned row, unsigned col, e_bool_t start);
	int e_load_group(char *executable, e_epiphany_t *dev, unsigned row,unsigned col, unsigned rows, unsigned cols,
	e_bool_t start);
        int e_free(e_mem_t *mbuf);
       // void *e_read(void *remote, void *dst, unsigned row, unsigned col, const void *src, size_t bytes);
        int e_close(e_epiphany_t *dev);
        int e_finalize();
	int e_alloc(e_mem_t *mbuf, off_t base, size_t size);
	ssize_t e_read(void *dev, unsigned row, unsigned col, off_t from_addr, void *buf, size_t size);
	ssize_t e_write(void *dev, unsigned row, unsigned col, off_t to_addr, const void *buf, size_t size);

        int printf(const char *format, ...);

""")

C = ffi.verify("""


	/*
	Includes	
	*/

        #include <stdlib.h>
        #include <stdio.h>
        #include <string.h>
        #include <unistd.h>
        #include <errno.h>
        #include <malloc.h>
        #include <e-hal.h>
	#include <sys/types.h>
	#include "common.h"
	#include <stddef.h>
	/*
	Definitions
	*/

	/*
	variables
	*/

	e_platform_t platform;
	e_epiphany_t dev;
	e_mem_t emem;
	e_bool_t bool;
	

	/*
	setup
	*/

	e_get_platform_info(platform);

""", libraries=["/opt/adapteva/esdk.5.13.09.10/bsps/parallella_E16G3_1GB/e-hal"], library_dirs=["/opt/adapteva/esdk.5.13.09.10/bsps/parallella_E16G3_1GB/"], include_dirs=["/opt/adapteva/esdk/tools/host/include"])




def compileFile(fileName):

	file = open(fileName)
	fileNameVar = file.name
	file.close
	fileNameVarTwo = fileNameVar[:-2]
	commandString = """
e-gcc -T /opt/adapteva/esdk/bsps/current/fast.ldf " + fileNameVar + " -o " + fileNameVarTwo + ".elf  -Wall -le-lib -lm -O3
	"""
	os.system(commandString)
	commandString = "e-objcopy --srec-forceS3 --output-target srec "+ fileNameVarTwo+".elf " + fileNameVarTwo+ ".srec"
	os.system(commandString);
	os.system("e-gcc -T /opt/adapteva/esdk/bsps/current/fast.ldf testCore.c -o testCore.elf -Wall -le-lib -lm -O3")

	

	return fileNameVarTwo+".srec"



def helloWorld(fileName):

	try:
	
		openFile = open(fileName, 'w');
	
		openFile.write("""

#include <stdio.h>\n
#include <stdlib.h>\n
#include <string.h>\n

#include "e_lib.h"\n

char outbuf[128] SECTION("shared_dram");\n

int main(void) {\n
        e_coreid_t coreid;\n

        // Who am I? Query the CoreID from hardware.\n
//        coreid = e_get_coreid();\n

        // The PRINTF family of functions do not fit\n
        // in the internal memory, so we link against\n
        // the FAST.LDF linker script, where these\n
        // functions are placed in external memory.\n
  //      sprintf(outbuf, "Hello World from core 0x%03x!", coreid);\n

        return EXIT_SUCCESS;\n
}


        	""")
		openFile.close()
        except:
		return False

	return True


def createFile(fileNameVar):

	try:
        ####################
        #Create a time stamp
        ####################
       		timeInSeconds = time.time()
        	timeStamp = datetime.datetime.fromtimestamp(timeInSeconds).strftime('%Y-%m-%d-%H:%M:%S')

        ###################
        #Create A c file
        ###################
       		fileNameVar =  fileNameVar + '-' + timeStamp +".c"
        	file = open(fileNameVar, 'w+')
        	file.close
		print "C file created: " + fileNameVar
	
	except:
		return False
	
	return fileNameVar

       

def writeString(fileNameVar, cCode):

	
	try:
	
		file = open(fileNameVar, 'w')
	
		file.write(cCode)

		file.close

	except:
		return False

	return True

###############################
#Wrappers for Epiphany commands!
###############################
def e_init(hdf):

	if hdf is None:
		return  C.e_init(ffi.NULL);
	


	return	C.e_init(hdf);




def e_reset_system():

	return C.e_reset_system();



def e_epiphany_create():

	dev = ffi.new("e_epiphany_t *")

	return dev


def e_mem_create():
	
	mem = ffi.new("e_mem_t *")

	return mem

def e_get_platform_info():

	platform = ffi.new("e_platform_t *")
	
	C.e_get_platform_info(platform);

	return platform


def e_open(dev, row, col, rows, cols):

	return C.e_open(dev, row, col, rows, cols);




def e_reset_group():

	return C.e_reset_group(dev);




def e_load(file, dev, row, col):

	

	start = ffi.new("e_bool_t*", C.E_TRUE)

	return C.e_load(file, dev, row, col, start[0]);

	

def e_load_group(file, dev, row, col, rows, cols):

	start = ffi.new("e_bool_t*", C.E_TRUE)

	return C.e_load_group(file, dev, row, col, rows, cols, start[0])


def e_alloc(emem, base, size):

	return C.e_alloc(emem, base, size);




def e_free():

	return C.e_free(emem);




def e_read(dev_emem, row, col, memStart, buffSize):

	buffer = ffi.new("int *")
	
	C.e_read(dev_emem, row, col, memStart, buffer, buffSize);
	
	return buffer[0]

def e_write(dev_emem, row, col, memStart, buffer, size):
	return C.e_write(dev_emem, row, col, memStart, buffer, size)
	 


def e_close(dev):


	return C.e_close(dev);




def e_finalize():


	return C.e_finalize();

def createStruct():

	shm = ffi.new("shm_t *")
	return shm

def get_offset(shmString, numString):



	return ffi.offsetof(shmString, numString)

	 
def get_sizeof(type):


	return ffi.sizeof(type)



