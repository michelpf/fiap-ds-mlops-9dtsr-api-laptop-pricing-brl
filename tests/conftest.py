# testes/conftest.py
import sys
import os

# Obtém o caminho do diretório pai (projeto/)
projeto_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Adiciona o caminho do diretório pai ao sys.path
sys.path.insert(0, projeto_path)