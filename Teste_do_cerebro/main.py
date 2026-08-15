"""
main.py
-------
Este arquivo existe para ser o "orquestrador": é o único lugar que
sabe o fluxo inteiro da conversa. Ele:
  1. mantém o histórico da conversa em memória (lista de mensagens);
  2. manda o histórico para o Qwen3 (via modelo.py);
  3. olha a resposta: é conversa normal ou pedido de ferramenta?
  4. se for ferramenta: valida e executa (via ferramentas.py),
     devolve o resultado ao modelo e pede a resposta final;
  5. imprime a resposta final e volta para o passo 1.

Os outros arquivos (config.py, modelo.py, ferramentas.py) não sabem
nada sobre esse fluxo — eles só expõem funções. Quem decide a ORDEM
das coisas é só este arquivo. Essa separação facilita trocar peças
depois (ex.: trocar Qwen3 por outro modelo) sem mexer no fluxo.
"""

import cerebro
import config
import modelo
import ferramentas


def executar_tool_call(tool_call) -> str:
    """
    Recebe UMA chamada de ferramenta sugerida pelo modelo, valida o
    nome contra o registro conhecido (FUNCOES_DISPONIVEIS) e executa.

    Retorna sempre uma string (o resultado, ou uma mensagem de erro
    controlada) — nunca deixa uma exceção subir e derrubar o loop.
    """
    nome_funcao = tool_call["function"]["name"]
    argumentos = tool_call["function"].get("arguments") or {}

    funcao = ferramentas.FUNCOES_DISPONIVEIS.get(nome_funcao)

    if funcao is None:
        # O modelo pediu uma ferramenta que não existe/não está
        # registrada. Isso não deveria acontecer (o modelo só vê as
        # ferramentas do TOOLS_SCHEMA), mas nunca confiamos cegamente.
        return f"Erro: ferramenta '{nome_funcao}' não é reconhecida pelo sistema."

    try:
        resultado = funcao(**argumentos)
        return str(resultado)
    except ferramentas.FerramentaError as erro:
        return f"Erro ao executar '{nome_funcao}': {erro}"
    except TypeError as erro:
        # Ex.: argumentos faltando ou nome de argumento errado.
        return f"Erro: argumentos inválidos para '{nome_funcao}' ({erro})."


def processar_turno(historico: list) -> str:
    """
    Processa UM turno completo do usuário: manda o histórico ao
    modelo, resolve eventuais chamadas de ferramenta, e devolve o
    texto final que deve ser mostrado ao usuário.

    `historico` é modificado in-place (mensagens de assistant/tool
    vão sendo adicionadas), para que o histórico continue completo
    no próximo turno.
    """
    resposta = modelo.conversar_com_qwen(historico, tools=ferramentas.TOOLS_SCHEMA)

    thinking = modelo.extrair_thinking(resposta)
    if config.THINKING_ATIVADO and thinking:
        # Mostrado separado só para você enxergar o raciocínio nesta
        # fase de laboratório. Na versão final do Gatuno, provavelmente
        # isso não seria exibido ao usuário comum.
        print(f"\n[thinking do Qwen3]\n{thinking}\n")

    tool_calls = modelo.extrair_tool_calls(resposta)

    if not tool_calls:
        # Caso 1 e 3 do enunciado: conversa normal, ou pergunta sem
        # ferramenta correspondente. Em ambos os casos o modelo só
        # respondeu texto — não há diferença de fluxo entre eles.
        texto = modelo.extrair_texto(resposta)
        historico.append({"role": "assistant", "content": texto})
        return texto

    # Caso 2: o modelo pediu uma ou mais ferramentas.
    # Primeiro, registramos no histórico a mensagem do assistente que
    # contém o pedido de tool call (isso é o formato que o Ollama
    # espera para manter o contexto coerente).
    historico.append(resposta["message"])

    for tool_call in tool_calls:
        resultado = executar_tool_call(tool_call)

        # O resultado da ferramenta entra no histórico com role "tool",
        # para que o modelo saiba que aquilo é um resultado de execução
        # e não uma fala do usuário.
        historico.append({"role": "tool", "content": resultado})

    # Depois que a(s) ferramenta(s) rodaram, chamamos o modelo de novo
    # para que ele transforme o resultado bruto em uma resposta natural
    # para o usuário (ex.: "Pronto, a pasta Estudos foi criada.").
    resposta_final = modelo.conversar_com_qwen(historico, tools=ferramentas.TOOLS_SCHEMA)
    texto_final = modelo.extrair_texto(resposta_final)
    historico.append({"role": "assistant", "content": texto_final})
    return texto_final


def main():
    print("=== Gatuno (protótipo de laboratório) ===")
    print("Digite 'sair' para encerrar.\n")

    identidade = cerebro.replicar_identidade() 

    historico = [{"role": "system", "content": config.SYSTEM_PROMPT},
        {"role": "system", "content": identidade}]

    while True:
        entrada = input("Você: ").strip()

        if entrada.lower() in ("sair", "exit", "quit"):
            print("Gatuno: Até mais, Erick.")
            break

        if not entrada:
            continue

        historico.append({"role": "user", "content": entrada})

        try:
            resposta_texto = processar_turno(historico)
        except Exception as erro:
            # Camada final de segurança: nenhum erro inesperado deve
            # derrubar o programa. Em produção isso viraria log.
            print(f"[erro inesperado: {erro}]")
            continue

        print(f"Gatuno: {resposta_texto}\n")


if __name__ == "__main__":
    main()
