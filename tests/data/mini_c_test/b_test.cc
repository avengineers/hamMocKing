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
  LOCAL_MOCK(mymock);
  EXPECT_CALL(mymock, a_get_y2()).WillRepeatedly(Return(13));
  EXPECT_CALL(mymock, c_set_u2(13));
  b_step();
}

TEST(b_test, TestSignalChain_3)
{
  LOCAL_MOCK(mymock);
  EXPECT_CALL(mymock, a_get_y3_and_set_u5(_)).WillRepeatedly(Return(13));
  EXPECT_CALL(mymock, c_set_u3_and_u4(13, _));
  b_step();
}

TEST(b_test, TestSignalChain_4)
{
  LOCAL_MOCK(mymock);
  a_y4 = 13;
  EXPECT_CALL(mymock, c_set_u3_and_u4(_, 13));
  b_step();
}

TEST(b_test, TestSignalChain_5)
{
  LOCAL_MOCK(mymock);
  EXPECT_CALL(mymock, a_get_y5())
      .WillOnce(Return(13));
  EXPECT_CALL(mymock, c_get_y3_and_set_u5(13));
  b_step();
}

TEST(b_test, TestSignalChain_6)
{
  LOCAL_MOCK(mymock);
  EXPECT_CALL(mymock, a_get_y6(_))
      .WillOnce(SetArgPointee<0>(13));
  EXPECT_CALL(mymock, c_set_u6(13));
  b_step();
}
