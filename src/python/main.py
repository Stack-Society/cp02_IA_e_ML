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


# ---------- 5. Renderização ----------
def renderizar_cards(lista):
    container = document.querySelector("#lista-instrumentos")

    if not lista:
        container.innerHTML = "<p>Nenhum instrumento encontrado.</p>"
        return

    html = ""

    for i in lista:
        html += f"""
        <div class="card">
            <img src="{i['imagem']}" alt="{i['nome']}">
            <h3>{i['nome']}</h3>
            <p>{i['categoria']}</p>
            <p>Estoque: {i['estoque']}</p>
            <p>Aula: R$ {i['preco_aula']:.2f}</p>
        </div>
        """

    container.innerHTML = html


def preencher_select():
    select = document.querySelector("#select-instrumento")

    opcoes = ""

    for i in instrumentos:
        opcoes += f'<option value="{i["id"]}">{i["nome"]}</option>'

    select.innerHTML = opcoes


# ---------- 6. Eventos ----------
@when("click", "#btn-buscar")
def buscar(event):
    texto = document.querySelector("#campo-busca").value
    msg = document.querySelector("#msg-validacao")

    valido, resultado = validar_entrada(texto)

    if not valido:
        msg.innerText = resultado
        msg.className = "erro"
        registrar_telemetria(f"Busca bloqueada: {resultado}")
        return

    filtrados = [
        i for i in instrumentos
        if resultado.lower() in i["nome"].lower()
    ]

    renderizar_cards(filtrados)

    msg.innerText = f"{len(filtrados)} resultado(s)."
    msg.className = "ok"

    registrar_telemetria(f"Busca por '{resultado}'")


@when("click", "#btn-analisar")
def analisar(event):
    select = document.querySelector("#select-instrumento")

    if not select.value:
        return

    id_escolhido = int(select.value)

    instrumento = next(
        (i for i in instrumentos if i["id"] == id_escolhido),
        None
    )

    if instrumento is None:
        return

    norma = calcular_norma(instrumento["embedding"])
    parecido = mais_parecido(instrumento)

    if parecido is not None:
        distancia = calcular_distancia(
            instrumento["embedding"],
            parecido["embedding"]
        )

        resultado_parecido = (
            f"<p>Mais parecido: {parecido['nome']} "
            f"(distância {distancia:.4f})</p>"
        )
    else:
        resultado_parecido = (
            "<p>Não há outro instrumento para comparar.</p>"
        )

    document.querySelector("#resultado-vetor").innerHTML = f"""
        <p>
            <b>{instrumento['nome']}</b>
            - vetor: {instrumento['embedding']}
        </p>
        <p>Norma Euclidiana: {norma:.4f}</p>
        {resultado_parecido}
    """

    registrar_telemetria(
        f"Análise vetorial: {instrumento['nome']}"
    )