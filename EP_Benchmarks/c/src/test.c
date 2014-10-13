/****************************************
		Includes
****************************************/
#include <sys/time.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <e-hal.h>
#include "common.h"
#include <stddef.h>

#define SHM_OFFSET 0x01000000
/****************************************
		main method!
****************************************/

int main(int argc, char * argv[])
{


/****************************************
       Standard  Varialbes
***************************************/

//array to read done flags and int to count the numer of done flags set
int done[Cores], all_done; 
//used for loos
int oneLoopVar, twoLoopVar; 
//written to memory to clear it
unsigned clr;
clr = (unsigned) 0x00000000;
//Start and end timer varialbes
struct timeval  tvStart;
struct timeval  tvEnd;
//used as a temporary store for floating poit numers
double          temp;
unsigned int addr;
//Used to retrieve integers from memory
int anint;
//shm_t which will be written to memory. All values set to 0 to ensure it has the size of an int
shm_t shm;
shm.naught = 0;
shm.one = 0;
shm.two = 0;
shm.three = 0;
shm.four = 0;
shm.five = 0;
shm.six = 0;
shm.seven = 0;
shm.eight = 0;


/****************************************
        epiphany variables
***************************************/
e_platform_t platform;
e_epiphany_t dev;
e_mem_t mem;


/****************************************
        epiphany setup
***************************************/
e_init(NULL);
e_reset_system();
e_get_platform_info(&platform);
e_open(&dev, 0, 0 , platform.rows, platform.cols);

/*************************************************************************
        Clear the "done" flag of each core by writing clr variable to them
**************************************************************************/

printf("clearing flag data \n");
for(oneLoopVar = 0; oneLoopVar < platform.rows; oneLoopVar++){

        for(twoLoopVar = 0; twoLoopVar < platform.cols; twoLoopVar++){

                e_write(&dev, oneLoopVar, twoLoopVar, 0x7000, &clr, sizeof(clr)); // Clear the done flag memory location.

        }

}


/****************************************
       Allocate memory in shared RAM
***************************************/

e_alloc(&mem, SHM_OFFSET, sizeof(shm_t));

/****************************************
      Write the shm struct to memory
***************************************/


e_write(&mem, 0, 0, (off_t)0, &shm, sizeof(shm_t));


/****************************************
        Get start time
****************************************/

gettimeofday(&tvStart, NULL);

/****************************************
        Loads cores with EP test
****************************************/

printf("loading groups with testCores.c amd testCore_mutex.c \n");
//Load a single eCore to initiate the mutex
e_load("testCore_mutex.srec", &dev, 0, 0, E_TRUE);
usleep(10000);
// Load the device program onto all the other eCores
e_load_group("testCore.srec", &dev, 0, 1, 1, 3, E_TRUE);
e_load_group("testCore.srec", &dev, 1, 0, 3, 4, E_TRUE);

printf("groups loaded \n");

/*************************************************
        Wait for all cores to set their done flag 
**************************************************/


while(1){
    all_done=0;
    for (oneLoopVar=0; oneLoopVar<platform.rows; oneLoopVar++){
      for (twoLoopVar=0; twoLoopVar<platform.cols;twoLoopVar++){
        e_read(&dev, oneLoopVar, twoLoopVar, 0x7000, &done[oneLoopVar*platform.cols+twoLoopVar], sizeof(int));
        all_done+=done[oneLoopVar*platform.cols+twoLoopVar];
       }
    }
    if(all_done == Cores){
      break;
    }
  }

printf("All cores completed loading programme! \n");

/****************************************
        Get and print results
****************************************/

printf("l       QT \n----------------\n");

for(oneLoopVar = 0; oneLoopVar <10; oneLoopVar++){

	switch(oneLoopVar)
	{

		case 0:
			addr = offsetof(shm_t, naught);
			e_read(&mem, 0, 0, addr, &anint, sizeof(int));
			break;
		case 1:
			addr = offsetof(shm_t, one);
			e_read(&mem, 0, 0, addr, &anint, sizeof(int));

			break;
		case 2:
			addr = offsetof(shm_t, two);
			e_read(&mem, 0, 0, addr, &anint, sizeof(int));
			break;
		case 3:
			addr = offsetof(shm_t, three);
			e_read(&mem, 0, 0, addr, &anint, sizeof(int));
			break;
		case 4:
			addr = offsetof(shm_t, four);
			e_read(&mem, 0, 0, addr, &anint, sizeof(int));
			break;
		case 5:
			addr = offsetof(shm_t, five);
			e_read(&mem, 0, 0, addr, &anint, sizeof(int));
			break;
		case 6:
			addr = offsetof(shm_t, six);
			e_read(&mem, 0, 0, addr, &anint, sizeof(int));
			break;
		case 7:
			addr = offsetof(shm_t, seven);
			e_read(&mem, 0, 0, addr, &anint, sizeof(int));
			break;

		case 8:
			addr = offsetof(shm_t, eight);
			e_read(&mem, 0, 0, addr, &anint, sizeof(int));
			break;
		case 9:
			addr = offsetof(shm_t, nine);
			e_read(&mem, 0, 0, addr, &anint, sizeof(int));
			break;


	}


	printf("%d	%d \n", oneLoopVar, anint);

}

gettimeofday(&tvEnd, NULL);

temp = ((tvEnd.tv_sec + ((double) tvEnd.tv_usec / 1000000)) -
        (tvStart.tv_sec + ((double) tvStart.tv_usec / 1000000)));

printf("Time: %.4lf seconds.\n", temp);



/****************************************
 	close and end 
****************************************/


 e_close(&dev);
 e_finalize();



	return 1;

}

