from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import math
import sys
import webbrowser


# ==============================================================================
# WIDGET 1: BASE DO MOTOR (Figura 2D + Número de Cilindros Exclusivo)
# ==============================================================================
def gerar_svg_motor_inline(num_cilindros: int = 4, formato: str = "I") -> str:
    """
    Desenha o SVG 2D técnico do motor de acordo com o formato escolhido
    (I, V, VR ou W), suportando até 16 cilindros.
    """
    num_cilindros = max(1, min(16, int(num_cilindros)))
    formato = str(formato).upper()
    if formato not in ("I", "V", "VR", "W"):
        formato = "I"

    def desenhar_cilindro(cx: float, cy: float, r: float) -> str:
        r_pistao = max(2.8, r * 0.48)
        r_pino = max(1.4, r * 0.16)
        return (
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="rgba(34, 211, 238, 0.08)" stroke="#22D3EE" stroke-width="2" />\n'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_pistao:.1f}" '
            f'fill="rgba(129, 140, 248, 0.18)" stroke="#F8FAFC" stroke-width="1.7" />\n'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_pino:.1f}" '
            f'fill="#22D3EE" />\n'
        )

    corpo_svg = ""
    guia_cad = (
        '<path d="M 14,24 L 14,12 L 26,12 M 346,24 L 346,12 L 334,12 '
        'M 14,166 L 14,178 L 26,178 M 346,166 L 346,178 L 334,178" '
        'fill="none" stroke="rgba(34, 211, 238, 0.28)" stroke-width="1.2" stroke-linecap="round" />\n'
    )

    if formato == "I":
        largura_bloco = 260.0
        inicio_x = 50.0
        espaco = largura_bloco / num_cilindros
        raio = min(22.0, max(5.2, (espaco - 5.0) / 2.0))
        cilindros = "".join(
            desenhar_cilindro(inicio_x + i * espaco + espaco / 2.0, 95.0, raio)
            for i in range(num_cilindros)
        )
        corpo_svg = f"""
        <rect x="60" y="20" width="240" height="25" rx="6" fill="rgba(15, 23, 42, 0.72)" stroke="#CBD5E1" stroke-width="1.8" />
        <rect x="40" y="45" width="280" height="100" rx="12" fill="rgba(15, 23, 42, 0.85)" stroke="#E2E8F0" stroke-width="2" />
        {cilindros}
        <path d="M 70,145 L 290,145 L 270,172 L 90,172 Z" fill="rgba(15, 23, 42, 0.65)" stroke="#94A3B8" stroke-width="1.8" stroke-linejoin="round" />
        """

    elif formato == "V":
        n_sup = (num_cilindros + 1) // 2
        n_inf = num_cilindros // 2
        cols = max(1, n_sup, n_inf)
        largura = 240.0
        inicio_x = 60.0
        espaco = largura / cols
        raio = min(17.0, max(6.0, (espaco - 6.0) / 2.0))

        cilindros = ""
        for i in range(n_sup):
            cilindros += desenhar_cilindro(inicio_x + i * espaco + espaco / 2.0, 57.0, raio)
        for i in range(n_inf):
            cilindros += desenhar_cilindro(inicio_x + i * espaco + espaco / 2.0, 133.0, raio)

        corpo_svg = f"""
        <rect x="50" y="28" width="260" height="58" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#E2E8F0" stroke-width="2" />
        <rect x="50" y="104" width="260" height="58" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#E2E8F0" stroke-width="2" />
        <rect x="28" y="76" width="16" height="38" rx="4" fill="rgba(129, 140, 248, 0.22)" stroke="#818CF8" stroke-width="1.8" />
        <line x1="44" y1="95" x2="322" y2="95" stroke="#818CF8" stroke-width="2" stroke-dasharray="6,4" />
        {cilindros}
        """

    elif formato == "VR":
        largura = 244.0
        inicio_x = 58.0
        espaco = largura / num_cilindros
        raio = min(17.0, max(7.5, (espaco * 1.15 - 4.0) / 2.0))
        if num_cilindros >= 10:
            raio = min(raio, 10.5)

        cilindros = ""
        for i in range(num_cilindros):
            cx = inicio_x + i * espaco + espaco / 2.0
            cy = 80.0 if i % 2 == 0 else 110.0
            cilindros += desenhar_cilindro(cx, cy, raio)

        corpo_svg = f"""
        <rect x="65" y="22" width="230" height="20" rx="6" fill="rgba(15, 23, 42, 0.72)" stroke="#CBD5E1" stroke-width="1.8" />
        <rect x="44" y="42" width="272" height="106" rx="12" fill="rgba(15, 23, 42, 0.85)" stroke="#E2E8F0" stroke-width="2" />
        {cilindros}
        <path d="M 75,148 L 285,148 L 268,172 L 92,172 Z" fill="rgba(15, 23, 42, 0.65)" stroke="#94A3B8" stroke-width="1.8" stroke-linejoin="round" />
        """

    else:  # formato == "W"
        n_sup = (num_cilindros + 1) // 2
        n_inf = num_cilindros // 2
        cols = max(1, n_sup, n_inf)
        largura = 244.0
        inicio_x = 58.0
        espaco_sup = largura / max(1, n_sup)
        espaco_inf = largura / max(1, n_inf)
        raio = min(12.0, max(7.0, (largura / cols) * 0.35))

        cilindros = ""
        for i in range(n_sup):
            cx = inicio_x + i * espaco_sup + espaco_sup / 2.0
            cy = 43.0 if i % 2 == 0 else 63.0
            cilindros += desenhar_cilindro(cx, cy, raio)
        for i in range(n_inf):
            cx = inicio_x + i * espaco_inf + espaco_inf / 2.0
            cy = 127.0 if i % 2 == 0 else 147.0
            cilindros += desenhar_cilindro(cx, cy, raio)

        corpo_svg = f"""
        <rect x="44" y="20" width="272" height="66" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#E2E8F0" stroke-width="2" />
        <rect x="44" y="104" width="272" height="66" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#E2E8F0" stroke-width="2" />
        <rect x="24" y="78" width="14" height="34" rx="4" fill="rgba(129, 140, 248, 0.22)" stroke="#818CF8" stroke-width="1.8" />
        <line x1="38" y1="95" x2="326" y2="95" stroke="#818CF8" stroke-width="2" stroke-dasharray="6,4" />
        {cilindros}
        """

    return f"""
    <svg class="motor-svg" viewBox="0 0 360 190" xmlns="http://www.w3.org/2000/svg"
         aria-label="Motor {formato} 2D">
        {guia_cad}
        {corpo_svg}
    </svg>
    """


def widget_motor_inline(num_cilindros: int = 4, formato: str = "I") -> str:
    """
    Gera o Widget 1 com a figura 2D do motor
    e exibe exclusivamente o número de cilindros.
    """
    return f"""
    <section class="widget-card widget-visual" id="widget-1">
        <div id="motor-svg-container" class="motor-stage">
            {gerar_svg_motor_inline(num_cilindros, formato)}
        </div>

        <!-- Exibição EXCLUSIVA do número de cilindros -->
        <div class="cilindros-box">
            <span class="cilindros-numero" id="motor-num-cilindros">{num_cilindros}</span>
            <span class="cilindros-texto">CILINDROS</span>
        </div>
    </section>
    """


# ==============================================================================
# WIDGET 2: 5 MOTORES PREDEFINIDOS FAMOSOS (DedSec Minimalista: Preto & WhiteSmoke)
# ==============================================================================
FORMATOS_MOTOR = {
    "I": "I (Em Linha)",
    "V": "V (Em V)",
    "VR": "VR (V Estreito)",
    "W": "W (Em W)",
}

PERFIS_ADMISSAO = {
    "Atmosférico": {
        "pressao": "0.0 bar (Atmosférico)",
        "mult_potencia": 1.00,
        "mult_binario": 1.00,
    },
    "Turbo": {
        "pressao": "+1.5 bar",
        "mult_potencia": 1.55,
        "mult_binario": 1.60,
    },
    "Supercompressor": {
        "pressao": "+0.8 bar",
        "mult_potencia": 1.35,
        "mult_binario": 1.45,
    },
    "Biturbo": {
        "pressao": "+2.0 bar",
        "mult_potencia": 1.80,
        "mult_binario": 1.85,
    },
    "Bicarregado": {
        "pressao": "+2.0 bar",
        "mult_potencia": 1.90,
        "mult_binario": 1.95,
    },
}

MOTORES_PREDEFINIDOS = [
    {
        "id": "koenigsegg_jesko",
        "nome": "Koenigsegg Jesko — Hot V8",
        "resumo": "V8 · 5.0L · Biturbo · Etanol (E85)",
        "formato": "V",
        "cilindros": 8,
        "admissao": "Biturbo",
        "bore": 92.0,
        "stroke": 95.25,
        "compression_ratio": 8.6,
        "max_rpm": 7800,
        "combustivel": "Etanol (E85)",
        "ciclo": "4T",
    },
    {
        "id": "bugatti_bolide",
        "nome": "Bugatti Bolide — W16",
        "resumo": "W16 · 8.0L · Biturbo · Gasolina",
        "formato": "W",
        "cilindros": 16,
        "admissao": "Biturbo",
        "bore": 86.0,
        "stroke": 86.0,
        "compression_ratio": 9.0,
        "max_rpm": 7000,
        "combustivel": "Gasolina",
        "ciclo": "4T",
    },
    {
        "id": "vw_vr6",
        "nome": "Volkswagen R32 — VR6",
        "resumo": "VR6 · 3.2L · Atmosférico · Gasolina",
        "formato": "VR",
        "cilindros": 6,
        "admissao": "Atmosférico",
        "bore": 84.0,
        "stroke": 95.9,
        "compression_ratio": 10.9,
        "max_rpm": 6800,
        "combustivel": "Gasolina",
        "ciclo": "4T",
    },
    {
        "id": "dodge_hellcat",
        "nome": "Dodge Hellcat — V8",
        "resumo": "V8 · 6.2L · Supercompressor · Gasolina",
        "formato": "V",
        "cilindros": 8,
        "admissao": "Supercompressor",
        "bore": 103.9,
        "stroke": 90.9,
        "compression_ratio": 9.5,
        "max_rpm": 6200,
        "combustivel": "Gasolina",
        "ciclo": "4T",
    },
    {
        "id": "audi_quattro",
        "nome": "Audi Sport Quattro — I5",
        "resumo": "I5 · 2.1L · Turbo · Gasolina",
        "formato": "I",
        "cilindros": 5,
        "admissao": "Turbo",
        "bore": 79.5,
        "stroke": 86.4,
        "compression_ratio": 7.5,
        "max_rpm": 7500,
        "combustivel": "Gasolina",
        "ciclo": "4T",
    },
]


