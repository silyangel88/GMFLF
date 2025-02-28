import pyauparser
import os
import random
from efsm.EFSMparser import EFSMParser

dir_name = os.path.dirname(os.getcwd())


class Operator(object):
    def __init__(self, efsm_obj):
        #self.mutation_type = mutation_type
        self.efsmp = EFSMParser(os.path.join(dir_name, "EFSMparser/grammar/EFSMparser.egt"))
        self.grammar = self.efsmp.get_grammar()
        self.efsm_obj = efsm_obj

    def mutate(self, operation):
        try:
            flag = True
            tree = pyauparser.parse_string_to_tree(self.grammar, operation)
            element = []
            self.efsmp.analysis_element(tree, element)

            number = []
            operator = []
            for index, e in enumerate(element):
                if isinstance(e, int):
                    number.append((e, index))
                elif e in self.comparison_op():
                    operator.append((e, index))


            if len(number) != 0 and len(operator) != 0:
                r = random.randint(0, 1)
                if r:
                    selected = random.choice(number)
                    selected_index = selected[1]
                    while True:
                        random_integer = random.randint(0, 2)
                        if random_integer != selected:
                            break
                    element[selected_index] = random_integer
                else:
                    selected = random.choice(operator)
                    self.mutation_points(elements=element, item=selected[0], index=selected[1])

            elif len(number) != 0:
                selected = random.choice(number)
                selected_index = selected[1]
                element[selected_index] = random.randint(0, 3)

            elif len(operator) != 0:
                selected = random.choice(operator)
                self.mutation_points(elements=element, item=selected[0], index=selected[1])

            else:
                flag = False

            result = ' '.join(str(e) for e in element)
            return result, flag
        except pyauparser.ParseError as e:
            print(e)
            return False


    def mutation_points(self, elements, item, index):
        elements[index] = self.comparison_op().get(item)

    def comparison_op(self):
        cmp = {
            '+': '-',
            '-': '+',
            '*': '/',
            '/': '*',
            '//': '/',
            '%': '/',
            '<<': '>>',
            '>>': '<<',
            '&&': '||',
            '||': '&&',
            '^': '&',
            '**': '*',
            '~': '',

            '+=': '-=',
            '-=': '+=',
            '*=': '/=',
            '/=': '*=',
            '//=': '/=',
            '%=': '/=',
            '<<=': '>>=',
            '>>=': '<<=',
            '&=': '|=',
            '|=': '&=',
            '^=': '&=',
            '**=': '*=',
            '~=': '=',

            '<': '<=',
            '<=': '<',
            '>': '>=',
            '>=': '>',
            '=': '<>',
            '<>': '=',
        }
        return cmp