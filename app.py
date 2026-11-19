"""
Dashboard Web Modular em Python
Oficina de Multimédia 2026/2027

Estrutura Modular:
- Widget 1: Motor Inline 2D (contorno 2pt WhiteSmoke) + Nº de Cilindros exclusivo
- Widget 2: Seletor de Cilindros e Admissão (NA, Turbo, Supercharger) -> Ficha Técnica
  (estilo de cores DedSec / Cyberpunk minimalista: fundo preto e texto WhiteSmoke)
- Widget 3: Calculadora de Combustão (Bore, Stroke, Compression Ratio, Max RPM,
  Combustível e Ciclo 2T/4T) -> Cilindrada (L), Potência (hp), Binário (Nm) e Paleta HEX
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import math
import sys
import webbrowser


# ==============================================================================
# WIDGET 1: BASE DO MOTOR (Modelo Inline 2D + Número de Cilindros Exclusivo)
# ==============================================================================
def gerar_svg_motor_inline(num_cilindros: int = 4) -> str:
    """Desenha o SVG 2D do motor em linha com contorno de 2pt em WhiteSmoke."""
    num_cilindros = max(1, min(12, int(num_cilindros)))
    largura_bloco = 260
    inicio_x = 50
    espaco = largura_bloco / num_cilindros
    raio_cilindro = min(22.0, (espaco - 10) / 2)

    cilindros_svg = ""
    for i in range(num_cilindros):
        cx = inicio_x + (i * espaco) + (espaco / 2)
        cilindros_svg += (
            f'<circle cx="{cx:.1f}" cy="95" r="{raio_cilindro:.1f}" '
            f'fill="none" stroke="WhiteSmoke" stroke-width="2pt" />\n'
        )
        cilindros_svg += (
            f'<circle cx="{cx:.1f}" cy="95" r="{max(4.0, raio_cilindro * 0.45):.1f}" '
            f'fill="none" stroke="WhiteSmoke" stroke-width="2pt" />\n'
        )

    return f"""
    <svg class="motor-svg" viewBox="0 0 360 190" xmlns="http://www.w3.org/2000/svg"
         aria-label="Motor Inline 2D">
        <!-- Tampa superior do motor em linha -->
        <rect x="60" y="20" width="240" height="25" rx="4"
              fill="none" stroke="WhiteSmoke" stroke-width="2pt" />

        <!-- Bloco principal do motor em linha (Inline Block) -->
        <rect x="40" y="45" width="280" height="100" rx="8"
              fill="none" stroke="WhiteSmoke" stroke-width="2pt" />

        <!-- Cilindros dispostos em linha (Inline) -->
        {cilindros_svg}

        <!-- Base / Cárter inferior -->
        <path d="M 70,145 L 290,145 L 270,172 L 90,172 Z"
              fill="none" stroke="WhiteSmoke" stroke-width="2pt" stroke-linejoin="round" />
    </svg>
    """


def widget_motor_inline(num_cilindros: int = 4) -> str:
    """
    Gera o Widget 1 com a figura 2D do motor em linha (contorno 2pt WhiteSmoke)
    e exibe exclusivamente o número de cilindros.
    """
    return f"""
    <section class="widget-card" id="widget-1">
        <div id="motor-svg-container" style="width: 100%; display: flex; justify-content: center;">
            {gerar_svg_motor_inline(num_cilindros)}
        </div>

        <!-- Exibição EXCLUSIVA do número de cilindros -->
        <div class="cilindros-box">
            <span class="cilindros-numero" id="motor-num-cilindros">{num_cilindros}</span>
            <span class="cilindros-texto">CILINDROS</span>
        </div>
    </section>
    """


# ==============================================================================
# WIDGET 2: FICHA TÉCNICA (Seleção de Cilindros e Admissão -> Processamento Python)
# ==============================================================================
def processar_ficha_tecnica(num_cilindros: int = 4, admissao: str = "NA") -> dict:
    """
    Processa em Python o número de cilindros e o tipo de admissão (NA, Turbo ou Supercharger)
    e gera automaticamente os dados de uma ficha técnica fictícia.
    """
    num_cilindros = max(1, min(12, int(num_cilindros)))

    perfis_admissao = {
        "NA": {
            "tipo": "NA (Naturalmente Aspirado)",
            "mult_potencia": 1.00,
            "mult_binario": 1.00,
            "pressao": "0.0 bar (Atmosférico)",
            "resposta": "Linear / Imediata",
            "rpm_max": 7800,
        },
        "Turbo": {
            "tipo": "Turbo (Turbocompressor)",
            "mult_potencia": 1.55,
            "mult_binario": 1.60,
            "pressao": "+1.3 bar",
            "resposta": "Progressiva / Alta Pressão",
            "rpm_max": 7000,
        },
        "Supercharger": {
            "tipo": "Supercharger (Compressor Mecânico)",
            "mult_potencia": 1.35,
            "mult_binario": 1.45,
            "pressao": "+0.8 bar",
            "resposta": "Instantânea / Baixa Rotação",
            "rpm_max": 7300,
        },
    }

    perfil = perfis_admissao.get(admissao, perfis_admissao["NA"])
    admissao_valida = admissao if admissao in perfis_admissao else "NA"

    potencia_cv = int(round(num_cilindros * 45 * perfil["mult_potencia"]))
    binario_nm = int(round(num_cilindros * 55 * perfil["mult_binario"]))
    rpm_corte = perfil["rpm_max"] - (num_cilindros * 100)

    return {
        "cilindros": num_cilindros,
        "admissao": admissao_valida,
        "configuracao": f"Inline-{num_cilindros} ({num_cilindros} Cilindros)",
        "tipo_admissao": perfil["tipo"],
        "pressao_boost": perfil["pressao"],
        "potencia": f"{potencia_cv} cv",
        "binario": f"{binario_nm} Nm",
        "entrega": perfil["resposta"],
        "rotacao_max": f"{rpm_corte} RPM",
    }


def render_tabela_ficha(ficha: dict) -> str:
    """Renderiza o HTML da ficha técnica com estética minimalista (preto e WhiteSmoke)."""
    return f"""
    <div class="ficha-tecnica">
        <div class="ficha-titulo">FICHA TÉCNICA</div>
        <div class="ficha-linha"><span>MOTOR</span><strong>{ficha['configuracao']}</strong></div>
        <div class="ficha-linha"><span>ADMISSÃO</span><strong>{ficha['tipo_admissao']}</strong></div>
        <div class="ficha-linha"><span>PRESSÃO</span><strong>{ficha['pressao_boost']}</strong></div>
        <div class="ficha-linha"><span>POTÊNCIA EST.</span><strong>{ficha['potencia']}</strong></div>
        <div class="ficha-linha"><span>BINÁRIO EST.</span><strong>{ficha['binario']}</strong></div>
        <div class="ficha-linha"><span>ENTREGA</span><strong>{ficha['entrega']}</strong></div>
        <div class="ficha-linha"><span>ROTAÇÃO MÁX.</span><strong>{ficha['rotacao_max']}</strong></div>
    </div>
    """


def widget_2_modular(num_cilindros: int = 4, admissao: str = "NA") -> str:
    """
    Widget 2: Permite selecionar o nº de cilindros e o tipo de admissão (NA, Turbo, Supercharger)
    e exibe a ficha técnica processada com estética cyberpunk minimalista (preto e WhiteSmoke).
    """
    ficha = processar_ficha_tecnica(num_cilindros, admissao)
    opcoes_cilindros = [3, 4, 5, 6, 8, 10, 12]
    opcoes_admissao = ["NA", "Turbo", "Supercharger"]

    options_cyl_html = "\n".join(
        f'<option value="{c}" {"selected" if c == num_cilindros else ""}>{c} Cilindros</option>'
        for c in opcoes_cilindros
    )
    options_adm_html = "\n".join(
        f'<option value="{a}" {"selected" if a == admissao else ""}>{a}</option>'
        for a in opcoes_admissao
    )

    return f"""
    <section class="widget-card" id="widget-2">
        <div class="widget-form">
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
        </div>

        <div id="ficha-output" style="width: 100%;">
            {render_tabela_ficha(ficha)}
        </div>
    </section>
    """


# ==============================================================================
# WIDGET 3: CALCULADORA DE COMBUSTÃO, POTÊNCIA (HP), BINÁRIO (NM) E PALETA HEX
# ==============================================================================
def processar_combustao(
    bore: float = 86.0,
    stroke: float = 86.0,
    compression_ratio: float = 10.5,
    max_rpm: int = 7500,
    combustivel: str = "Gasolina",
    ciclo: str = "4T",
    num_cilindros: int = 4,
) -> dict:
    """
    Calcula automaticamente em Python:
    - Cilindrada total em Litros (L)
    - Potência estimada em hp
    - Binário (torque) estimado em Nm
    - Paleta de cores em formato HEX para o dashboard cyberpunk
    """
    bore = max(10.0, float(bore))
    stroke = max(10.0, float(stroke))
    cr = max(2.0, float(compression_ratio))
    max_rpm = max(500, int(max_rpm))
    num_cilindros = max(1, min(12, int(num_cilindros)))
    ciclo = "2T" if str(ciclo).upper() == "2T" else "4T"

    perfis_combustivel = {
        "Gasolina": {"fator_tq": 1.00, "cor_hex": "#00F0FF"},
        "Etanol (E85)": {"fator_tq": 1.08, "cor_hex": "#39FF14"},
        "Diesel": {"fator_tq": 1.15, "cor_hex": "#FF9F1C"},
        "Metanol": {"fator_tq": 1.12, "cor_hex": "#C724FF"},
    }
    perfil_comb = perfis_combustivel.get(combustivel, perfis_combustivel["Gasolina"])

    # 1. Cilindrada em Litros: V = (pi/4) * (bore_cm^2) * stroke_cm * cilindros / 1000
    cilindrada_unit_cc = (math.pi / 4.0) * ((bore / 10.0) ** 2) * (stroke / 10.0)
    cilindrada_litros = (cilindrada_unit_cc * num_cilindros) / 1000.0

    # 2. Binário (Nm) e Potência (hp)
    fator_cr = 1.0 + max(-0.25, min(0.35, (cr - 10.0) * 0.025))
    fator_ciclo_tq = 1.25 if ciclo == "2T" else 1.00
    torque_nm = int(round(cilindrada_litros * 105.0 * fator_cr * perfil_comb["fator_tq"] * fator_ciclo_tq))

    # Relação física Potência (hp) = (Torque_Nm * RPM_pico) / 7121
    fator_rpm_potencia = 0.88 if ciclo == "4T" else 0.94
    potencia_hp = int(round((torque_nm * max_rpm * fator_rpm_potencia) / 7121.0))

    # 3. Paleta de cores em formato HEX
    cor_destaque = "#FF007F" if (ciclo == "2T" and max_rpm >= 8500) else perfil_comb["cor_hex"]
    paleta_hex = [
        {"nome": "Fundo", "hex": "#000000"},
        {"nome": "Base", "hex": "#F5F5F5"},
        {"nome": "Acento", "hex": cor_destaque},
        {"nome": "Painel", "hex": "#12161F"},
        {"nome": "Redline", "hex": "#FF2A4B"},
    ]

    return {
        "cilindrada_litros": f"{cilindrada_litros:.2f} L",
        "potencia_hp": f"{potencia_hp} hp",
        "torque_nm": f"{torque_nm} Nm",
        "paleta_hex": paleta_hex,
    }


def render_resultado_combustao(dados: dict) -> str:
    """Renderiza os resultados calculados e a paleta de cores em formato HEX."""
    caixas_hex = "".join(
        f"""
        <div class="swatch-item">
            <span class="swatch-cor" style="background-color: {cor['hex']};"></span>
            <span class="swatch-codigo">{cor['hex']}</span>
        </div>
        """
        for cor in dados["paleta_hex"]
    )

    return f"""
    <div class="ficha-tecnica">
        <div class="ficha-titulo">PARÂMETROS CALCULADOS</div>
        <div class="ficha-linha"><span>CILINDRADA</span><strong>{dados['cilindrada_litros']}</strong></div>
        <div class="ficha-linha"><span>POTÊNCIA</span><strong>{dados['potencia_hp']}</strong></div>
        <div class="ficha-linha"><span>BINÁRIO (TORQUE)</span><strong>{dados['torque_nm']}</strong></div>

        <div class="ficha-titulo" style="margin-top: 6px;">PALETA DE CORES (HEX)</div>
        <div class="paleta-grid">
            {caixas_hex}
        </div>
    </div>
    """


def widget_3_modular(num_cilindros: int = 4) -> str:
    """
    Widget 3: Inputs de Bore, Stroke, Compression Ratio, Max RPM, Combustível e Ciclo (2T/4T),
    exibindo Cilindrada (L), Potência (hp), Binário (Nm) e Paleta de Cores HEX.
    """
    dados_iniciais = processar_combustao(num_cilindros=num_cilindros)

    return f"""
    <section class="widget-card" id="widget-3">
        <div class="widget-form">
            <div class="grid-2-col">
                <div class="campo-grupo">
                    <label for="input-bore">BORE (mm)</label>
                    <input type="number" id="input-bore" class="input-cyber" value="86.0" step="0.5" min="20" max="200">
                </div>
                <div class="campo-grupo">
                    <label for="input-stroke">STROKE (mm)</label>
                    <input type="number" id="input-stroke" class="input-cyber" value="86.0" step="0.5" min="20" max="200">
                </div>
                <div class="campo-grupo">
                    <label for="input-cr">COMP. RATIO (:1)</label>
                    <input type="number" id="input-cr" class="input-cyber" value="10.5" step="0.1" min="4" max="25">
                </div>
                <div class="campo-grupo">
                    <label for="input-rpm">MAX RPM</label>
                    <input type="number" id="input-rpm" class="input-cyber" value="7500" step="100" min="1000" max="20000">
                </div>
                <div class="campo-grupo">
                    <label for="select-combustivel">COMBUSTÍVEL</label>
                    <select id="select-combustivel" class="input-cyber">
                        <option value="Gasolina" selected>Gasolina</option>
                        <option value="Etanol (E85)">Etanol (E85)</option>
                        <option value="Diesel">Diesel</option>
                        <option value="Metanol">Metanol</option>
                    </select>
                </div>
                <div class="campo-grupo">
                    <label for="select-ciclo">CICLO (2T / 4T)</label>
                    <select id="select-ciclo" class="input-cyber">
                        <option value="4T" selected>4T</option>
                        <option value="2T">2T</option>
                    </select>
                </div>
            </div>
        </div>

        <div id="combustao-output" style="width: 100%;">
            {render_resultado_combustao(dados_iniciais)}
        </div>
    </section>
    """


# ==============================================================================
# MONTAGEM DO DASHBOARD WEB (HTML + CSS INLINE SIMPLES)
# ==============================================================================
def gerar_dashboard_html(num_cilindros: int = 4, admissao: str = "NA") -> str:
    """
    Junta os 3 widgets modulares numa página HTML com fundo preto,
    texto WhiteSmoke e estética cyberpunk minimalista.
    """
    w1 = widget_motor_inline(num_cilindros)
    w2 = widget_2_modular(num_cilindros, admissao)
    w3 = widget_3_modular(num_cilindros)

    return f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Motor Inline</title>
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

        .ficha-linha {{
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            border-bottom: 1px dotted rgba(245, 245, 245, 0.3);
            padding-bottom: 3px;
        }}

        /* Paleta de Cores HEX (Widget 3) */
        .paleta-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 6px;
            margin-top: 4px;
        }}

        .swatch-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 3px;
        }}

        .swatch-cor {{
            width: 100%;
            height: 16px;
            border: 1px solid WhiteSmoke;
            display: block;
        }}

        .swatch-codigo {{
            font-size: 0.62rem;
            color: WhiteSmoke;
        }}
    </style>
</head>
<body>
    <main class="dashboard-container">
        {w1}
        {w2}
        {w3}
    </main>

    <script>
        const selectCilindros = document.getElementById('select-cilindros');
        const selectAdmissao = document.getElementById('select-admissao');
        const fichaOutput = document.getElementById('ficha-output');
        const motorSvgContainer = document.getElementById('motor-svg-container');
        const motorNumCilindros = document.getElementById('motor-num-cilindros');

        const inputBore = document.getElementById('input-bore');
        const inputStroke = document.getElementById('input-stroke');
        const inputCr = document.getElementById('input-cr');
        const inputRpm = document.getElementById('input-rpm');
        const selectCombustivel = document.getElementById('select-combustivel');
        const selectCiclo = document.getElementById('select-ciclo');
        const combustaoOutput = document.getElementById('combustao-output');

        async function atualizarWidget3() {{
            const payload = {{
                bore: parseFloat(inputBore.value) || 86.0,
                stroke: parseFloat(inputStroke.value) || 86.0,
                compression_ratio: parseFloat(inputCr.value) || 10.5,
                max_rpm: parseInt(inputRpm.value, 10) || 7500,
                combustivel: selectCombustivel.value || 'Gasolina',
                ciclo: selectCiclo.value || '4T',
                cilindros: parseInt(selectCilindros.value, 10) || 4
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
                    return;
                }}
            }} catch (_) {{}}

            // Fallback local idêntico ao cálculo Python para abertura direta do index.html
            const perfisComb = {{
                'Gasolina': {{ ftq: 1.00, hex: '#00F0FF' }},
                'Etanol (E85)': {{ ftq: 1.08, hex: '#39FF14' }},
                'Diesel': {{ ftq: 1.15, hex: '#FF9F1C' }},
                'Metanol': {{ ftq: 1.12, hex: '#C724FF' }}
            }};
            const pc = perfisComb[payload.combustivel] || perfisComb['Gasolina'];
            const unitCc = (Math.PI / 4.0) * Math.pow(payload.bore / 10.0, 2) * (payload.stroke / 10.0);
            const litros = (unitCc * payload.cilindros) / 1000.0;

            const fatorCr = 1.0 + Math.max(-0.25, Math.min(0.35, (payload.compression_ratio - 10.0) * 0.025));
            const fatorCicloTq = payload.ciclo === '2T' ? 1.25 : 1.00;
            const torqueNm = Math.round(litros * 105.0 * fatorCr * pc.ftq * fatorCicloTq);
            const fatorRpmHp = payload.ciclo === '4T' ? 0.88 : 0.94;
            const potenciaHp = Math.round((torqueNm * payload.max_rpm * fatorRpmHp) / 7121.0);

            const corAcento = (payload.ciclo === '2T' && payload.max_rpm >= 8500) ? '#FF007F' : pc.hex;
            const paleta = ['#000000', '#F5F5F5', corAcento, '#12161F', '#FF2A4B'];

            const caixasHex = paleta.map(hex => `
                <div class="swatch-item">
                    <span class="swatch-cor" style="background-color: ${{hex}};"></span>
                    <span class="swatch-codigo">${{hex}}</span>
                </div>
            `).join('');

            combustaoOutput.innerHTML = `
                <div class="ficha-tecnica">
                    <div class="ficha-titulo">PARÂMETROS CALCULADOS</div>
                    <div class="ficha-linha"><span>CILINDRADA</span><strong>${{litros.toFixed(2)}} L</strong></div>
                    <div class="ficha-linha"><span>POTÊNCIA</span><strong>${{potenciaHp}} hp</strong></div>
                    <div class="ficha-linha"><span>BINÁRIO (TORQUE)</span><strong>${{torqueNm}} Nm</strong></div>

                    <div class="ficha-titulo" style="margin-top: 6px;">PALETA DE CORES (HEX)</div>
                    <div class="paleta-grid">${{caixasHex}}</div>
                </div>
            `;
        }}

        async function atualizarDados() {{
            const cilindros = parseInt(selectCilindros.value, 10) || 4;
            const admissao = selectAdmissao.value || 'NA';

            try {{
                const res = await fetch('/api/ficha', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ cilindros, admissao }})
                }});
                if (res.ok) {{
                    const data = await res.json();
                    fichaOutput.innerHTML = data.ficha_html;
                    motorSvgContainer.innerHTML = data.motor_svg;
                    motorNumCilindros.textContent = data.cilindros;
                    atualizarWidget3();
                    return;
                }}
            }} catch (_) {{}}

            const perfis = {{
                'NA': {{ tipo: 'NA (Naturalmente Aspirado)', mp: 1.00, mb: 1.00, pressao: '0.0 bar (Atmosférico)', resp: 'Linear / Imediata', rpm: 7800 }},
                'Turbo': {{ tipo: 'Turbo (Turbocompressor)', mp: 1.55, mb: 1.60, pressao: '+1.3 bar', resp: 'Progressiva / Alta Pressão', rpm: 7000 }},
                'Supercharger': {{ tipo: 'Supercharger (Compressor Mecânico)', mp: 1.35, mb: 1.45, pressao: '+0.8 bar', resp: 'Instantânea / Baixa Rotação', rpm: 7300 }}
            }};
            const p = perfis[admissao] || perfis['NA'];
            const cv = Math.round(cilindros * 45 * p.mp);
            const nm = Math.round(cilindros * 55 * p.mb);
            const rpmMax = p.rpm - (cilindros * 100);

            fichaOutput.innerHTML = `
                <div class="ficha-tecnica">
                    <div class="ficha-titulo">FICHA TÉCNICA</div>
                    <div class="ficha-linha"><span>MOTOR</span><strong>Inline-${{cilindros}} (${{cilindros}} Cilindros)</strong></div>
                    <div class="ficha-linha"><span>ADMISSÃO</span><strong>${{p.tipo}}</strong></div>
                    <div class="ficha-linha"><span>PRESSÃO</span><strong>${{p.pressao}}</strong></div>
                    <div class="ficha-linha"><span>POTÊNCIA EST.</span><strong>${{cv}} cv</strong></div>
                    <div class="ficha-linha"><span>BINÁRIO EST.</span><strong>${{nm}} Nm</strong></div>
                    <div class="ficha-linha"><span>ENTREGA</span><strong>${{p.resp}}</strong></div>
                    <div class="ficha-linha"><span>ROTAÇÃO MÁX.</span><strong>${{rpmMax}} RPM</strong></div>
                </div>
            `;

            const espaco = 260 / cilindros;
            const raio = Math.min(22, (espaco - 10) / 2);
            let circulos = '';
            for (let i = 0; i < cilindros; i++) {{
                const cx = 50 + (i * espaco) + (espaco / 2);
                circulos += `<circle cx="${{cx.toFixed(1)}}" cy="95" r="${{raio.toFixed(1)}}" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />`;
                circulos += `<circle cx="${{cx.toFixed(1)}}" cy="95" r="${{Math.max(4, raio * 0.45).toFixed(1)}}" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />`;
            }}
            motorSvgContainer.innerHTML = `
                <svg class="motor-svg" viewBox="0 0 360 190" xmlns="http://www.w3.org/2000/svg">
                    <rect x="60" y="20" width="240" height="25" rx="4" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
                    <rect x="40" y="45" width="280" height="100" rx="8" fill="none" stroke="WhiteSmoke" stroke-width="2pt" />
                    ${{circulos}}
                    <path d="M 70,145 L 290,145 L 270,172 L 90,172 Z" fill="none" stroke="WhiteSmoke" stroke-width="2pt" stroke-linejoin="round" />
                </svg>
            `;
            motorNumCilindros.textContent = cilindros;
            atualizarWidget3();
        }}

        selectCilindros.addEventListener('change', atualizarDados);
        selectAdmissao.addEventListener('change', atualizarDados);

        [inputBore, inputStroke, inputCr, inputRpm, selectCombustivel, selectCiclo].forEach(el => {{
            el.addEventListener('input', atualizarWidget3);
            el.addEventListener('change', atualizarWidget3);
        }});
    </script>
</body>
</html>
"""