def widget_2_modular() -> str:
    """
    Widget 2: Apresenta 5 motores famosos predefinidos. Ao clicar num deles,
    todas as configurações do motor e a Ficha Técnica são preenchidas automaticamente.
    """
    botoes_html = "\n".join(
        f"""
        <button type="button" class="btn-preset-motor" data-preset-id="{m['id']}">
            <span class="preset-nome">{m['nome']}</span>
            <span class="preset-resumo">{m['resumo']}</span>
        </button>
        """
        for m in MOTORES_PREDEFINIDOS
    )

    return f"""
    <section class="widget-card widget-presets" id="widget-2">
        <div class="widget-header">
            <span class="ficha-titulo">MOTORES PREDEFINIDOS</span>
            <span class="widget-badge">5 ÍCONES</span>
        </div>
        <div class="presets-lista" id="presets-lista">
            {botoes_html}
        </div>
    </section>
    """


# ==============================================================================
# WIDGET 3: TODAS AS CONFIGURAÇÕES DO MOTOR + FICHA TÉCNICA INFERIOR
# ==============================================================================
def processar_combustao(
    bore: float = 86.0,
    stroke: float = 86.0,
    compression_ratio: float = 10.5,
    max_rpm: int = 7500,
    combustivel: str = "Gasolina",
    ciclo: str = "4T",
    num_cilindros: int = 4,
    admissao: str = "Atmosférico",
    formato: str = "I",
) -> dict:
    """
    Calcula automaticamente em Python os parâmetros para a Ficha Técnica:
    - Tipo de motor (Formato + Cilindros + Admissão + Ciclo)
    - Cilindrada total em Litros (L)
    - Pressão em bar (consoante a admissão)
    - Binário estimado em Nm
    - Potência estimada em cv
    """
    bore = max(10.0, float(bore))
    stroke = max(10.0, float(stroke))
    cr = max(2.0, float(compression_ratio))
    max_rpm = max(500, int(max_rpm))
    num_cilindros = max(1, min(16, int(num_cilindros)))
    ciclo = "2T" if str(ciclo).upper() == "2T" else "4T"
    formato_valido = str(formato).upper() if str(formato).upper() in FORMATOS_MOTOR else "I"
    admissao_valida = admissao if admissao in PERFIS_ADMISSAO else "Atmosférico"
    perfil_adm = PERFIS_ADMISSAO[admissao_valida]

    fatores_combustivel = {
        "Gasolina": 1.00,
        "Etanol (E85)": 1.08,
        "Metanol": 1.12,
    }
    fator_comb = fatores_combustivel.get(combustivel, 1.00)

    # 1. Cilindrada em Litros: V = (pi/4) * (diametro_cm^2) * curso_cm * cilindros / 1000
    cilindrada_unit_cc = (math.pi / 4.0) * ((bore / 10.0) ** 2) * (stroke / 10.0)
    cilindrada_litros = (cilindrada_unit_cc * num_cilindros) / 1000.0

    # 2. Binário estimado (Nm) e Potência estimada (cv) considerando o boost da admissão
    fator_cr = 1.0 + max(-0.25, min(0.35, (cr - 10.0) * 0.025))
    fator_ciclo_tq = 1.25 if ciclo == "2T" else 1.00
    torque_nm = int(round(
        cilindrada_litros * 105.0 * fator_cr * fator_comb * fator_ciclo_tq * perfil_adm["mult_binario"]
    ))

    fator_rpm_potencia = 0.88 if ciclo == "4T" else 0.94
    potencia_cv = int(round(
        ((torque_nm * max_rpm * fator_rpm_potencia) / 7121.0)
        * (perfil_adm["mult_potencia"] / perfil_adm["mult_binario"])
        * 1.01387
    ))

    # 3. Validação da velocidade média do pistão (Vm = 2 * Curso_m * RPM / 60) e taxa de compressão > 15
    velocidade_pistao_mps = (2.0 * (stroke / 1000.0) * max_rpm) / 60.0
    motivos_alerta = []
    if velocidade_pistao_mps > 25.0:
        motivos_alerta.append(f"Vel. média do pistão elevada ({velocidade_pistao_mps:.1f} m/s > 25.0 m/s)")
    if cr > 15.0:
        motivos_alerta.append("Taxa de compressão > 15:1")
    alerta_rpm = len(motivos_alerta) > 0

    return {
        "tipo_motor": f"{formato_valido}{num_cilindros} · {admissao_valida} ({ciclo})",
        "cilindrada_litros": f"{cilindrada_litros:.2f} L",
        "pressao_bar": perfil_adm["pressao"],
        "torque_nm": f"{torque_nm} Nm",
        "potencia_cv": f"{potencia_cv} cv",
        "velocidade_pistao_mps": round(velocidade_pistao_mps, 2),
        "alerta_rpm": alerta_rpm,
        "motivos_alerta": motivos_alerta,
    }


def render_resultado_combustao(dados: dict) -> str:
    """Renderiza a Ficha Técnica em formato de painel horizontal na parte inferior do ecrã."""
    return f"""
    <div class="ficha-tecnica-inferior">
        <div class="ficha-titulo">FICHA TÉCNICA</div>
        <div class="ficha-itens-grid">
            <div class="ficha-item"><span>TIPO DE MOTOR</span><strong>{dados['tipo_motor']}</strong></div>
            <div class="ficha-item"><span>CILINDRADA</span><strong>{dados['cilindrada_litros']}</strong></div>
            <div class="ficha-item"><span>PRESSÃO</span><strong>{dados['pressao_bar']}</strong></div>
            <div class="ficha-item"><span>BINÁRIO EST.</span><strong>{dados['torque_nm']}</strong></div>
            <div class="ficha-item"><span>POTÊNCIA EST.</span><strong>{dados['potencia_cv']}</strong></div>
        </div>
    </div>
    """


def widget_3_modular(
    num_cilindros: int = 4,
    admissao: str = "Atmosférico",
    formato: str = "I",
) -> str:
    """
    Widget 3: Concentra todas as configurações do motor e de combustão num único espaço
    (Formato, Cilindros, Admissão, Diâmetro, Curso, Taxa de Compressão, Rotação Máx.,
    Combustível e Ciclo 2T/4T).
    """
    dados_iniciais = processar_combustao(
        num_cilindros=num_cilindros,
        admissao=admissao,
        formato=formato,
    )
    classe_rpm = "input-cyber input-alerta" if dados_iniciais["alerta_rpm"] else "input-cyber"
    texto_alerta = " | ".join(dados_iniciais["motivos_alerta"])

    opcoes_cilindros = [3, 4, 5, 6, 8, 10, 12, 16]
    options_fmt_html = "\n".join(
        f'<option value="{cod}" {"selected" if cod == formato else ""}>{rotulo}</option>'
        for cod, rotulo in FORMATOS_MOTOR.items()
    )
    options_cyl_html = "\n".join(
        f'<option value="{c}" {"selected" if c == num_cilindros else ""}>{c} Cilindros</option>'
        for c in opcoes_cilindros
    )
    options_adm_html = "\n".join(
        f'<option value="{a}" {"selected" if a == admissao else ""}>{a}</option>'
        for a in PERFIS_ADMISSAO.keys()
    )

    return f"""
    <section class="widget-card widget-configs" id="widget-3">
        <div class="widget-header">
            <span class="ficha-titulo">CONFIGURAÇÕES DO MOTOR</span>
            <span class="widget-badge badge-live">TEMPO REAL</span>
        </div>
        <div class="widget-form">
            <div class="grid-2-col">
                <div class="campo-grupo">
                    <label for="select-formato">FORMATO DO MOTOR</label>
                    <select id="select-formato" class="input-cyber">
                        {options_fmt_html}
                    </select>
                </div>
                <div class="campo-grupo">
                    <label for="select-cilindros">NÚMERO DE CILINDROS</label>
                    <select id="select-cilindros" class="input-cyber">
                        {options_cyl_html}
                    </select>
                </div>
                <div class="campo-grupo">
                    <label for="select-admissao">TIPO DE ADMISSÃO</label>
                    <select id="select-admissao" class="input-cyber">
                        {options_adm_html}
                    </select>
                </div>
                <div class="campo-grupo">
                    <label for="select-ciclo">CICLO (2T / 4T)</label>
                    <select id="select-ciclo" class="input-cyber">
                        <option value="4T" selected>4T</option>
                        <option value="2T">2T</option>
                    </select>
                </div>
                <div class="campo-grupo">
                    <label for="input-bore">DIÂMETRO (mm)</label>
                    <input type="number" id="input-bore" class="input-cyber" value="86.0" step="0.5" min="20" max="200">
                </div>
                <div class="campo-grupo">
                    <label for="input-stroke">CURSO (mm)</label>
                    <input type="number" id="input-stroke" class="input-cyber" value="86.0" step="0.5" min="20" max="200">
                </div>
                <div class="campo-grupo">
                    <label for="input-cr">TAXA DE COMPRESSÃO (:1)</label>
                    <input type="number" id="input-cr" class="input-cyber" value="10.5" step="0.1" min="4" max="25">
                </div>
                <div class="campo-grupo">
                    <label for="input-rpm">ROTAÇÃO MÁX. (RPM)</label>
                    <input type="number" id="input-rpm" class="{classe_rpm}" value="7500" step="100" min="1000" max="25000">
                </div>
                <div class="campo-grupo campo-largura-total">
                    <label for="select-combustivel">COMBUSTÍVEL</label>
                    <select id="select-combustivel" class="input-cyber">
                        <option value="Gasolina" selected>Gasolina</option>
                        <option value="Etanol (E85)">Etanol (E85)</option>
                        <option value="Metanol">Metanol</option>
                    </select>
                </div>
            </div>
            <div id="rpm-alerta-msg" class="rpm-alerta-msg">{texto_alerta}</div>
        </div>
    </section>
    """


