from time import time
from subprocess import run, PIPE
import ctypes

now = time()
out = run("./hello", stdout=PIPE)
print("Subprocess run: {}μs\n\n".format((time() - now)*1000000))

now = time()
print("Hello World")
print("Native Python print: {}μs\n\n".format((time() - now)*1000000))

lib = ctypes.cdll.LoadLibrary("./test.so")
now = time()
lib.Print()
print("Shared Library: {}μs".format((time() - now)*1000000))
