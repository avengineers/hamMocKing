# cmake project definition
cmake_minimum_required(VERSION 3.20.0)

set(CMAKE_C_COMPILER clang CACHE STRING "C Compiler")
set(CMAKE_CXX_COMPILER clang++ CACHE STRING "C++ Compiler")
set(CMAKE_C_COMPILER clang CACHE STRING "C Compiler")
set(CMAKE_CXX_COMPILER clang++ CACHE STRING "C++ Compiler")
project(mini_c)

# GTEST + GMOCK STUFF ####################################
# GoogleTest requires at least C++14
set(CMAKE_CXX_STANDARD 14)

include(FetchContent)
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG release-1.12.1
)

if(WIN32)
    # Prevent overriding the parent project's compiler/linker
    # settings on Windows
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
endif()

FetchContent_MakeAvailable(googletest)

include(GoogleTest)

find_package(Threads REQUIRED)

enable_testing()
# END OF GTEST + GMOCK STUFF #############################

set(PROD_SRC b.c)
set(MOCK_SRC mockup.cc)
set(TEST_SRC b_test.cc)
set(PROD_PARTIAL_LINK prod.obj)

include_directories("includes")

# One command to mock them all!
set(HAMMOCK_DIR ${CMAKE_CURRENT_LIST_DIR}/../../../hammocking)
add_custom_command(
    OUTPUT ${MOCK_SRC}
    BYPRODUCTS mockup.h
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
    COMMAND_EXPAND_LISTS
    COMMAND python ${HAMMOCK_DIR}/hammocking.py --sources ${PROD_SRC} --plink ${CMAKE_CURRENT_BINARY_DIR}/${PROD_PARTIAL_LINK} --outdir ${CMAKE_CURRENT_BINARY_DIR} "-I$<JOIN:$<TARGET_PROPERTY:prodlib,INCLUDE_DIRECTORIES>,;-I>"
    DEPENDS
    ${HAMMOCK_DIR}/hammocking.py
    ${PROD_PARTIAL_LINK}
)

add_library(prodlib OBJECT ${PROD_SRC})

add_custom_command(
    OUTPUT ${PROD_PARTIAL_LINK}
    COMMAND ${CMAKE_CXX_COMPILER} -r -nostdlib -o ${PROD_PARTIAL_LINK} $<TARGET_OBJECTS:prodlib>
    COMMAND_EXPAND_LISTS
    VERBATIM
    DEPENDS $<TARGET_OBJECTS:prodlib>
)

add_executable(
    ${PROJECT_NAME}
    ${MOCK_SRC}
    ${TEST_SRC}
)

target_include_directories(
    ${PROJECT_NAME}
    PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
    ${CMAKE_CURRENT_LIST_DIR}
)

target_link_libraries(
    ${PROJECT_NAME}
    prodlib
    GTest::gtest_main
    GTest::gmock_main
    Threads::Threads
)

gtest_discover_tests(${PROJECT_NAME})

add_custom_command(
    TARGET ${PROJECT_NAME}
    POST_BUILD
    COMMAND ${CMAKE_CTEST_COMMAND} --output-on-failure
)
