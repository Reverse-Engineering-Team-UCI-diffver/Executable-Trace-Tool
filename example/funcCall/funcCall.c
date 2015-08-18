#include<stdio.h>

void func1(){
	printf("This is func1\n");
}

void func2(){
	printf("This is func2\n");
}

int main(){
	func1();
	func2();
	func1();
	return 0;
}

