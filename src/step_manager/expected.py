from __future__ import absolute_import

import logging


class Expected(object):

    def __init__(self, owner, method, **kwargs):
        self.owner = owner
        self.log = owner.log
        self._method = method
        self._kwargs = dict(**kwargs)
        self.__info_provided = False

    def run(self):
        if hasattr(self._method, "__name__"):
            method_name = self._method.__name__
        else:
            method_name = self._method

        if not self.__info_provided:
            self.__info_provided = True
            self.log(logging.INFO,
                 "Check expected '{method}' with params {params}".format(method=method_name, params=self._kwargs))

        res = self._method(**self._kwargs)
        if not isinstance(res, tuple):
            res = (res, "No message provided")
        if not res[0]:
            return res
        else:
            self.log(logging.INFO, "Check of expected passed")
            return res


