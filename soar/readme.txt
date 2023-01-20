/* -------------------------------------------------------------------
 * SoarSession.java
 *
 * Bob Follek 
 * Thesis I Fall 2002
 * bob@codeblitz.com
 *
 * Version 0.1
 *
 * Copyright (c) 2002, Robert I. Follek
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without 
 * modification, are permitted provided that the following conditions are met:
 *
 * Redistributions of source code must retain the above copyright notice, 
 * this list of conditions and the following disclaimer.
 *
 * Redistributions in binary form must reproduce the above copyright notice, 
 * this list of conditions and the following disclaimer in the documentation 
 * and/or other materials provided with the distribution.
 * Neither the name of the copyright holder nor the names of its contributors 
 * may be used to endorse or promote products derived from this software without 
 * specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
 * THE POSSIBILITY OF SUCH DAMAGE.
 *
 * -----------------------------------------------------------------*/

		SoarSession is a Java class	that lets Java applications use
		Soar. 

		Installation instructions:

		Step 0. Requirements

		Linux
		Java SDK 1.4.x (Very important! 1.3.x is trouble.)
		Tcl 8.0
		Soar 8.3

----------------------------------------------------------------------

		Step 1. Feather

		Feather is Alden Dima's public domain package "that allows a 
		Java application to embed native Tcl interpreters within the 
		same process as the Java virtual machine.". It lets Java 
		programs run Tcl commands.

		Feather is a 0.1 release, but I've been hitting it pretty hard
		without trouble.

		Get Feather and install it:
		http://www.itl.nist.gov/div897/ctg/java/feather/

----------------------------------------------------------------------

		Step 2. Feather for Linux

		The Feather distribution was built for Tcl 8.2, and there's no
		Linux library. To fix this, create a linux/lib subdirectory in
		your feather directory. Then put these files in linux/lib:

			 libfeather.so
			 Makefile

----------------------------------------------------------------------

		Step 3. Environment Variables for Feather

		Add /your/path/to/feather to CLASSPATH.
		Add /your/path/to/feather/linux/lib to LD_LIBRARY_PATH.

----------------------------------------------------------------------

		Step 4. SoarSession

		Create a SoarSession directory. Put these files in it:

			   SoarSession.java
			   SoarSession.class
			   queens.soar
			   queens.ini

----------------------------------------------------------------------

	    Step 5. Environment Variables for SoarSession
			
		Add /your/path/to/SoarSession to CLASSPATH.

----------------------------------------------------------------------

		Step 6. Test SoarSession

		SoarSession.java includes a test stub main function that runs queens.soar.
		
		* Edit queens.ini so that the TCL_DIR and SOAR_DIR params are
		correct for your machine. 
		* cd to your SoarSession directory.
		* java SoarSession queens.ini
		
		queens.soar should run, with output to stdout, like this. (The
		number of moves will vary.) If you get to Goal!, SoarSession
		is  working correctly.

dir = /usr/share/soar-8.3/library
************
     0: ==>S: S1 
Initial positions:
(1,1) (2,5) (3,2) (4,1)
(5,4) (6,4) (7,8) (8,2)
     1:    O: O44 (move-queen)
     2:    O: O68 (move-queen)
     3:    O: O139 (move-queen)
     4:    O: O221 (move-queen)
     5:    O: O225 (move-queen)
     6:    O: O282 (move-queen)
     7:    O: O372 (move-queen)
     8:    O: O421 (move-queen)
     9:    O: O486 (move-queen)
    10:    O: O560 (move-queen)
Goal!
(1,3) (2,6) (3,2) (4,7)
(5,1) (6,4) (7,8) (8,5)
System halted.Exiting Soar...

	