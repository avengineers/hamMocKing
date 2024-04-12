#!/usr/bin/env python3

import unittest

import pytest

from hammocking.hammocking import *

# Apply default config
ConfigReader()

def clang_parse(snippet: str):
    parseOpts = {
        "path": "~.c",
        "unsaved_files": [("~.c", snippet)],
        "options": TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE,
    }
    translation_unit = Index.create(excludeDecls=True).parse(**parseOpts)
    def is_var_or_func(c: Cursor) -> bool:
        return c.kind == CursorKind.VAR_DECL or c.kind == CursorKind.FUNCTION_DECL
    return next(filter (is_var_or_func, Hammock.iter_children(translation_unit.cursor)))

class TestVariable:
    def test_simple(self):
        "Basic type"
        v = Variable(clang_parse("char x"))
        assert v.name == "x"
        assert v.is_constant() == False
        assert v.get_definition() == "char x"
        assert v.initializer() == "(char)0"
        
    def test_array(self):
        "Array type"
        w = Variable(clang_parse("int my_array[2]"))
        assert w.name == "my_array"
        assert w.is_constant() == False
        assert w.get_definition() == "int my_array[2]"
        assert w.initializer() == "{0}"

    def test_unlimited_array(self):
        "Unlimited array type"
        w = Variable(clang_parse("int my_array[]"))
        assert w.name == "my_array"
        assert w.is_constant() == False
        assert w.get_definition() == "int my_array[]"
        assert w.initializer() == "{0}"  # Cannot be initialized, but hey...

    def test_constant(self):
        "Basic constant"
        w = Variable(clang_parse("const int y;"))
        assert w.name == "y"
        assert w.is_constant() == True
        assert w.get_definition() == "const int y"
        assert w.initializer() == "(const int)0"

    def test_constant_array(self):
        "Basic constant array"
        w = Variable(clang_parse("const int y[3];"))
        assert w.name == "y"
        assert w.is_constant() == True
        assert w.get_definition() == "const int y[3]"
        assert w.initializer() == "{0}"

    def test_constant_struct(self):
        "Constant structure"
        w = Variable(clang_parse("""
            typedef struct { int a; int b; } y_t; 
            extern const y_t y;"""))
        assert w.name == "y"
        assert w.is_constant() == True
        assert w.get_definition() == "const y_t y"
        assert w.initializer() == "(const y_t){0}"

    def test_ptr_int(self):
        "Pointer to integer"
        w = Variable(clang_parse("""int *ptr;"""))
        assert w.name == "ptr"
        assert w.is_constant() == False
        assert w.get_definition() == "int * ptr"
        assert w.initializer() == "(int *)0"

    def test_ptr_func(self):
        "Pointer to function"
        w = Variable(clang_parse("""int (*func)(int,int)"""))
        assert w.name == "func"
        assert w.is_constant() == False
        assert w.get_definition() == "int (*func)(int,int)"
        assert w.initializer() == "(int (*)(int, int))0"

    def test_constant_ptr(self):
        "Constant pointer"
        w = Variable(clang_parse("""const int *y;"""))
        assert w.name == "y"
        assert w.is_constant() == False
        assert w.get_definition() == "const int * y"
        assert w.initializer() == "(const int *)0"

    def test_ptr_to_constant(self):
        "Pointer to constant"
        w = Variable(clang_parse("""int *const y;"""))
        assert w.name == "y"
        assert w.is_constant() == True
        assert w.get_definition() == "int *const y"
        assert w.initializer() == "(int *const)0"


