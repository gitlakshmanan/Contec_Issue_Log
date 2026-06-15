import py_compile
import glob
import sys

errs = False
for f in glob.glob('**/*.py', recursive=True):
    try:
        py_compile.compile(f, doraise=True)
    except Exception as e:
        print(f + ': ' + str(e))
        errs = True

if errs:
    sys.exit(1)
else:
    print('No syntax errors found')