def guardar_index_html(num_cilindros: int = 4, admissao: str = "NA") -> None:
    """
    Gera primeiro todo o HTML em memória e só depois grava o ficheiro index.html
    (evita que o index.html fique vazio/0 bytes caso ocorra algum erro).
    """
    conteudo_html = gerar_dashboard_html(num_cilindros, admissao)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(conteudo_html)
    print("[OK] Ficheiro index.html gerado com sucesso.")


class DashboardHandler(SimpleHTTPRequestHandler):
    """Servidor HTTP que processa os pedidos dos Widgets 2 e 3 diretamente em Python."""

    def do_POST(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        corpo = self.rfile.read(tamanho).decode("utf-8") if tamanho > 0 else "{}"
        dados = json.loads(corpo)

        if self.path == "/api/ficha":
            cil = int(dados.get("cilindros", 4))
            adm = str(dados.get("admissao", "NA"))
            ficha = processar_ficha_tecnica(cil, adm)

            resposta = json.dumps({
                "cilindros": ficha["cilindros"],
                "ficha_html": render_tabela_ficha(ficha),
                "motor_svg": gerar_svg_motor_inline(ficha["cilindros"]),
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
            )
            resposta = json.dumps({
                "combustao_html": render_resultado_combustao(resultado),
            }).encode("utf-8")

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
