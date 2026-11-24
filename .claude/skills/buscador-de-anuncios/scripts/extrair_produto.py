#!/usr/bin/env python3
"""Extrai dados estruturados de páginas de produto (JSON-LD schema.org + meta tags).

A maioria dos e-commerces embute um bloco JSON-LD do tipo "Product" com nome,
marca, modelo/SKU, preço, moeda, disponibilidade, condição, vendedor e nota média.
Este script baixa a página e devolve esses campos em JSON, mais o título e um
trecho do texto visível, para conferência rápida de vários anúncios.

Uso:
    python3 extrair_produto.py URL [URL ...]
    python3 extrair_produto.py --arquivo pagina.html     # HTML já salvo (ex.: pelo navegador)

Só usa a biblioteca padrão. Lojas que bloqueiam robôs (captcha, 403) ou que
montam a página via JavaScript devolvem "bloqueado"/"sem_dados": nesses casos
abra a página com um navegador (Playwright/ferramenta de browser), salve o HTML
e rode de novo com --arquivo, ou leia a página com outra ferramenta.
"""
import argparse
import gzip
import html
import json
import re
import sys
import urllib.error
import urllib.request
import zlib

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

SINAIS_BLOQUEIO = ("captcha", "robot check", "are you a human", "access denied",
                   "verifique que você é humano", "acesso negado", "unusual traffic")


def baixar(url: str, timeout: int = 25) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.6",
        "Accept-Encoding": "gzip, deflate",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            dados = r.read()
            enc = (r.headers.get("Content-Encoding") or "").lower()
            if enc == "gzip":
                dados = gzip.decompress(dados)
            elif enc == "deflate":
                dados = zlib.decompress(dados)
            charset = r.headers.get_content_charset() or "utf-8"
            return r.status, dados.decode(charset, errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, ""


def _iter_nos(obj):
    """Percorre JSON-LD aninhado (@graph, listas, objetos)."""
    if isinstance(obj, list):
        for o in obj:
            yield from _iter_nos(o)
    elif isinstance(obj, dict):
        yield obj
        for k in ("@graph", "mainEntity", "itemListElement", "item"):
            if k in obj:
                yield from _iter_nos(obj[k])


def _tipo(no) -> list[str]:
    t = no.get("@type", [])
    return [t] if isinstance(t, str) else list(t)


def _nome(v):
    if isinstance(v, dict):
        return v.get("name") or v.get("@id")
    if isinstance(v, list):
        return ", ".join(filter(None, (_nome(x) for x in v)))
    return v


def _curto(v):
    """'https://schema.org/InStock' -> 'InStock'."""
    if isinstance(v, str) and "schema.org/" in v:
        return v.rsplit("/", 1)[-1]
    return v


def extrair_jsonld(texto: str) -> list[dict]:
    produtos = []
    for bloco in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
                            texto, flags=re.S | re.I):
        try:
            dados = json.loads(html.unescape(bloco.strip()))
        except json.JSONDecodeError:
            continue
        for no in _iter_nos(dados):
            if "Product" not in _tipo(no) and "ProductGroup" not in _tipo(no):
                continue
            ofertas = no.get("offers") or {}
            ofertas_lista = []
            for of in _iter_nos(ofertas):
                if not any(t in _tipo(of) for t in ("Offer", "AggregateOffer")) and "price" not in of:
                    continue
                ofertas_lista.append({
                    "preco": of.get("price") or of.get("lowPrice"),
                    "preco_max": of.get("highPrice"),
                    "moeda": of.get("priceCurrency"),
                    "disponibilidade": _curto(of.get("availability")),
                    "condicao": _curto(of.get("itemCondition")),
                    "vendedor": _nome(of.get("seller")),
                    "url": of.get("url"),
                    "qtd_ofertas": of.get("offerCount"),
                })
            nota = no.get("aggregateRating") or {}
            produtos.append({
                "nome": no.get("name"),
                "marca": _nome(no.get("brand")),
                "modelo": no.get("model") if isinstance(no.get("model"), str) else _nome(no.get("model")),
                "sku": no.get("sku"),
                "gtin": no.get("gtin13") or no.get("gtin") or no.get("gtin12"),
                "condicao": _curto(no.get("itemCondition")),
                "nota_media": nota.get("ratingValue"),
                "num_avaliacoes": nota.get("reviewCount") or nota.get("ratingCount"),
                "ofertas": ofertas_lista,
                "descricao": (no.get("description") or "")[:600] or None,
            })
    return produtos


def extrair_meta(texto: str) -> dict:
    meta = {}
    for m in re.finditer(r'<meta\s+[^>]*>', texto, flags=re.I):
        tag = m.group(0)
        chave = re.search(r'(?:property|name|itemprop)=["\']([^"\']+)["\']', tag, flags=re.I)
        valor = re.search(r'content=["\']([^"\']*)["\']', tag, flags=re.I)
        if not chave or not valor:
            continue
        k = chave.group(1).lower()
        if k in ("og:title", "og:description", "og:url", "og:price:amount", "og:price:currency",
                 "product:price:amount", "product:price:currency", "product:availability",
                 "product:condition", "price", "pricecurrency", "availability", "twitter:data1"):
            meta[k] = html.unescape(valor.group(1))
    return meta


def texto_visivel(texto: str, limite: int = 1500) -> str:
    t = re.sub(r"<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", texto, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(re.sub(r"\s+", " ", t)).strip()
    return t[:limite]


def analisar(texto: str, origem: str, status: int | None = None) -> dict:
    titulo = re.search(r"<title[^>]*>(.*?)</title>", texto, flags=re.S | re.I)
    res = {
        "origem": origem,
        "status_http": status,
        "titulo": html.unescape(titulo.group(1).strip()) if titulo else None,
        "produtos_jsonld": extrair_jsonld(texto),
        "meta": extrair_meta(texto),
    }
    baixo = texto.lower()
    if status and status >= 400:
        res["situacao"] = "bloqueado" if status in (401, 403, 429, 503) else "erro"
    elif any(s in baixo for s in SINAIS_BLOQUEIO) and not res["produtos_jsonld"]:
        res["situacao"] = "bloqueado"
    elif res["produtos_jsonld"] or any(k.endswith("price:amount") for k in res["meta"]):
        res["situacao"] = "ok"
    else:
        res["situacao"] = "sem_dados"
        res["trecho_texto"] = texto_visivel(texto)
    return res


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("urls", nargs="*", help="URLs de anúncios")
    p.add_argument("--arquivo", action="append", default=[], help="arquivo HTML local (pode repetir)")
    p.add_argument("--texto", action="store_true", help="incluir trecho do texto visível mesmo quando há dados")
    a = p.parse_args()
    if not a.urls and not a.arquivo:
        p.error("informe ao menos uma URL ou --arquivo")

    resultados = []
    for url in a.urls:
        try:
            status, texto = baixar(url)
            r = analisar(texto, url, status)
        except Exception as e:  # rede, timeout, DNS, proxy
            r = {"origem": url, "situacao": "erro", "erro": f"{type(e).__name__}: {e}"}
        else:
            if a.texto and texto:
                r["trecho_texto"] = texto_visivel(texto)
        resultados.append(r)
    for caminho in a.arquivo:
        with open(caminho, encoding="utf-8", errors="replace") as f:
            texto = f.read()
        r = analisar(texto, caminho)
        if a.texto:
            r["trecho_texto"] = texto_visivel(texto)
        resultados.append(r)

    json.dump(resultados, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
