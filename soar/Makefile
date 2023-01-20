# Changes for linux. Also made tcl version flexible.

JAVA_INC = /usr/java/j2sdk1.4.1/include
JAVA_LINUX_INC = ${JAVA_INC}/linux
SRC_DIR = ../../src
TCL_VERSION = 8.0
LIBS = -ltcl${TCL_VERSION} -ldl -lm

feather.so : ${SRC_DIR}/feather.c
	gcc -Wall -shared -I${JAVA_INC} -I${JAVA_LINUX_INC} \
	${SRC_DIR}/feather.c -o libfeather.so ${LIBS}

clean :	
	rm libfeather.so

