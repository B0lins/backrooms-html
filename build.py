#!/usr/bin/env python3
"""
Gera uma versao standalone do jogo pra um tema (grupo de amigos) especifico.

Uso: python3 build.py <tema>
Ex:  python3 build.py janta   -> gera backrooms-janta.html

Convencao: cada asset customizavel tem um "nome base" (ex: "villao").
O script procura primeiro em assets/<tema>/<nome-base>.*; se nao achar,
usa o arquivo equivalente em assets/default/.
"""
import base64
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent
TEMPLATE = ROOT / "template" / "backrooms.template.html"
ASSETS = ROOT / "assets"

MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".mp3": "audio/mpeg",
}

# Cada entrada liga um placeholder do template a um "nome base" de arquivo em assets/<tema>/
ASSET_PLACEHOLDERS = {
    "__VILLAIN_IMAGE_DATA_URI__": "villao",
    "__CHASE_AUDIO_DATA_URI__": "perseguicao",
    "__COLLECTIBLE_IMAGE_DATA_URI__": "colecionavel",
    "__JUMPSCARE_AUDIO_DATA_URI__": "jumpscare",
}


def find_asset(theme, base_name):
    for folder in (ASSETS / theme, ASSETS / "default"):
        matches = sorted(folder.glob(base_name + ".*"))
        if matches:
            return matches[0]
    raise FileNotFoundError(
        f"Nenhum arquivo '{base_name}.*' encontrado em assets/{theme}/ nem em assets/default/"
    )


def to_data_uri(path):
    mime = MIME_TYPES.get(path.suffix.lower(), "application/octet-stream")
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def build(theme):
    content = TEMPLATE.read_text(encoding="utf-8")

    for placeholder, base_name in ASSET_PLACEHOLDERS.items():
        asset_path = find_asset(theme, base_name)
        content = content.replace(placeholder, to_data_uri(asset_path))
        print(f"  {base_name}: usando {asset_path.relative_to(ROOT)}")

    out_path = ROOT / f"backrooms-{theme}.html"
    out_path.write_text(content, encoding="utf-8")
    print(f"Gerado: {out_path.name}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 build.py <tema>")
        sys.exit(1)
    build(sys.argv[1])
