"""
ferramentas.py
--------------
Este arquivo existe para conter as "capacidades" do Gatuno: funções
Python reais que o modelo pode pedir para o orquestrador executar.

Regra de ouro deste arquivo: o Qwen3 NUNCA executa nada sozinho.
Ele só pode SUGERIR o nome de uma ferramenta e os argumentos. Quem
decide se a chamada é válida e quem efetivamente executa é sempre
este código Python, de forma determinística e auditável.

Por segurança, nesta fase:
- as ferramentas só enxergam a pasta de laboratório (config.PASTA_LABORATORIO)
- os nomes recebidos são validados (sem "..", sem barras, sem caminhos absolutos)
- não existe eval()/exec() em nenhum lugar
- não existe exclusão de arquivos/pastas reais
- futuramente, aqui é onde entrariam checagens de permissão/confirmação
  do usuário antes de ações mais sensíveis (marcado abaixo com TODO)
"""

import os
import config


class FerramentaError(Exception):
    """Erro previsível de uma ferramenta (nome inválido, etc.),
    diferente de um bug. É isso que devolvemos ao modelo como
    resultado, em vez de deixar o programa quebrar."""
    pass


def _validar_nome_pasta(nome: str) -> str:
    """
    Valida que 'nome' é um nome de pasta simples e seguro:
    - precisa ser string não vazia
    - não pode conter separadores de caminho (/ ou \\)
    - não pode conter ".." (tentativa de sair da pasta de laboratório)

    Isso é o que garante que o modelo não consiga, por exemplo, pedir
    para criar "../../Windows/algumacoisa" e escapar da sandbox.
    """
    if not isinstance(nome, str) or not nome.strip():
        raise FerramentaError("O nome da pasta precisa ser um texto não vazio.")

    nome = nome.strip()

    if "/" in nome or "\\" in nome or ".." in nome:
        raise FerramentaError(
            f"Nome de pasta inválido: '{nome}'. Não é permitido usar "
            "barras ou '..'."
        )

    return nome


def _garantir_pasta_laboratorio():
    """Cria a pasta de laboratório se ela ainda não existir.
    Só a pasta raiz do laboratório — nunca nada fora dela."""
    os.makedirs(config.PASTA_LABORATORIO, exist_ok=True)


def criar_pasta_teste(nome: str) -> str:
    """
    Cria uma subpasta dentro da pasta de laboratório.

    TODO (futuro): antes de executar em produção, pedir confirmação
    explícita do usuário quando a ação envolver escrita no disco.
    """
    nome_validado = _validar_nome_pasta(nome)
    _garantir_pasta_laboratorio()

    caminho_final = os.path.join(config.PASTA_LABORATORIO, nome_validado)

    # Segunda camada de proteção: confirma que o caminho final ainda
    # está dentro da pasta de laboratório, mesmo depois do join.
    caminho_absoluto = os.path.abspath(caminho_final)
    if not caminho_absoluto.startswith(os.path.abspath(config.PASTA_LABORATORIO)):
        raise FerramentaError("Tentativa de criar pasta fora da área permitida.")

    if os.path.exists(caminho_absoluto):
        return f"A pasta '{nome_validado}' já existia."

    os.makedirs(caminho_absoluto)
    return f"Pasta '{nome_validado}' criada com sucesso em {config.PASTA_LABORATORIO}."


def listar_pastas_teste() -> str:
    """Lista as subpastas existentes dentro da pasta de laboratório."""
    _garantir_pasta_laboratorio()

    itens = os.listdir(config.PASTA_LABORATORIO)
    pastas = [
        item for item in itens
        if os.path.isdir(os.path.join(config.PASTA_LABORATORIO, item))
    ]

    if not pastas:
        return "Não há nenhuma pasta na área de laboratório ainda."

    return "Pastas encontradas: " + ", ".join(sorted(pastas))


# --------------------------------------------------------------------
# Registro das ferramentas
# --------------------------------------------------------------------
# Este dicionário é o que o main.py usa para, a partir do NOME que o
# modelo devolveu, achar a função Python real correspondente. É a
# "ponte" controlada entre o que o modelo pediu e o que é executado.
FUNCOES_DISPONIVEIS = {
    "criar_pasta_teste": criar_pasta_teste,
    "listar_pastas_teste": listar_pastas_teste,
}

# Este é o "cardápio" de ferramentas que é enviado ao Qwen3 a cada
# chamada, no formato de tool calling esperado pelo Ollama (compatível
# com o padrão usado por OpenAI/function calling). É a partir daqui
# que o modelo sabe quais ferramentas existem, o que elas fazem e
# quais argumentos elas esperam.
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "criar_pasta_teste",
            "description": (
                "Cria uma nova pasta dentro da área de laboratório do "
                "Gatuno. Use quando o usuário pedir explicitamente para "
                "criar uma pasta."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {
                        "type": "string",
                        "description": "Nome simples da pasta a ser criada, sem caminhos.",
                    }
                },
                "required": ["nome"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_pastas_teste",
            "description": (
                "Lista as pastas que já existem dentro da área de "
                "laboratório do Gatuno. Não recebe argumentos."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]
