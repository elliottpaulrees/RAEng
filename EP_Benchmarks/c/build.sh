#!/bin/bash

set -e

ESDK=${EPIPHANY_HOME}
ELIBS=${ESDK}/tools/host/lib
EINCS=${ESDK}/tools/host/include
ELDF=${ESDK}/bsps/current/fast.ldf

SCRIPT=$(readlink -f "$0")
EXEPATH=$(dirname "$SCRIPT")
cd $EXEPATH

CROSS_PREFIX=
case $(uname -p) in
	arm*)
		# Use native arm compiler (no cross prefix)
		CROSS_PREFIX=
		;;
	   *)
		# Use cross compiler
		CROSS_PREFIX="arm-linux-gnueabihf-"
		;;
esac

# Build HOST side application
${CROSS_PREFIX}gcc src/test.c -o Debug/main.elf -Wall -I ${EINCS} -L ${ELIBS} -le-hal -lm -O3 #-le-loader

# Build DEVICE side program
e-gcc -T ${ELDF} src/testCore.c -o Debug/testCore.elf -Wall -le-lib -lm -O3

e-gcc -T ${ELDF} src/testCore_mutex.c -o Debug/testCore_mutex.elf -Wall -le-lib -lm -O3



# Convert ebinary to SREC file
e-objcopy --srec-forceS3 --output-target srec Debug/testCore.elf Debug/testCore.srec

e-objcopy --srec-forceS3 --output-target srec Debug/testCore_mutex.elf Debug/testCore_mutex.srec




