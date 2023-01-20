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

import java.io.*;
import java.text.*;
import java.util.*;

import nist.feather.*;

// -------------------------------------------------------------------

class SoarSession extends TclInterpreter {

	public SoarSession(String tclDir, String soarDir)
		throws TclEvalException {

		super();
		construct(tclDir, soarDir);
	}

// -------------------------------------------------------------------

	// Alternative constructor - uses properties file
	public SoarSession(String propertiesFile) 
		throws TclEvalException, FileNotFoundException, IOException {

		super();
		Properties props = new Properties();
	    props.load(new FileInputStream(propertiesFile));
	    String tclDir = props.getProperty("TCL_DIR");
	    String soarDir = props.getProperty("SOAR_DIR");
		construct(tclDir, soarDir);
	}

// -------------------------------------------------------------------

	public void init() 
		throws TclEvalException {

		eval("init-soar");
	}

// -------------------------------------------------------------------

	public void loadAgent(String agentFile) 
		throws TclEvalException {

		evalFile(new File(agentFile));
	}

// -------------------------------------------------------------------

	public void run()
		throws TclEvalException {

		eval("run");
	}

// -------------------------------------------------------------------

	public void runTillOutput()
		throws TclEvalException {

		eval("run out");
	}

// -------------------------------------------------------------------

	public void stop()
		throws TclEvalException {

		eval("quit");
	}

// -------------------------------------------------------------------

	public void finalize() {

		try {
			stop();
		}
		catch (TclEvalException tee) {
			// ignore it
		}
	}

// -------------------------------------------------------------------

	public boolean setPrintCommandBeforeEval(boolean b) {

		boolean old = m_printCommandBeforeEval;
		m_printCommandBeforeEval = b;
		return old;
	}

// -------------------------------------------------------------------

	public String eval(String cmd) 
		throws TclEvalException {

		if (m_printCommandBeforeEval) {
			printCommandBeforeEval(cmd);
		}
	    return super.eval(cmd);
	}

// -------------------------------------------------------------------

	private void construct(String tclDir, String soarDir)
		throws TclEvalException {

		String cmd = MessageFormat.format(START_TCL, new String[] {tclDir});
		eval(cmd);
		cmd = MessageFormat.format(START_SOAR, new String[] {soarDir});
		eval(cmd);
		init();
	}

// -------------------------------------------------------------------

	private void printCommandBeforeEval(String cmd) {

		System.out.println("SoarSession - About to eval: " + cmd);
		System.out.flush();
	}

// -------------------------------------------------------------------

	// For testing
	static public void main(String[] args)
		throws TclEvalException, FileNotFoundException, IOException {

		SoarSession ss = null;

		switch (args.length) {
		case 2:
			String tclDir = args[0];
			String soarDir = args[1];
			ss = new SoarSession(tclDir, soarDir);
			break;
		case 1:
			String propertiesFile = args[0];
			ss = new SoarSession(propertiesFile);
			break;
		default:
			System.out.println("Usage error!");
			System.out.println("Usage: SoarSession tclDir soarDir");
			System.out.println("Or   : SoarSession propertiesFile");
			System.exit(1);
		}
	
		ss.loadAgent("queens.soar");
		ss.run();
		ss.stop();
	}

// -------------------------------------------------------------------

	private boolean m_printCommandBeforeEval = false;

// -------------------------------------------------------------------

	static private final String START_TCL = 
		"set tcl_library [file join \"{0}\" library];\n" +
		"source [file join \"{0}\" init.tcl];\n";

	static private final String START_SOAR = 
		"set soar_library [file join \"{0}\" library];\n" +
		"set env(SOAR_LIBRARY) $soar_library;\n" +
		"lappend auto_path  $soar_library;\n" + 
		"set soar_doc_dir [file join $soar_library ../doc];\n" +
		"package require Soar;\n";

// -------------------------------------------------------------------

}

