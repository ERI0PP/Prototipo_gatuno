"""
modelo.py
---------
Este arquivo existe para isolar TODA a comunicação com o Ollama/Qwen3
em um único lugar. Nenhum outro arquivo do projeto deveria precisar
saber como montar uma requisição para o Ollama — eles só chamam
`conversar_com_qwen(...)` e recebem uma resposta pronta.

Isso separa "como eu falo com o modelo" (aqui) de "o que eu faço com
a resposta" (main.py) e de "quais ferramentas existem" (ferramentas.py).

Requer a biblioteca oficial do Ollama para Python:
    pip install ollama
"""

import ollama
import config


def conversar_com_qwen(mensagens: list, tools: list | None = None):
    """
    Envia o histórico de mensagens para o Qwen3 via Ollama e devolve
    a resposta bruta da API.

    Parâmetros
    ----------
    mensagens : list[dict]
        Histórico no formato [{"role": "user"/"assistant"/"system"/"tool", "content": "..."}]
    tools : list[dict] | None
        Lista de ferramentas no formato TOOLS_SCHEMA (ferramentas.py).
        Se None, o modelo responde sem a opção de chamar ferramentas.

    Retorno
    -------
    O objeto de resposta do Ollama (ollama.ChatResponse), de onde o
    main.py extrai o conteúdo e/ou as tool_calls.
    """
    kwargs = {
        "model": config.MODEL_NAME,
        "messages": mensagens,
        "options":{
            "num_ctx": config.tokens}
    }

    if tools:
        kwargs["tools"] = tools

    # --- Sobre o "thinking" do Qwen3 --------------------------------
    # A biblioteca `ollama` (e o servidor Ollama, a partir das versões
    # que suportam modelos "híbridos" como o Qwen3) aceita um parâmetro
    # `think` em client.chat(). Quando disponível:
    #   think=True  -> o modelo pode gerar um bloco de raciocínio,
    #                  exposto separadamente em response.message.thinking
    #   think=False -> o modelo responde direto, sem esse bloco
    #
    # Isso NÃO é algo que estou inventando: é um campo real da API do
    # Ollama para modelos com essa capacidade. Se a SUA versão instalada
    # do pacote `ollama` ou do servidor Ollama for antiga e não suportar
    # esse parâmetro, a chamada abaixo vai lançar um erro (TypeError ou
    # erro de API) em vez de falhar silenciosamente — nesse caso, o
    # ideal é atualizar com `pip install -U ollama` e `ollama --version`.
    if config.THINKING_ATIVADO:
        kwargs["think"] = True

    resposta = ollama.chat(**kwargs)
    return resposta


def extrair_texto(resposta) -> str:
    """Extrai apenas o texto final da resposta do modelo."""
    return resposta["message"]["content"]


def extrair_thinking(resposta) -> str | None:
    """
    Extrai o bloco de raciocínio (thinking), se ele existir na resposta.

    Se o campo não existir (versão da API não suporta, ou thinking
    desligado), devolve None — não inventamos um valor default.
    """
    mensagem = resposta.get("message", {})
    return mensagem.get("thinking")


def extrair_tool_calls(resposta):
    """
    Extrai a lista de chamadas de ferramenta pedidas pelo modelo,
    se houver. Cada item tem, no mínimo, um nome de função e os
    argumentos sugeridos pelo modelo (ainda não validados — isso é
    feito depois, em ferramentas.py).

    Se o modelo decidiu apenas conversar, isso volta vazio/None.
    """
    mensagem = resposta.get("message", {})
    return mensagem.get("tool_calls")
