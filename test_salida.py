import sys
print("Test 1: Salida estándar")
sys.stdout.write("Test 2: Salida directa\n")
sys.stderr.write("Test 3: Salida de error\n")
sys.stdout.flush()
sys.stderr.flush()

