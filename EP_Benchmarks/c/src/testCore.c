/*
 * Origion version: Copyright (c) 2010 Derrell Lipman
 * Parallel Kernel EP: An embarrassingly parallel benchmark
 * C with MPI implementation

 * Adapted by Elliott Rees to benchmark an apiphany chip on a Parallella board
 * as part of the the resarch paper: 
 * "Dynamix Language Support for Low-Power Accelerated Architectures"
 *  for none profit research.

 * Website: www.elliottpaulrees.biz
 * Email: elliottpaulrees@gmail.com
 */



#include <stdio.h>
#include <math.h>
#include "e-lib.h"
#include "common.h"

///////////////////////////////////
//      Global variables
///////////////////////////////////

volatile shm_t shm SECTION(".shared_dram"); //saves the shm_t struct (from common.h) into shared RAM 

e_mutex_t *mutex_p;

#define INITIAL_SEED    271828183

static int      p = 1;
static double   n;
static double   a;
static double   random_seed;

static double   POW_2_N23; /* 2^-23 */
static double   POW_2_23;  /* 2^23 */
static double   POW_2_N46; /* 2^-46 */
static double   POW_2_46;  /* 2^46 */

#ifndef FALSE
# define        FALSE   (0)
# define        TRUE    (! FALSE)
#endif



/** Structure to provide pairs of random numbers */
typedef struct Pair
{
    double          x;
    double          y;
} Pair;


/**
 * Find the maximum of two floating-point numbers.
 *
 * @param a
 *   The first of two numbers to be compared
 *
 * @param b
 *   The second of two numbers to be compared
 *
 * @return
 *   The floor of the maximum of the two parameter values.
 */
int
maximum(double a, double b)
{
    /* Return the integer (truncated) value of the maximum of a and b */
    return a >= b ? a : b;
}


/**
 * Multiple two floating point numbers, modulo 46.
 *
 * @param a
 *   The first of two numbers to be multiplied
 *
 * @param b
 *   The second of two numbers to be multiplied
 *
 * @return
 *   The modulo 46 product of the two parameter values.
 */
double
multiplyModulo46(double a, double b)
{
    static int          bInitialized = FALSE;
    double              a1;
    double              a2;
    double              b1;
    double              b2;
    double              t1;
    double              t2;
    double              t3;
    double              t4;
    double              t5;

    /* Have we initialized our very large and very small numbers? */
    if (! bInitialized)
    {
        /* Nope. Do it now. */
        POW_2_N23 = pow(2, -23);
        POW_2_23  = pow(2,  23);
        POW_2_N46 = pow(2, -46);
        POW_2_46  = pow(2,  46);

        /* Now we're initialized, so we don't need to run that code again. */
        bInitialized = TRUE;
    }

    /* Implementation of the modulo-46 multiplication from the NAS Benchmark */
    a1 = floor(POW_2_N23 * a);
    a2 = a - POW_2_23 * a1;
    b1 = floor(POW_2_N23 * b);
    b2 = b - POW_2_23 * b1;
    t1 = (a1 * b2) + (a2 * b1);
    t2 = floor(POW_2_N23 * t1);
    t3 = t1 - (POW_2_23 * t2);
    t4 = (POW_2_23 * t3) + (a2 * b2);
    t5 = floor(POW_2_N46 * t4);

    return t4 - (POW_2_46 * t5);
}


/**
 * Calculate and return the next pseudo-random number.
 *
 * @side-effects
 *   The global value random_seed is set to the seed for the random number of
 *   the next call to this function.
 *
 * @return
 *   The next pseudo-random number, as determined from the pre-existing seed.
 */
double
pseudorandom(void)
{
    double                      oldS;
    double                      ret;

    /* Save the old seed as it's used to calculate the return value */
    oldS = random_seed;

    /* Calculate the next seed */
    random_seed = multiplyModulo46(a, random_seed);

    /* Calculate the return value based on the current seed */
    ret = POW_2_N46 * oldS;
    return ret;
}


/**
 * Get the seed for the kth pseudo-random number
 *
 * @param k
 *   The index of the pseudo-random number for which the seed is desired
 *
 * @return
 *   The seed for the random number at the index specified by the parameter.
 */
double
getSeedFor(double k)
{
    int             i;
    int             j;
    double          b;
    double          t;
    int             m;

    m = floor(log2(k)) + 1;
    b = INITIAL_SEED;
    t = a;
    for (i = 1; i <= m; i++)
    {
        j = k / 2;
        if (2 * j != k)
        {
            b = multiplyModulo46(b, t);
        }
        t = multiplyModulo46(t, t);
        k = j;
    }

    return b;
}


/**
 * Get a pair of random numbers, scaled to the range (-1, 1).
 *
 * @return
 *   A pair of pseudo-random numbers, each of which is in the range (-1, 1)
 */
Pair
randomPair(void)
{
    Pair            pair;

    pair.x = 2 * pseudorandom() - 1;
    pair.y = 2 * pseudorandom() - 1;

    return pair;
}


/**
 * Implementation of the main EP loop, generating pairs of pseudorandom
 * numbers, deciding if they're acceptable, tracking counts, and calculating
 * sums. This procedure is itself not free, but makes use of many free
 * sub-procedures.
 */
void
ep(void)
{
    unsigned long   j;
    int             maxXY;
    Pair            pair;
    double          t;
    double          temp;
 /*
Memory Allocation for a single integer
*/

  /* Each process generates n/p acceptable pairs of numbers */
    for (j = 1; j <= n / p; j++)
    {
        /* Generate a random number pair */
        pair = randomPair();

        /* Is this pair acceptable? */

	 t = (pair.x * pair.x) + (pair.y * pair.y);
 
	if (t > 1)
        {
            /* Nope. Reject */
            continue;
        }

       /* Calculate the multiplier for the values in this pair, and multiply */
        temp = sqrt((-2 * log(t)) / t);
        pair.x *= temp;
        pair.y *= temp;

        /*
         * Find the maximum of the absolute value of each value in the
         * pair. Take the floor of that maximum (by converting it to an
         * integer) so that we can use it as an index into the results
         * counters array.
         */
        maxXY = maximum(fabs(pair.x), fabs(pair.y));

       /* Update the appropriate counter in shared memory  corresponding to the value of maxXY. */
  
		e_mutex_lock(0, 0, mutex_p);


		switch(maxXY)
		{
			case 0:

				shm.naught++;

				break;

			case 1:

				shm.one++;

        	                break;


			case 2:

				shm.two++;

                        	break;


			case 3:

				shm.three++;

                        	break;



			case 4:

				shm.four++;

                        	break;



			case 5:

				shm.five++;

                        	break;


			case 6:

				shm.six++;

                        	break;



			case 7:

				shm.seven++;

                       		 break;



			case 8:

				shm.eight++;

                       		 break;



			case 9:
				shm.nine++;
		}



	e_mutex_unlock(0, 0, mutex_p);

	}
}

int
main(int argc, char * argv[]){

 //Define memory location to be used as a mutex
	mutex_p = (void*) 0x00004000;


        //memomory allocation to be used as a flag which informs the main core the program has completed running
        unsigned *d;
        d    = (unsigned *) 0x7000;

        //Setup
        p = Cores; //numberOfCores defined in common.h
        a = pow(5, 13);
        n = pow(2, Nno); //Nno defined in common.h
        random_seed = INITIAL_SEED;

        ep(); //Start the EP test


        //Raising "done" flag
        (*(d)) = 0x00000001;

        __asm__ __volatile__("idle");


return 0;
}