# ==============================================================================
# MÓDULO QUIZ AUTOMÓVEL (11 Perguntas no Banco, 5 Aleatórias por Sessão)
# ==============================================================================
QUIZ_NUM_PERGUNTAS = 5

QUIZ_PERGUNTAS = [
    {
        "id": 1,
        "pergunta": "Qual é a função principal do radiador num automóvel com motor de combustão interna?",
        "opcoes": [
            "Aquecer o habitáculo do veículo.",
            "Filtrar o ar que entra para o motor.",
            "Arrefecer o líquido de refrigeração do motor.",
            "Armazenar energia para o arranque.",
        ],
        "correta": 2,
    },
    {
        "id": 2,
        "pergunta": 'O que significa a sigla "ABS" nos sistemas de travagem?',
        "opcoes": [
            "Sistema de Travagem Antibloqueio (Anti-lock Braking System).",
            "Suporte Automático de Travagem (Automatic Brake Support).",
            "Segurança Avançada de Travões (Advanced Brake Security).",
            "Sistema de Equilíbrio Assistido (Assisted Balance System).",
        ],
        "correta": 0,
    },
    {
        "id": 3,
        "pergunta": "Qual destes componentes é responsável por converter o movimento linear dos pistões em movimento rotativo?",
        "opcoes": [
            "Árvore de cames.",
            "Volante do motor.",
            "Caixa de velocidades.",
            "Cambota.",
        ],
        "correta": 3,
    },
    {
        "id": 4,
        "pergunta": "Qual é a função do alternador num veículo?",
        "opcoes": [
            "Alternar entre tração dianteira e traseira.",
            "Gerar energia elétrica para carregar a bateria e alimentar o carro.",
            "Regular a mistura de ar e combustível.",
            "Enviar corrente contínua diretamente para as velas.",
        ],
        "correta": 1,
    },
    {
        "id": 5,
        "pergunta": "Para que serve o diferencial num automóvel?",
        "opcoes": [
            "Aumentar a potência do motor em subidas.",
            "Permitir que as rodas do mesmo eixo girem a velocidades diferentes em curva.",
            "Equilibrar o peso entre a frente e a traseira.",
            "Desligar o motor da transmissão quando o carro para.",
        ],
        "correta": 1,
    },
    {
        "id": 6,
        "pergunta": "Num sistema de suspensão, qual é a função exata do amortecedor?",
        "opcoes": [
            "Suportar o peso total do veículo.",
            "Ajustar automaticamente a altura ao solo.",
            "Impedir a inclinação da carroçaria em curva.",
            "Controlar as oscilações das molas, mantendo o pneu no solo.",
        ],
        "correta": 3,
    },
    {
        "id": 7,
        "pergunta": 'O que define a "taxa de compressão" de um motor de combustão interna?',
        "opcoes": [
            "A relação entre o volume total do cilindro e o volume da câmara de combustão.",
            "A pressão máxima atingida no cilindro durante a explosão.",
            "A força dos segmentos contra as paredes do cilindro.",
            "A relação entre a pressão atmosférica e a pressão do turbo.",
        ],
        "correta": 0,
    },
    {
        "id": 8,
        "pergunta": 'Qual é a vantagem técnica de utilizar um "Intercooler" num motor sobrealimentado (turbo ou compressor)?',
        "opcoes": [
            "Arrefece o óleo que lubrifica a turbina.",
            "Reduz a temperatura dos gases de escape.",
            "Elimina o atraso do turbo (turbo lag).",
            "Arrefece o ar comprimido, aumentando a sua densidade e oxigénio.",
        ],
        "correta": 3,
    },
    {
        "id": 9,
        "pergunta": 'O que é o fenómeno da "detonação" (ou "grilar" / knocking) num motor a gasolina?',
        "opcoes": [
            "Explosão de combustível não queimado no escape.",
            "Falha completa da bobina de ignição.",
            "Ignição prematura e descontrolada da mistura antes da faísca da vela.",
            "Bater das válvulas por falta de pressão de óleo.",
        ],
        "correta": 2,
    },
    {
        "id": 10,
        "pergunta": 'O que é um sistema de lubrificação por "cárter seco" (dry sump), comum em automóveis desportivos de alta performance?',
        "opcoes": [
            "Armazena o óleo num depósito externo para baixar o motor e manter a lubrificação em curva.",
            "Usa rolamentos selados e dispensa óleo lubrificante.",
            "Pulveriza óleo em estado gasoso sobre as bielas.",
            "Usa um cárter em fibra de carbono para dissipar calor.",
        ],
        "correta": 0,
    },
    {
        "id": 11,
        "pergunta": 'Qual é a função da "Waste-gate" num sistema de turbocompressor?',
        "opcoes": [
            "Libertar pressão da admissão ao tirar o pé do acelerador.",
            "Desviar gases de escape da turbina para limitar a pressão e velocidade do turbo.",
            "Filtrar partículas antes de atingirem a turbina.",
            "Injetar combustível no escape para manter o turbo a girar.",
        ],
        "correta": 1,
    },
]


def avaliar_quiz(respostas: dict, ids: list | None = None) -> dict:
    """
    Avalia em Python as respostas submetidas pelo utilizador para o quiz.
    `respostas` mapeia id da pergunta (str ou int) para índice da opção escolhida (int).
    `ids` indica a lista ordenada de IDs das perguntas apresentadas na sessão atual.
    """
    pontuacao = 0
    detalhes = []

    mapa_perguntas = {q["id"]: q for q in QUIZ_PERGUNTAS}
    if ids:
        perguntas_avaliar = []
        for qid_raw in ids:
            try:
                qid_int = int(qid_raw)
            except (TypeError, ValueError):
                continue
            if qid_int in mapa_perguntas:
                perguntas_avaliar.append(mapa_perguntas[qid_int])
    else:
        perguntas_avaliar = QUIZ_PERGUNTAS

    for q in perguntas_avaliar:
        qid = str(q["id"])
        escolha_raw = respostas.get(qid)
        if escolha_raw is None:
            escolha_raw = respostas.get(q["id"])

        try:
            escolha_idx = int(escolha_raw) if escolha_raw is not None else -1
        except (TypeError, ValueError):
            escolha_idx = -1

        correta_idx = q["correta"]
        acertou = escolha_idx == correta_idx
        if acertou:
            pontuacao += 1

        detalhes.append({
            "id": q["id"],
            "acertou": acertou,
            "respondida": escolha_idx >= 0,
            "escolha": escolha_idx,
            "correta": correta_idx,
            "texto_correto": q["opcoes"][correta_idx],
        })

    total = len(perguntas_avaliar)
    percentagem = int(round((pontuacao / total) * 100)) if total else 0

    if percentagem >= 70:
        classificacao = "Verdadeiro purista!"
    elif percentagem >= 50:
        classificacao = "Purista emergente"
    else:
        classificacao = "Condutor diário"

    return {
        "pontuacao": pontuacao,
        "total": total,
        "percentagem": percentagem,
        "classificacao": classificacao,
        "detalhes": detalhes,
    }


def widget_quiz_modular() -> str:
    """
    Gera o HTML do modal/painel interativo do Quiz automóvel (5 perguntas aleatórias).
    """
    return f"""
    <div class="quiz-modal" id="quiz-modal" aria-hidden="true">
        <div class="quiz-container" role="dialog" aria-modal="true" aria-labelledby="quiz-titulo">
            <header class="quiz-header">
                <div class="quiz-header-info">
                    <h2 id="quiz-titulo">QUIZ AUTOMÓVEL · {QUIZ_NUM_PERGUNTAS} PERGUNTAS ALEATÓRIAS</h2>
                    <div class="quiz-progresso-wrap">
                        <span class="quiz-progresso" id="quiz-progresso">Respondidas: 0 / {QUIZ_NUM_PERGUNTAS}</span>
                        <div class="quiz-progresso-barra">
                            <div class="quiz-progresso-fill" id="quiz-progresso-fill"></div>
                        </div>
                    </div>
                </div>
                <button type="button" class="btn-cyber-acao" id="btn-fechar-quiz">VOLTAR AO PAINEL</button>
            </header>

            <div class="quiz-resultado-banner" id="quiz-resultado-banner" style="display: none;"></div>

            <form id="quiz-form" class="quiz-lista" onsubmit="return false;">
                <div id="quiz-perguntas-container" class="quiz-lista"></div>

                <div class="quiz-acoes-footer">
                    <button type="submit" class="btn-cyber-acao btn-destaque" id="btn-submeter-quiz">
                        VERIFICAR RESPOSTAS
                    </button>
                    <button type="button" class="btn-cyber-acao" id="btn-reiniciar-quiz">
                        REINICIAR QUIZ
                    </button>
                </div>
            </form>
        </div>
    </div>
    """


