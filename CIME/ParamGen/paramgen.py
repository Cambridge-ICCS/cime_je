
from __future__ import print_function
from collections import OrderedDict
import os
import re
from abc import ABC, abstractmethod
from copy import deepcopy
from paramgen_utils import is_logical_expr
from paramgen_utils import has_expandable_var, eval_formula

class ParamGen(ABC):
    """
    Base class for CIME Flexible Parameter Generator.
    Attributes
    ----------
    data : dict or OrderedDict
        The data attribute to operate over. See Methods for the list of operations.
    Methods
    -------
    from_json(input_path)
        Reads in a given json input file and initializes a ParamGen object.
    from_yaml(input_path)
        Reads in a given yalm input file and initializes a ParamGen object.
    """

    def __init__(self, data_dict, match='last'):
        assert isinstance(data_dict, dict), \
            "ParamGen class requires a dict or OrderedDict as the initial data."
        #self._validate_schema(data_dict)
        self._data = deepcopy(data_dict)
        self._reduced = False
        self._match = match

    @property
    def data(self):
        """Returns the data attribute of the ParamGen instance."""
        return self._data

    @classmethod
    def from_json(cls, input_path):
        """
        Reads in a given json input file and initializes a ParamGen object.
        Parameters
        ----------
        input_path: str
            Path to json input file containing the defaults.
        Returns
        -------
        ParamGen
            A ParamGen object with the data read from input_path.
        """

        import json
        with open(input_path) as json_file:
            _data = json.load(json_file, object_pairs_hook=OrderedDict)
        return cls(_data)

    @classmethod
    def from_yaml(cls, input_path):
        """
        Reads in a given yaml input file and initializes a ParamGen object.
        Parameters
        ----------
        input_path: str
            Path to yaml input file containing the defaults.
        Returns
        -------
        ParamGen
            A ParamGen object with the data read from input_path.
        """

        import yaml
        with open(input_path) as yaml_file:
            _data = yaml.safe_load(yaml_file)
        return cls(_data)


    @staticmethod
    def _expand_vars(expr, expand_func):
        assert isinstance(expr, str), "Expression passed to _expand_vars must be string."
        expandable_vars = re.findall(r'(\$\w+|\${\w+\})',expr)
        for word in expandable_vars:
            word_stripped = word.\
                replace("$","").\
                replace("{","").\
                replace("}","")
            word_expanded = expand_func(word_stripped)
            assert word_expanded!=None, "Cannot expand the variable "+word+" using the given expand_func."
            assert isinstance(word_expanded,str), "expand_func must return string."
            expr = expr.replace(word,word_expanded)
        return expr


    @staticmethod
    def _is_guarded_dict(data_dict):
        """ returns true if all the keys of a dictionary are logical expressions, i.e., guards."""
        if not isinstance(data_dict, dict):
            return False

        keys_logical = [is_logical_expr(str(key)) for key in data_dict]
        if all(keys_logical):
            return True
        elif any(keys_logical):
            print("data_dict: ", data_dict)
            raise RuntimeError("Only subset of the keys of the above dict are guards, i.e., logical expressions")
        else:
            return False

    def _impose_guards(self, data_dict):

        def _eval_guard(guard):
            """ returns true if a guard evaluates to true."""
            assert isinstance(guard, str), "Expression passed to _eval_guard must be string."

            if has_expandable_var(guard):
                raise RuntimeError("The guard "+guard+" has an expandable case variable! "+\
                    "All variables must already be expanded before guards can be evaluated.")
            
            guard_evaluated = eval_formula(guard)
            assert type(guard_evaluated)==type(True), "Guard is not boolean: "+guard
            return guard_evaluated


        if not ParamGen._is_guarded_dict(data_dict):
            return data_dict
        else:

            guards_eval_true = [] # list of guards that evaluate to true.
            for guard in data_dict:
                if guard=="else" or _eval_guard(str(guard)) == True:
                    guards_eval_true.append(guard)
                    
            if len(guards_eval_true)>1 and "else" in guards_eval_true:
                guards_eval_true.remove("else")
            elif len(guards_eval_true)==0:
                raise RuntimeError("None of the guards evaluate to true: "+str(data_dict))
            
            if self._match == 'first':
                return data_dict[guards_eval_true[0]]
            elif self._match == 'last':
                return data_dict[guards_eval_true[-1]]
            else:
                raise RuntimeError("Unknown match option.")


    def _reduce_recursive(self, data_dict, expand_func=None):
 
        # (1) Expand variables in keys, .e.g, "$OCN_GRID" to "gx1v7":
        if expand_func!=None:
            for key in data_dict.copy():
                if has_expandable_var(key):
                    new_key = ParamGen._expand_vars(key, expand_func)
                    data_dict[new_key] = data_dict.pop(key)

        # (2) Evaluate the keys if they are all logical expressions, i.e., guards.
        # Pick the value of the first or last key evaluating to True and drop everything else.
        while ParamGen._is_guarded_dict(data_dict):
            data_dict = self._impose_guards(data_dict)

        # (3) Expand variables in values, .e.g, "$OCN_GRID" to "gx1v7":
        if isinstance(data_dict, dict):
            for key, val in data_dict.copy().items():
                if isinstance(val, str):
                    data_dict[key] = ParamGen._expand_vars(val, expand_func)

        # if the reduced data is still a dictionary, recursively call _reduce_recursive before returning
        if isinstance(data_dict, dict):
            keys_of_nested_dicts = [] # i.e., keys of values that are of type dict
            for key, val in data_dict.items():
                if isinstance(val, dict):
                    keys_of_nested_dicts.append(key)
            for key in keys_of_nested_dicts:
                data_dict[key] = self._reduce_recursive(data_dict[key], expand_func)

        return data_dict


    def reduce(self, expand_func=None):
        """
        Reduces the data of a ParamGen instances by recursively (1) expanding its variables,
        (2) dropping entries whose conditional guards evaluate to true and (3) evaluating
        formulas to determine the final values
        """

        assert callable(expand_func) or expand_func==None, "expand_func argument must be a function"
        assert not self._reduced, "ParamGen data already reduced."
        assert len(self._data)>0, "Empty ParamGen data."

        self._data = self._reduce_recursive(self._data, expand_func)

        self._reduced = True