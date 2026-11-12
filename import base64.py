import base64
from pathlib import Path


def get_base64_image(image_path: str) -> str:
    """Converte uma imagem local para string Base64 para usar no CSS."""
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    # Detecta a extensão para o formato MIME correto
    ext = path.suffix.lower().replace(".", "")
    mime = "jpeg" if ext in ["jpg", "jpeg"] else ext

    with open(path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")

    return f"data:image/{mime};base64,{encoded}"


def gerar_css(caminho_imagem_fundo: str) -> str:
    """Gera o bloco CSS com as espypecificações solicitadas."""
    bg_base64 = get_base64_image(caminho_imagem_fundo)

    css = f"""
    <style>
        /* 1. Imagem de fundo cobrindo toda a tela/página */
        body {{
            background-image: url('{bg_base64}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            margin: 0;
            padding: 20px;
        }}

        /* 2. Corpo de texto: Arial, 12pt */
        body, p, span, label, li, td, th {{
            font-family: Arial, sans-serif;
            font-size: 12pt;
        }}

        /* 3. Títulos: Helvetica, Bold, 24pt */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif;
            font-weight: bold;
            font-size: 24pt;
        }}

        /* 4. Caixas de texto: Fundo branco e borda azul de 5pt */
        input[type="text"],
        input[type="password"],
        input[type="email"],
        input[type="number"],
        textarea,
        select,
        .caixa-texto {{
            background-color: #FFFFFF;
            border: 5pt solid #0056b3; /* Azul (ajuste o tom se preferir #0000FF, #1E90FF, etc.) */
            border-radius: 6px;        /* Cantos levemente arredondados (opcional) */
            font-family: Arial, sans-serif;
            font-size: 12pt;
            padding: 8px 12px;
            color: #333333;
            outline: none;
            box-sizing: border-box;
        }}

        /* Destaque ao focar na caixa de texto */
        input[type="text"]:focus,
        textarea:focus {{
            border-color: #003366; /* Azul mais escuro no foco */
        }}
    </style>
    """
    return css