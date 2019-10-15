import cppyy

import os.path
cppyy.add_include_path(os.path.join(os.path.dirname(__file__), "include"))
