#include <stdio.h>
#include <string.h>

char myFunc(char character)
{
    int key=105;
    return (character)^key;
}

int main() 
{
    char text[8]="testtext";
    int cipher[8];
    int i=0;
    while (i<8)
    {
        cipher[i]=myFunc(text[i]);
        printf("%02x",cipher[i]);
        i++;
    }


    return 0;
}




