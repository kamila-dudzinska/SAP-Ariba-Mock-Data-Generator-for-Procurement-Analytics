import sys
import os

# Dodaj folder src do ścieżki importu zanim pytest zacznie zbierać testy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
