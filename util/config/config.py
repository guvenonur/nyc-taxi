import os
import re
import sys
from configobj import ConfigObj
from util import is_empty


class ConfigParser:
    @staticmethod
    def to_object(d):
        """
        Convert config object to custom object
        :param ConfigObj d: config object
        :return: custom object
        :rtype: object
        """
        top = type('new', (object,), d)
        seq = tuple, list, set, frozenset
        for i, j in d.items():
            if isinstance(j, dict):
                setattr(top, i, ConfigParser.to_object(j))
            elif isinstance(j, seq):
                typed = []
                for sj in j:
                    if isinstance(sj, dict):
                        typed.append(ConfigParser.to_object(sj))
                    else:
                        typed.append(sj)
                setattr(top, i, typed)
            else:
                if j in ['true', 'false']:
                    j = 'true' == j
                elif re.match(r'^[0-9]+[\\.]+[0-9]+$', j):
                    j = float(j)
                elif j.isnumeric():
                    if '.' in j:
                        j = float(j)
                    else:
                        j = int(j)
                setattr(top, i, j)
        return top

    @staticmethod
    def load(path=None):
        """
        Load configuration by given path or `CONFIG` environment.
        The environment variable is primary lookup
        :param str or None path: the configuration path
        :return: the configuration object
        :rtype: object
        """
        if path is None:
            if 'CONFIG' in os.environ:
                path = os.environ['CONFIG']
            elif len(sys.argv) > 1:
                path = sys.argv[1]
            else:
                raise Exception('Configuration parameter must be set')

        if is_empty(path):
            raise Exception('Configuration path is missing')

        if not os.path.exists(path):
            raise Exception(f'Configuration file does not exists "{path}"')

        conf = ConfigObj(path)

        # size of sections must be greater than one
        if len(conf.sections) == 0:
            raise Exception('There are no any sections')

        return ConfigParser.to_object(conf)
