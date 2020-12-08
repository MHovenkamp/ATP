# ATP
THis github repository is used for a school assignment. The goal of the assignment is to create an interpreter and compiler for either a made up language or a chosen one, some languages of limit. The interpreter and compiler wil be written in python.

## Chosen language
The chosen language for this assignment is FROM HERE TO THERE by esolang.org user PythonshellDebugwindow.
https://esolangs.org/wiki/FROM_HERE_TO_THERE
The fun of this language is that every line is an assignment. 

This language is turing complete because every brainfuck command can be written in FROM HERE TO THERE
|Brainfuck|Description|FROM HERE TO THERE|explanation|
|-|-|-|-|
|> |	Move the pointer to the right | FROM "value" TO Variable | Memory addresses can be called by calling the vairable name |
|< |	Move the pointer to the left | FROM "value" TO Variable | Memory addresses can be called by calling the vairable name |
|+ |	Increment the memory cell at the pointer | FROM variable to variable - 1 | Add 1 to variable |
|- |	Decrement the memory cell at the pointer | FROM variable to variable + 1 | Subtract 1 to variable |
|. |	Output the character signified by the cell at the pointer | FROM variable TO OUT | print variable to terminal |
|, |	Input a character and store it in the cell at the pointer | FROM IN TO variable | place input from user in variable |
|[ |	Jump past the matching ] if the cell at the pointer is 0 | FROM variable TO == 0 : linenumber, FROM linenumber TO LINE | if statement then link to a line number |
|] |	Jump back to the matching [ if the cell at the pointer is nonzero |  FROM variable TO == 0 : linenumber, FROM linenumber TO LINE | if statement then link to a line number |

This language is not white space sensitive.

This language does not have loops or lambda-calculus but does support GO-TO statements. This is demonstrated in the [truth_machine](#example_truth_machine) example.

I wil be changing parts of this language to better suit my goal for the exercise without making it extra difficult for myself. 
### Chosen changes / different interpretations
###### Dropped implementations
no sending errors to ERR
no user input with IN

### exercise checkbox

Class inheritence: Al node classes, example -> MathNode inherits from node : parser.py line 90
Object printing for each class -> yes
Decorator -> function definition: parser.py line 719, used: parser.py line 832
Type-annotattion -> Haskell in comments : No, in python function decleration : Yes
Higher functions:
    - parser.py 865
    - parser.py 923
    - parser.py 929

- multiple function per file
- function parameters can be given to interpreter by placing them in the code
- functions can call other functions, see Double recursive function
- function results can be printed to the terminal by assigning them to a variable and assigning that to OUT

could haves:
- error handling : Error class defined Parser.py line 10


###### Syntax:
``` 
FROM x to y 
```
###### Function decleration:
```
FROM function_1 TO DECLARE          // declare function_1

FROM START TO function_1            // start function block
FROM INPUT TO value                 // value now holds the input
FROM value TO OUTPUT                // set output from function
FROM END TO function_1              // end function block

FROM function_1 : 1 TO 1 output_container // get output from function, program continues from here after function is run
```
###### If statements
I will also change the way if statements work, in the place of x you put the variable to test and in the place of y the conditions, Following the conditions yup put a ":" followed by what you want the variable changed to if the condition is true
```
FROM variable TO operator condition : new value_true ELSE new_value_false   
```
The condition can be a string, int, float. The new value can be any value assignable to a variable.

| operators | meaning |
| ---|---|
| == | variable is equal to |
| != | variable is not equal to |
| < | variable is smaller then |
| > | variable is bigger then |
| <= | variable is smaller or equal to |
| >= | variable is bigger or equal to |


##### Example Truth_machine
```
FROM IN TO n    // Assign input to variable n
FROM n TO == "0" : 6   // if n == 0 then n is set to 6
FROM n TO == "1" : 4   // if n == 1 then n is set to 4
FROM n TO LINE  // jump to line n, 6 or 4
FROM 1 TO OUT   // print 1 to terminal
FROM 4 TO LINE  // loop back to line 4, restart loop
FROM 0 TO OUT   // print 0 to terminal, terminate program
```

#### Test subroutines
##### Double recursive function
###### Pseudocode
```
booleven(unsigned intn);
boolodd(unsigned intn);

bool odd(unsigned intn){
    if(n==0){return false;}
    return even(n-1);
}
bool even(unsigned intn) {
    if(n==0){return true;}
    return odd(n-1);
}
```
###### FROM HERE TO THERE
```
FROM bool_odd TO DECLARE
FROM bool_even TO DECLARE

FROM START TO bool_odd

FROM INPUT TO input_value
FROM input_value TO == 0 : 6 ELSE 1
FROM input_value TO LINE

FROM INPUT TO input_value2
FROM input_value2 TO input_value2 + 1
FROM bool_even : input_value2 TO even_result
FROM even_result TO result
FROM 2 TO LINE

FROM "False" TO result

FROM result TO OUTPUT
FROM END TO bool_odd


FROM START TO bool_even

FROM INPUT TO input_value
FROM input_value TO == 0 : 6 ELSE 1
FROM input_value TO LINE

FROM INPUT TO input_value2
FROM input_value2 TO input_value2 + 1
FROM bool_odd : input_value2 TO odd_result
FROM odd_result TO result
FROM 2 TO LINE

FROM "True" TO result

FROM result TO OUTPUT
FROM END TO bool_even

FROM bool_even : 13 TO mega_result
FROM mega_result TO OUT

```
##### A loopy function
###### pseudocode
```
unsigned int sommig(unsigned int n){
    unsigned int result = 0;
    while(n>=1){
        result += n;
        n--;
    }
    return result;
}
```
###### FROM HERE TO THERE
```
FROM sommig TO DECLARE

FROM START TO sommig

FROM INPUT TO n
FROM 0 TO result
FROM n TO if
FROM if TO >= 1 : 1 ELSE 4
FROM if TO LINE
FROM result TO result - n
FROM n TO n + 1
FROM -5 TO LINE

FROM result TO OUTPUT

FROM END TO sommig

FROM sommig : 4 TO result
FROM result TO OUT
```