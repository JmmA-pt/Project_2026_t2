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
    Desenha o SVG 2D do motor com contorno de 2pt em WhiteSmoke
    de acordo com o formato escolhido (I, V, VR ou W), suportando até 16 cilindros.
    """
    num_cilindros = max(1, min(16, int(num_cilindros)))
    formato = str(formato).upper()
    if formato not in ("I", "V", "VR", "W"):
        formato = "I"

    def desenhar_cilindro(cx: float, cy: float, r: float) -> str:
        r_pistao = max(2.8, r * 0.45)
        return (
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="none" stroke="WhiteSmoke" stroke-width="2pt" />\n'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_pistao:.1f}" '
            f'fill="none" stroke="WhiteSmoke" stroke-width="2pt" />\n'
        )

    corpo_svg = ""

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
        <rect x="60" y="20" width="240" height="25" rx="4" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
        <rect x="40" y="45" width="280" height="100" rx="8" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
        {cilindros}
        <path d="M 70,145 L 290,145 L 270,172 L 90,172 Z" fill="none" stroke="WhiteSmoke" stroke-width="2pt" stroke-linejoin="round" />
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
        <rect x="50" y="28" width="260" height="58" rx="6" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
        <rect x="50" y="104" width="260" height="58" rx="6" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
        <rect x="28" y="76" width="16" height="38" rx="2" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
        <line x1="44" y1="95" x2="322" y2="95" stroke="WhiteSmoke" stroke-width="2pt" stroke-dasharray="6,4" />
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
        <rect x="65" y="22" width="230" height="20" rx="4" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
        <rect x="44" y="42" width="272" height="106" rx="8" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
        {cilindros}
        <path d="M 75,148 L 285,148 L 268,172 L 92,172 Z" fill="none" stroke="WhiteSmoke" stroke-width="2pt" stroke-linejoin="round" />
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
        <rect x="44" y="20" width="272" height="66" rx="6" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
        <rect x="44" y="104" width="272" height="66" rx="6" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
        <rect x="24" y="78" width="14" height="34" rx="2" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
        <line x1="38" y1="95" x2="326" y2="95" stroke="WhiteSmoke" stroke-width="2pt" stroke-dasharray="6,4" />
        {cilindros}
        """

    return f"""
    <svg class="motor-svg" viewBox="0 0 360 190" xmlns="http://www.w3.org/2000/svg"
         aria-label="Motor {formato} 2D">
        {corpo_svg}
    </svg>
    """


