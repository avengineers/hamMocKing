#include "mockup.h"

mock_ptr_t mockup_global_ptr = nullptr;


extern "C" {

void set_some_int(int some_value){
    if(mockup_global_ptr)
        mockup_global_ptr->set_some_int(some_value);
} /* set_some_int */
}
