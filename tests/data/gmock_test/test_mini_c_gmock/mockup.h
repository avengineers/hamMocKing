#ifndef mockup_h
#define mockup_h

#include "gmock/gmock.h" 

extern "C" {
#include "a.h"
#include "c.h"
} /* extern "C" */

class class_mockup;
typedef class_mockup* mock_ptr_t;
extern mock_ptr_t mockup_global_ptr;

class class_mockup {

 public:
   class_mockup()  { mockup_global_ptr = this; }
   ~class_mockup() { mockup_global_ptr = nullptr; }
   MOCK_METHOD((int), a_get_y2, ());
   MOCK_METHOD((int), a_get_y3_and_set_u5, (int));
   MOCK_METHOD((int), a_get_y5, ());
   MOCK_METHOD((void), a_get_y6, (int *));
   MOCK_METHOD((int), c_get_y3_and_set_u5, (int));
   MOCK_METHOD((void), c_set_u2, (int));
   MOCK_METHOD((void), c_set_u3_and_u4, (int, int));
   MOCK_METHOD((void), c_set_u6, (int));
}; /* class_mockup */

/* Version A: Create a local object that is destroyed when out of scope */
#define CREATE_MOCK(name)   class_mockup name

/* Version B: Allocate an object that will be only explicitly deallocated */
#define CREATE_PERSISTENT_MOCK()     new class_mockup
#define DESTROY_PERSISTENT_MOCK()    {if(mockup_global_ptr) delete mockup_global_ptr;}

#endif /* mockup_h */
