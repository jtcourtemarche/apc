#!/usr/bin/python
import os

__all__ = [module for module in os.listdir(os.getcwd()+'/bomara/vendors') if module[0] != '_' and module[-3:] == '.py']
__all__ = [module.replace('.py', '') for module in __all__]