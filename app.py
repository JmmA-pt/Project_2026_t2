from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import math
import sys
import webbrowser


# ==============================================================================
# WIDGET 1: BASE DO MOTOR (Design Simplista & Estilizado 2D + Admissão)
# ==============================================================================
SVG_MOTOR_DEFS = """
<defs>
    <linearGradient id="eng-block" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#171b24" />
        <stop offset="100%" stop-color="#0b0e14" />
    </linearGradient>
    <radialGradient id="eng-piston" cx="38%" cy="35%" r="65%">
        <stop offset="0%" stop-color="#64748b" />
        <stop offset="65%" stop-color="#1e293b" />
        <stop offset="100%" stop-color="#0f172a" />
    </radialGradient>
    <linearGradient id="eng-accent" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#ff1e38" />
        <stop offset="100%" stop-color="#ff6b00" />
    </linearGradient>
    <linearGradient id="eng-amber" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#ff9f1c" />
        <stop offset="100%" stop-color="#ff6b00" />
    </linearGradient>
    <linearGradient id="eng-pipe" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#94a3b8" />
        <stop offset="100%" stop-color="#475569" />
    </linearGradient>
</defs>
"""


def gerar_svg_motor_inline(
    num_cilindros: int = 4,
    formato: str = "I",
    admissao: str = "Atmosférico",
) -> str:
    """
    Desenha o SVG 2D simplista e estilizado do motor de acordo com o formato escolhido
    (I, V, VR ou W) e tipo de admissão (Atmosférico, Turbo, Supercompressor,
    Biturbo ou Twincharge), suportando até 16 cilindros.
    """
    num_cilindros = max(1, min(16, int(num_cilindros)))
    formato = str(formato).upper()
    if formato not in ("I", "V", "VR", "W"):
        formato = "I"

    adm = str(admissao) if str(admissao) in (
        "Atmosférico", "Turbo", "Supercompressor", "Biturbo", "Twincharge"
    ) else "Atmosférico"

    def desenhar_cilindro(cx: float, cy: float, r: float) -> str:
        r_pistao = max(3.4, r * 0.72)
        r_centro = max(1.3, min(3.2, r * 0.18))
        return (
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#06080c" stroke="#94a3b8" stroke-width="1.35" />\n'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_pistao:.1f}" fill="url(#eng-piston)" stroke="#334155" stroke-width="0.8" />\n'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_centro:.1f}" fill="#ff1e38" />\n'
        )

    def desenhar_polia(cx: float, cy: float, r: float, cor_centro: str = "#ff1e38") -> str:
        r_in = max(2.2, r * 0.44)
        return (
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#0d1017" stroke="#94a3b8" stroke-width="1.3" />\n'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_in:.1f}" fill="none" stroke="{cor_centro}" stroke-width="1.2" />\n'
        )

    def desenhar_parafusos(x: float, y: float, w: float, h: float, pad: float = 6.5) -> str:
        coords = [
            (x + pad, y + pad),
            (x + w - pad, y + pad),
            (x + pad, y + h - pad),
            (x + w - pad, y + h - pad),
        ]
        return "".join(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.3" fill="#475569" />\n'
            for px, py in coords
        )

    def desenhar_turbo(cx: float, cy: float, escala: float = 1.0) -> str:
        return (
            f'<g transform="translate({cx:.1f},{cy:.1f}) scale({escala:.2f})">\n'
            f'  <line x1="-10" y1="0" x2="10" y2="0" stroke="#94a3b8" stroke-width="2" />\n'
            f'  <rect x="-4" y="-3.5" width="8" height="7" rx="2" fill="#1e293b" stroke="#64748b" stroke-width="0.9" />\n'
            f'  <circle cx="-11" cy="0" r="10.5" fill="#0f141e" stroke="#e2e8f0" stroke-width="1.3" />\n'
            f'  <path d="M -11,-5.5 L -11,5.5 M -16.5,0 L -5.5,0" stroke="#64748b" stroke-width="1.1" />\n'
            f'  <circle cx="-11" cy="0" r="2.2" fill="#ff1e38" />\n'
            f'  <circle cx="11" cy="0" r="9.5" fill="#180d0c" stroke="#ff6b00" stroke-width="1.3" />\n'
            f'  <circle cx="11" cy="0" r="4.0" fill="#0b090a" stroke="#ff6b00" stroke-width="0.9" />\n'
            f'</g>\n'
        )

    def desenhar_intercooler(x: float, y: float, w: float, h: float, vertical: bool = False) -> str:
        linhas = ""
        for k in range(1, 4):
            if vertical:
                ly = y + k * (h / 4.0)
                linhas += f'<line x1="{x + 4:.1f}" y1="{ly:.1f}" x2="{x + w - 4:.1f}" y2="{ly:.1f}" stroke="#475569" stroke-width="1" />\n'
            else:
                lx = x + k * (w / 4.0)
                linhas += f'<line x1="{lx:.1f}" y1="{y + 4:.1f}" x2="{lx:.1f}" y2="{y + h - 4:.1f}" stroke="#475569" stroke-width="1" />\n'
        return (
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="#090c12" stroke="#94a3b8" stroke-width="1.3" />\n'
            f'{linhas}'
        )

    def desenhar_filtro_conico(x: float, y: float, w: float, h: float) -> str:
        return (
            f'<polygon points="{x:.1f},{y + 2.5:.1f} {x + w:.1f},{y:.1f} {x + w:.1f},{y + h:.1f} {x:.1f},{y + h - 2.5:.1f}" '
            f'fill="#190c10" stroke="#ff1e38" stroke-width="1.2" stroke-linejoin="round" />\n'
            f'<line x1="{x + w * 0.45:.1f}" y1="{y + 3.5:.1f}" x2="{x + w * 0.45:.1f}" y2="{y + h - 3.5:.1f}" stroke="#7f1d1d" stroke-width="1" />\n'
        )

    def desenhar_supercharger(
        x: float, y: float, w: float, h: float,
        pulley_x: float, pulley_y: float, crank_x: float, crank_y: float
    ) -> str:
        snout_y = y + h / 2.0
        return (
            f'<line x1="{pulley_x:.1f}" y1="{pulley_y:.1f}" x2="{crank_x:.1f}" y2="{crank_y:.1f}" stroke="#475569" stroke-width="2.6" />\n'
            f'<rect x="{pulley_x:.1f}" y="{snout_y - 3.5:.1f}" width="{max(6.0, x - pulley_x + 2):.1f}" height="7" rx="2" fill="#1e293b" stroke="#64748b" stroke-width="1" />\n'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" fill="#121620" stroke="#cbd5e1" stroke-width="1.3" />\n'
            f'<rect x="{x + 14:.1f}" y="{snout_y - 2:.1f}" width="{w - 28:.1f}" height="4" rx="2" fill="url(#eng-amber)" />\n'
            f'{desenhar_polia(pulley_x, pulley_y, 7.2, "#ff9f1c")}'
        )

    corpo_svg = ""

    if formato in ("I", "VR"):
        largura_bloco = 260.0 if formato == "I" else 248.0
        inicio_x = 72.0 if formato == "I" else 78.0
        espaco = largura_bloco / num_cilindros
        if formato == "I":
            raio = min(21.0, max(5.2, (espaco - 4.5) / 2.0))
        else:
            raio = min(16.0, max(7.0, (espaco * 1.15 - 4.0) / 2.0))
            if num_cilindros >= 10:
                raio = min(raio, 10.2)
        sw_runner = max(2.2, min(5.5, raio * 0.35))

        cilindros = ""
        coletores = ""
        for i in range(num_cilindros):
            cx = inicio_x + i * espaco + espaco / 2.0
            cy = 123.0 if formato == "I" else (104.0 if i % 2 == 0 else 142.0)
            cilindros += desenhar_cilindro(cx, cy, raio)
            coletores += (
                f'<line x1="{cx:.1f}" y1="54" x2="{cx:.1f}" y2="72" stroke="#64748b" stroke-width="{sw_runner:.1f}" stroke-linecap="round" />\n'
                f'<line x1="{cx:.1f}" y1="174" x2="{cx:.1f}" y2="192" stroke="#c2410c" stroke-width="{sw_runner:.1f}" stroke-linecap="round" />\n'
            )

        admissao_svg = ""
        if adm == "Atmosférico":
            admissao_svg = (
                f'<rect x="78" y="40" width="248" height="14" rx="5" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'<rect x="90" y="45.5" width="224" height="3" rx="1.5" fill="url(#eng-accent)" />\n'
                f'<line x1="54" y1="47" x2="78" y2="47" stroke="#64748b" stroke-width="5" />\n'
                f'{desenhar_filtro_conico(22.0, 38.0, 32.0, 18.0)}'
                f'<rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />\n'
            )
        elif adm == "Turbo":
            admissao_svg = (
                f'<path d="M 30,190 L 30,47 L 78,47" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 68,210 L 184,210" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" />\n'
                f'{desenhar_intercooler(16.0, 194.0, 50.0, 26.0)}'
                f'<rect x="78" y="40" width="248" height="14" rx="5" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'<rect x="90" y="45.5" width="224" height="3" rx="1.5" fill="url(#eng-accent)" />\n'
                f'<rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />\n'
                f'{desenhar_turbo(216.0, 211.0, 1.32)}'
            )
        elif adm == "Supercompressor":
            admissao_svg = (
                f'<rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />\n'
                f'<line x1="304" y1="43" x2="328" y2="43" stroke="#64748b" stroke-width="5" />\n'
                f'{desenhar_filtro_conico(328.0, 34.0, 30.0, 18.0)}'
                f'{desenhar_supercharger(92.0, 30.0, 212.0, 24.0, 48.0, 42.0, 48.0, 123.0)}'
            )
        elif adm == "Biturbo":
            admissao_svg = (
                f'<path d="M 30,190 L 30,47 L 78,47" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 68,210 L 266,210" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" />\n'
                f'{desenhar_intercooler(16.0, 194.0, 50.0, 26.0)}'
                f'<rect x="78" y="40" width="248" height="14" rx="5" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'<rect x="90" y="45.5" width="224" height="3" rx="1.5" fill="url(#eng-accent)" />\n'
                f'<rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />\n'
                f'{desenhar_turbo(146.0, 211.0, 1.24)}'
                f'{desenhar_turbo(282.0, 211.0, 1.24)}'
            )
        else:  # Twincharge
            admissao_svg = (
                f'<path d="M 24,190 L 24,38 L 84,38" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" stroke-linejoin="round" />\n'
                f'<path d="M 68,210 L 194,210" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" />\n'
                f'{desenhar_intercooler(14.0, 194.0, 50.0, 26.0)}'
                f'<rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />\n'
                f'{desenhar_turbo(224.0, 211.0, 1.28)}'
                f'{desenhar_supercharger(92.0, 30.0, 212.0, 24.0, 48.0, 42.0, 48.0, 123.0)}'
            )

        corpo_svg = f"""
        {coletores}
        {admissao_svg}
        <rect x="41" y="84" width="15" height="52" rx="7" fill="#0d1017" stroke="#475569" stroke-width="1.2" />
        {desenhar_polia(48.0, 93.0, 6.4)}
        {desenhar_polia(48.0, 123.0, 11.4)}
        <rect x="342" y="93" width="11" height="60" rx="3" fill="#1e293b" stroke="#64748b" stroke-width="1.2" />
        <rect x="64" y="70" width="276" height="106" rx="10" fill="url(#eng-block)" stroke="#64748b" stroke-width="1.5" />
        {desenhar_parafusos(64.0, 70.0, 276.0, 106.0)}
        {cilindros}
        """

    else:  # formato == "V" ou "W"
        n_sup = (num_cilindros + 1) // 2
        n_inf = num_cilindros // 2
        cols = max(1, n_sup, n_inf)
        largura = 244.0
        inicio_x = 80.0
        espaco_sup = largura / max(1, n_sup)
        espaco_inf = largura / max(1, n_inf)

        if formato == "V":
            raio = min(15.5, max(5.8, (largura / cols - 6.0) / 2.0))
            bank_sup_y, bank_sup_h = 55.0, 50.0
            bank_inf_y, bank_inf_h = 141.0, 50.0
            y_exh_sup, y_exh_inf = 39.0, 193.0
            y_col_sup, y_col_inf = 38.0, 201.0
        else:
            raio = min(10.8, max(6.6, (largura / cols) * 0.34))
            bank_sup_y, bank_sup_h = 47.0, 58.0
            bank_inf_y, bank_inf_h = 141.0, 58.0
            y_exh_sup, y_exh_inf = 32.0, 200.0
            y_col_sup, y_col_inf = 31.0, 208.0

        sw_runner = max(2.0, min(4.8, raio * 0.35))
        cilindros = ""
        escapes = ""
        trombetas = ""

        for i in range(n_sup):
            cx = inicio_x + i * espaco_sup + espaco_sup / 2.0
            cy = 80.0 if formato == "V" else (64.0 if i % 2 == 0 else 87.0)
            cilindros += desenhar_cilindro(cx, cy, raio)
            escapes += f'<line x1="{cx:.1f}" y1="{y_exh_sup:.1f}" x2="{cx:.1f}" y2="{y_exh_sup + 16:.1f}" stroke="#c2410c" stroke-width="{sw_runner:.1f}" stroke-linecap="round" />\n'
            trombetas += f'<circle cx="{cx:.1f}" cy="116" r="{max(2.2, min(3.4, sw_runner * 0.72)):.1f}" fill="#ff1e38" opacity="0.85" />\n'
        for i in range(n_inf):
            cx = inicio_x + i * espaco_inf + espaco_inf / 2.0
            cy = 166.0 if formato == "V" else (159.0 if i % 2 == 0 else 182.0)
            cilindros += desenhar_cilindro(cx, cy, raio)
            escapes += f'<line x1="{cx:.1f}" y1="{y_exh_inf:.1f}" x2="{cx:.1f}" y2="{y_exh_inf + 16:.1f}" stroke="#c2410c" stroke-width="{sw_runner:.1f}" stroke-linecap="round" />\n'
            trombetas += f'<circle cx="{cx:.1f}" cy="130" r="{max(2.2, min(3.4, sw_runner * 0.72)):.1f}" fill="#ff1e38" opacity="0.85" />\n'

        admissao_vw = ""
        if adm == "Atmosférico":
            admissao_vw = (
                f'<rect x="78" y="109" width="250" height="28" rx="6" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'{trombetas}'
                f'<line x1="328" y1="123" x2="352" y2="123" stroke="#64748b" stroke-width="5" />\n'
                f'{desenhar_filtro_conico(352.0, 113.0, 30.0, 20.0)}'
            )
        elif adm == "Turbo":
            admissao_vw = (
                f'<path d="M 185,24 L 24,24 L 24,87" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 24,159 L 24,123 L 82,123" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'{desenhar_intercooler(14.0, 86.0, 20.0, 74.0, True)}'
                f'<rect x="78" y="109" width="250" height="28" rx="6" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'<rect x="94" y="121.5" width="218" height="3" rx="1.5" fill="url(#eng-accent)" />\n'
                f'{desenhar_turbo(212.0, 24.0, 1.24)}'
            )
        elif adm == "Supercompressor":
            admissao_vw = (
                f'<line x1="318" y1="123" x2="342" y2="123" stroke="#64748b" stroke-width="5" />\n'
                f'{desenhar_filtro_conico(342.0, 113.0, 30.0, 20.0)}'
                f'<line x1="48" y1="80" x2="48" y2="166" stroke="#475569" stroke-width="2.6" />\n'
                f'{desenhar_supercharger(84.0, 108.0, 236.0, 30.0, 48.0, 123.0, 48.0, 123.0)}'
            )
        elif adm == "Biturbo":
            admissao_vw = (
                f'<path d="M 185,24 L 24,24 L 24,86" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 185,222 L 24,222 L 24,160" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<line x1="34" y1="123" x2="82" y2="123" stroke="url(#eng-pipe)" stroke-width="4.5" />\n'
                f'{desenhar_intercooler(14.0, 86.0, 20.0, 74.0, True)}'
                f'<rect x="78" y="109" width="250" height="28" rx="6" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'<rect x="94" y="121.5" width="218" height="3" rx="1.5" fill="url(#eng-accent)" />\n'
                f'{desenhar_turbo(212.0, 24.0, 1.22)}'
                f'{desenhar_turbo(212.0, 222.0, 1.22)}'
            )
        else:  # Twincharge
            admissao_vw = (
                f'<path d="M 185,24 L 24,24 L 24,86" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" stroke-linejoin="round" />\n'
                f'<path d="M 24,160 L 24,226 L 348,226 L 348,123 L 318,123" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" stroke-linejoin="round" />\n'
                f'{desenhar_intercooler(14.0, 86.0, 20.0, 74.0, True)}'
                f'{desenhar_turbo(212.0, 24.0, 1.22)}'
                f'{desenhar_supercharger(84.0, 108.0, 236.0, 30.0, 48.0, 123.0, 48.0, 123.0)}'
            )

        corpo_svg = f"""
        {escapes}
        <rect x="82" y="{y_col_sup:.1f}" width="240" height="6.5" rx="3" fill="#1a100e" stroke="#ea580c" stroke-width="1" />
        <rect x="82" y="{y_col_inf:.1f}" width="240" height="6.5" rx="3" fill="#1a100e" stroke="#ea580c" stroke-width="1" />
        <path d="M 39,77 L 64,61 L 64,185 L 39,169 Z" fill="#0d1017" stroke="#475569" stroke-width="1.2" />
        {desenhar_polia(48.0, 80.0, 8.2)}
        {desenhar_polia(48.0, 166.0, 8.2)}
        <rect x="342" y="91" width="11" height="64" rx="3" fill="#1e293b" stroke="#64748b" stroke-width="1.2" />
        <rect x="64" y="{bank_sup_y:.1f}" width="276" height="{bank_sup_h:.1f}" rx="9" fill="url(#eng-block)" stroke="#64748b" stroke-width="1.5" />
        <rect x="64" y="{bank_inf_y:.1f}" width="276" height="{bank_inf_h:.1f}" rx="9" fill="url(#eng-block)" stroke="#64748b" stroke-width="1.5" />
        <rect x="76" y="{bank_sup_y - 2.5:.1f}" width="252" height="3" rx="1.5" fill="url(#eng-accent)" />
        <rect x="76" y="{bank_inf_y + bank_inf_h - 0.5:.1f}" width="252" height="3" rx="1.5" fill="url(#eng-accent)" />
        <rect x="64" y="105" width="276" height="36" fill="#080a0f" stroke="rgba(255,255,255,0.06)" stroke-width="0.9" />
        <line x1="54" y1="123" x2="342" y2="123" stroke="#475569" stroke-width="4" stroke-linecap="round" />
        {cilindros}
        {admissao_vw}
        {desenhar_polia(48.0, 123.0, 9.8, "#ff9f1c" if adm in ("Supercompressor", "Twincharge") else "#ff1e38")}
        """

    return f"""
    <svg class="motor-svg" viewBox="0 0 400 246" xmlns="http://www.w3.org/2000/svg"
         aria-label="Motor {formato} {adm} 2D">
        {SVG_MOTOR_DEFS}
        {corpo_svg}
    </svg>
    """


