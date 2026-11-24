#!/usr/bin/env python3
"""Gera URLs de busca e consultas `site:` para e-commerces brasileiros.

Uso:
    python3 urls_busca.py "baixo 5 cordas ativo"
    python3 urls_busca.py "iphone 13 128gb" --usado --uf SP
    python3 urls_busca.py "rtx 4060" --categoria hardware
    python3 urls_busca.py "geladeira frost free" --json

Só usa a biblioteca padrão. Não acessa a rede: apenas monta os links.
Padrões de URL das lojas podem mudar; se um link falhar, use a consulta `site:`.
"""
import argparse
import json
import re
import unicodedata
from urllib.parse import quote, quote_plus


def slug(texto: str) -> str:
    """'Baixo 5 Cordas' -> 'baixo-5-cordas' (sem acentos)."""
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t.lower()).strip("-")
    return t


GERAIS = [
    ("Mercado Livre", "mercadolivre.com.br", lambda q: f"https://lista.mercadolivre.com.br/{slug(q)}"),
    ("Mercado Livre (menor preço)", "mercadolivre.com.br",
     lambda q: f"https://lista.mercadolivre.com.br/{slug(q)}_OrderId_PRICE_NoIndex_True"),
    ("Amazon", "amazon.com.br", lambda q: f"https://www.amazon.com.br/s?k={quote_plus(q)}"),
    ("Magalu", "magazineluiza.com.br", lambda q: f"https://www.magazineluiza.com.br/busca/{quote_plus(q)}/"),
    ("Shopee", "shopee.com.br", lambda q: f"https://shopee.com.br/search?keyword={quote_plus(q)}"),
    ("Americanas", "americanas.com.br", lambda q: f"https://www.americanas.com.br/busca/{quote(slug(q))}"),
    ("Casas Bahia", "casasbahia.com.br", None),
    ("Carrefour", "carrefour.com.br", None),
    ("Fast Shop", "fastshop.com.br", None),
]

COMPARADORES = [
    ("Google Shopping", None, lambda q: f"https://www.google.com/search?tbm=shop&q={quote_plus(q)}"),
    ("Buscapé", "buscape.com.br", lambda q: f"https://www.buscape.com.br/search?q={quote_plus(q)}"),
    ("Zoom", "zoom.com.br", lambda q: f"https://www.zoom.com.br/search?q={quote_plus(q)}"),
    ("Pelando (promoções)", "pelando.com.br", None),
]

USADOS_BASE = [
    ("Mercado Livre usados", "mercadolivre.com.br",
     lambda q: f"https://lista.mercadolivre.com.br/{slug(q)}_ITEM*CONDITION_2230581"),
    ("Enjoei", "enjoei.com.br", lambda q: f"https://www.enjoei.com.br/s?q={quote_plus(q)}"),
    ("Facebook Marketplace (exige login)", None,
     lambda q: f"https://www.facebook.com/marketplace/search/?query={quote_plus(q)}"),
]

INTERNACIONAL = [
    ("AliExpress", "aliexpress.com", lambda q: f"https://pt.aliexpress.com/w/wholesale-{slug(q)}.html"),
]

ESPECIALIZADAS = {
    "hardware": [
        ("KaBuM", "kabum.com.br", lambda q: f"https://www.kabum.com.br/busca/{slug(q)}"),
        ("Pichau", "pichau.com.br", lambda q: f"https://www.pichau.com.br/search?q={quote_plus(q)}"),
        ("Terabyte", "terabyteshop.com.br", lambda q: f"https://www.terabyteshop.com.br/busca?str={quote_plus(q)}"),
    ],
    "instrumentos": [
        ("Made in Brazil", "madeinbrazil.com.br", None),
        ("Multisom", "multisom.com.br", None),
        ("Mundomax", "mundomax.com.br", None),
        ("Teclacenter", "teclacenter.com.br", None),
    ],
    "casa": [
        ("Leroy Merlin", "leroymerlin.com.br", None),
        ("Telhanorte", "telhanorte.com.br", None),
    ],
    "esportes": [
        ("Centauro", "centauro.com.br", None),
        ("Decathlon", "decathlon.com.br", None),
        ("Netshoes", "netshoes.com.br", None),
    ],
    "livros": [
        ("Estante Virtual (usados)", "estantevirtual.com.br", None),
    ],
    "moda": [
        ("Dafiti", "dafiti.com.br", None),
        ("Zattini", "zattini.com.br", None),
    ],
}
ESPECIALIZADAS["games"] = ESPECIALIZADAS["hardware"]
ESPECIALIZADAS["informatica"] = ESPECIALIZADAS["hardware"]
ESPECIALIZADAS["ferramentas"] = ESPECIALIZADAS["casa"]


def montar(q: str, usado: bool, uf: str | None, categoria: str | None, internacional: bool):
    grupos = {}

    def item(nome, dominio, fn):
        return {
            "loja": nome,
            "url": fn(q) if fn else None,
            "consulta_site": f'site:{dominio} "{q}"' if dominio else None,
        }

    grupos["Marketplaces gerais"] = [item(*l) for l in GERAIS]
    if categoria:
        esp = ESPECIALIZADAS.get(categoria.lower())
        if esp:
            grupos[f"Especializadas ({categoria})"] = [item(*l) for l in esp]
        else:
            grupos[f"Especializadas ({categoria})"] = [{
                "loja": "(categoria sem lista pronta)",
                "url": None,
                "consulta_site": f'lojas especializadas em {categoria} "{q}"',
            }]
    grupos["Comparadores de preço"] = [item(*l) for l in COMPARADORES]

    if usado:
        olx_regiao = f"estado-{uf.lower()}" if uf else "brasil"
        olx = {
            "loja": f"OLX ({uf.upper() if uf else 'Brasil'})",
            "url": f"https://www.olx.com.br/{olx_regiao}?q={quote_plus(q)}",
            "consulta_site": f'site:olx.com.br "{q}"' + (f" {uf.upper()}" if uf else ""),
        }
        grupos["Usados"] = [olx] + [item(*l) for l in USADOS_BASE]

    if internacional:
        grupos["Internacional"] = [item(*l) for l in INTERNACIONAL]

    return grupos


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("termo", help="o que buscar, ex.: 'iphone 13 128gb'")
    p.add_argument("--usado", action="store_true", help="incluir fontes de usados (OLX, ML usados, Enjoei, Marketplace)")
    p.add_argument("--uf", help="sigla do estado para a OLX, ex.: SP, MG, RJ")
    p.add_argument("--categoria", help="hardware, games, informatica, instrumentos, casa, ferramentas, esportes, livros, moda")
    p.add_argument("--internacional", action="store_true", help="incluir AliExpress")
    p.add_argument("--json", action="store_true", help="saída em JSON")
    a = p.parse_args()

    grupos = montar(a.termo, a.usado, a.uf, a.categoria, a.internacional)
    if a.json:
        print(json.dumps(grupos, ensure_ascii=False, indent=2))
        return
    print(f'Busca: "{a.termo}"\n')
    for grupo, itens in grupos.items():
        print(f"## {grupo}")
        for i in itens:
            linha = f"- {i['loja']}"
            if i["url"]:
                linha += f"\n    URL:   {i['url']}"
            if i["consulta_site"]:
                linha += f"\n    Busca: {i['consulta_site']}"
            print(linha)
        print()


if __name__ == "__main__":
    main()
