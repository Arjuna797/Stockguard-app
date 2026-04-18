import os
import sys

try:
    os.add_dll_directory(r"D:\anaconda3\Library\bin")
    os.add_dll_directory(r"D:\anaconda3\bin")
except Exception as e:
    pass

import numpy as np
import pandas as pd
print("SUCCESS IMPORTING NUMPY AND PANDAS!")
