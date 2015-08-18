#include<stdio.h>

void func1(){
	printf("This is func1\n");
}

void func2(){
	printf("This is func2\n");
	func1();
}

int main(){
	int i = 0;
	for (i = 0; i < 6; i++){
		if (i % 2 == 0)
			func1();
		else
			func2();
	}
	return 0;
}