class TestFunction:
    def test_void_void(self):
        "returns void / void parameters"
        f = Function(clang_parse("void func(void);"))
        assert f.name == "func"
        assert f.get_signature() == "void func()"
        assert f.get_call() == "func()"
        assert f.get_param_types() == ""
        assert f.has_return_value() == False
        assert f.default_return() == "void"  # "return void" is a valid way to exit a void function

    def test_void_int(self):
        "Integer parameter"
        f = Function(clang_parse("void set(int a);"))
        assert f.name == "set"
        assert f.get_signature() == "void set(int a)"
        assert f.get_call() == "set(a)"
        assert f.get_param_types() == "int"
        assert f.has_return_value() == False

    def test_int_void(self):
        "Integer return type"
        f = Function(clang_parse("int get(void);"))
        assert f.name == "get"
        assert f.get_signature() == "int get()"
        assert f.get_call() == "get()"
        assert f.get_param_types() == ""
        assert f.has_return_value() == True
        assert f.default_return() == "(int)0"

    def test_typedef_int(self):
        "Integer/typedef return type"
        f = Function(clang_parse("typedef int some_type; some_type get(void);"))
        assert f.name == "get"
        assert f.get_signature() == "some_type get()"
        assert f.get_call() == "get()"
        assert f.get_param_types() == ""
        assert f.has_return_value() == True
        assert f.default_return() == "(some_type)0"

    def test_void_int_double(self):
        "Integer and double parameters"
        f = Function(clang_parse("void set(int a, double b);"))
        assert f.name == "set"
        assert f.get_signature() == "void set(int a, double b)"
        assert f.get_call() == "set(a, b)"
        assert f.get_param_types() == "int, double"
        assert f.has_return_value() == False

    def test_function_with_unnamed_arguments(self):
        "Unnamed arguments"
        f = Function(clang_parse("float my_func(float, float);"))
        assert f.name == "my_func"
        assert f.get_signature() == "float my_func(float unnamed1, float unnamed2)"
        assert f.get_call() == "my_func(unnamed1, unnamed2)"
        assert f.get_param_types() == "float, float"
        assert f.default_return() == "(float)0"

    def test_variadic_function(self):
        "Variadic function"
        f = Function(clang_parse("int printf_func(const char* fmt, ...);"))
        assert f.name == "printf_func"
        assert f.get_signature() == "int printf_func(const char * fmt, ...)"
        assert f.get_call() == "printf_func(fmt)" # TODO
        assert f.get_param_types() == "const char *"  # ?

    def test_array_param(self):
        "Takes an array parameter"
        f = Function(clang_parse("void x(int arg[]);"))
        assert f.name == "x"
        assert f.get_signature() == "void x(int arg[])"
        assert f.get_call() == "x(arg)"
        assert f.get_param_types() == "int[]"

    def test_funcptr_param(self):
        "Takes a function-pointer parameter"
        f = Function(clang_parse("void x(int (*cb)(void));"))
        assert f.name == "x"
        assert f.get_signature() == "void x(int (*cb)())"
        assert f.get_call() == "x(cb)"
        assert f.get_param_types() == "int (*)(void)"

    def test_blank_func(self):
        "Blank (nonproto) function"
        f = Function(clang_parse("void x();"))
        assert f.name == "x"
        assert f.get_signature() == "void x()"
        assert f.get_call() == "x()"
        assert f.get_param_types() == ""

    def test_const_ptr_return(self):
        "const-Pointer const-value return type"
        f = Function(clang_parse("const char* const x(void);"))
        assert f.name == "x"
        assert f.return_type == "const char *const"
        assert f.get_signature() == "const char *const x()"
        assert f.get_call() == "x()"
        assert f.get_param_types() == ""
        assert f.default_return() == "(const char *const)0"

    def test_struct_param_func(self):
        "Structure type parameter"
        f = Function(clang_parse("""
            typedef struct { int a; int b; } x_t; 
            extern void f(x_t x);"""))
        assert f.name == "f"
        assert f.return_type == "void"
        assert f.get_signature() == "void f(x_t x)"
        assert f.get_call() == "f(x)"
        assert f.get_param_types() == "x_t"
        assert f.has_return_value() == False

    def test_struct_type_return_func(self):
        "Structure/typedef return type"
        f = Function(clang_parse("""
            typedef struct { int a; int b; } x_t; 
            extern x_t f();"""))
        assert f.name == "f"
        assert f.return_type == "x_t"
        assert f.get_signature() == "x_t f()"
        assert f.get_call() == "f()"
        assert f.get_param_types() == ""
        assert f.default_return() == "(x_t){0}"

    def test_named_struct_return_func(self):
        "Structure return type"
        f = Function(clang_parse("""
            struct x_s { int a; int b; }; 
            struct x_s f();
        """))
        assert f.name == "f"
        assert f.return_type == "struct x_s"
        assert f.get_signature() == "struct x_s f()"
        assert f.get_call() == "f()"
        assert f.get_param_types() == ""
        assert f.default_return() == "(struct x_s){0}"

    def test_enum_param(self):
        "enum/typedef parameter"
        f = Function(clang_parse("""
            typedef enum { FIRST; SECOND } e_t; 
            void f(e_t param);
        """))
        assert f.name == "f"
        assert f.return_type == "void"
        assert f.get_signature() == "void f(e_t param)"
        assert f.get_call() == "f(param)"
        assert f.get_param_types() == "e_t"

    def test_named_enum_param(self):
        "named enum parameter"
        f = Function(clang_parse("""
            enum some_enum { FIRST; SECOND }; 
            void f(enum some_enum param);
        """))
        assert f.name == "f"
        assert f.return_type == "void"
        assert f.get_signature() == "void f(enum some_enum param)"
        assert f.get_call() == "f(param)"
        assert f.get_param_types() == "enum some_enum"

    def test_named_enum_return(self):
        "named enum return"
        f = Function(clang_parse("""
            enum some_enum { FIRST; SECOND }; 
            enum some_enum get_enum(void);
        """))
        assert f.name == "get_enum"
        assert f.return_type == "enum some_enum"
        assert f.get_signature() == "enum some_enum get_enum()"
        assert f.get_call() == "get_enum()"
        assert f.default_return() == "(enum some_enum)0"