def widget_motor_inline(num_cilindros: int = 4, formato: str = "I") -> str:
    """
    Gera o Widget 1 com a figura 2D do motor (contorno 2pt WhiteSmoke)
    e exibe exclusivamente o número de cilindros.
    """
    return f"""
    <section class="widget-card" id="widget-1">
        <div id="motor-svg-container" style="width: 100%; display: flex; justify-content: center;">
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
        <div class="ficha-titulo" style="width: 100%; text-align: center;">MOTORES PREDEFINIDOS</div>
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
        <div class="ficha-titulo" style="width: 100%; text-align: center;">CONFIGURAÇÕES DO MOTOR</div>
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
# MÓDULO QUIZ AUTOMÓVEL (10 Perguntas de Escolha Múltipla)
# ==============================================================================
QUIZ_PERGUNTAS = [
    {
        "id": 1,
        "pergunta": "1. De que país é a marca Bugatti?",
        "opcoes": ["França", "Itália", "Alemanha", "EUA"],
        "correta": 0,
    },
    {
        "id": 2,
        "pergunta": "2. Qual destas marcas é sueca?",
        "opcoes": ["Pagani", "Koenigsegg", "Ferrari", "McLaren"],
        "correta": 1,
    },
    {
        "id": 3,
        "pergunta": "3. Qual destas marcas produz o hipercarro Chiron?",
        "opcoes": ["Bugatti", "Rimac", "Aston Martin", "Hennessey"],
        "correta": 0,
    },
    {
        "id": 4,
        "pergunta": "4. Qual destas marcas é britânica?",
        "opcoes": ["Corvette", "Volvo", "Lotus", "Cupra"],
        "correta": 2,
    },
    {
        "id": 5,
        "pergunta": "5. Qual destes carros bateu o recorde mundial de velocidade numa estrada pública ao atingir 447,19 km/h em 2017?",
        "opcoes": ["Rimac Nevera", "Mazda RX-7", "Pagani Huayra", "Koenigsegg Agera RS"],
        "correta": 3,
    },
    {
        "id": 6,
        "pergunta": "6. Qual destas marcas fabrica o Valkyrie?",
        "opcoes": ["Aston Martin", "Lamborghini", "Pagani", "Honda"],
        "correta": 0,
    },
    {
        "id": 7,
        "pergunta": "7. Qual destas marcas nasceu numa garagem em 2009 a partir da conversão elétrica de um BMW Série 3 (E30)?",
        "opcoes": ["Lada", "Lancia", "Lincoln", "Rimac"],
        "correta": 3,
    },
    {
        "id": 8,
        "pergunta": "8. Qual foi o primeiro automóvel de produção em série a combinar tração integral permanente e motor turbo?",
        "opcoes": [
            "Lancia Delta HF integrale",
            "Audi Quattro (Ur-Quattro)",
            "Subaru Impreza WRX STI",
            "Porsche 959",
        ],
        "correta": 1,
    },
    {
        "id": 9,
        "pergunta": '9. O que significa "twin-turbo" num motor?',
        "opcoes": [
            "Dois motores elétricos",
            "Dois turbocompressores",
            "Dois intercoolers",
            "Duas caixas de velocidades",
        ],
        "correta": 1,
    },
    {
        "id": 10,
        "pergunta": "10. Num motor 4 tempos, quantas vezes ocorre a combustão por cilindro a cada 2 rotações da cambota?",
        "opcoes": ["1 vez", "2 vezes", "4 vezes", "Depende do combustível"],
        "correta": 0,
    },
]


def avaliar_quiz(respostas: dict) -> dict:
    """
    Avalia em Python as respostas submetidas pelo utilizador para o quiz de 10 perguntas.
    `respostas` mapeia id da pergunta (str ou int) para índice da opção escolhida (int).
    """
    pontuacao = 0
    detalhes = []

    for q in QUIZ_PERGUNTAS:
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

    total = len(QUIZ_PERGUNTAS)
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
    Gera o HTML do modal/painel interativo do Quiz automóvel com 10 escolhas múltiplas.
    """
    blocos_perguntas = []
    letras = ["A", "B", "C", "D"]

    for q in QUIZ_PERGUNTAS:
        opcoes_html = ""
        for idx, texto in enumerate(q["opcoes"]):
            opcoes_html += f"""
            <label class="quiz-opcao" data-qid="{q['id']}" data-idx="{idx}">
                <input type="radio" name="q_{q['id']}" value="{idx}">
                <span class="quiz-letra">{letras[idx]})</span>
                <span class="quiz-texto">{texto}</span>
            </label>
            """

        blocos_perguntas.append(f"""
        <div class="quiz-pergunta-box" id="quiz-q-{q['id']}">
            <p class="quiz-pergunta-texto">{q['pergunta']}</p>
            <div class="quiz-opcoes-grid">
                {opcoes_html}
            </div>
            <div class="quiz-feedback" id="quiz-fb-{q['id']}"></div>
        </div>
        """)

    perguntas_html = "\n".join(blocos_perguntas)

    return f"""
    <div class="quiz-modal" id="quiz-modal" aria-hidden="true">
        <div class="quiz-container" role="dialog" aria-modal="true" aria-labelledby="quiz-titulo">
            <header class="quiz-header">
                <div>
                    <h2 id="quiz-titulo">QUIZ AUTOMÓVEL // 10 ESCOLHAS MÚLTIPLAS</h2>
                    <span class="quiz-progresso" id="quiz-progresso">Respondidas: 0 / {len(QUIZ_PERGUNTAS)}</span>
                </div>
                <button type="button" class="btn-cyber-acao" id="btn-fechar-quiz">VOLTAR AO PAINEL</button>
            </header>

            <div class="quiz-resultado-banner" id="quiz-resultado-banner" style="display: none;"></div>

            <form id="quiz-form" class="quiz-lista" onsubmit="return false;">
                {perguntas_html}

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
        [{"id": q["id"], "opcoes": q["opcoes"], "correta": q["correta"]} for q in QUIZ_PERGUNTAS],
        ensure_ascii=False,
    )
    presets_json = json.dumps(MOTORES_PREDEFINIDOS, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel de Motor</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        /* Base do site: Fundo Preto e texto WhiteSmoke */
        body {{
            background-color: #000000;
            color: WhiteSmoke;
            font-family: 'Consolas', 'Courier New', monospace;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }}

        /* Grelha simples para os 3 widgets */
        .dashboard-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(310px, 1fr));
            gap: 20px;
            width: 100%;
            max-width: 1200px;
        }}

        /* Cartão de cada widget com contorno de 2pt em WhiteSmoke */
        .widget-card {{
            background-color: #000000;
            border: 2pt solid WhiteSmoke;
            padding: 22px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            min-height: 360px;
            gap: 16px;
        }}

        .motor-svg {{
            width: 100%;
            max-width: 320px;
            height: auto;
        }}

        /* Exibição exclusiva do número de cilindros (Widget 1) */
        .cilindros-box {{
            border: 2pt solid WhiteSmoke;
            padding: 10px 28px;
            text-align: center;
        }}

        .cilindros-numero {{
            display: block;
            font-size: 2.6rem;
            font-weight: bold;
            color: WhiteSmoke;
            line-height: 1.1;
        }}

        .cilindros-texto {{
            font-size: 0.85rem;
            letter-spacing: 0.15em;
            color: WhiteSmoke;
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
            gap: 8px;
        }}

        .campo-grupo {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .campo-largura-total {{
            grid-column: 1 / -1;
        }}

        .campo-grupo label {{
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            color: WhiteSmoke;
        }}

        .input-cyber {{
            background-color: #000000;
            color: WhiteSmoke;
            border: 1.5pt solid WhiteSmoke;
            padding: 7px 8px;
            font-family: inherit;
            font-size: 0.85rem;
            outline: none;
            width: 100%;
            transition: border-color 0.15s ease, background-color 0.15s ease, color 0.15s ease;
        }}

        .input-cyber.input-alerta {{
            border-color: #FF2A4B;
            background-color: rgba(255, 42, 75, 0.22);
            color: #FF5C77;
            font-weight: bold;
        }}

        .rpm-alerta-msg {{
            color: #FF2A4B;
            font-size: 0.72rem;
            min-height: 1em;
            line-height: 1.3;
        }}

        .ficha-tecnica {{
            width: 100%;
            border: 1.5pt solid WhiteSmoke;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 7px;
        }}

        .ficha-titulo {{
            font-size: 0.82rem;
            font-weight: bold;
            letter-spacing: 0.12em;
            border-bottom: 1pt solid WhiteSmoke;
            padding-bottom: 5px;
            margin-bottom: 2px;
        }}

        /* Widget 2: Motores Predefinidos */
        .widget-presets {{
            justify-content: flex-start;
            gap: 12px;
        }}

        .presets-lista {{
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .btn-preset-motor {{
            background-color: #000000;
            color: WhiteSmoke;
            border: 1.5pt solid rgba(245, 245, 245, 0.55);
            padding: 9px 11px;
            text-align: left;
            font-family: inherit;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            gap: 3px;
            transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
        }}

        .btn-preset-motor:hover {{
            border-color: WhiteSmoke;
            background-color: #141414;
        }}

        .btn-preset-motor.ativo {{
            background-color: WhiteSmoke;
            color: #000000;
            border-color: WhiteSmoke;
        }}

        .preset-nome {{
            font-size: 0.82rem;
            font-weight: bold;
        }}

        .preset-resumo {{
            font-size: 0.7rem;
            opacity: 0.8;
        }}

        /* Widget 3: Todas as Configurações */
        .widget-configs {{
            justify-content: flex-start;
            gap: 12px;
        }}

        /* Painel Inferior: Ficha Técnica a ocupar toda a largura inferior */
        .ficha-painel-inferior {{
            width: 100%;
            max-width: 1200px;
            margin-top: 20px;
            background-color: #000000;
            border: 2pt solid WhiteSmoke;
            padding: 18px 22px;
        }}

        .ficha-tecnica-inferior {{
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .ficha-itens-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 12px;
        }}

        .ficha-item {{
            border: 1pt solid rgba(245, 245, 245, 0.4);
            padding: 10px 12px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .ficha-item span {{
            font-size: 0.7rem;
            color: #b5b5b5;
            letter-spacing: 0.08em;
        }}

        .ficha-item strong {{
            font-size: 0.95rem;
            color: WhiteSmoke;
        }}

        /* Barra Superior & Botão de Acesso ao Quiz */
        .dashboard-topbar {{
            width: 100%;
            max-width: 1200px;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin-bottom: 18px;
            padding-bottom: 12px;
            border-bottom: 2pt solid WhiteSmoke;
        }}

        .topbar-titulo {{
            font-size: 1rem;
            font-weight: bold;
            letter-spacing: 0.12em;
            color: WhiteSmoke;
        }}

        .btn-cyber-acao {{
            background-color: #000000;
            color: WhiteSmoke;
            border: 2pt solid WhiteSmoke;
            padding: 9px 16px;
            font-family: inherit;
            font-size: 0.82rem;
            font-weight: bold;
            letter-spacing: 0.08em;
            cursor: pointer;
            transition: background-color 0.15s ease, color 0.15s ease;
        }}

        .btn-cyber-acao:hover,
        .btn-destaque {{
            background-color: WhiteSmoke;
            color: #000000;
        }}

        .btn-destaque:hover {{
            background-color: #d9d9d9;
        }}

        /* Modal do Quiz (10 Escolhas Múltiplas) */
        .quiz-modal {{
            position: fixed;
            inset: 0;
            background-color: rgba(0, 0, 0, 0.92);
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
            background-color: #000000;
            border: 2pt solid WhiteSmoke;
            width: 100%;
            max-width: 840px;
            max-height: 90vh;
            overflow-y: auto;
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 18px;
        }}

        .quiz-header {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            padding-bottom: 12px;
            border-bottom: 1.5pt solid WhiteSmoke;
        }}

        .quiz-header h2 {{
            font-size: 1.05rem;
            letter-spacing: 0.1em;
            color: WhiteSmoke;
        }}

        .quiz-progresso {{
            display: inline-block;
            margin-top: 4px;
            font-size: 0.78rem;
            color: #b5b5b5;
        }}

        .quiz-resultado-banner {{
            border: 2pt solid WhiteSmoke;
            background-color: #0a0a0a;
            padding: 14px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            font-size: 0.95rem;
            font-weight: bold;
        }}

        .quiz-lista {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .quiz-pergunta-box {{
            border: 1.5pt solid rgba(245, 245, 245, 0.45);
            background-color: #050505;
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .quiz-pergunta-texto {{
            font-size: 0.88rem;
            line-height: 1.45;
            color: WhiteSmoke;
            font-weight: bold;
        }}

        .quiz-opcoes-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 8px;
        }}

        .quiz-opcao {{
            display: flex;
            align-items: center;
            gap: 8px;
            border: 1pt solid rgba(245, 245, 245, 0.45);
            background-color: #000000;
            color: WhiteSmoke;
            padding: 9px 11px;
            font-size: 0.82rem;
            cursor: pointer;
            transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
        }}

        .quiz-opcao input[type="radio"] {{
            display: none;
        }}

        .quiz-opcao:hover {{
            border-color: WhiteSmoke;
            background-color: #141414;
        }}

        .quiz-opcao.selecionada {{
            background-color: WhiteSmoke;
            color: #000000;
            border-color: WhiteSmoke;
            font-weight: bold;
        }}

        .quiz-opcao.correta {{
            border-color: #39FF14;
            color: #39FF14;
            background-color: rgba(57, 255, 20, 0.1);
            font-weight: bold;
        }}

        .quiz-opcao.errada {{
            border-color: #FF2A4B;
            color: #FF2A4B;
            background-color: rgba(255, 42, 75, 0.12);
            font-weight: bold;
        }}

        .quiz-feedback {{
            font-size: 0.76rem;
            min-height: 1em;
        }}

        .quiz-feedback.ok {{
            color: #39FF14;
        }}

        .quiz-feedback.erro {{
            color: #FF2A4B;
        }}

        .quiz-acoes-footer {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            padding-top: 6px;
        }}
    </style>
</head>
<body>
    <header class="dashboard-topbar">
        <span class="topbar-titulo">PAINEL DO MOTOR // CONTROLO AUTOMÓVEL</span>
        <button type="button" class="btn-cyber-acao" id="btn-abrir-quiz">
            QUIZ AUTOMÓVEL (10 PERGUNTAS)
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
            const rPistao = Math.max(2.8, r * 0.45);
            return `
                <circle cx="${{cx.toFixed(1)}}" cy="${{cy.toFixed(1)}}" r="${{r.toFixed(1)}}" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
                <circle cx="${{cx.toFixed(1)}}" cy="${{cy.toFixed(1)}}" r="${{rPistao.toFixed(1)}}" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
            `;
        }}

        function gerarSvgMotorLocal(cilindros, formato) {{
            const n = Math.max(1, Math.min(16, cilindros));
            const fmt = ['I', 'V', 'VR', 'W'].includes(formato) ? formato : 'I';
            let corpo = '';

            if (fmt === 'I') {{
                const espaco = 260.0 / n;
                const raio = Math.min(22.0, Math.max(5.2, (espaco - 5.0) / 2.0));
                let circs = '';
                for (let i = 0; i < n; i++) {{
                    circs += desenharCilindroSvg(50.0 + i * espaco + espaco / 2.0, 95.0, raio);
                }}
                corpo = `
                    <rect x="60" y="20" width="240" height="25" rx="4" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
                    <rect x="40" y="45" width="280" height="100" rx="8" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
                    ${{circs}}
                    <path d="M 70,145 L 290,145 L 270,172 L 90,172 Z" fill="none" stroke="WhiteSmoke" stroke-width="2pt" stroke-linejoin="round" />
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
                    <rect x="50" y="28" width="260" height="58" rx="6" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
                    <rect x="50" y="104" width="260" height="58" rx="6" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
                    <rect x="28" y="76" width="16" height="38" rx="2" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
                    <line x1="44" y1="95" x2="322" y2="95" stroke="WhiteSmoke" stroke-width="2pt" stroke-dasharray="6,4" />
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
                    <rect x="65" y="22" width="230" height="20" rx="4" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
                    <rect x="44" y="42" width="272" height="106" rx="8" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
                    ${{circs}}
                    <path d="M 75,148 L 285,148 L 268,172 L 92,172 Z" fill="none" stroke="WhiteSmoke" stroke-width="2pt" stroke-linejoin="round" />
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
                    <rect x="44" y="20" width="272" height="66" rx="6" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
                    <rect x="44" y="104" width="272" height="66" rx="6" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
                    <rect x="24" y="78" width="14" height="34" rx="2" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
                    <line x1="38" y1="95" x2="326" y2="95" stroke="WhiteSmoke" stroke-width="2pt" stroke-dasharray="6,4" />
                    ${{circs}}
                `;
            }}
            return `<svg class="motor-svg" viewBox="0 0 360 190" xmlns="http://www.w3.org/2000/svg">${{corpo}}</svg>`;
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
           MÓDULO QUIZ AUTOMÓVEL (10 Escolhas Múltiplas)
           ---------------------------------------------------------------------- */
        const QUIZ_DATA = {quiz_json};
        const quizModal = document.getElementById('quiz-modal');
        const btnAbrirQuiz = document.getElementById('btn-abrir-quiz');
        const btnFecharQuiz = document.getElementById('btn-fechar-quiz');
        const btnReiniciarQuiz = document.getElementById('btn-reiniciar-quiz');
        const quizForm = document.getElementById('quiz-form');
        const quizProgresso = document.getElementById('quiz-progresso');
        const quizBanner = document.getElementById('quiz-resultado-banner');
        const quizContainer = quizModal ? quizModal.querySelector('.quiz-container') : null;

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
            QUIZ_DATA.forEach(q => {{
                if (quizForm.querySelector(`input[name="q_${{q.id}}"]:checked`)) {{
                    respondidas += 1;
                }}
            }});
            quizProgresso.textContent = `Respondidas: ${{respondidas}} / ${{QUIZ_DATA.length}}`;
        }}

        function obterClassificacaoQuiz(percentagem) {{
            if (percentagem >= 70) return 'Verdadeiro purista!';
            if (percentagem >= 50) return 'Purista emergente';
            return 'Condutor diário';
        }}

        function aplicarResultadoQuiz(resultado) {{
            let corBanner = '#FF2A4B';
            let fundoBanner = 'rgba(255, 42, 75, 0.16)';
            if (resultado.percentagem >= 70) {{
                corBanner = '#39FF14';
                fundoBanner = 'rgba(57, 255, 20, 0.14)';
            }} else if (resultado.percentagem >= 50) {{
                corBanner = '#FFBE0B';
                fundoBanner = 'rgba(255, 190, 11, 0.16)';
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
                    fb.textContent = '[CORRETA] Resposta certa!';
                }} else if (!item.respondida) {{
                    fb.className = 'quiz-feedback erro';
                    fb.textContent = `[SEM RESPOSTA] Correta: ${{item.texto_correto}}`;
                }} else {{
                    fb.className = 'quiz-feedback erro';
                    fb.textContent = `[INCORRETA] Resposta correta: ${{item.texto_correto}}`;
                }}
            }});

            if (quizContainer) quizContainer.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        async function submeterQuiz() {{
            const respostas = {{}};
            QUIZ_DATA.forEach(q => {{
                const checked = quizForm.querySelector(`input[name="q_${{q.id}}"]:checked`);
                if (checked) {{
                    respostas[String(q.id)] = parseInt(checked.value, 10);
                }}
            }});

            try {{
                const res = await fetch('/api/quiz', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ respostas }})
                }});
                if (res.ok) {{
                    const resultado = await res.json();
                    aplicarResultadoQuiz(resultado);
                    return;
                }}
            }} catch (_) {{}}

            // Fallback local idêntico à função avaliar_quiz() do Python
            let pontuacao = 0;
            const detalhes = QUIZ_DATA.map(q => {{
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
            const percentagem = Math.round((pontuacao / QUIZ_DATA.length) * 100);
            aplicarResultadoQuiz({{
                pontuacao,
                total: QUIZ_DATA.length,
                percentagem,
                classificacao: obterClassificacaoQuiz(percentagem),
                detalhes
            }});
        }}

        function reiniciarQuiz() {{
            quizForm.reset();
            quizForm.querySelectorAll('.quiz-opcao').forEach(op => {{
                op.classList.remove('selecionada', 'correta', 'errada');
            }});
            quizForm.querySelectorAll('.quiz-feedback').forEach(fb => {{
                fb.className = 'quiz-feedback';
                fb.textContent = '';
            }});
            quizBanner.style.display = 'none';
            quizBanner.style.borderColor = '';
            quizBanner.style.backgroundColor = '';
            quizBanner.innerHTML = '';
            atualizarProgressoQuiz();
            if (quizContainer) quizContainer.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        if (btnAbrirQuiz && quizModal) {{
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

            quizForm.querySelectorAll('.quiz-opcao input[type="radio"]').forEach(radio => {{
                radio.addEventListener('change', () => {{
                    const qid = radio.name.replace('q_', '');
                    quizForm.querySelectorAll(`.quiz-opcao[data-qid="${{qid}}"]`).forEach(op => {{
                        op.classList.remove('selecionada', 'correta', 'errada');
                    }});
                    radio.closest('.quiz-opcao').classList.add('selecionada');
                    atualizarProgressoQuiz();
                }});
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

    def do_POST(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        corpo = self.rfile.read(tamanho).decode("utf-8") if tamanho > 0 else "{}"
        dados = json.loads(corpo)

        if self.path == "/api/ficha":
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

        if self.path == "/api/combustao":
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

        if self.path == "/api/quiz":
            resultado = avaliar_quiz(dados.get("respostas", {}))
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
    url = f"http://localhost:{porta}"
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
