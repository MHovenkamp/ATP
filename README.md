# ATP
THis github repository is used for a school assignment. The goal of the assignment is to create an interpreter and compiler for either a made up language or a chosen one, some languages of limit. The interpreter and compiler wil be written in python.

## Chosen language
The chosen language for this assignment is FROM HERE TO THERE by esolang.org user PythonshellDebugwindow.
https://esolangs.org/wiki/FROM_HERE_TO_THERE
The fun of this language is that every line is an assignment. This language is turing complete and provides an example of a truth-machine. is does not have an interpreter or compiler yet. 

### Chosen changes / different interpretations
``` 
FROM x to y 
```
```
FROM function_1 TO DECLARE          // declare function_1

FROM START TO function_1            // start function block
FROM INPUT TO value                 // value now holds the input
FROM value TO OUTPUT                // set output from function
FROM END TO function_1              // end function block

FROM 1 TO function_1                // give input to function_1
FROM function_1 TO output_container // get output from function, program continues from here after function is run
```
*The "if" statements only apply to the scope in or out the function

##### Example Truth_machine
```
FROM IN TO n    // Assign input to variable n
FROM "0" TO 6   // if n == 0 then n is set to 6
FROM "1" TO 4   // if n == 1 then n is set to 4
FROM n TO LINE  // jump to line n, 6 or 4
FROM 1 TO OUT   // print 1 to terminal
FROM 4 TO LINE  // loop back to line 4, restart loop
FROM 0 TO OUT   // print 0 to terminal, terminate program
```

#### Test subroutines
##### Double recursive function
Pseudocode
```
bool even(unsigned intn);
bool odd(unsigned intn);

bool odd(unsigned intn){
    if(n==0){return false;}
    return even(n-1);
}
bool even(unsigned intn) {
    if(n==0){return true;}
    return odd(n-1);
```
FROM HERE TO THERE


