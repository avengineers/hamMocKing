#include "mockup.h"

mock_ptr_t mockup_global_ptr = nullptr;


extern "C" {

float my_func(float unnamed1){
    if(mockup_global_ptr)
        return mockup_global_ptr->my_func(unnamed1);
    else
        return (float)0;
} /* my_func */
}
