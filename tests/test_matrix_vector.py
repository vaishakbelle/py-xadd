from __future__ import print_function

import unittest

from pyxadd import matrix_vector
from pyxadd.build import Builder
from pyxadd.diagram import Diagram, Pool
from pyxadd.matrix_vector import SummationWalker, matrix_multiply
from pyxadd.partial import PartialWalker
from pyxadd.reduce import LinearReduction
from pyxadd.test import LinearTest


class TestMatrixVector(unittest.TestCase):
    def setUp(self):
        self.diagram = TestMatrixVector.construct_diagram()

    @staticmethod
    def construct_diagram():
        pool = Pool()
        pool.int_var("x", "y")

        b = Builder(pool)
        bounds = b.test("x", ">=", 0) & b.test("x", "<=", 8) & b.test("y", ">=", 1) & b.test("y", "<=", 10)
        return bounds * b.ite(b.test("x", ">=", "y"), b.terminal("2*x + 3*y"), b.terminal("3*x + 2*y"))

    # FIXME In case I forget: Introduce ordering on integer comparisons

    def test_summation_one_var(self):
        pool = Pool()
        pool.add_var("x", "int")
        pool.add_var("y", "int")
        b = Builder(pool)
        bounds = b.test("x", ">=", 0) & b.test("x", "<=", 10)
        d = b.ite(bounds, b.terminal("x"), b.terminal(0))
        d_const = Diagram(pool, SummationWalker(d, "x").walk())
        # from pyxadd import bounds_diagram
        # d_const = pool.diagram(bounds_diagram.BoundResolve(pool).integrate(d.root_id, "x"))
        self.assertEqual(55, d_const.evaluate({}))

    def test_summation_two_var(self):
        pool = Pool()
        pool.add_var("x", "int")
        pool.add_var("y", "int")
        b = Builder(pool)
        bounds = b.test("x", ">=", 0) & b.test("x", "<=", 10)
        bounds &= b.test("y", ">=", 0) & b.test("y", "<=", 1)
        d = b.ite(bounds, b.terminal("x"), b.terminal(0))
        d_const = Diagram(pool, SummationWalker(d, "x").walk())
        # from pyxadd import bounds_diagram
        # d_const = pool.diagram(bounds_diagram.BoundResolve(pool).integrate(d.root_id, "x"))
        for y in range(2):
            self.assertEqual(55, d_const.evaluate({"y": y}))

    def test_summation_two_var_test(self):
        pool = Pool()
        pool.add_var("x", "int")
        pool.add_var("y", "int")
        b = Builder(pool)
        bounds = b.test("x", ">=", 0) & b.test("x", "<=", 1)
        bounds &= b.test("y", ">=", 1) & b.test("y", "<=", 3)
        two = b.test("x", ">=", "y")
        d = b.ite(bounds, b.ite(two, b.terminal("x"), b.terminal("10")), b.terminal(0))

        summed = Diagram(pool, SummationWalker(d, "x").walk())
        from pyxadd import bounds_diagram
        summed = pool.diagram(bounds_diagram.BoundResolve(pool).integrate(d.root_id, "x"))
        d_const = summed.reduce(["y"])
        for y in range(-20, 20):
            s = 0
            for x in range(-20, 20):
                s += d.evaluate({"x": x, "y": y})
            self.assertEqual(s, d_const.evaluate({"y": y}))

    def test_mixed_symbolic(self):
        pool = self.diagram.pool
        diagram_y = Diagram(pool, SummationWalker(self.diagram, "x").walk())
        # from pyxadd import bounds_diagram
        # diagram_y = pool.diagram(bounds_diagram.BoundResolve(pool).integrate(diagram_y.root_id, "x"))

        diagram_y = Diagram(diagram_y.pool, LinearReduction(diagram_y.pool).reduce(diagram_y.root_node.node_id, ["y"]))

        for y in range(0, 12):
            row_result = 0
            for x in range(0, 12):
                row_result += self.diagram.evaluate({"x": x, "y": y})
            self.assertEqual(diagram_y.evaluate({"y": y}), row_result)

    def test_partial(self):
        partial = PartialWalker(self.diagram, {"y": 2}).walk()
        for x in range(-10, 10):
            if x < 0 or x > 8:
                self.assertEqual(0, partial.evaluate({"x": x}))
            elif x > 2:
                self.assertEqual(2 * x + 6, partial.evaluate({"x": x}))
            else:
                self.assertEqual(3 * x + 4, partial.evaluate({"x": x}))

    def _test_bounds_resolve_1(self):
        import os
        from tests import test_evaluate
        from pyxadd import bounds_diagram
        from pyxadd import variables
        from tests import export

        exporter = export.Exporter(os.path.join(os.path.dirname(os.path.realpath(__file__)), "visual"), "resolve", True)
        diagram_1, vars_1 = test_evaluate.get_diagram_1()
        exporter.export(diagram_1, "diagram")
        pool = diagram_1.pool
        b = Builder(pool)
        resolve = bounds_diagram.BoundResolve(pool)
        result_id = diagram_1.root_id
        control_id = diagram_1.root_id
        reducer = LinearReduction(pool)
        c = 1000.0
        for var in vars_1:
            var_name = str(var[0])
            result_id = resolve.integrate(result_id, var_name)
            control_id = matrix_vector.sum_out(pool, control_id, [var_name])
            result_diagram = pool.diagram(result_id)
            control_diagram = pool.diagram(control_id)
            #result_diagram = pool.diagram(reducer.reduce(result_diagram.root_id))
            #control_diagram = pool.diagram(reducer.reduce(control_diagram.root_id))
            difference_diagram = pool.diagram(reducer.reduce((result_diagram - control_diagram).root_id))
            exporter.export(result_diagram, "resolve_without_{}".format(var_name))
            exporter.export(control_diagram, "control_without_{}".format(var_name))
            exporter.export(difference_diagram, "difference_without_{}".format(var_name))
            result_id = (b.terminal(1/c) * result_diagram).root_id
            control_id = (b.terminal(1/c) * control_diagram).root_id
            self.assertTrue(var_name not in variables.variables(result_diagram), "{} not eliminated".format(var_name))
            self.assertTrue(var_name not in variables.variables(control_diagram), "{} not eliminated".format(var_name))
        self.assertTrue(len(variables.variables(result_diagram)) == 0)
        self.assertTrue(len(variables.variables(control_diagram)) == 0)
        self.assertEquals(control_diagram.evaluate({}), result_diagram.evaluate({}))

    def test_bounds_resolve_some_ub_1(self):
        import os
        from tests import export
        from pyxadd import bounds_diagram

        exporter = export.Exporter(os.path.join(os.path.dirname(os.path.realpath(__file__)), "visual"), "resolve", True)
        b = Builder()
        b.ints("x", "b", "c", "d", "y")
        zero_test = b.test("x", ">=", 0)
        b_test = b.test("x", "<=", "b")
        y_test = b.test("y", "<=", 10)
        c_test = b.test("x", "<=", "c")
        d_test = b.test("x", "<=", "d")
        d = zero_test * b_test * b.ite(y_test,
                                       c_test * b.exp("3"),
                                       d_test * b.exp("11"))
        exporter.export(d, "some_ub_diagram")
        resolve = bounds_diagram.BoundResolve(b.pool, "./visual/resolve/debug/")
        result_id = resolve.integrate(d.root_id, "x")
        result_diagram = b.pool.diagram(result_id)
        exporter.export(result_diagram, "some_ub_result")
        reducer = LinearReduction(b.pool)
        reduced_result = b.pool.diagram(reducer.reduce(result_id))
        exporter.export(reduced_result, "some_ub_result_reduced")

        control_id = matrix_vector.sum_out(b.pool, d.root_id, ["x"])
        control_diagram = b.pool.diagram(control_id)
        exporter.export(control_diagram, "some_ub_control")

        reduced_control = b.pool.diagram(reducer.reduce(control_id))
        exporter.export(reduced_control, "some_ub_control_reduced")

    def test_multiplication(self):
        pool = Pool()
        pool.int_var("x1", "x2")
        x_two = Diagram(pool, pool.terminal("x2"))
        two = Diagram(pool, pool.terminal("2"))
        three = Diagram(pool, pool.terminal("3"))
        four = Diagram(pool, pool.terminal("4"))

        test11 = Diagram(pool, pool.bool_test(LinearTest("x1", ">=")))
        test12 = Diagram(pool, pool.bool_test(LinearTest("x1 - 1", "<=")))
        test13 = Diagram(pool, pool.bool_test(LinearTest("x1 - 3", ">")))

        test21 = Diagram(pool, pool.bool_test(LinearTest("x2", ">=")))
        test22 = Diagram(pool, pool.bool_test(LinearTest("x2", ">")))
        test23 = Diagram(pool, pool.bool_test(LinearTest("x2 - 1", ">")))
        test24 = Diagram(pool, pool.bool_test(LinearTest("x2 - 2", ">")))

        x_twos = test12 * ~test23 * x_two
        twos = test12 * test23 * two
        threes = ~test12 * ~test22 * three
        fours = ~test12 * test22 * four

        unlimited = x_twos + twos + threes + fours
        restricted = unlimited * test11 * ~test13 * test21 * ~test24

        vector = test21 * ~test24 * Diagram(pool, pool.terminal("x2 + 1"))

        result = Diagram(pool, matrix_multiply(pool, restricted.root_node.node_id, vector.root_node.node_id, ["x2"]))
        for x1 in range(0, 4):
            self.assertEqual(8 if x1 < 2 else 23, result.evaluate({"x1": x1}))

if __name__ == '__main__':
    unittest.main()