def widget_motor_inline(
    num_cilindros: int = 4,
    formato: str = "I",
    admissao: str = "Atmosférico",
) -> str:
    """
    Gera o Widget 1 com a figura 2D realista do motor (incluindo admissão)
    e exibe exclusivamente o número de cilindros.
    """
    return f"""
    <section class="widget-card widget-visual" id="widget-1">
        <div id="motor-svg-container" class="motor-stage">
            {gerar_svg_motor_inline(num_cilindros, formato, admissao)}
        </div>

        <!-- Exibição EXCLUSIVA do número de cilindros -->
        <div class="cilindros-box">
            <span class="cilindros-numero" id="motor-num-cilindros">{num_cilindros}</span>
            <span class="cilindros-texto">CILINDROS</span>
        </div>
    </section>
    """


# ==============================================================================
# WIDGET 2: 5 MOTORES PREDEFINIDOS FAMOSOS
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
    "Twincharge": {
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
                <div class="quiz-header-brand">
                    <div class="topbar-icon" aria-hidden="true">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z" />
                            <line x1="4" y1="22" x2="4" y2="15" />
                        </svg>
                    </div>
                    <div class="quiz-header-info">
                        <div class="quiz-titulo-linha">
                            <h2 id="quiz-titulo">QUIZ AUTOMÓVEL</h2>
                            <span class="widget-badge badge-live">TRACK CHALLENGE // {QUIZ_NUM_PERGUNTAS} PERGUNTAS</span>
                        </div>
                        <div class="quiz-progresso-wrap">
                            <span class="quiz-progresso" id="quiz-progresso">Respondidas: 0 / {QUIZ_NUM_PERGUNTAS}</span>
                            <div class="quiz-progresso-barra">
                                <div class="quiz-progresso-fill" id="quiz-progresso-fill"></div>
                            </div>
                        </div>
                    </div>
                </div>
                <button type="button" class="btn-cyber-acao btn-quiz-sec" id="btn-fechar-quiz">VOLTAR AO PAINEL</button>
            </header>

            <div class="quiz-resultado-banner" id="quiz-resultado-banner" style="display: none;"></div>

            <form id="quiz-form" class="quiz-lista" onsubmit="return false;">
                <div id="quiz-perguntas-container" class="quiz-lista"></div>

                <div class="quiz-acoes-footer">
                    <button type="submit" class="btn-cyber-acao btn-destaque" id="btn-submeter-quiz">
                        VERIFICAR RESPOSTAS
                    </button>
                    <button type="button" class="btn-cyber-acao btn-quiz-sec" id="btn-reiniciar-quiz">
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
    w1 = widget_motor_inline(num_cilindros, formato, admissao)
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
    <link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            color-scheme: dark;
            --bg-base: #050608;
            --bg-elevated: rgba(12, 13, 18, 0.92);
            --bg-surface: rgba(16, 18, 25, 0.95);
            --bg-surface-hover: rgba(28, 30, 40, 0.96);
            --border-subtle: rgba(255, 255, 255, 0.1);
            --border-red: rgba(255, 30, 56, 0.55);
            --text-primary: #f8fafc;
            --text-secondary: #9ca3af;
            --text-muted: #6b7280;
            --accent-red: #ff1e38;
            --accent-red-bright: #ff4d63;
            --accent-amber: #ff9f1c;
            --accent-emerald: #00e676;
            --accent-warn: #ffb800;
            --radius-lg: 8px;
            --radius-md: 5px;
            --shadow-card: 0 24px 50px -18px rgba(0, 0, 0, 0.92), inset 0 1px 0 rgba(255, 255, 255, 0.06);
            --font-sans: 'Chakra Petch', 'Segoe UI Variable', system-ui, -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', 'Cascadia Code', 'Consolas', monospace;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        /* Base do site: Dark Motorsport / Carbon Aggressive */
        body {{
            background-color: var(--bg-base);
            background-image:
                radial-gradient(circle at 12% 8%, rgba(255, 30, 56, 0.18), transparent 36%),
                radial-gradient(circle at 88% 12%, rgba(255, 107, 0, 0.13), transparent 38%),
                radial-gradient(circle at 50% 96%, rgba(255, 30, 56, 0.09), transparent 44%),
                repeating-linear-gradient(
                    -45deg,
                    rgba(255, 255, 255, 0.014) 0px,
                    rgba(255, 255, 255, 0.014) 2px,
                    transparent 2px,
                    transparent 7px
                );
            color: var(--text-primary);
            font-family: var(--font-sans);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 24px;
            position: relative;
            overflow-x: hidden;
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
            margin-bottom: 18px;
            padding: 13px 20px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            border-left: 4px solid var(--accent-red);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-card);
        }}

        .topbar-brand {{
            display: flex;
            align-items: center;
            gap: 13px;
        }}

        .topbar-icon {{
            width: 40px;
            height: 40px;
            border-radius: 6px;
            background: linear-gradient(135deg, rgba(255, 30, 56, 0.25), rgba(255, 107, 0, 0.18));
            border: 1px solid rgba(255, 30, 56, 0.55);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--accent-red-bright);
            flex-shrink: 0;
            box-shadow: 0 0 18px -4px rgba(255, 30, 56, 0.55);
        }}

        .topbar-textos {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}

        .topbar-titulo {{
            font-size: 1.15rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: var(--text-primary);
            line-height: 1.15;
            text-transform: uppercase;
        }}

        .topbar-subtitulo {{
            font-family: var(--font-mono);
            font-size: 0.67rem;
            font-weight: 700;
            letter-spacing: 0.16em;
            color: var(--accent-red-bright);
            text-transform: uppercase;
        }}

        .btn-cyber-acao {{
            background: #11131a;
            color: var(--text-primary);
            border: 1px solid rgba(255, 255, 255, 0.22);
            border-radius: var(--radius-md);
            padding: 10px 18px;
            font-family: var(--font-sans);
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease, background-color 0.15s ease;
        }}

        .btn-cyber-acao:hover {{
            border-color: var(--accent-red);
            background: #1b1e28;
            transform: translateY(-1px);
            box-shadow: 0 8px 22px -8px rgba(255, 30, 56, 0.65);
        }}

        .btn-cyber-acao:active {{
            transform: translateY(0);
        }}

        .btn-quiz-cta,
        .btn-destaque {{
            background: linear-gradient(135deg, #ff1e38 0%, #ff6b00 100%);
            color: #ffffff;
            border: none;
            clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
            border-radius: 0;
            padding: 11px 22px;
            box-shadow: 0 10px 28px -8px rgba(255, 30, 56, 0.72);
        }}

        .btn-quiz-cta:hover,
        .btn-destaque:hover {{
            background: linear-gradient(135deg, #ff3850 0%, #ff851b 100%);
            color: #ffffff;
            box-shadow: 0 14px 32px -6px rgba(255, 30, 56, 0.9);
        }}

        /* Grelha principal para os 3 widgets */
        .dashboard-container {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 18px;
            width: 100%;
            max-width: 1240px;
        }}

        /* Cartão de cada widget com estilo agressivo de pista */
        .widget-card {{
            position: relative;
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            border-top: 2px solid rgba(255, 30, 56, 0.75);
            border-radius: var(--radius-lg);
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            min-height: 400px;
            gap: 15px;
            box-shadow: var(--shadow-card);
            transition: border-color 0.18s ease, box-shadow 0.18s ease;
        }}

        .widget-card:hover {{
            border-color: rgba(255, 255, 255, 0.22);
            border-top-color: var(--accent-red);
            box-shadow: 0 24px 52px -18px rgba(0, 0, 0, 0.95), 0 0 24px -14px rgba(255, 30, 56, 0.55);
        }}

        .widget-header {{
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            padding-bottom: 11px;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .ficha-titulo {{
            font-size: 0.9rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            color: var(--text-primary);
            text-transform: uppercase;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}

        .widget-header .ficha-titulo::before {{
            content: '';
            width: 4px;
            height: 14px;
            background: var(--accent-red);
            transform: skewX(-18deg);
            display: inline-block;
        }}

        .widget-badge {{
            font-family: var(--font-mono);
            font-size: 0.64rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            padding: 4px 8px;
            border-radius: 3px;
            background: rgba(255, 255, 255, 0.06);
            color: var(--text-secondary);
            border: 1px solid rgba(255, 255, 255, 0.14);
            white-space: nowrap;
        }}

        .widget-badge.badge-live {{
            color: var(--accent-red-bright);
            background: rgba(255, 30, 56, 0.14);
            border-color: rgba(255, 30, 56, 0.45);
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        .widget-badge.badge-live::before {{
            content: '';
            width: 6px;
            height: 6px;
            border-radius: 99px;
            background: var(--accent-red);
            box-shadow: 0 0 8px var(--accent-red);
            animation: pulseRed 1.4s infinite ease-in-out;
        }}

        @keyframes pulseRed {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.4; transform: scale(0.8); }}
        }}

        /* Widget 1: Banco de Ensaio + Contador Exclusivo de Cilindros */
        .widget-visual {{
            justify-content: space-between;
        }}

        .motor-stage {{
            width: 100%;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 14px 10px;
            border-radius: 6px;
            background-color: #06070a;
            background-image:
                linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 18px 18px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: inset 0 0 36px rgba(0, 0, 0, 0.85);
        }}

        .motor-svg {{
            width: 100%;
            max-width: 360px;
            height: auto;
            filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.75));
            transition: transform 0.22s ease;
        }}

        /* Exibição exclusiva do número de cilindros (Widget 1) */
        .cilindros-box {{
            width: 100%;
            background: linear-gradient(135deg, #101219 0%, #19131a 100%);
            border: 1px solid rgba(255, 30, 56, 0.42);
            border-left: 4px solid var(--accent-red);
            border-radius: 6px;
            padding: 11px 22px;
            text-align: center;
            display: flex;
            align-items: baseline;
            justify-content: center;
            gap: 12px;
            box-shadow: inset 0 0 22px rgba(255, 30, 56, 0.08);
        }}

        .cilindros-numero {{
            font-family: var(--font-mono);
            font-size: 2.6rem;
            font-weight: 700;
            line-height: 1;
            font-variant-numeric: tabular-nums;
            background: linear-gradient(180deg, #ffffff 30%, #ff4d63 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }}

        .cilindros-texto {{
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.22em;
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
            gap: 9px;
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
            font-size: 0.67rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            color: var(--text-secondary);
            text-transform: uppercase;
        }}

        .input-cyber {{
            background-color: #06070b;
            color: var(--text-primary);
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: var(--radius-md);
            padding: 9px 10px;
            font-family: var(--font-mono);
            font-size: 0.82rem;
            outline: none;
            width: 100%;
            transition: border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease;
        }}

        select.input-cyber {{
            font-family: var(--font-sans);
            font-weight: 600;
            appearance: none;
            -webkit-appearance: none;
            padding-right: 30px;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%23ff4d63' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 10px center;
            cursor: pointer;
        }}

        select.input-cyber option {{
            background-color: #090b10;
            color: #f8fafc;
        }}

        .btn-cyber-acao:focus-visible,
        .btn-preset-motor:focus-visible,
        .quiz-opcao:focus-within {{
            outline: 2px solid var(--accent-red);
            outline-offset: 2px;
        }}

        .input-cyber:hover {{
            border-color: rgba(255, 255, 255, 0.34);
        }}

        .input-cyber:focus {{
            border-color: var(--accent-red);
            background-color: #0b0d14;
            box-shadow: 0 0 0 3px rgba(255, 30, 56, 0.22);
        }}

        .input-cyber.input-alerta {{
            border-color: var(--accent-red);
            background-color: rgba(255, 30, 56, 0.18);
            color: #ff8fa3;
            font-weight: 700;
            box-shadow: 0 0 0 3px rgba(255, 30, 56, 0.25);
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
            background: rgba(255, 30, 56, 0.15);
            border: 1px solid rgba(255, 30, 56, 0.55);
            border-left: 3px solid var(--accent-red);
            color: #ffb3c0;
            font-weight: 600;
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
            gap: 8px;
        }}

        .btn-preset-motor {{
            position: relative;
            background: #08090e;
            color: var(--text-primary);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 6px;
            padding: 11px 14px 11px 18px;
            text-align: left;
            font-family: var(--font-sans);
            cursor: pointer;
            display: flex;
            flex-direction: column;
            gap: 3px;
            overflow: hidden;
            transition: transform 0.15s ease, border-color 0.15s ease, background-color 0.15s ease, box-shadow 0.15s ease;
        }}

        .btn-preset-motor::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: rgba(255, 255, 255, 0.18);
            transition: background-color 0.15s ease, box-shadow 0.15s ease;
        }}

        .btn-preset-motor:hover {{
            border-color: rgba(255, 30, 56, 0.6);
            background: #14161f;
            transform: translateX(2px);
        }}

        .btn-preset-motor:hover::before {{
            background: var(--accent-red);
        }}

        .btn-preset-motor.ativo {{
            background: linear-gradient(135deg, rgba(255, 30, 56, 0.24), rgba(255, 107, 0, 0.15));
            border-color: var(--accent-red);
            box-shadow: 0 8px 24px -12px rgba(255, 30, 56, 0.85);
        }}

        .btn-preset-motor.ativo::before {{
            background: var(--accent-amber);
            box-shadow: 0 0 12px rgba(255, 159, 28, 0.9);
        }}

        .preset-nome {{
            font-size: 0.88rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            color: var(--text-primary);
        }}

        .preset-resumo {{
            font-family: var(--font-mono);
            font-size: 0.68rem;
            color: var(--text-secondary);
        }}

        .btn-preset-motor.ativo .preset-resumo {{
            color: #fed7aa;
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
            margin-top: 18px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            border-top: 2px solid var(--accent-red);
            border-radius: var(--radius-lg);
            padding: 18px 22px;
            box-shadow: var(--shadow-card);
        }}

        .ficha-tecnica-inferior {{
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 13px;
        }}

        .ficha-tecnica-inferior .ficha-titulo {{
            display: flex;
            align-items: center;
            gap: 9px;
        }}

        .ficha-tecnica-inferior .ficha-titulo::before {{
            content: '';
            width: 8px;
            height: 8px;
            background: var(--accent-red);
            transform: rotate(45deg);
            box-shadow: 0 0 12px var(--accent-red);
        }}

        .ficha-itens-grid {{
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 11px;
        }}

        .ficha-item {{
            background: #07080d;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-bottom: 2px solid rgba(255, 255, 255, 0.14);
            border-radius: 6px;
            padding: 12px 14px;
            display: flex;
            flex-direction: column;
            gap: 5px;
            transition: border-color 0.16s ease, transform 0.16s ease;
        }}

        .ficha-item:hover {{
            border-color: rgba(255, 30, 56, 0.45);
            transform: translateY(-1px);
        }}

        .ficha-item span {{
            font-size: 0.66rem;
            font-weight: 700;
            color: var(--text-secondary);
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }}

        .ficha-item strong {{
            font-family: var(--font-mono);
            font-size: 1.02rem;
            font-weight: 700;
            color: var(--text-primary);
            font-variant-numeric: tabular-nums;
        }}

        .ficha-item:nth-child(4) {{
            border-bottom-color: var(--accent-amber);
        }}

        .ficha-item:nth-child(4) strong {{
            color: var(--accent-amber);
        }}

        .ficha-item:nth-child(5) {{
            border-bottom-color: var(--accent-red);
        }}

        .ficha-item:nth-child(5) strong {{
            color: var(--accent-red-bright);
            text-shadow: 0 0 14px rgba(255, 30, 56, 0.4);
        }}

        /* Modal do Quiz (5 Perguntas Aleatórias - Estilo Pista / Carbon) */
        .quiz-modal {{
            position: fixed;
            inset: 0;
            background-color: rgba(3, 4, 6, 0.88);
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
            background-color: #07080d;
            background-image:
                radial-gradient(circle at 8% 4%, rgba(255, 30, 56, 0.16), transparent 36%),
                radial-gradient(circle at 92% 8%, rgba(255, 107, 0, 0.12), transparent 36%),
                repeating-linear-gradient(
                    -45deg,
                    rgba(255, 255, 255, 0.014) 0px,
                    rgba(255, 255, 255, 0.014) 2px,
                    transparent 2px,
                    transparent 7px
                );
            border: 1px solid rgba(255, 255, 255, 0.14);
            border-top: 3px solid var(--accent-red);
            border-left: 4px solid var(--accent-red);
            border-radius: var(--radius-lg);
            width: 100%;
            max-width: 880px;
            max-height: 90vh;
            overflow-y: auto;
            padding: 22px 24px;
            display: flex;
            flex-direction: column;
            gap: 18px;
            box-shadow: 0 32px 72px -15px rgba(0, 0, 0, 0.96), 0 0 42px -16px rgba(255, 30, 56, 0.52);
            animation: modalEntrar 0.2s ease-out;
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
            background: #050608;
        }}

        .quiz-container::-webkit-scrollbar-thumb {{
            background: rgba(255, 30, 56, 0.5);
            border-radius: 3px;
        }}

        .quiz-header {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 14px;
            padding-bottom: 14px;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .quiz-header-brand {{
            display: flex;
            align-items: center;
            gap: 13px;
            flex: 1;
            min-width: 260px;
        }}

        .quiz-header-info {{
            display: flex;
            flex-direction: column;
            gap: 7px;
            flex: 1;
        }}

        .quiz-titulo-linha {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
        }}

        .quiz-header h2 {{
            font-size: 1.08rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            color: var(--text-primary);
            text-transform: uppercase;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}

        .quiz-header h2::before {{
            content: '';
            width: 4px;
            height: 15px;
            background: var(--accent-red);
            transform: skewX(-18deg);
            display: inline-block;
        }}

        .quiz-progresso-wrap {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .quiz-progresso {{
            font-family: var(--font-mono);
            font-size: 0.72rem;
            font-weight: 700;
            color: var(--text-secondary);
            letter-spacing: 0.06em;
            text-transform: uppercase;
            white-space: nowrap;
        }}

        .quiz-progresso-barra {{
            flex: 1;
            max-width: 220px;
            height: 7px;
            border-radius: 2px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.1);
            overflow: hidden;
        }}

        .quiz-progresso-fill {{
            width: 0%;
            height: 100%;
            background: linear-gradient(90deg, var(--accent-red), var(--accent-amber));
            box-shadow: 0 0 12px rgba(255, 30, 56, 0.65);
            transition: width 0.25s ease;
        }}

        .btn-quiz-sec {{
            clip-path: polygon(8px 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%, 0 8px);
            border-radius: 0;
            background: #141720;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 10px 18px;
        }}

        .btn-quiz-sec:hover {{
            background: #1d212e;
            border-color: var(--accent-red);
        }}

        .quiz-resultado-banner {{
            border: 1px solid var(--border-red);
            border-left: 4px solid var(--accent-red);
            border-radius: 6px;
            background-color: #0d0f16;
            padding: 14px 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            font-size: 0.92rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .quiz-lista {{
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}

        .quiz-pergunta-box {{
            border: 1px solid var(--border-subtle);
            border-top: 2px solid rgba(255, 30, 56, 0.6);
            border-radius: var(--radius-lg);
            background: rgba(12, 13, 19, 0.94);
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            box-shadow: 0 12px 28px -16px rgba(0, 0, 0, 0.85);
            transition: border-color 0.16s ease;
        }}

        .quiz-pergunta-box:hover {{
            border-color: rgba(255, 255, 255, 0.2);
            border-top-color: var(--accent-red);
        }}

        .quiz-pergunta-topo {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }}

        .quiz-num-badge {{
            font-family: var(--font-mono);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: var(--accent-red-bright);
            background: rgba(255, 30, 56, 0.14);
            border: 1px solid rgba(255, 30, 56, 0.45);
            border-left: 3px solid var(--accent-red);
            padding: 3px 8px;
            border-radius: 3px;
            flex-shrink: 0;
            margin-top: 1px;
        }}

        .quiz-pergunta-texto {{
            font-size: 0.95rem;
            line-height: 1.45;
            color: var(--text-primary);
            font-weight: 700;
            letter-spacing: 0.01em;
        }}

        .quiz-opcoes-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 9px;
        }}

        .quiz-opcao {{
            position: relative;
            display: flex;
            align-items: center;
            gap: 10px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 6px;
            background: #08090e;
            color: var(--text-primary);
            padding: 10px 12px 10px 15px;
            font-size: 0.83rem;
            line-height: 1.35;
            cursor: pointer;
            overflow: hidden;
            transition: background-color 0.15s ease, border-color 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
        }}

        .quiz-opcao::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: rgba(255, 255, 255, 0.16);
            transition: background-color 0.15s ease, box-shadow 0.15s ease;
        }}

        .quiz-opcao input[type="radio"] {{
            display: none;
        }}

        .quiz-letra {{
            width: 24px;
            height: 24px;
            border-radius: 3px;
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.14);
            color: var(--text-secondary);
            font-family: var(--font-mono);
            font-size: 0.74rem;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
        }}

        .quiz-opcao:hover {{
            border-color: rgba(255, 30, 56, 0.6);
            background: #14161f;
            transform: translateX(2px);
        }}

        .quiz-opcao:hover::before {{
            background: var(--accent-red);
        }}

        .quiz-opcao.selecionada {{
            background: linear-gradient(135deg, rgba(255, 30, 56, 0.24), rgba(255, 107, 0, 0.14));
            border-color: var(--accent-red);
            color: var(--text-primary);
            font-weight: 700;
            box-shadow: 0 8px 22px -12px rgba(255, 30, 56, 0.8);
        }}

        .quiz-opcao.selecionada::before {{
            background: var(--accent-amber);
            box-shadow: 0 0 10px rgba(255, 159, 28, 0.85);
        }}

        .quiz-opcao.selecionada .quiz-letra {{
            background: var(--accent-red);
            border-color: var(--accent-red);
            color: #ffffff;
        }}

        .quiz-opcao.correta {{
            border-color: var(--accent-emerald);
            color: var(--accent-emerald);
            background: rgba(0, 230, 118, 0.13);
            font-weight: 700;
        }}

        .quiz-opcao.correta::before {{
            background: var(--accent-emerald);
        }}

        .quiz-opcao.correta .quiz-letra {{
            background: var(--accent-emerald);
            border-color: var(--accent-emerald);
            color: #050608;
        }}

        .quiz-opcao.errada {{
            border-color: var(--accent-red);
            color: #ff8fa3;
            background: rgba(255, 30, 56, 0.16);
            font-weight: 700;
        }}

        .quiz-opcao.errada::before {{
            background: var(--accent-red);
        }}

        .quiz-opcao.errada .quiz-letra {{
            background: var(--accent-red);
            border-color: var(--accent-red);
            color: #ffffff;
        }}

        .quiz-feedback {{
            font-family: var(--font-mono);
            font-size: 0.74rem;
            font-weight: 700;
            min-height: 1em;
        }}

        .quiz-feedback.ok {{
            color: var(--accent-emerald);
        }}

        .quiz-feedback.erro {{
            color: #ff8fa3;
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
                padding: 14px 12px;
            }}
            .dashboard-container {{
                grid-template-columns: 1fr;
            }}
            .widget-card {{
                min-height: auto;
                padding: 16px;
            }}
            .quiz-container {{
                padding: 16px;
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
                <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2v4M4.9 6.2l2.6 2.6M19.1 6.2l-2.6 2.6M3 13h3M18 13h3" />
                    <path d="M5 19h14a2 2 0 0 0 2-2v-2a9 9 0 1 0-18 0v2a2 2 0 0 0 2 2Z" />
                    <path d="M12 14l4-4" />
                </svg>
            </div>
            <div class="topbar-textos">
                <span class="topbar-titulo">PAINEL DO MOTOR</span>
                <span class="topbar-subtitulo">TRACK TELEMETRY // CUSTOM ENGINE</span>
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

        const SVG_MOTOR_DEFS = `
        <defs>
            <linearGradient id="eng-block" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#171b24" />
                <stop offset="100%" stop-color="#0b0e14" />
            </linearGradient>
            <radialGradient id="eng-piston" cx="38%" cy="35%" r="65%">
                <stop offset="0%" stop-color="#64748b" />
                <stop offset="65%" stop-color="#1e293b" />
                <stop offset="100%" stop-color="#0f172a" />
            </radialGradient>
            <linearGradient id="eng-accent" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stop-color="#ff1e38" />
                <stop offset="100%" stop-color="#ff6b00" />
            </linearGradient>
            <linearGradient id="eng-amber" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stop-color="#ff9f1c" />
                <stop offset="100%" stop-color="#ff6b00" />
            </linearGradient>
            <linearGradient id="eng-pipe" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#94a3b8" />
                <stop offset="100%" stop-color="#475569" />
            </linearGradient>
        </defs>`;

        function desenharCilindroSvg(cx, cy, r) {{
            const rPistao = Math.max(3.4, r * 0.72);
            const rCentro = Math.max(1.3, Math.min(3.2, r * 0.18));
            return `
                <circle cx="${{cx.toFixed(1)}}" cy="${{cy.toFixed(1)}}" r="${{r.toFixed(1)}}" fill="#06080c" stroke="#94a3b8" stroke-width="1.35" />
                <circle cx="${{cx.toFixed(1)}}" cy="${{cy.toFixed(1)}}" r="${{rPistao.toFixed(1)}}" fill="url(#eng-piston)" stroke="#334155" stroke-width="0.8" />
                <circle cx="${{cx.toFixed(1)}}" cy="${{cy.toFixed(1)}}" r="${{rCentro.toFixed(1)}}" fill="#ff1e38" />
            `;
        }}

        function desenharPoliaSvg(cx, cy, r, corCentro = '#ff1e38') {{
            const rIn = Math.max(2.2, r * 0.44);
            return `
                <circle cx="${{cx.toFixed(1)}}" cy="${{cy.toFixed(1)}}" r="${{r.toFixed(1)}}" fill="#0d1017" stroke="#94a3b8" stroke-width="1.3" />
                <circle cx="${{cx.toFixed(1)}}" cy="${{cy.toFixed(1)}}" r="${{rIn.toFixed(1)}}" fill="none" stroke="${{corCentro}}" stroke-width="1.2" />
            `;
        }}

        function desenharParafusosSvg(x, y, w, h, pad = 6.5) {{
            const coords = [
                [x + pad, y + pad],
                [x + w - pad, y + pad],
                [x + pad, y + h - pad],
                [x + w - pad, y + h - pad],
            ];
            return coords
                .map(([px, py]) => `<circle cx="${{px.toFixed(1)}}" cy="${{py.toFixed(1)}}" r="1.3" fill="#475569" />`)
                .join('');
        }}

        function desenharTurboSvg(cx, cy, escala = 1.0) {{
            return `
                <g transform="translate(${{cx.toFixed(1)}},${{cy.toFixed(1)}}) scale(${{escala.toFixed(2)}})">
                    <line x1="-10" y1="0" x2="10" y2="0" stroke="#94a3b8" stroke-width="2" />
                    <rect x="-4" y="-3.5" width="8" height="7" rx="2" fill="#1e293b" stroke="#64748b" stroke-width="0.9" />
                    <circle cx="-11" cy="0" r="10.5" fill="#0f141e" stroke="#e2e8f0" stroke-width="1.3" />
                    <path d="M -11,-5.5 L -11,5.5 M -16.5,0 L -5.5,0" stroke="#64748b" stroke-width="1.1" />
                    <circle cx="-11" cy="0" r="2.2" fill="#ff1e38" />
                    <circle cx="11" cy="0" r="9.5" fill="#180d0c" stroke="#ff6b00" stroke-width="1.3" />
                    <circle cx="11" cy="0" r="4.0" fill="#0b090a" stroke="#ff6b00" stroke-width="0.9" />
                </g>
            `;
        }}

        function desenharIntercoolerSvg(x, y, w, h, vertical = false) {{
            let linhas = '';
            for (let k = 1; k < 4; k++) {{
                if (vertical) {{
                    const ly = y + k * (h / 4.0);
                    linhas += `<line x1="${{(x + 4).toFixed(1)}}" y1="${{ly.toFixed(1)}}" x2="${{(x + w - 4).toFixed(1)}}" y2="${{ly.toFixed(1)}}" stroke="#475569" stroke-width="1" />`;
                }} else {{
                    const lx = x + k * (w / 4.0);
                    linhas += `<line x1="${{lx.toFixed(1)}}" y1="${{(y + 4).toFixed(1)}}" x2="${{lx.toFixed(1)}}" y2="${{(y + h - 4).toFixed(1)}}" stroke="#475569" stroke-width="1" />`;
                }}
            }}
            return `
                <rect x="${{x.toFixed(1)}}" y="${{y.toFixed(1)}}" width="${{w.toFixed(1)}}" height="${{h.toFixed(1)}}" rx="4" fill="#090c12" stroke="#94a3b8" stroke-width="1.3" />
                ${{linhas}}
            `;
        }}

        function desenharFiltroConicoSvg(x, y, w, h) {{
            return `
                <polygon points="${{x.toFixed(1)}},${{(y + 2.5).toFixed(1)}} ${{(x + w).toFixed(1)}},${{y.toFixed(1)}} ${{(x + w).toFixed(1)}},${{(y + h).toFixed(1)}} ${{x.toFixed(1)}},${{(y + h - 2.5).toFixed(1)}}" fill="#190c10" stroke="#ff1e38" stroke-width="1.2" stroke-linejoin="round" />
                <line x1="${{(x + w * 0.45).toFixed(1)}}" y1="${{(y + 3.5).toFixed(1)}}" x2="${{(x + w * 0.45).toFixed(1)}}" y2="${{(y + h - 3.5).toFixed(1)}}" stroke="#7f1d1d" stroke-width="1" />
            `;
        }}

        function desenharSuperchargerSvg(x, y, w, h, pulleyX, pulleyY, crankX, crankY) {{
            const snoutY = y + h / 2.0;
            const snoutW = Math.max(6.0, x - pulleyX + 2);
            return `
                <line x1="${{pulleyX.toFixed(1)}}" y1="${{pulleyY.toFixed(1)}}" x2="${{crankX.toFixed(1)}}" y2="${{crankY.toFixed(1)}}" stroke="#475569" stroke-width="2.6" />
                <rect x="${{pulleyX.toFixed(1)}}" y="${{(snoutY - 3.5).toFixed(1)}}" width="${{snoutW.toFixed(1)}}" height="7" rx="2" fill="#1e293b" stroke="#64748b" stroke-width="1" />
                <rect x="${{x.toFixed(1)}}" y="${{y.toFixed(1)}}" width="${{w.toFixed(1)}}" height="${{h.toFixed(1)}}" rx="6" fill="#121620" stroke="#cbd5e1" stroke-width="1.3" />
                <rect x="${{(x + 14).toFixed(1)}}" y="${{(snoutY - 2).toFixed(1)}}" width="${{(w - 28).toFixed(1)}}" height="4" rx="2" fill="url(#eng-amber)" />
                ${{desenharPoliaSvg(pulleyX, pulleyY, 7.2, '#ff9f1c')}}
            `;
        }}

        function gerarSvgMotorLocal(cilindros, formato, admissao = 'Atmosférico') {{
            const n = Math.max(1, Math.min(16, cilindros));
            const fmt = ['I', 'V', 'VR', 'W'].includes(formato) ? formato : 'I';
            const adm = ['Atmosférico', 'Turbo', 'Supercompressor', 'Biturbo', 'Twincharge'].includes(admissao) ? admissao : 'Atmosférico';
            let corpo = '';

            if (fmt === 'I' || fmt === 'VR') {{
                const larguraBloco = fmt === 'I' ? 260.0 : 248.0;
                const inicioX = fmt === 'I' ? 72.0 : 78.0;
                const espaco = larguraBloco / n;
                let raio = fmt === 'I'
                    ? Math.min(21.0, Math.max(5.2, (espaco - 4.5) / 2.0))
                    : Math.min(16.0, Math.max(7.0, (espaco * 1.15 - 4.0) / 2.0));
                if (fmt === 'VR' && n >= 10) raio = Math.min(raio, 10.2);
                const swRunner = Math.max(2.2, Math.min(5.5, raio * 0.35));
                let circs = '';
                let coletores = '';
                for (let i = 0; i < n; i++) {{
                    const cx = inicioX + i * espaco + espaco / 2.0;
                    const cy = fmt === 'I' ? 123.0 : (i % 2 === 0 ? 104.0 : 142.0);
                    circs += desenharCilindroSvg(cx, cy, raio);
                    coletores += `<line x1="${{cx.toFixed(1)}}" y1="54" x2="${{cx.toFixed(1)}}" y2="72" stroke="#64748b" stroke-width="${{swRunner.toFixed(1)}}" stroke-linecap="round" />`;
                    coletores += `<line x1="${{cx.toFixed(1)}}" y1="174" x2="${{cx.toFixed(1)}}" y2="192" stroke="#c2410c" stroke-width="${{swRunner.toFixed(1)}}" stroke-linecap="round" />`;
                }}

                let admissaoSvg = '';
                if (adm === 'Atmosférico') {{
                    admissaoSvg = `
                        <rect x="78" y="40" width="248" height="14" rx="5" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />
                        <rect x="90" y="45.5" width="224" height="3" rx="1.5" fill="url(#eng-accent)" />
                        <line x1="54" y1="47" x2="78" y2="47" stroke="#64748b" stroke-width="5" />
                        ${{desenharFiltroConicoSvg(22.0, 38.0, 32.0, 18.0)}}
                        <rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />
                    `;
                }} else if (adm === 'Turbo') {{
                    admissaoSvg = `
                        <path d="M 30,190 L 30,47 L 78,47" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />
                        <path d="M 68,210 L 184,210" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" />
                        ${{desenharIntercoolerSvg(16.0, 194.0, 50.0, 26.0)}}
                        <rect x="78" y="40" width="248" height="14" rx="5" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />
                        <rect x="90" y="45.5" width="224" height="3" rx="1.5" fill="url(#eng-accent)" />
                        <rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />
                        ${{desenharTurboSvg(216.0, 211.0, 1.32)}}
                    `;
                }} else if (adm === 'Supercompressor') {{
                    admissaoSvg = `
                        <rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />
                        <line x1="304" y1="43" x2="328" y2="43" stroke="#64748b" stroke-width="5" />
                        ${{desenharFiltroConicoSvg(328.0, 34.0, 30.0, 18.0)}}
                        ${{desenharSuperchargerSvg(92.0, 30.0, 212.0, 24.0, 48.0, 42.0, 48.0, 123.0)}}
                    `;
                }} else if (adm === 'Biturbo') {{
                    admissaoSvg = `
                        <path d="M 30,190 L 30,47 L 78,47" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />
                        <path d="M 68,210 L 266,210" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" />
                        ${{desenharIntercoolerSvg(16.0, 194.0, 50.0, 26.0)}}
                        <rect x="78" y="40" width="248" height="14" rx="5" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />
                        <rect x="90" y="45.5" width="224" height="3" rx="1.5" fill="url(#eng-accent)" />
                        <rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />
                        ${{desenharTurboSvg(146.0, 211.0, 1.24)}}
                        ${{desenharTurboSvg(282.0, 211.0, 1.24)}}
                    `;
                }} else {{
                    admissaoSvg = `
                        <path d="M 24,190 L 24,38 L 84,38" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" stroke-linejoin="round" />
                        <path d="M 68,210 L 194,210" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" />
                        ${{desenharIntercoolerSvg(14.0, 194.0, 50.0, 26.0)}}
                        <rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />
                        ${{desenharTurboSvg(224.0, 211.0, 1.28)}}
                        ${{desenharSuperchargerSvg(92.0, 30.0, 212.0, 24.0, 48.0, 42.0, 48.0, 123.0)}}
                    `;
                }}

                corpo = `
                    ${{coletores}}
                    ${{admissaoSvg}}
                    <rect x="41" y="84" width="15" height="52" rx="7" fill="#0d1017" stroke="#475569" stroke-width="1.2" />
                    ${{desenharPoliaSvg(48.0, 93.0, 6.4)}}
                    ${{desenharPoliaSvg(48.0, 123.0, 11.4)}}
                    <rect x="342" y="93" width="11" height="60" rx="3" fill="#1e293b" stroke="#64748b" stroke-width="1.2" />
                    <rect x="64" y="70" width="276" height="106" rx="10" fill="url(#eng-block)" stroke="#64748b" stroke-width="1.5" />
                    ${{desenharParafusosSvg(64.0, 70.0, 276.0, 106.0)}}
                    ${{circs}}
                `;
            }} else {{
                const nSup = Math.floor((n + 1) / 2);
                const nInf = Math.floor(n / 2);
                const cols = Math.max(1, nSup, nInf);
                const largura = 244.0;
                const inicioX = 80.0;
                const espacoSup = largura / Math.max(1, nSup);
                const espacoInf = largura / Math.max(1, nInf);

                const raio = fmt === 'V'
                    ? Math.min(15.5, Math.max(5.8, (largura / cols - 6.0) / 2.0))
                    : Math.min(10.8, Math.max(6.6, (largura / cols) * 0.34));
                const bankSupY = fmt === 'V' ? 55.0 : 47.0;
                const bankSupH = fmt === 'V' ? 50.0 : 58.0;
                const bankInfY = 141.0;
                const bankInfH = fmt === 'V' ? 50.0 : 58.0;
                const yExhSup = fmt === 'V' ? 39.0 : 32.0;
                const yExhInf = fmt === 'V' ? 193.0 : 200.0;
                const yColSup = fmt === 'V' ? 38.0 : 31.0;
                const yColInf = fmt === 'V' ? 201.0 : 208.0;

                const swRunner = Math.max(2.0, Math.min(4.8, raio * 0.35));
                let circs = '';
                let escapes = '';
                let trombetas = '';

                for (let i = 0; i < nSup; i++) {{
                    const cx = inicioX + i * espacoSup + espacoSup / 2.0;
                    const cy = fmt === 'V' ? 80.0 : (i % 2 === 0 ? 64.0 : 87.0);
                    circs += desenharCilindroSvg(cx, cy, raio);
                    escapes += `<line x1="${{cx.toFixed(1)}}" y1="${{yExhSup.toFixed(1)}}" x2="${{cx.toFixed(1)}}" y2="${{(yExhSup + 16).toFixed(1)}}" stroke="#c2410c" stroke-width="${{swRunner.toFixed(1)}}" stroke-linecap="round" />`;
                    trombetas += `<circle cx="${{cx.toFixed(1)}}" cy="116" r="${{Math.max(2.2, Math.min(3.4, swRunner * 0.72)).toFixed(1)}}" fill="#ff1e38" opacity="0.85" />`;
                }}
                for (let i = 0; i < nInf; i++) {{
                    const cx = inicioX + i * espacoInf + espacoInf / 2.0;
                    const cy = fmt === 'V' ? 166.0 : (i % 2 === 0 ? 159.0 : 182.0);
                    circs += desenharCilindroSvg(cx, cy, raio);
                    escapes += `<line x1="${{cx.toFixed(1)}}" y1="${{yExhInf.toFixed(1)}}" x2="${{cx.toFixed(1)}}" y2="${{(yExhInf + 16).toFixed(1)}}" stroke="#c2410c" stroke-width="${{swRunner.toFixed(1)}}" stroke-linecap="round" />`;
                    trombetas += `<circle cx="${{cx.toFixed(1)}}" cy="130" r="${{Math.max(2.2, Math.min(3.4, swRunner * 0.72)).toFixed(1)}}" fill="#ff1e38" opacity="0.85" />`;
                }}

                let admissaoVw = '';
                if (adm === 'Atmosférico') {{
                    admissaoVw = `
                        <rect x="78" y="109" width="250" height="28" rx="6" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />
                        ${{trombetas}}
                        <line x1="328" y1="123" x2="352" y2="123" stroke="#64748b" stroke-width="5" />
                        ${{desenharFiltroConicoSvg(352.0, 113.0, 30.0, 20.0)}}
                    `;
                }} else if (adm === 'Turbo') {{
                    admissaoVw = `
                        <path d="M 185,24 L 24,24 L 24,87" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />
                        <path d="M 24,159 L 24,123 L 82,123" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />
                        ${{desenharIntercoolerSvg(14.0, 86.0, 20.0, 74.0, true)}}
                        <rect x="78" y="109" width="250" height="28" rx="6" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />
                        <rect x="94" y="121.5" width="218" height="3" rx="1.5" fill="url(#eng-accent)" />
                        ${{desenharTurboSvg(212.0, 24.0, 1.24)}}
                    `;
                }} else if (adm === 'Supercompressor') {{
                    admissaoVw = `
                        <line x1="318" y1="123" x2="342" y2="123" stroke="#64748b" stroke-width="5" />
                        ${{desenharFiltroConicoSvg(342.0, 113.0, 30.0, 20.0)}}
                        <line x1="48" y1="80" x2="48" y2="166" stroke="#475569" stroke-width="2.6" />
                        ${{desenharSuperchargerSvg(84.0, 108.0, 236.0, 30.0, 48.0, 123.0, 48.0, 123.0)}}
                    `;
                }} else if (adm === 'Biturbo') {{
                    admissaoVw = `
                        <path d="M 185,24 L 24,24 L 24,86" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />
                        <path d="M 185,222 L 24,222 L 24,160" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />
                        <line x1="34" y1="123" x2="82" y2="123" stroke="url(#eng-pipe)" stroke-width="4.5" />
                        ${{desenharIntercoolerSvg(14.0, 86.0, 20.0, 74.0, true)}}
                        <rect x="78" y="109" width="250" height="28" rx="6" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />
                        <rect x="94" y="121.5" width="218" height="3" rx="1.5" fill="url(#eng-accent)" />
                        ${{desenharTurboSvg(212.0, 24.0, 1.22)}}
                        ${{desenharTurboSvg(212.0, 222.0, 1.22)}}
                    `;
                }} else {{
                    admissaoVw = `
                        <path d="M 185,24 L 24,24 L 24,86" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" stroke-linejoin="round" />
                        <path d="M 24,160 L 24,226 L 348,226 L 348,123 L 318,123" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" stroke-linejoin="round" />
                        ${{desenharIntercoolerSvg(14.0, 86.0, 20.0, 74.0, true)}}
                        ${{desenharTurboSvg(212.0, 24.0, 1.22)}}
                        ${{desenharSuperchargerSvg(84.0, 108.0, 236.0, 30.0, 48.0, 123.0, 48.0, 123.0)}}
                    `;
                }}

                corpo = `
                    ${{escapes}}
                    <rect x="82" y="${{yColSup.toFixed(1)}}" width="240" height="6.5" rx="3" fill="#1a100e" stroke="#ea580c" stroke-width="1" />
                    <rect x="82" y="${{yColInf.toFixed(1)}}" width="240" height="6.5" rx="3" fill="#1a100e" stroke="#ea580c" stroke-width="1" />
                    <path d="M 39,77 L 64,61 L 64,185 L 39,169 Z" fill="#0d1017" stroke="#475569" stroke-width="1.2" />
                    ${{desenharPoliaSvg(48.0, 80.0, 8.2)}}
                    ${{desenharPoliaSvg(48.0, 166.0, 8.2)}}
                    <rect x="342" y="91" width="11" height="64" rx="3" fill="#1e293b" stroke="#64748b" stroke-width="1.2" />
                    <rect x="64" y="${{bankSupY.toFixed(1)}}" width="276" height="${{bankSupH.toFixed(1)}}" rx="9" fill="url(#eng-block)" stroke="#64748b" stroke-width="1.5" />
                    <rect x="64" y="${{bankInfY.toFixed(1)}}" width="276" height="${{bankInfH.toFixed(1)}}" rx="9" fill="url(#eng-block)" stroke="#64748b" stroke-width="1.5" />
                    <rect x="76" y="${{(bankSupY - 2.5).toFixed(1)}}" width="252" height="3" rx="1.5" fill="url(#eng-accent)" />
                    <rect x="76" y="${{(bankInfY + bankInfH - 0.5).toFixed(1)}}" width="252" height="3" rx="1.5" fill="url(#eng-accent)" />
                    <rect x="64" y="105" width="276" height="36" fill="#080a0f" stroke="rgba(255,255,255,0.06)" stroke-width="0.9" />
                    <line x1="54" y1="123" x2="342" y2="123" stroke="#475569" stroke-width="4" stroke-linecap="round" />
                    ${{circs}}
                    ${{admissaoVw}}
                    ${{desenharPoliaSvg(48.0, 123.0, 9.8, (adm === 'Supercompressor' || adm === 'Twincharge') ? '#ff9f1c' : '#ff1e38')}}
                `;
            }}
            return `<svg class="motor-svg" viewBox="0 0 400 246" xmlns="http://www.w3.org/2000/svg" aria-label="Motor ${{fmt}} ${{adm}} 2D">${{SVG_MOTOR_DEFS}}${{corpo}}</svg>`;
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
                'Twincharge': {{ pressao: '+2.0 bar', mp: 1.90, mb: 1.95 }}
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
            const admissao = selectAdmissao.value || 'Atmosférico';

            try {{
                const res = await fetch('/api/ficha', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ cilindros, formato, admissao }})
                }});
                if (res.ok) {{
                    const data = await res.json();
                    motorSvgContainer.innerHTML = data.motor_svg;
                    motorNumCilindros.textContent = data.cilindros;
                    atualizarWidget3();
                    return;
                }}
            }} catch (_) {{}}

            motorSvgContainer.innerHTML = gerarSvgMotorLocal(cilindros, formato, admissao);
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
                        <div class="quiz-pergunta-topo">
                            <span class="quiz-num-badge">Q0${{numeroIdx + 1}}</span>
                            <p class="quiz-pergunta-texto">${{escaparHtmlQuiz(q.pergunta)}}</p>
                        </div>
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
            let corBanner = '#FF1E38';
            let fundoBanner = 'rgba(255, 30, 56, 0.16)';
            if (resultado.percentagem >= 70) {{
                corBanner = '#00E676';
                fundoBanner = 'rgba(0, 230, 118, 0.14)';
            }} else if (resultado.percentagem >= 50) {{
                corBanner = '#FFB800';
                fundoBanner = 'rgba(255, 184, 0, 0.15)';
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
            adm = str(dados.get("admissao", "Atmosférico"))

            resposta = json.dumps({
                "cilindros": cil,
                "formato": fmt,
                "admissao": adm,
                "motor_svg": gerar_svg_motor_inline(cil, fmt, adm),
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
