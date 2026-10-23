import json
import numpy as np
from datetime import datetime
from pyscript import document, when


def carregar_dados():
    with open("dados.json", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    return dados["instrumentos"]
 
 
instrumentos = carregar_dados()