class TestMockupWriter:
    def test_empty_templates(self):
        writer = MockupWriter()
        assert writer.get_mockup('mockup.h') == open("tests/data/gmock_test/test_empty_templates/mockup.h").read()
        assert writer.get_mockup('mockup.cc') == open("tests/data/gmock_test/test_empty_templates/mockup.cc").read()

    @pytest.mark.parametrize(
        "filename,suffix,expected_name",
        [
            ("my_file.c.j2", None, "my_file.c"),
            ("my_file.cpp.j2", "_new", "my_file_new.cpp")
        ],
    )
    def test_create_out_filename(self, filename, suffix, expected_name):
        """ @validates Req0001 """
        writer = MockupWriter(suffix=suffix)
        assert writer.create_out_filename(filename) == expected_name

    def test_add_header(self):
        writer = MockupWriter()
        writer.add_header("y.h")
        writer.add_header("a.h")
        writer.add_header("x.h")
        assert (
                writer.get_mockup('mockup.h')
                == """#ifndef mockup_h
#define mockup_h

#include "gmock/gmock.h" 

extern "C" {
#include "a.h"
#include "x.h"
#include "y.h"
} /* extern "C" */

class class_mockup;
typedef class_mockup* mock_ptr_t;
extern mock_ptr_t mockup_global_ptr;

class class_mockup {

 public:
   class_mockup()  { mockup_global_ptr = this; }
   ~class_mockup() { mockup_global_ptr = nullptr; }
}; /* class_mockup */

/* Version A: Create a local object that is destroyed when out of scope */
#define CREATE_MOCK(name)   class_mockup name

/* Version B: Allocate an object that will be only explicitly deallocated */
#define CREATE_PERSISTENT_MOCK()     new class_mockup
#define DESTROY_PERSISTENT_MOCK()    {if(mockup_global_ptr) delete mockup_global_ptr;}

#endif /* mockup_h */
"""
        )

    def test_add_variable(self):
        writer = MockupWriter(suffix="_new")
        writer.add_variable(clang_parse("float y"))
        writer.add_variable(clang_parse("unsigned int a"))
        writer.add_variable(clang_parse("int x"))

        assert (
                writer.get_mockup('mockup.h')
                == """#ifndef mockup_new_h
#define mockup_new_h

#include "gmock/gmock.h" 

extern "C" {
} /* extern "C" */

class class_mockup;
typedef class_mockup* mock_ptr_t;
extern mock_ptr_t mockup_global_ptr;

class class_mockup {

 public:
   class_mockup()  { mockup_global_ptr = this; }
   ~class_mockup() { mockup_global_ptr = nullptr; }
}; /* class_mockup */

/* Version A: Create a local object that is destroyed when out of scope */
#define CREATE_MOCK(name)   class_mockup name

/* Version B: Allocate an object that will be only explicitly deallocated */
#define CREATE_PERSISTENT_MOCK()     new class_mockup
#define DESTROY_PERSISTENT_MOCK()    {if(mockup_global_ptr) delete mockup_global_ptr;}

#endif /* mockup_new_h */
"""
        )

        assert (
                writer.get_mockup('mockup.cc')
                == """#include "mockup_new.h"

mock_ptr_t mockup_global_ptr = nullptr;

unsigned int a;
int x;
float y;

extern "C" {
}
"""
        )

    def test_add_function_get(self):
        writer = MockupWriter()
        writer.add_function(clang_parse("int a_get_y2();"))
        assert writer.get_mockup('mockup.h') == open("tests/data/gmock_test/test_add_function_get/mockup.h").read()
        assert writer.get_mockup('mockup.cc') == open("tests/data/gmock_test/test_add_function_get/mockup.cc").read()

    def test_add_function_set_one_arg(self):
        writer = MockupWriter()
        writer.add_function(clang_parse("void set_some_int(int some_value);"))
        assert writer.get_mockup('mockup.h') == open(
            "tests/data/gmock_test/test_add_function_set_one_arg/mockup.h").read()
        assert writer.get_mockup('mockup.cc') == open(
            "tests/data/gmock_test/test_add_function_set_one_arg/mockup.cc").read()

    def test_add_function_with_unnamed_arg(self):
        writer = MockupWriter()
        writer.add_function(clang_parse("float my_func(float);"))
        assert writer.get_mockup('mockup.h') == open(
            "tests/data/gmock_test/test_add_function_with_unnamed_arg/mockup.h").read()
        assert writer.get_mockup('mockup.cc') == open(
            "tests/data/gmock_test/test_add_function_with_unnamed_arg/mockup.cc").read()

    def test_mini_c_gmock(self):
        writer = MockupWriter()
        writer.add_header("a.h")
        writer.add_header("c.h")
        writer.add_variable(clang_parse("extern int a_y1"))
        writer.add_variable(clang_parse("extern int c_u1"))
        writer.add_variable(clang_parse("extern a_y4_t a_y4"))
        writer.add_variable(clang_parse("extern const int const_a;"))
        writer.add_variable(clang_parse("extern const int const_array[3];"))
        writer.add_function(clang_parse("int  a_get_y2();"))
        writer.add_function(clang_parse("int  a_get_y3_and_set_u5(int u5);"))
        writer.add_function(clang_parse("a_y5_t a_get_y5();"))
        writer.add_function(clang_parse("void a_get_y6(int* y6);"))
        writer.add_function(clang_parse("int  c_get_y3_and_set_u5(int u5);"))
        writer.add_function(clang_parse("void c_set_u2(int u2);"))
        writer.add_function(clang_parse("void c_set_u3_and_u4(int u3, int u4);"))
        writer.add_function(clang_parse("void c_set_u6(c_u6_t u6);"))
        assert writer.get_mockup('mockup.h') == open("tests/data/gmock_test/test_mini_c_gmock/mockup.h").read()
        assert writer.get_mockup('mockup.cc') == open("tests/data/gmock_test/test_mini_c_gmock/mockup.cc").read()

    def test_languagemode(self):
        writer = MockupWriter()
        assert writer.default_language_mode() == 'c++'
        writer.set_mockup_style('plain_c')
        assert writer.default_language_mode() == 'c'


