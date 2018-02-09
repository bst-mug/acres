# This module "paths" returns
# absolute paths for all sibling
# directories invoked
# A dictionary is retunred, with
# the dir name in upper case as key
# and the whole path with backslash as value
# extra entry "ROOT" for the root of these
# sibling directories
# and "SELF" for the own directory 

import os
def subdirs (scriptfile):
    d = {} 
    p = os.path.realpath(scriptfile)
    p1 = p.split("\\")[0:-2]
    p2 = p.split("\\")[0:-1]
    d["SELF"] = "\\".join(p2) + "\\"
    p = "\\".join(p1) + "\\"
    for name in os.listdir(p):
        d[name.upper()] = p + name + "\\"
    d["ROOT"] = p
    return d
 
