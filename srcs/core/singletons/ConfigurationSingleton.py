"""********************************************************************"""
"""                                                                    """
"""   [singletons] ConfigurationSingleton.py                           """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 30/07/2021 05:17:22                                     """
"""   Updated: 02/08/2021 07:22:47                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

class ConfigurationSingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]