class TestNmWrapper(unittest.TestCase):

    def test_regex(self):
        assert not NmWrapper.mock_it('some_func')

        assert 'some_func' == NmWrapper.mock_it('         U some_func')
        assert not NmWrapper.mock_it('__gcov_exit')
        assert not NmWrapper.mock_it('         U __gcov_exit')

    def test_custom_regex(self):
        NmWrapper.set_exclude_pattern('^_')
        NmWrapper.set_include_pattern('^_(xyz)')
        assert not NmWrapper.mock_it('  U _abc')  # Every underline function is now excluded
        assert '_xyz' == NmWrapper.mock_it('  U _xyz') # ... except _xyz

class TestHammock(unittest.TestCase):
    def test_variable(self):
        """Mock a variable"""
        mock = Hammock(["a"])
        self.assertFalse(mock.done, "Should not be done yet")
        self.assertListEqual(mock.symbols, ["a"])

        mock.parse("extern int a;")
        self.assertTrue(mock.done, "Should be done now")
        self.assertListEqual(mock.symbols, [])
        self.assertEqual(len(mock.writer.variables), 1, "Mockup shall have a variable")
        self.assertEqual(mock.writer.variables[0].get_definition(), "int a", "Variable shall be created in the mockup")

    def test_struct_variable(self):
        """Mock a struct variable"""
        mock = Hammock(["x"])
        self.assertFalse(mock.done, "Should not be done yet")
        self.assertListEqual(mock.symbols, ["x"])

        mock.parse("""typedef struct { int a; int b; } struct_t;
                   extern struct_t x;""")
        self.assertTrue(mock.done, "Should be done now")
        self.assertListEqual(mock.symbols, [])
        self.assertEqual(len(mock.writer.variables), 1, "Mockup shall have a variable")
        self.assertEqual(mock.writer.variables[0].get_definition(), "struct_t x", "Variable shall be created in the mockup")

    def test_const_struct_variable(self):
        """Mock a constant struct variable"""
        mock = Hammock(["cx"])
        self.assertFalse(mock.done, "Should not be done yet")
        self.assertListEqual(mock.symbols, ["cx"])

        mock.parse("""typedef struct { int a; int b; } struct_t;
                   extern const struct_t cx;""")
        self.assertTrue(mock.done, "Should be done now")
        self.assertListEqual(mock.symbols, [])
        self.assertEqual(len(mock.writer.variables), 1, "Mockup shall have a variable")
        self.assertEqual(mock.writer.variables[0].get_definition(), "const struct_t cx", "Constant shall be created in the mockup")
        self.assertEqual(mock.writer.variables[0].initializer(), "(const struct_t){0}", "Constant shall be initialized with struct initializer")

    def test_void_func(self):
        """Mock a void(void) function"""
        mock = Hammock(["x"])
        mock.parse("extern void x(void);")
        self.assertTrue(mock.done, "Should be done now")
        self.assertEqual(len(mock.writer.functions), 1, "Mockup shall have a function")
        self.assertEqual(
            mock.writer.functions[0].get_signature(), "void x()", "Function shall be created in the mockup"
        )

    def test_int_int_func(self):
        """Mock a int(int) function"""
        mock = Hammock(["xxx"])
        mock.parse("extern int xxx(int var1);")
        self.assertTrue(mock.done, "Should be done now")
        self.assertEqual(len(mock.writer.functions), 1, "Mockup shall have a function")
        self.assertEqual(
            mock.writer.functions[0].get_signature(), "int xxx(int var1)", "Function shall be created in the mockup"
        )

    def test_variable_with_config_guard(self):
        """Mock a variable with config guard"""
        mock = Hammock(["b"])
        mock.parse(
            """#ifdef SOME_CONFIG
extern int b;
#endif
"""
        )
        assert False == mock.done, "Should not be done due to missing definition"

        mock = Hammock(["b"], ["-DSOME_CONFIG"])
        mock.parse(
            """#ifdef SOME_CONFIG
extern int b;
#endif
"""
        )
        assert mock.done, "Should be done now"

        assert len(mock.writer.variables) == 1, "Mockup shall have a variable"
        assert mock.writer.variables[0].get_definition() == "int b", "Variable shall be created in the mockup"

    def test_variable_and_function_with_config_guards(self):
        """Mock a variable and a function with different config guards"""
        mock = Hammock(["b", "foo"], ["-DSOME_CONFIG", "-DSOME_OTHER_CONFIG=2"])
        mock.parse(
            """#ifdef SOME_CONFIG
extern int b;
#endif

#ifdef SOME_OTHER_CONFIG
extern void foo();
#endif

#ifdef SOME_FUNC_TO_BE_IGNORED
extern void ignore_me();
#endif
"""
        )
        assert mock.done, "Should be done now"
        assert len(mock.writer.variables) == 1, "Mockup shall have a variable"
        assert mock.writer.variables[0].get_definition() == "int b", "Variable shall be created in the mockup"
        assert len(mock.writer.functions) == 1, "Mockup shall have a function"
        assert mock.writer.functions[0].get_signature() == "void foo()", "Function shall be created in the mockup"

    def test_extern_c_variable(self):
        """Mock a variable that is inside an "extern C" section"""
        mock = Hammock(["foo"])
        mock.parse("""
extern "C" {
extern void foo();
}
"""
        )
        assert mock.done, "Should be done now"
        assert len(mock.writer.functions) == 1, "Mockup shall have a function"
        assert mock.writer.functions[0].get_signature() == "void foo()", "Function shall be created in the mockup"

    def test_variable_array(self):
        """Mock an int array"""
        mock = Hammock(["my_array"])
        mock.parse("extern int my_array[2];")
        assert mock.done, "Should be done now"
        assert len(mock.writer.variables) == 1, "Mockup shall have a variable"
        assert mock.writer.variables[0].get_definition() == "int my_array[2]", "Variable shall be created in the mockup" 

    def test_langmode_auto(self):
        """Read as c++ compiler determined from output style"""
        mock = Hammock(["bool_status"])
        mock.parse(Path("tests/data/mini_c++_test/use_bool.c"))
        assert mock.done, "Should be done now"
        assert len(mock.writer.functions) == 1, "Mockup shall have a function"
        assert mock.writer.functions[0].get_signature() == "bool bool_status()", "Function shall be created with bool type"

    def test_langmode_override(self):
        """Read as c compiler"""
        mock = Hammock(["bool_status"], ["-xc"])
        mock.parse(Path("tests/data/mini_c++_test/use_bool.c"))
        assert mock.done, "Should be done now"
        assert len(mock.writer.functions) == 1, "Mockup shall have a function"
        assert mock.writer.functions[0].get_signature() == "_Bool bool_status()", "Function shall be created with C99 bool type"

    def test_variadic_function(self):
        """Mock a variadic function"""
        mock = Hammock(["printf"])
        mock.parse("extern int printf(const char * format, ...);")
        assert mock.done, "Should be done now"
        assert len(mock.writer.functions) == 1, "Mockup shall have a function"
        self.assertEqual(
            mock.writer.functions[0].get_signature(), "int printf(const char * format, ...)", "Function shall be created in the mockup"
        )

if __name__ == "__main__":
    unittest.main()