# ==============================================================================
# MONTAGEM DO PAINEL WEB (HTML + CSS INLINE SIMPLES)
# ==============================================================================
def gerar_dashboard_html(
    num_cilindros: int = 4,
    admissao: str = "Atmosférico",
    formato: str = "I",
) -> str:
    """
    Junta os 3 widgets superiores, a Ficha Técnica inferior de largura total
    e o botão/modal de acesso ao Quiz numa página HTML em português.
    """
    w1 = widget_motor_inline(num_cilindros, formato)
    w2 = widget_2_modular()
    w3 = widget_3_modular(num_cilindros, admissao, formato)
    ficha_inicial = render_resultado_combustao(
        processar_combustao(num_cilindros=num_cilindros, admissao=admissao, formato=formato)
    )
    quiz_html = widget_quiz_modular()
    quiz_json = json.dumps(
        [
            {
                "id": q["id"],
                "pergunta": q["pergunta"],
                "opcoes": q["opcoes"],
                "correta": q["correta"],
            }
            for q in QUIZ_PERGUNTAS
        ],
        ensure_ascii=False,
    )
    presets_json = json.dumps(MOTORES_PREDEFINIDOS, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel de Motor</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            color-scheme: dark;
            --bg-base: #070a12;
            --bg-elevated: rgba(15, 22, 38, 0.78);
            --bg-surface: rgba(11, 16, 29, 0.9);
            --bg-surface-hover: rgba(25, 36, 60, 0.92);
            --border-subtle: rgba(148, 163, 184, 0.16);
            --border-cyan: rgba(34, 211, 238, 0.45);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-cyan: #22d3ee;
            --accent-indigo: #818cf8;
            --accent-lime: #a3e635;
            --accent-emerald: #34d399;
            --accent-amber: #fbbf24;
            --accent-danger: #ff3b5c;
            --radius-xl: 20px;
            --radius-lg: 14px;
            --radius-md: 10px;
            --shadow-card: 0 22px 48px -20px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(255, 255, 255, 0.06);
            --font-sans: 'Space Grotesk', 'Segoe UI Variable', 'Inter', system-ui, -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', 'Cascadia Code', 'Consolas', monospace;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        /* Base do site: Dark Motorsport Glass */
        body {{
            background-color: var(--bg-base);
            background-image:
                radial-gradient(circle at 12% 10%, rgba(34, 211, 238, 0.14), transparent 36%),
                radial-gradient(circle at 88% 12%, rgba(99, 102, 241, 0.15), transparent 38%),
                radial-gradient(circle at 50% 95%, rgba(163, 230, 53, 0.07), transparent 42%);
            color: var(--text-primary);
            font-family: var(--font-sans);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 28px 24px;
            position: relative;
            overflow-x: hidden;
        }}

        body::before {{
            content: '';
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(rgba(148, 163, 184, 0.035) 1px, transparent 1px),
                linear-gradient(90deg, rgba(148, 163, 184, 0.035) 1px, transparent 1px);
            background-size: 38px 38px;
            mask-image: radial-gradient(ellipse at center, black 35%, transparent 85%);
            -webkit-mask-image: radial-gradient(ellipse at center, black 35%, transparent 85%);
            pointer-events: none;
            z-index: 0;
        }}

        body > * {{
            position: relative;
            z-index: 1;
        }}

        /* Barra Superior & Botão de Acesso ao Quiz */
        .dashboard-topbar {{
            width: 100%;
            max-width: 1240px;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 14px;
            margin-bottom: 20px;
            padding: 14px 20px;
            background: var(--bg-elevated);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-xl);
            box-shadow: var(--shadow-card);
        }}

        .topbar-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .topbar-icon {{
            width: 38px;
            height: 38px;
            border-radius: 12px;
            background: linear-gradient(135deg, rgba(34, 211, 238, 0.22), rgba(129, 140, 248, 0.24));
            border: 1px solid rgba(34, 211, 238, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--accent-cyan);
            flex-shrink: 0;
        }}

        .topbar-textos {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}

        .topbar-titulo {{
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            color: var(--text-primary);
            line-height: 1.2;
        }}

        .topbar-subtitulo {{
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.14em;
            color: var(--accent-cyan);
            text-transform: uppercase;
        }}

        .btn-cyber-acao {{
            background: rgba(15, 23, 42, 0.85);
            color: var(--text-primary);
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 999px;
            padding: 10px 18px;
            font-family: var(--font-sans);
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease, background-color 0.18s ease;
        }}

        .btn-cyber-acao:hover {{
            border-color: var(--accent-cyan);
            background: rgba(30, 41, 59, 0.95);
            transform: translateY(-1px);
            box-shadow: 0 8px 20px -8px rgba(34, 211, 238, 0.45);
        }}

        .btn-cyber-acao:active {{
            transform: translateY(0);
        }}

        .btn-quiz-cta,
        .btn-destaque {{
            background: linear-gradient(135deg, #22d3ee 0%, #6366f1 100%);
            color: #060911;
            border: none;
            font-weight: 700;
            box-shadow: 0 10px 26px -10px rgba(34, 211, 238, 0.65);
        }}

        .btn-quiz-cta:hover,
        .btn-destaque:hover {{
            background: linear-gradient(135deg, #67e8f9 0%, #818cf8 100%);
            color: #060911;
            box-shadow: 0 12px 30px -8px rgba(34, 211, 238, 0.8);
        }}

        /* Grelha principal para os 3 widgets */
        .dashboard-container {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 20px;
            width: 100%;
            max-width: 1240px;
        }}

        /* Cartão de cada widget com estilo glassmorphism moderno */
        .widget-card {{
            background: var(--bg-elevated);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-xl);
            padding: 22px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            min-height: 390px;
            gap: 16px;
            box-shadow: var(--shadow-card);
            transition: border-color 0.2s ease, transform 0.2s ease;
        }}

        .widget-card:hover {{
            border-color: rgba(148, 163, 184, 0.28);
        }}

        .widget-header {{
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .ficha-titulo {{
            font-size: 0.84rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            color: var(--text-primary);
            text-transform: uppercase;
        }}

        .widget-badge {{
            font-family: var(--font-mono);
            font-size: 0.66rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            padding: 4px 9px;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.12);
            color: var(--text-secondary);
            border: 1px solid rgba(148, 163, 184, 0.18);
            white-space: nowrap;
        }}

        .widget-badge.badge-live {{
            color: var(--accent-lime);
            background: rgba(163, 230, 53, 0.1);
            border-color: rgba(163, 230, 53, 0.3);
        }}

        /* Widget 1: Stage Blueprint + Contador Exclusivo de Cilindros */
        .widget-visual {{
            justify-content: space-between;
        }}

        .motor-stage {{
            width: 100%;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 16px 12px;
            border-radius: 16px;
            background-color: rgba(6, 9, 17, 0.86);
            background-image: radial-gradient(rgba(34, 211, 238, 0.14) 1px, transparent 1px);
            background-size: 16px 16px;
            border: 1px solid rgba(34, 211, 238, 0.18);
            box-shadow: inset 0 0 32px rgba(0, 0, 0, 0.65);
        }}

        .motor-svg {{
            width: 100%;
            max-width: 320px;
            height: auto;
            filter: drop-shadow(0 0 12px rgba(34, 211, 238, 0.16));
            transition: transform 0.25s ease;
        }}

        /* Exibição exclusiva do número de cilindros (Widget 1) */
        .cilindros-box {{
            width: 100%;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.65));
            border: 1px solid rgba(34, 211, 238, 0.28);
            border-radius: 14px;
            padding: 12px 24px;
            text-align: center;
            display: flex;
            align-items: baseline;
            justify-content: center;
            gap: 12px;
        }}

        .cilindros-numero {{
            font-family: var(--font-mono);
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1;
            font-variant-numeric: tabular-nums;
            background: linear-gradient(135deg, #f8fafc 25%, #22d3ee 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }}

        .cilindros-texto {{
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.18em;
            color: var(--text-secondary);
        }}

        /* Formulários e Tabelas (Widgets 2 e 3) */
        .widget-form {{
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .grid-2-col {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}

        .campo-grupo {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}

        .campo-largura-total {{
            grid-column: 1 / -1;
        }}

        .campo-grupo label {{
            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            color: var(--text-secondary);
            text-transform: uppercase;
        }}

        .input-cyber {{
            background-color: rgba(7, 10, 18, 0.85);
            color: var(--text-primary);
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: var(--radius-md);
            padding: 9px 11px;
            font-family: var(--font-mono);
            font-size: 0.82rem;
            outline: none;
            width: 100%;
            transition: border-color 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease;
        }}

        select.input-cyber {{
            font-family: var(--font-sans);
            font-weight: 500;
            appearance: none;
            -webkit-appearance: none;
            padding-right: 30px;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 10px center;
            cursor: pointer;
        }}

        select.input-cyber option {{
            background-color: #0b101d;
            color: #f8fafc;
        }}

        .btn-cyber-acao:focus-visible,
        .btn-preset-motor:focus-visible,
        .quiz-opcao:focus-within {{
            outline: 2px solid var(--accent-cyan);
            outline-offset: 2px;
        }}

        .input-cyber:hover {{
            border-color: rgba(148, 163, 184, 0.42);
        }}

        .input-cyber:focus {{
            border-color: var(--accent-cyan);
            background-color: rgba(11, 16, 29, 0.98);
            box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.16);
        }}

        .input-cyber.input-alerta {{
            border-color: var(--accent-danger);
            background-color: rgba(255, 59, 92, 0.14);
            color: #ff99ab;
            font-weight: 700;
            box-shadow: 0 0 0 3px rgba(255, 59, 92, 0.16);
        }}

        .rpm-alerta-msg {{
            font-size: 0.72rem;
            line-height: 1.35;
            min-height: 0;
        }}

        .rpm-alerta-msg:not(:empty) {{
            margin-top: 2px;
            padding: 8px 11px;
            border-radius: var(--radius-md);
            background: rgba(255, 59, 92, 0.12);
            border: 1px solid rgba(255, 59, 92, 0.38);
            color: #ff99ab;
            font-weight: 500;
        }}

        /* Widget 2: Motores Predefinidos */
        .widget-presets {{
            justify-content: flex-start;
            gap: 14px;
        }}

        .presets-lista {{
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 9px;
        }}

        .btn-preset-motor {{
            position: relative;
            background: rgba(7, 10, 18, 0.65);
            color: var(--text-primary);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 12px;
            padding: 11px 14px 11px 17px;
            text-align: left;
            font-family: var(--font-sans);
            cursor: pointer;
            display: flex;
            flex-direction: column;
            gap: 3px;
            overflow: hidden;
            transition: transform 0.16s ease, border-color 0.16s ease, background-color 0.16s ease, box-shadow 0.16s ease;
        }}

        .btn-preset-motor::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 8px;
            bottom: 8px;
            width: 3px;
            border-radius: 99px;
            background: rgba(148, 163, 184, 0.25);
            transition: background-color 0.16s ease, box-shadow 0.16s ease;
        }}

        .btn-preset-motor:hover {{
            border-color: rgba(34, 211, 238, 0.45);
            background: var(--bg-surface-hover);
            transform: translateY(-1px);
        }}

        .btn-preset-motor:hover::before {{
            background: var(--accent-cyan);
        }}

        .btn-preset-motor.ativo {{
            background: linear-gradient(135deg, rgba(34, 211, 238, 0.18), rgba(99, 102, 241, 0.2));
            border-color: var(--accent-cyan);
            box-shadow: 0 10px 24px -14px rgba(34, 211, 238, 0.75);
        }}

        .btn-preset-motor.ativo::before {{
            background: var(--accent-lime);
            box-shadow: 0 0 10px rgba(163, 230, 53, 0.8);
        }}

        .preset-nome {{
            font-size: 0.86rem;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .preset-resumo {{
            font-family: var(--font-mono);
            font-size: 0.69rem;
            color: var(--text-secondary);
        }}

        .btn-preset-motor.ativo .preset-resumo {{
            color: #bae6fd;
        }}

        /* Widget 3: Todas as Configurações */
        .widget-configs {{
            justify-content: flex-start;
            gap: 14px;
        }}

        /* Painel Inferior: Ficha Técnica a ocupar toda a largura inferior */
        .ficha-painel-inferior {{
            width: 100%;
            max-width: 1240px;
            margin-top: 20px;
            background: var(--bg-elevated);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-xl);
            padding: 20px 24px;
            box-shadow: var(--shadow-card);
        }}

        .ficha-tecnica-inferior {{
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}

        .ficha-tecnica-inferior .ficha-titulo {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .ficha-tecnica-inferior .ficha-titulo::before {{
            content: '';
            width: 8px;
            height: 8px;
            border-radius: 99px;
            background: var(--accent-cyan);
            box-shadow: 0 0 10px var(--accent-cyan);
        }}

        .ficha-itens-grid {{
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 12px;
        }}

        .ficha-item {{
            background: rgba(7, 10, 18, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: var(--radius-lg);
            padding: 13px 15px;
            display: flex;
            flex-direction: column;
            gap: 5px;
            transition: border-color 0.18s ease, transform 0.18s ease;
        }}

        .ficha-item:hover {{
            border-color: rgba(34, 211, 238, 0.35);
            transform: translateY(-1px);
        }}

        .ficha-item span {{
            font-size: 0.67rem;
            font-weight: 600;
            color: var(--text-secondary);
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }}

        .ficha-item strong {{
            font-family: var(--font-mono);
            font-size: 1rem;
            font-weight: 700;
            color: var(--text-primary);
            font-variant-numeric: tabular-nums;
        }}

        .ficha-item:nth-child(4) strong {{
            color: var(--accent-cyan);
        }}

        .ficha-item:nth-child(5) strong {{
            color: var(--accent-lime);
        }}

        /* Modal do Quiz (5 Perguntas Aleatórias) */
        .quiz-modal {{
            position: fixed;
            inset: 0;
            background-color: rgba(4, 6, 12, 0.82);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            display: none;
            align-items: center;
            justify-content: center;
            padding: 20px;
            z-index: 1000;
        }}

        .quiz-modal.ativo {{
            display: flex;
        }}

        .quiz-container {{
            background: #0c1220;
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 22px;
            width: 100%;
            max-width: 860px;
            max-height: 90vh;
            overflow-y: auto;
            padding: 26px;
            display: flex;
            flex-direction: column;
            gap: 18px;
            box-shadow: 0 32px 70px -15px rgba(0, 0, 0, 0.9);
            animation: modalEntrar 0.22s ease-out;
        }}

        @keyframes modalEntrar {{
            from {{
                opacity: 0;
                transform: translateY(10px) scale(0.985);
            }}
            to {{
                opacity: 1;
                transform: translateY(0) scale(1);
            }}
        }}

        .quiz-container::-webkit-scrollbar {{
            width: 8px;
        }}

        .quiz-container::-webkit-scrollbar-track {{
            background: rgba(15, 23, 42, 0.5);
            border-radius: 99px;
        }}

        .quiz-container::-webkit-scrollbar-thumb {{
            background: rgba(148, 163, 184, 0.3);
            border-radius: 99px;
        }}

        .quiz-header {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 14px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .quiz-header-info {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            flex: 1;
            min-width: 240px;
        }}

        .quiz-header h2 {{
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: var(--text-primary);
        }}

        .quiz-progresso-wrap {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .quiz-progresso {{
            font-family: var(--font-mono);
            font-size: 0.74rem;
            color: var(--text-secondary);
            white-space: nowrap;
        }}

        .quiz-progresso-barra {{
            flex: 1;
            max-width: 200px;
            height: 6px;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.16);
            overflow: hidden;
        }}

        .quiz-progresso-fill {{
            width: 0%;
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-lime));
            transition: width 0.25s ease;
        }}

        .quiz-resultado-banner {{
            border: 1px solid var(--border-cyan);
            border-radius: var(--radius-lg);
            background-color: rgba(15, 23, 42, 0.85);
            padding: 14px 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            font-size: 0.92rem;
            font-weight: 700;
        }}

        .quiz-lista {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .quiz-pergunta-box {{
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            background: rgba(7, 10, 18, 0.65);
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .quiz-pergunta-texto {{
            font-size: 0.92rem;
            line-height: 1.5;
            color: var(--text-primary);
            font-weight: 600;
        }}

        .quiz-opcoes-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
        }}

        .quiz-opcao {{
            display: flex;
            align-items: center;
            gap: 10px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            background: rgba(15, 23, 42, 0.65);
            color: var(--text-primary);
            padding: 10px 12px;
            font-size: 0.82rem;
            line-height: 1.35;
            cursor: pointer;
            transition: background-color 0.16s ease, border-color 0.16s ease, transform 0.16s ease;
        }}

        .quiz-opcao input[type="radio"] {{
            display: none;
        }}

        .quiz-letra {{
            width: 24px;
            height: 24px;
            border-radius: 8px;
            background: rgba(148, 163, 184, 0.14);
            color: var(--text-secondary);
            font-family: var(--font-mono);
            font-size: 0.74rem;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            transition: background-color 0.16s ease, color 0.16s ease;
        }}

        .quiz-opcao:hover {{
            border-color: rgba(34, 211, 238, 0.5);
            background: rgba(30, 41, 59, 0.85);
            transform: translateY(-1px);
        }}

        .quiz-opcao.selecionada {{
            background: rgba(34, 211, 238, 0.16);
            border-color: var(--accent-cyan);
            color: var(--text-primary);
            font-weight: 600;
        }}

        .quiz-opcao.selecionada .quiz-letra {{
            background: var(--accent-cyan);
            color: #060911;
        }}

        .quiz-opcao.correta {{
            border-color: var(--accent-emerald);
            color: var(--accent-emerald);
            background: rgba(52, 211, 153, 0.14);
            font-weight: 600;
        }}

        .quiz-opcao.correta .quiz-letra {{
            background: var(--accent-emerald);
            color: #060911;
        }}

        .quiz-opcao.errada {{
            border-color: var(--accent-danger);
            color: #ff99ab;
            background: rgba(255, 59, 92, 0.14);
            font-weight: 600;
        }}

        .quiz-opcao.errada .quiz-letra {{
            background: var(--accent-danger);
            color: #ffffff;
        }}

        .quiz-feedback {{
            font-size: 0.78rem;
            font-weight: 500;
            min-height: 1em;
        }}

        .quiz-feedback.ok {{
            color: var(--accent-emerald);
        }}

        .quiz-feedback.erro {{
            color: #ff99ab;
        }}

        .quiz-acoes-footer {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            padding-top: 6px;
        }}

        @media (max-width: 1080px) {{
            .dashboard-container {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
            .widget-visual {{
                grid-column: 1 / -1;
                min-height: 320px;
            }}
            .ficha-itens-grid {{
                grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
            }}
        }}

        @media (max-width: 680px) {{
            body {{
                padding: 16px 14px;
            }}
            .dashboard-container {{
                grid-template-columns: 1fr;
            }}
            .widget-card {{
                min-height: auto;
                padding: 18px;
            }}
            .quiz-container {{
                padding: 18px;
            }}
            .quiz-opcoes-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <header class="dashboard-topbar">
        <div class="topbar-brand">
            <div class="topbar-icon" aria-hidden="true">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2v4M5 6l2.5 2.5M19 6l-2.5 2.5M4 14h3M17 14h3M6 19h12a2 2 0 0 0 2-2v-3a8 8 0 1 0-16 0v3a2 2 0 0 0 2 2Z" />
                    <path d="M12 14l3-3" />
                </svg>
            </div>
            <div class="topbar-textos">
                <span class="topbar-titulo">PAINEL DO MOTOR</span>
                <span class="topbar-subtitulo">CONTROLO AUTOMÓVEL · CUSTOM ENGINE</span>
            </div>
        </div>
        <button type="button" class="btn-cyber-acao btn-quiz-cta" id="btn-abrir-quiz">
            <span>QUIZ AUTOMÓVEL</span>
            <span>({QUIZ_NUM_PERGUNTAS} PERGUNTAS)</span>
        </button>
    </header>

    <main class="dashboard-container">
        {w1}
        {w2}
        {w3}
    </main>

    <!-- Ficha Técnica ocupando toda a largura inferior do ecrã -->
    <section class="ficha-painel-inferior" id="combustao-output">
        {ficha_inicial}
    </section>

    {quiz_html}

    <script>
        if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {{
            const basePath = window.location.pathname.replace(/\\/index\\.html$/, '').replace(/\\/+$/, '');
            if (!basePath.endsWith('/custom-engine')) {{
                const novoPath = `${{basePath}}/custom-engine`;
                try {{
                    window.history.replaceState(null, '', novoPath + window.location.search + window.location.hash);
                }} catch (_) {{}}
            }}
        }}

        const PRESETS_DATA = {presets_json};
        const presetButtons = document.querySelectorAll('.btn-preset-motor');
        const selectFormato = document.getElementById('select-formato');
        const selectCilindros = document.getElementById('select-cilindros');
        const selectAdmissao = document.getElementById('select-admissao');
        const motorSvgContainer = document.getElementById('motor-svg-container');
        const motorNumCilindros = document.getElementById('motor-num-cilindros');

        const inputBore = document.getElementById('input-bore');
        const inputStroke = document.getElementById('input-stroke');
        const inputCr = document.getElementById('input-cr');
        const inputRpm = document.getElementById('input-rpm');
        const selectCombustivel = document.getElementById('select-combustivel');
        const selectCiclo = document.getElementById('select-ciclo');
        const combustaoOutput = document.getElementById('combustao-output');
        const rpmAlertaMsg = document.getElementById('rpm-alerta-msg');

        function limparPresetAtivo() {{
            presetButtons.forEach(b => b.classList.remove('ativo'));
        }}

        function aplicarAlertaRpm(alerta, motivos) {{
            if (alerta) {{
                inputRpm.classList.add('input-alerta');
                if (rpmAlertaMsg) rpmAlertaMsg.textContent = (motivos || []).join(' | ');
            }} else {{
                inputRpm.classList.remove('input-alerta');
                if (rpmAlertaMsg) rpmAlertaMsg.textContent = '';
            }}
        }}

        function desenharCilindroSvg(cx, cy, r) {{
            const rPistao = Math.max(2.8, r * 0.48);
            const rPino = Math.max(1.4, r * 0.16);
            return `
                <circle cx="${{cx.toFixed(1)}}" cy="${{cy.toFixed(1)}}" r="${{r.toFixed(1)}}" fill="rgba(34, 211, 238, 0.08)" stroke="#22D3EE" stroke-width="2" />
                <circle cx="${{cx.toFixed(1)}}" cy="${{cy.toFixed(1)}}" r="${{rPistao.toFixed(1)}}" fill="rgba(129, 140, 248, 0.18)" stroke="#F8FAFC" stroke-width="1.7" />
                <circle cx="${{cx.toFixed(1)}}" cy="${{cy.toFixed(1)}}" r="${{rPino.toFixed(1)}}" fill="#22D3EE" />
            `;
        }}

        function gerarSvgMotorLocal(cilindros, formato) {{
            const n = Math.max(1, Math.min(16, cilindros));
            const fmt = ['I', 'V', 'VR', 'W'].includes(formato) ? formato : 'I';
            let corpo = '';
            const guiaCad = '<path d="M 14,24 L 14,12 L 26,12 M 346,24 L 346,12 L 334,12 M 14,166 L 14,178 L 26,178 M 346,166 L 346,178 L 334,178" fill="none" stroke="rgba(34, 211, 238, 0.28)" stroke-width="1.2" stroke-linecap="round" />';

            if (fmt === 'I') {{
                const espaco = 260.0 / n;
                const raio = Math.min(22.0, Math.max(5.2, (espaco - 5.0) / 2.0));
                let circs = '';
                for (let i = 0; i < n; i++) {{
                    circs += desenharCilindroSvg(50.0 + i * espaco + espaco / 2.0, 95.0, raio);
                }}
                corpo = `
                    <rect x="60" y="20" width="240" height="25" rx="6" fill="rgba(15, 23, 42, 0.72)" stroke="#CBD5E1" stroke-width="1.8" />
                    <rect x="40" y="45" width="280" height="100" rx="12" fill="rgba(15, 23, 42, 0.85)" stroke="#E2E8F0" stroke-width="2" />
                    ${{circs}}
                    <path d="M 70,145 L 290,145 L 270,172 L 90,172 Z" fill="rgba(15, 23, 42, 0.65)" stroke="#94A3B8" stroke-width="1.8" stroke-linejoin="round" />
                `;
            }} else if (fmt === 'V') {{
                const nSup = Math.floor((n + 1) / 2);
                const nInf = Math.floor(n / 2);
                const cols = Math.max(1, nSup, nInf);
                const espaco = 240.0 / cols;
                const raio = Math.min(17.0, Math.max(6.0, (espaco - 6.0) / 2.0));
                let circs = '';
                for (let i = 0; i < nSup; i++) circs += desenharCilindroSvg(60.0 + i * espaco + espaco / 2.0, 57.0, raio);
                for (let i = 0; i < nInf; i++) circs += desenharCilindroSvg(60.0 + i * espaco + espaco / 2.0, 133.0, raio);
                corpo = `
                    <rect x="50" y="28" width="260" height="58" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#E2E8F0" stroke-width="2" />
                    <rect x="50" y="104" width="260" height="58" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#E2E8F0" stroke-width="2" />
                    <rect x="28" y="76" width="16" height="38" rx="4" fill="rgba(129, 140, 248, 0.22)" stroke="#818CF8" stroke-width="1.8" />
                    <line x1="44" y1="95" x2="322" y2="95" stroke="#818CF8" stroke-width="2" stroke-dasharray="6,4" />
                    ${{circs}}
                `;
            }} else if (fmt === 'VR') {{
                const espaco = 244.0 / n;
                let raio = Math.min(17.0, Math.max(7.5, (espaco * 1.15 - 4.0) / 2.0));
                if (n >= 10) raio = Math.min(raio, 10.5);
                let circs = '';
                for (let i = 0; i < n; i++) {{
                    const cx = 58.0 + i * espaco + espaco / 2.0;
                    const cy = i % 2 === 0 ? 80.0 : 110.0;
                    circs += desenharCilindroSvg(cx, cy, raio);
                }}
                corpo = `
                    <rect x="65" y="22" width="230" height="20" rx="6" fill="rgba(15, 23, 42, 0.72)" stroke="#CBD5E1" stroke-width="1.8" />
                    <rect x="44" y="42" width="272" height="106" rx="12" fill="rgba(15, 23, 42, 0.85)" stroke="#E2E8F0" stroke-width="2" />
                    ${{circs}}
                    <path d="M 75,148 L 285,148 L 268,172 L 92,172 Z" fill="rgba(15, 23, 42, 0.65)" stroke="#94A3B8" stroke-width="1.8" stroke-linejoin="round" />
                `;
            }} else {{
                const nSup = Math.floor((n + 1) / 2);
                const nInf = Math.floor(n / 2);
                const cols = Math.max(1, nSup, nInf);
                const espacoSup = 244.0 / Math.max(1, nSup);
                const espacoInf = 244.0 / Math.max(1, nInf);
                const raio = Math.min(12.0, Math.max(7.0, (244.0 / cols) * 0.35));
                let circs = '';
                for (let i = 0; i < nSup; i++) circs += desenharCilindroSvg(58.0 + i * espacoSup + espacoSup / 2.0, i % 2 === 0 ? 43.0 : 63.0, raio);
                for (let i = 0; i < nInf; i++) circs += desenharCilindroSvg(58.0 + i * espacoInf + espacoInf / 2.0, i % 2 === 0 ? 127.0 : 147.0, raio);
                corpo = `
                    <rect x="44" y="20" width="272" height="66" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#E2E8F0" stroke-width="2" />
                    <rect x="44" y="104" width="272" height="66" rx="10" fill="rgba(15, 23, 42, 0.85)" stroke="#E2E8F0" stroke-width="2" />
                    <rect x="24" y="78" width="14" height="34" rx="4" fill="rgba(129, 140, 248, 0.22)" stroke="#818CF8" stroke-width="1.8" />
                    <line x1="38" y1="95" x2="326" y2="95" stroke="#818CF8" stroke-width="2" stroke-dasharray="6,4" />
                    ${{circs}}
                `;
            }}
            return `<svg class="motor-svg" viewBox="0 0 360 190" xmlns="http://www.w3.org/2000/svg" aria-label="Motor ${{fmt}} 2D">${{guiaCad}}${{corpo}}</svg>`;
        }}

        async function atualizarWidget3() {{
            const payload = {{
                bore: parseFloat(inputBore.value) || 86.0,
                stroke: parseFloat(inputStroke.value) || 86.0,
                compression_ratio: parseFloat(inputCr.value) || 10.5,
                max_rpm: parseInt(inputRpm.value, 10) || 7500,
                combustivel: selectCombustivel.value || 'Gasolina',
                ciclo: selectCiclo.value || '4T',
                cilindros: parseInt(selectCilindros.value, 10) || 4,
                admissao: selectAdmissao.value || 'Atmosférico',
                formato: selectFormato.value || 'I'
            }};

            try {{
                const res = await fetch('/api/combustao', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }});
                if (res.ok) {{
                    const data = await res.json();
                    combustaoOutput.innerHTML = data.combustao_html;
                    aplicarAlertaRpm(data.alerta_rpm, data.motivos_alerta);
                    return;
                }}
            }} catch (_) {{}}

            // Fallback local idêntico ao cálculo Python para abertura direta do index.html
            const fatoresComb = {{
                'Gasolina': 1.00,
                'Etanol (E85)': 1.08,
                'Metanol': 1.12
            }};
            const perfisAdm = {{
                'Atmosférico': {{ pressao: '0.0 bar (Atmosférico)', mp: 1.00, mb: 1.00 }},
                'Turbo': {{ pressao: '+1.5 bar', mp: 1.55, mb: 1.60 }},
                'Supercompressor': {{ pressao: '+0.8 bar', mp: 1.35, mb: 1.45 }},
                'Biturbo': {{ pressao: '+2.0 bar', mp: 1.80, mb: 1.85 }},
                'Bicarregado': {{ pressao: '+2.0 bar', mp: 1.90, mb: 1.95 }}
            }};
            const fatorComb = fatoresComb[payload.combustivel] || 1.00;
            const admKey = perfisAdm[payload.admissao] ? payload.admissao : 'Atmosférico';
            const fmtKey = ['I', 'V', 'VR', 'W'].includes(payload.formato) ? payload.formato : 'I';
            const pAdm = perfisAdm[admKey];

            const unitCc = (Math.PI / 4.0) * Math.pow(payload.bore / 10.0, 2) * (payload.stroke / 10.0);
            const litros = (unitCc * payload.cilindros) / 1000.0;

            const fatorCr = 1.0 + Math.max(-0.25, Math.min(0.35, (payload.compression_ratio - 10.0) * 0.025));
            const fatorCicloTq = payload.ciclo === '2T' ? 1.25 : 1.00;
            const torqueNm = Math.round(litros * 105.0 * fatorCr * fatorComb * fatorCicloTq * pAdm.mb);
            const fatorRpmHp = payload.ciclo === '4T' ? 0.88 : 0.94;
            const potenciaCv = Math.round(((torqueNm * payload.max_rpm * fatorRpmHp) / 7121.0) * (pAdm.mp / pAdm.mb) * 1.01387);

            const velMediaPistao = (2.0 * (payload.stroke / 1000.0) * payload.max_rpm) / 60.0;
            const motivosAlerta = [];
            if (velMediaPistao > 25.0) {{
                motivosAlerta.push(`Vel. média do pistão elevada (${{velMediaPistao.toFixed(1)}} m/s > 25.0 m/s)`);
            }}
            if (payload.compression_ratio > 15.0) {{
                motivosAlerta.push('Taxa de compressão > 15:1');
            }}
            aplicarAlertaRpm(motivosAlerta.length > 0, motivosAlerta);

            combustaoOutput.innerHTML = `
                <div class="ficha-tecnica-inferior">
                    <div class="ficha-titulo">FICHA TÉCNICA</div>
                    <div class="ficha-itens-grid">
                        <div class="ficha-item"><span>TIPO DE MOTOR</span><strong>${{fmtKey}}${{payload.cilindros}} · ${{admKey}} (${{payload.ciclo}})</strong></div>
                        <div class="ficha-item"><span>CILINDRADA</span><strong>${{litros.toFixed(2)}} L</strong></div>
                        <div class="ficha-item"><span>PRESSÃO</span><strong>${{pAdm.pressao}}</strong></div>
                        <div class="ficha-item"><span>BINÁRIO EST.</span><strong>${{torqueNm}} Nm</strong></div>
                        <div class="ficha-item"><span>POTÊNCIA EST.</span><strong>${{potenciaCv}} cv</strong></div>
                    </div>
                </div>
            `;
        }}

        async function atualizarDados() {{
            const cilindros = parseInt(selectCilindros.value, 10) || 4;
            const formato = selectFormato.value || 'I';

            try {{
                const res = await fetch('/api/ficha', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ cilindros, formato }})
                }});
                if (res.ok) {{
                    const data = await res.json();
                    motorSvgContainer.innerHTML = data.motor_svg;
                    motorNumCilindros.textContent = data.cilindros;
                    atualizarWidget3();
                    return;
                }}
            }} catch (_) {{}}

            motorSvgContainer.innerHTML = gerarSvgMotorLocal(cilindros, formato);
            motorNumCilindros.textContent = cilindros;
            atualizarWidget3();
        }}

        presetButtons.forEach(btn => {{
            btn.addEventListener('click', () => {{
                const preset = PRESETS_DATA.find(p => p.id === btn.dataset.presetId);
                if (!preset) return;

                presetButtons.forEach(b => b.classList.remove('ativo'));
                btn.classList.add('ativo');

                selectFormato.value = preset.formato;
                selectCilindros.value = String(preset.cilindros);
                selectAdmissao.value = preset.admissao;
                inputBore.value = preset.bore;
                inputStroke.value = preset.stroke;
                inputCr.value = preset.compression_ratio;
                inputRpm.value = preset.max_rpm;
                selectCombustivel.value = preset.combustivel;
                selectCiclo.value = preset.ciclo;

                atualizarDados();
            }});
        }});

        [selectFormato, selectCilindros, selectAdmissao].forEach(el => {{
            el.addEventListener('change', () => {{
                limparPresetAtivo();
                atualizarDados();
            }});
        }});

        [inputBore, inputStroke, inputCr, inputRpm, selectCombustivel, selectCiclo].forEach(el => {{
            el.addEventListener('input', () => {{
                limparPresetAtivo();
                atualizarWidget3();
            }});
            el.addEventListener('change', () => {{
                limparPresetAtivo();
                atualizarWidget3();
            }});
        }});

        /* ----------------------------------------------------------------------
           MÓDULO QUIZ AUTOMÓVEL ({QUIZ_NUM_PERGUNTAS} Perguntas Aleatórias)
           ---------------------------------------------------------------------- */
        const QUIZ_DATA = {quiz_json};
        const QUIZ_TOTAL_PERGUNTAS = {QUIZ_NUM_PERGUNTAS};
        const QUIZ_LETRAS = ['A', 'B', 'C', 'D'];
        let quizAtual = [];

        const quizModal = document.getElementById('quiz-modal');
        const btnAbrirQuiz = document.getElementById('btn-abrir-quiz');
        const btnFecharQuiz = document.getElementById('btn-fechar-quiz');
        const btnReiniciarQuiz = document.getElementById('btn-reiniciar-quiz');
        const quizForm = document.getElementById('quiz-form');
        const quizPerguntasContainer = document.getElementById('quiz-perguntas-container');
        const quizProgresso = document.getElementById('quiz-progresso');
        const quizProgressoFill = document.getElementById('quiz-progresso-fill');
        const quizBanner = document.getElementById('quiz-resultado-banner');
        const quizContainer = quizModal ? quizModal.querySelector('.quiz-container') : null;

        function escaparHtmlQuiz(texto) {{
            return String(texto)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }}

        function sortearPerguntasQuiz() {{
            const copia = [...QUIZ_DATA];
            for (let i = copia.length - 1; i > 0; i--) {{
                const j = Math.floor(Math.random() * (i + 1));
                [copia[i], copia[j]] = [copia[j], copia[i]];
            }}
            return copia.slice(0, Math.min(QUIZ_TOTAL_PERGUNTAS, copia.length));
        }}

        function renderizarQuizAleatorio() {{
            if (!quizPerguntasContainer) return;
            quizAtual = sortearPerguntasQuiz();
            quizPerguntasContainer.innerHTML = quizAtual.map((q, numeroIdx) => {{
                const opcoesHtml = q.opcoes.map((texto, idx) => `
                    <label class="quiz-opcao" data-qid="${{q.id}}" data-idx="${{idx}}">
                        <input type="radio" name="q_${{q.id}}" value="${{idx}}">
                        <span class="quiz-letra">${{QUIZ_LETRAS[idx]}}</span>
                        <span class="quiz-texto">${{escaparHtmlQuiz(texto)}}</span>
                    </label>
                `).join('');

                return `
                    <div class="quiz-pergunta-box" id="quiz-q-${{q.id}}">
                        <p class="quiz-pergunta-texto">${{numeroIdx + 1}}. ${{escaparHtmlQuiz(q.pergunta)}}</p>
                        <div class="quiz-opcoes-grid">
                            ${{opcoesHtml}}
                        </div>
                        <div class="quiz-feedback" id="quiz-fb-${{q.id}}"></div>
                    </div>
                `;
            }}).join('');
            atualizarProgressoQuiz();
        }}

        function abrirQuiz() {{
            quizModal.classList.add('ativo');
            quizModal.setAttribute('aria-hidden', 'false');
        }}

        function fecharQuiz() {{
            quizModal.classList.remove('ativo');
            quizModal.setAttribute('aria-hidden', 'true');
        }}

        function atualizarProgressoQuiz() {{
            let respondidas = 0;
            quizAtual.forEach(q => {{
                if (quizForm.querySelector(`input[name="q_${{q.id}}"]:checked`)) {{
                    respondidas += 1;
                }}
            }});
            quizProgresso.textContent = `Respondidas: ${{respondidas}} / ${{quizAtual.length}}`;
            if (quizProgressoFill) {{
                const pct = quizAtual.length ? (respondidas / quizAtual.length) * 100 : 0;
                quizProgressoFill.style.width = `${{pct}}%`;
            }}
        }}

        function obterClassificacaoQuiz(percentagem) {{
            if (percentagem >= 70) return 'Verdadeiro purista!';
            if (percentagem >= 50) return 'Purista emergente';
            return 'Condutor diário';
        }}

        function aplicarResultadoQuiz(resultado) {{
            let corBanner = '#FF3B5C';
            let fundoBanner = 'rgba(255, 59, 92, 0.14)';
            if (resultado.percentagem >= 70) {{
                corBanner = '#34D399';
                fundoBanner = 'rgba(52, 211, 153, 0.14)';
            }} else if (resultado.percentagem >= 50) {{
                corBanner = '#FBBF24';
                fundoBanner = 'rgba(251, 191, 36, 0.14)';
            }}
            const classificacao = resultado.classificacao || obterClassificacaoQuiz(resultado.percentagem);

            quizBanner.style.display = 'flex';
            quizBanner.style.borderColor = corBanner;
            quizBanner.style.backgroundColor = fundoBanner;
            quizBanner.innerHTML = `
                <span>RESULTADO FINAL: <strong style="color:${{corBanner}}">${{resultado.pontuacao}} / ${{resultado.total}} (${{resultado.percentagem}}%)</strong></span>
                <span style="color:${{corBanner}}; letter-spacing: 0.06em;">CLASSIFICAÇÃO: ${{classificacao}}</span>
            `;

            resultado.detalhes.forEach(item => {{
                const opcoes = quizForm.querySelectorAll(`.quiz-opcao[data-qid="${{item.id}}"]`);
                const fb = document.getElementById(`quiz-fb-${{item.id}}`);

                opcoes.forEach(op => {{
                    op.classList.remove('selecionada', 'correta', 'errada');
                    const idx = parseInt(op.dataset.idx, 10);
                    if (idx === item.correta) {{
                        op.classList.add('correta');
                    }} else if (idx === item.escolha && !item.acertou) {{
                        op.classList.add('errada');
                    }}
                }});

                if (item.acertou) {{
                    fb.className = 'quiz-feedback ok';
                    fb.textContent = '✓ Resposta certa!';
                }} else if (!item.respondida) {{
                    fb.className = 'quiz-feedback erro';
                    fb.textContent = `Sem resposta · Correta: ${{item.texto_correto}}`;
                }} else {{
                    fb.className = 'quiz-feedback erro';
                    fb.textContent = `✗ Incorreta · Resposta correta: ${{item.texto_correto}}`;
                }}
            }});

            if (quizContainer) quizContainer.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        async function submeterQuiz() {{
            const respostas = {{}};
            const ids = quizAtual.map(q => q.id);
            quizAtual.forEach(q => {{
                const checked = quizForm.querySelector(`input[name="q_${{q.id}}"]:checked`);
                if (checked) {{
                    respostas[String(q.id)] = parseInt(checked.value, 10);
                }}
            }});

            try {{
                const res = await fetch('/api/quiz', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ respostas, ids }})
                }});
                if (res.ok) {{
                    const resultado = await res.json();
                    aplicarResultadoQuiz(resultado);
                    return;
                }}
            }} catch (_) {{}}

            // Fallback local idêntico à função avaliar_quiz() do Python
            let pontuacao = 0;
            const detalhes = quizAtual.map(q => {{
                const raw = respostas[String(q.id)];
                const escolha = raw !== undefined ? raw : -1;
                const acertou = escolha === q.correta;
                if (acertou) pontuacao += 1;
                return {{
                    id: q.id,
                    acertou,
                    respondida: escolha >= 0,
                    escolha,
                    correta: q.correta,
                    texto_correto: q.opcoes[q.correta]
                }};
            }});
            const percentagem = quizAtual.length ? Math.round((pontuacao / quizAtual.length) * 100) : 0;
            aplicarResultadoQuiz({{
                pontuacao,
                total: quizAtual.length,
                percentagem,
                classificacao: obterClassificacaoQuiz(percentagem),
                detalhes
            }});
        }}

        function reiniciarQuiz() {{
            quizBanner.style.display = 'none';
            quizBanner.style.borderColor = '';
            quizBanner.style.backgroundColor = '';
            quizBanner.innerHTML = '';
            renderizarQuizAleatorio();
            if (quizContainer) quizContainer.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        if (btnAbrirQuiz && quizModal) {{
            renderizarQuizAleatorio();
            btnAbrirQuiz.addEventListener('click', abrirQuiz);
            btnFecharQuiz.addEventListener('click', fecharQuiz);
            btnReiniciarQuiz.addEventListener('click', reiniciarQuiz);
            quizForm.addEventListener('submit', submeterQuiz);

            quizModal.addEventListener('click', (e) => {{
                if (e.target === quizModal) fecharQuiz();
            }});

            document.addEventListener('keydown', (e) => {{
                if (e.key === 'Escape' && quizModal.classList.contains('ativo')) fecharQuiz();
            }});

            quizForm.addEventListener('change', (e) => {{
                const radio = e.target;
                if (!radio || radio.type !== 'radio') return;
                const qid = radio.name.replace('q_', '');
                quizForm.querySelectorAll(`.quiz-opcao[data-qid="${{qid}}"]`).forEach(op => {{
                    op.classList.remove('selecionada', 'correta', 'errada');
                }});
                const label = radio.closest('.quiz-opcao');
                if (label) label.classList.add('selecionada');
                atualizarProgressoQuiz();
            }});
        }}
    </script>
</body>
</html>
"""


def guardar_index_html(
    num_cilindros: int = 4,
    admissao: str = "Atmosférico",
    formato: str = "I",
) -> None:
    """
    Gera primeiro todo o HTML em memória e só depois grava o ficheiro index.html
    (evita que o index.html fique vazio/0 bytes caso ocorra algum erro).
    """
    conteudo_html = gerar_dashboard_html(num_cilindros, admissao, formato)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(conteudo_html)
    print("[OK] Ficheiro index.html gerado com sucesso.")


class DashboardHandler(SimpleHTTPRequestHandler):
    """Servidor HTTP que processa os pedidos dos Widgets 2, 3 e Quiz diretamente em Python."""

    def do_GET(self):
        caminho = self.path.split("?", 1)[0]
        if caminho in ("/", "/index.html"):
            self.send_response(302)
            self.send_header("Location", "/custom-engine")
            self.end_headers()
            return
        if caminho in ("/custom-engine", "/custom-engine/"):
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        caminho = self.path.split("?", 1)[0]
        if caminho.startswith("/custom-engine/"):
            caminho = caminho[len("/custom-engine"):]

        tamanho = int(self.headers.get("Content-Length", 0))
        corpo = self.rfile.read(tamanho).decode("utf-8") if tamanho > 0 else "{}"
        dados = json.loads(corpo)

        if caminho == "/api/ficha":
            cil = max(1, min(16, int(dados.get("cilindros", 4))))
            fmt = str(dados.get("formato", "I")).upper()

            resposta = json.dumps({
                "cilindros": cil,
                "formato": fmt,
                "motor_svg": gerar_svg_motor_inline(cil, fmt),
            }).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resposta)))
            self.end_headers()
            self.wfile.write(resposta)
            return

        if caminho == "/api/combustao":
            resultado = processar_combustao(
                bore=float(dados.get("bore", 86.0)),
                stroke=float(dados.get("stroke", 86.0)),
                compression_ratio=float(dados.get("compression_ratio", 10.5)),
                max_rpm=int(dados.get("max_rpm", 7500)),
                combustivel=str(dados.get("combustivel", "Gasolina")),
                ciclo=str(dados.get("ciclo", "4T")),
                num_cilindros=int(dados.get("cilindros", 4)),
                admissao=str(dados.get("admissao", "Atmosférico")),
                formato=str(dados.get("formato", "I")),
            )
            resposta = json.dumps({
                "combustao_html": render_resultado_combustao(resultado),
                "alerta_rpm": resultado["alerta_rpm"],
                "motivos_alerta": resultado["motivos_alerta"],
            }, ensure_ascii=False).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resposta)))
            self.end_headers()
            self.wfile.write(resposta)
            return

        if caminho == "/api/quiz":
            resultado = avaliar_quiz(dados.get("respostas", {}), dados.get("ids"))
            resposta = json.dumps(resultado, ensure_ascii=False).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resposta)))
            self.end_headers()
            self.wfile.write(resposta)
            return

        self.send_error(404)


def iniciar_servidor(porta: int = 8000) -> None:
    """Gera o index.html e inicia o servidor web local em Python."""
    guardar_index_html()
    url = f"http://localhost:{porta}/custom-engine"
    print(f"Servidor ativo em: {url} (Pressiona Ctrl+C para sair)")
    webbrowser.open(url)
    servidor = HTTPServer(("127.0.0.1", porta), DashboardHandler)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        servidor.server_close()


if __name__ == "__main__":
    if "--build-only" in sys.argv:
        guardar_index_html()
    else:
        iniciar_servidor(porta=8000)
