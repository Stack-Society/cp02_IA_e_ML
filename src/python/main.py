import json
import numpy as np
from datetime import datetime
from pyscript import document, when


# ---------- 1. Carregar dados ----------
def carregar_dados():
    with open("dados.json", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    return dados["instrumentos"]
 
 
instrumentos = carregar_dados()


# ---------- 2. Telemetria ----------
eventos = []
 
 
def registrar_telemetria(evento):
    hora = datetime.now().strftime("%H:%M:%S")
    eventos.append({"hora": hora, "evento": evento})
 
    item = document.createElement("li")
    item.innerText = f"[{hora}] {evento}"
    document.querySelector("#log-telemetria").prepend(item)


# ---------- 3. Guardrails ----------
PALAVRAS_BLOQUEADAS = ["<script", "drop", "delete", "select *"]
 
 
def validar_entrada(texto):
    texto = texto.strip()
 
    if texto == "":
        return False, "Digite o nome de um instrumento."
 
    if len(texto) > 30:
        return False, "Texto muito longo (máx. 30 caracteres)."
 
    for palavra in PALAVRAS_BLOQUEADAS:
        if palavra in texto.lower():
            return False, "Entrada bloqueada pelo guardrail."
 
    if not texto.replace(" ", "").isalpha():
        return False, "Use apenas letras."
 
    return True, texto
 
 
# ---------- 4. Cálculo vetorial ----------
def calcular_norma(embedding):
    vetor = np.array(embedding)
    return float(np.linalg.norm(vetor))
 
 
def calcular_distancia(emb_a, emb_b):
    return float(np.linalg.norm(np.array(emb_a) - np.array(emb_b)))
 
 
def mais_parecido(instrumento):
    outros = [i for i in instrumentos if i["id"] != instrumento["id"]]
    return min(outros, key=lambda i: calcular_distancia(instrumento["embedding"], i["embedding"]))


