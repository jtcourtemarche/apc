#!/usr/bin/python
import os

__all__ = [module.replace('.py', '') for module in os.listdir(os.getcwd()+'/bomara/vendors') if module[0] != '_']
