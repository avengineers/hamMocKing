#include "mockup.h"

mock_ptr_t mockup_global_ptr = nullptr;

int a_y1;
int a_y4;
int c_u1;
const int const_a = (const int)0;
const int const_array[3] = {0};

extern "C" {

int a_get_y2(){
    if(mockup_global_ptr)
        return mockup_global_ptr->a_get_y2();
    else
        return (int)0;
} /* a_get_y2 */

int a_get_y3_and_set_u5(int u5){
    if(mockup_global_ptr)
        return mockup_global_ptr->a_get_y3_and_set_u5(u5);
    else
        return (int)0;
} /* a_get_y3_and_set_u5 */

int a_get_y5(){
    if(mockup_global_ptr)
        return mockup_global_ptr->a_get_y5();
    else
        return (int)0;
} /* a_get_y5 */

void a_get_y6(int * y6){
    if(mockup_global_ptr)
        mockup_global_ptr->a_get_y6(y6);
} /* a_get_y6 */

int c_get_y3_and_set_u5(int u5){
    if(mockup_global_ptr)
        return mockup_global_ptr->c_get_y3_and_set_u5(u5);
    else
        return (int)0;
} /* c_get_y3_and_set_u5 */

void c_set_u2(int u2){
    if(mockup_global_ptr)
        mockup_global_ptr->c_set_u2(u2);
} /* c_set_u2 */

void c_set_u3_and_u4(int u3, int u4){
    if(mockup_global_ptr)
        mockup_global_ptr->c_set_u3_and_u4(u3, u4);
} /* c_set_u3_and_u4 */

void c_set_u6(int u6){
    if(mockup_global_ptr)
        mockup_global_ptr->c_set_u6(u6);
} /* c_set_u6 */
}
