"""
config.py
---------
Este arquivo existe para centralizar TODAS as configurações do protótipo
em um único lugar. A ideia é que, quando você quiser mudar o modelo, o
endereço do Ollama, a pasta de laboratório ou ligar/desligar o thinking,
você mexa em UM arquivo só — nunca dentro da lógica (main.py, modelo.py,
ferramentas.py).

Isso é uma prática comum em projetos maiores: separar "o que pode mudar"
(configuração) de "como o programa funciona" (lógica).
"""

import os

# --------------------------------------------------------------------
# Modelo / Ollama
# --------------------------------------------------------------------

# Nome exato do modelo como aparece em `ollama list`.
# Ajuste aqui se o nome/tag na sua instalação for diferente
# (ex.: "qwen3:8b", "qwen3:8b-q4_K_M", etc.)
MODEL_NAME = "Qwen3:latest"

# Host padrão do servidor Ollama rodando localmente.
OLLAMA_HOST = "http://localhost:11434"

# Liga/desliga o modo "thinking" do Qwen3, se a versão do Ollama/lib
# que você tem instalada suportar o parâmetro. Ver explicação detalhada
# no modelo.py sobre o que acontece se não for suportado.
THINKING_ATIVADO = True

# --------------------------------------------------------------------
# Pasta de laboratório (sandbox das ferramentas de arquivos)
# --------------------------------------------------------------------

# Todas as ferramentas que mexem em pastas/arquivos SÓ podem operar
# dentro deste diretório. Nada fora dele é acessível a partir das
# ferramentas — isso é validado em ferramentas.py.
PASTA_LABORATORIO = os.path.abspath("B:/Teste-Gatuno")

# --------------------------------------------------------------------
# Histórico de conversa
# --------------------------------------------------------------------

# Mensagem de sistema que define o "papel" do Qwen3 nesta fase do
# protótipo. Futuramente isso será substituído por uma identidade
# carregada do banco "Core" (ver planejamento do Gatuno).
SYSTEM_PROMPT = (
    "Você é o Gatuno, um assistente pessoal em fase de protótipo. "
    "Você pode conversar normalmente ou usar ferramentas quando o "
    "usuário pedir uma ação que corresponda a alguma ferramenta "
    "disponível. Só use uma ferramenta quando ela realmente for "
    "necessária para atender o pedido. Nunca invente nomes de "
    "ferramentas que não existem."
)

identidade = ('B:\Prototipo-Gatuno\Bancos\Core\Identidade.db') #caminho do banco de identidade

tokens = 16500