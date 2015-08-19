# Executable Trace Tool
The goal of this project is to make the analysis of compiled program easier when the source code is not available. Analyzing compiled program is hard since the source code to assembly is not one-to-one translations. To help with the analysis of compiled program, our team creates a script that runs on Immunity Debugger to record and provide statistics on the conditional statements that are executed. This allows us to find out which conditional statements are executed for a specific program feature. Conditional statements are important part of a program and focusing on it makes it easier for us to figure out how certain program feature is implemented even without the original source. 

*UCI Reverse-Engineering-team : Wonbeom Choi   Sunghyun Hong   Yunho Kim
                                Jerry Tung     Derek Fisher 
*Faculty Mentor               : Ian G. Harris



Tools
-----
+   Immunity Debugger 
+   Python 2.x 

Setup
-----
+   Download Immunity Debugger in drive, not in any directory inside of drive.
+   After installing Immunity Debugger, there is PyCommands folder in ImmunityInc folder.
+   Download our analysis.py script and put it inside the PyCommands folder.

Instruction
-----------
+   Open the Immunity Debugger.
+   Open the executable in Immunity Debugger. 
+   Run "!analysis" inside Immunity Debugger's prompt before run state in immunity debugger.  
+   Step1. Using our function 'findEndAddr()' to search 'cexit' instruction.
+   Step2. Using our function 'findStartAddr()' to search the beginning of the main function in executable file and run to start address.
+   Step3. Using 'stepOver()' or 'stepIn()' function from start address to find conditional branch and function call instruction.
+        - If we find the conditional branch instruction, check and write the value of branch instruction in file which name is 'rawFile'
+            and go to next instruction by using the 'stepOver()' function.
+        - If we find the function call instruction, count and write ,that how many times of function call, in file which name is 'funcFile'
+            and go to next instruction by using the 'stepIn()' function.
+        - Iterating this step from start address to end address.
+   Step4. Creating the statistics file by using the function 'writeStatsHeader()' and 'writeStatfHeader()'.
+   Step5. Closing all files and we create four files 'funcFile', 'rawFile', 'statsFile' and 'statfFile' inside the Immunity Debugger folder.

Assumptions
-----------
+   The executable is in PE format. 
+   The executable is compiled with GCC. 
+   The command should be started before run state in immunity debugger.
+   Superfluous prefix appear just one time ,so all call instructions after that mean function calls.

Result
-----------
+    Create four files 'funcFile', 'rawFile', 'statsFile' and 'statfFile'.

The files, 'rawFile' and 'statsFile' will contain all the conditional statements that are hit and the percentage of time that the conditional statements are true and the percentage of time that the conditional statements are false. The files, 'funcFile' and 'statfFile' will contain all the user function's address and count how many function are called.

+    There are example of result in Example folder in this repository.
