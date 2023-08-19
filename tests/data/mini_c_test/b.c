#include "b.h"

#include "a.h"
#include "c.h"

// This function is not found in a header, but only here.
extern int local_extern(int x);

void b_init(void){
}

void b_step(void){
    int b1;
    b1 = a_y1;
    c_u1 = b1;

    int b2;
    b2 = a_get_y2();
    c_set_u2(b2);

    int b3;
    b3 = a_get_y3_and_set_u5(0);

    int b4;
    b4 = (int)a_y4;
    c_set_u3_and_u4(b3, b4);

    int b5;
    b5 = (int)a_get_y5();
    (void)c_get_y3_and_set_u5(b5);

    int b6;
    a_get_y6(&b6);
    c_set_u6((c_u6_t)b6);
    
    local_extern(2);
}

int x1 = 1;

int get_x1(void)
{
   return x1;
}