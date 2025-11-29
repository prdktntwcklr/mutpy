import ast

from mutpy import utils
from mutpy.operators.arithmetic import AbstractArithmeticOperatorReplacement
from mutpy.operators.base import MutationOperator, MutationResign

# IMPORTANT: Capitalization of function names matters - do not change!

class AssignmentOperatorReplacement(AbstractArithmeticOperatorReplacement):
    def should_mutate(self, node):
        return isinstance(node.parent, ast.AugAssign)

    @classmethod
    def name(cls):
        return 'ASR'


class BreakContinueReplacement(MutationOperator):
    def mutate_Break(self, node):
        return ast.Continue()

    def mutate_Continue(self, node):
        return ast.Break()


class ConstantReplacement(MutationOperator):
    FIRST_CONST_STRING = 'mutpy'
    SECOND_CONST_STRING = 'python'

    def mutate_Num(self, node):
        return ast.Num(n=node.n + 1)
    
    def mutate_Constant_num(self, node):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return ast.Constant(value=node.value + 1)
        else:
            raise MutationResign()
        
    def _string_helper(self, node) -> str:
        if utils.is_docstring(node):
            raise MutationResign()

        if node.s != self.FIRST_CONST_STRING:
            return self.FIRST_CONST_STRING
        else:
            return self.SECOND_CONST_STRING
        
    def _string_helper_empty(self, node) -> str:
        if not node.s or utils.is_docstring(node):
            raise MutationResign()

        return ""

    def mutate_Str(self, node):
        return ast.Str(s=self._string_helper(node))
        
    def mutate_Constant_str(self, node):
        if isinstance(node.value, str):
            return ast.Constant(value=self._string_helper(node))
        else:
            raise MutationResign()

    def mutate_Str_empty(self, node):
        return ast.Str(s=self._string_helper_empty(node))
    
    def mutate_Constant_str_empty(self, node):
        if isinstance(node.value, str):
            return ast.Constant(s=self._string_helper_empty(node))
        else:
            raise MutationResign()

    @classmethod
    def name(cls):
        return 'CRP'


class SliceIndexRemove(MutationOperator):
    def mutate_Slice_remove_lower(self, node):
        if not node.lower:
            raise MutationResign()

        return ast.Slice(lower=None, upper=node.upper, step=node.step)

    def mutate_Slice_remove_upper(self, node):
        if not node.upper:
            raise MutationResign()

        return ast.Slice(lower=node.lower, upper=None, step=node.step)

    def mutate_Slice_remove_step(self, node):
        if not node.step:
            raise MutationResign()

        return ast.Slice(lower=node.lower, upper=node.upper, step=None)


class SelfVariableDeletion(MutationOperator):
    def mutate_Attribute(self, node):
        try:
            if node.value.id == 'self':
                return ast.Name(id=node.attr, ctx=ast.Load())
            else:
                raise MutationResign()
        except AttributeError:
            raise MutationResign()


class StatementDeletion(MutationOperator):
    def mutate_Assign(self, node):
        return ast.Pass()

    def mutate_Return(self, node):
        return ast.Pass()

    def mutate_Expr(self, node):
        if utils.is_docstring(node.value):
            raise MutationResign()
        return ast.Pass()

    @classmethod
    def name(cls):
        return 'SDL'
