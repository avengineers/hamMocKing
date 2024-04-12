#include <gtest/gtest.h>
using namespace testing;

extern "C"
{
#include "b.h"
}

#include "mockup.h"

TEST(b_test, TestSignalChain_1)
{
  a_y1 = 13;
  b_step();
  EXPECT_EQ(c_u1, 13) << "b_step shall convey value via chain 1.";
}

TEST(b_test, TestSignalChain_2)
{
  CREATE_MOCK(mymock);
  EXPECT_CALL(mymock, a_get_y2()).WillRepeatedly(Return(13));
  EXPECT_CALL(mymock, c_set_u2(13));
  b_step();
}

TEST(b_test, TestSignalChain_3)
{
  CREATE_MOCK(mymock);
  EXPECT_CALL(mymock, a_get_y3_and_set_u5(_)).WillRepeatedly(Return(13));
  EXPECT_CALL(mymock, c_set_u3_and_u4(13, _));
  b_step();
}

/* Introducing a test fixture */

class B : public Test {
  void SetUp() override {
     mock = CREATE_PERSISTENT_MOCK();   // Create the mock handle in the fixture
     // Now some generic reactions can be set up
     ON_CALL(*mock, a_get_y5).WillByDefault(Return(13));
  }
  void TearDown() override {
     DESTROY_PERSISTENT_MOCK();  // Tear down the mock handle to finalize its expecations
  }
  
protected:
   mock_ptr_t mock;
};

TEST_F(B, TestSignalChain_4)
{
  a_y4 = 13;
  EXPECT_CALL(*mock, c_set_u3_and_u4(_, 13));
  b_step();
}

TEST_F(B, TestSignalChain_5)
{
  // Makes use of a_get_y5 behavior from the fixture's setup
  EXPECT_CALL(*mock, c_get_y3_and_set_u5(13));
  b_step();
}

TEST_F(B, TestSignalChain_6)
{
  EXPECT_CALL(*mock, a_get_y6(_))
      .WillOnce(SetArgPointee<0>(13));
  EXPECT_CALL(*mock, c_set_u6(13));
  b_step();
}
