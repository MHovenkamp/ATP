#include "hwlib.hpp"
#include <algorithm>
#include <string.h>

extern "C" int divide(int a, int b){
  return a / b;
}

extern "C" void print_number(int x)
{
    hwlib::cout << x << "\n";
    return;
}

extern "C" void print_word(char* x)
{
  unsigned int length_of_word = strlen(x);
  std::for_each( x, x+length_of_word, []( const char a){hwlib::cout << a;});
  hwlib::cout << hwlib::endl;
  return;
}

extern "C" int fib(int x);
extern "C" int sommig(int x);
extern "C" int bool_even(int x);
extern "C" int bool_odd(int x);

// TEST_CASE( "sommig functie"){
//   hwlib::cout << "start program from main.cpp \n";
//   REQUIRE( sommig(4) == 10);
//   REQUIRE( sommig(10) == 55);
//   hwlib::cout << "end program from main.cpp \n";
// };



int main(){
  hwlib::wait_ms(4000);
  hwlib::cout << "start program \n";
  if( bool_even(1) == 0 ){
    hwlib::cout << "TEST COMPLETE, booleven(1) == 0 \n";
  } else{
    hwlib::cout << "TEST FAILED, booleven(1) == 0 \n";
  }
  if( bool_odd(1) == 1 ){
    hwlib::cout << "TEST COMPLETE, bool_odd(1) == 1 \n";
  } else{
    hwlib::cout << "TEST FAILED, bool_odd(1) == 1 \n";
  }
  if( bool_even(11) == 0 ){
    hwlib::cout << "TEST COMPLETE, booleven(11) == 0 \n";
  } else{
    hwlib::cout << "TEST FAILED, booleven(11) == 0 \n";
  }
  if( bool_odd(11) == 1 ){
    hwlib::cout << "TEST COMPLETE, bool_odd(11) == 1 \n";
  } else{
    hwlib::cout << "TEST FAILED, bool_odd(11) == 1 \n";
  }
  if( bool_even(8) == 1 ){
    hwlib::cout << "TEST COMPLETE, bool_even(8) == 1 \n";
  } else{
    hwlib::cout << "TEST FAILED, bool_even(8) == 1 \n";
  }
  if( bool_odd(8) == 0 ){
    hwlib::cout << "TEST COMPLETE, bool_odd(8) == 0 \n";
  } else{
    hwlib::cout << "TEST FAILED, bool_odd(8) == 0 \n";
  } if( fib(10) == 89 ){ // fibonacci
    hwlib::cout << "TEST COMPLETE, code(10) == 89 \n";
  } else{
    hwlib::cout << "TEST FAILED, code(10) == 89 \n";
  }
  hwlib::cout << "end program \n";
  return 1;
}
