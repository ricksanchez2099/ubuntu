# Lojas e fontes de busca

Padrões de URL mudam com o tempo: se uma URL de busca não funcionar, use a busca na web com `site:dominio "termo"` ou entre pela página inicial da loja. O script `scripts/urls_busca.py` gera tudo isso automaticamente.

## Índice
0. Como acessar cada site (o que bloqueia robô)
1. Marketplaces gerais
2. Especializadas (por categoria)
3. Comparadores de preço e histórico
4. Usados
5. Internacional
6. Como identificar quem vende de verdade
7. Verificando se uma loja desconhecida é confiável

---

## 0. Como acessar cada site (o que bloqueia robô)

Teste feito em nov/2026 a partir de um servidor na nuvem (Claude Code na web), com a rede liberada para esses domínios. Várias lojas bloqueiam acessos vindos de datacenter **mesmo com navegador real** (Cloudflare, verificação de conta). Não gaste tentativas nelas: use a busca na web, que traz título, preço e trechos dos anúncios a partir do índice do buscador.

| Site | Acesso direto (script/curl) | Navegador (Playwright) | Melhor caminho |
|---|---|---|---|
| KaBuM | ✅ busca e produto; JSON-LD completo | ✅ | `extrair_produto.py` direto |
| AliExpress | ✅ (JSON-LD na busca) | ✅ | direto |
| Americanas | ✅ abre (conteúdo parcial) | ✅ | direto + busca na web |
| Buscapé / Zoom | ⚠️ HTML pesado | ✅ abre com preços | navegador |
| Reclame Aqui | ❌ 403 | ✅ | navegador |
| Mercado Livre | ❌ redireciona para verificação de conta | ❌ | **busca na web** (`site:mercadolivre.com.br`) |
| OLX | ❌ Cloudflare | ❌ | **busca na web** (`site:olx.com.br`, cobre `sp.olx.com.br` etc.) |
| Amazon | ❌ 503 / "Algo deu errado" | ❌ | **busca na web** |
| Magalu | ❌ 403 | ❌ | **busca na web** |
| Casas Bahia, Pichau, Terabyte, Pelando | ❌ 403 / Cloudflare | ❌ | **busca na web** |
| Shopee | ⚠️ página vazia (tudo via JS) | ⚠️ vazia | **busca na web** |
| Enjoei | ⚠️ abre a home, sem resultados | — | busca na web |

Observações:
- Se a sessão roda **no computador da pessoa** (IP residencial, navegador logado), esses bloqueios em geral não acontecem: prefira abrir as páginas de verdade.
- Ferramentas de leitura de página que rodam fora do ambiente (ex.: agente `web-fetch`) podem não enxergar a rede liberada da sessão; se derem erro de DNS, não insista.
- Quando a informação vier só da busca na web (sem abrir a página), deixe isso claro na tabela ("dados do buscador, não verificado na página") e recomende que a pessoa confira o anúncio antes de pagar.
- Um anúncio da OLX pode ter saído do ar; o índice do buscador pode estar dias atrasado. Prefira resultados com data recente.

## 1. Marketplaces gerais

### Mercado Livre — `mercadolivre.com.br`
- Busca: `https://lista.mercadolivre.com.br/termo-com-hifens`
- Ordenar por menor preço: acrescente `_OrderId_PRICE_NoIndex_True`
- Só usados: busque e aplique o filtro "Condição: Usado" (ou acrescente `_ITEM*CONDITION_2230581`).
- Anúncios ficam em `produto.mercadolivre.com.br/MLB-...` ou páginas de catálogo `mercadolivre.com.br/.../p/MLB...` (catálogo agrupa vários vendedores do mesmo produto — veja "Outras opções de compra").
- Checar: **reputação do vendedor** (termômetro verde = bom; MercadoLíder/Platinum = alto volume), **Loja oficial** (selo), "Full" (estoque no galpão do ML, entrega rápida e mais confiável), quantidade vendida, garantia ("garantia do vendedor" vs "de fábrica"), compra garantida, perguntas e respostas.
- Pegadinhas: anúncios de catálogo com variantes misturadas; "frete grátis" só acima de certo valor; produtos importados sem garantia nacional anunciados como novos.

### Amazon — `amazon.com.br`
- Busca: `https://www.amazon.com.br/s?k=termo+de+busca`
- Página de produto: `amazon.com.br/dp/ASIN`
- Checar: **"Enviado de / Vendido por"** — "Amazon.com.br" é o mais seguro; vendedor terceiro com envio pela Amazon (FBA) é intermediário; terceiro com envio próprio pede mais cuidado. Veja "Outros vendedores" na mesma página — às vezes mais barato. Prime (frete), avaliações verificadas, data das avaliações.
- Pegadinhas: avaliações de outra variante somadas no mesmo anúncio; "de/por" inflado; produtos com envio internacional (prazo longo, imposto). Para histórico de preço, Keepa e CamelCamelCamel cobrem amazon.com.br.

### Magalu — `magazineluiza.com.br`
- Busca: `https://www.magazineluiza.com.br/busca/termo+de+busca/`
- Checar: "Vendido e entregue por Magalu" vs lojista parceiro do marketplace; preço no Pix/à vista vs parcelado; cashback MagaluPay quando houver; retirada em loja física.

### Shopee — `shopee.com.br`
- Busca: `https://shopee.com.br/search?keyword=termo`
- Checar: "Loja Oficial"/"Indicado", avaliações com foto, local de envio (nacional vs exterior), cupons da loja e da plataforma. Muito produto genérico/réplica — conferir marca e originalidade.

### Casas Bahia / Ponto — `casasbahia.com.br`, `pontofrio.com.br`
- Busca: use o campo de busca do site ou `site:casasbahia.com.br "termo"`.
- Checar: vendido por Casas Bahia vs parceiro; reclamações recentes de entrega no Reclame Aqui.

### Americanas — `americanas.com.br`
- Busca: `https://www.americanas.com.br/busca/termo`
- Checar: vendedor parceiro vs Americanas; situação recente da empresa e prazos de entrega.

### Outros gerais
- Carrefour (`carrefour.com.br`), Fast Shop (`fastshop.com.br`, forte em eletro/eletrônicos premium), Leroy Merlin (`leroymerlin.com.br`, casa/ferramentas), Netshoes/Centauro (esportes), loja oficial da marca (Samsung, Apple, LG, Dell, Lenovo, Xiaomi etc. — costumam ter cupons e garantia sem dúvida).

## 2. Especializadas (por categoria)

- **Hardware/informática/games:** KaBuM (`kabum.com.br/busca/termo-com-hifens`), Pichau (`pichau.com.br/search?q=termo`), Terabyte (`terabyteshop.com.br/busca?str=termo`), Mercado Livre.
- **Instrumentos musicais e áudio:** Made in Brazil (`madeinbrazil.com.br`), Multisom (`multisom.com.br`), Mundomax (`mundomax.com.br`), Teclacenter (`teclacenter.com.br`), além de ML/OLX para usados (muito comum no meio musical). Confirme a URL de busca de cada loja na hora.
- **Casa, construção, ferramentas:** Leroy Merlin, Telhanorte, C&C, Ferramentas Kennedy, Loja do Mecânico.
- **Bicicletas/esportes:** Centauro, Decathlon, lojas de bike especializadas.
- **Livros:** Amazon, Estante Virtual (usados).
- **Moda:** Dafiti, Zattini, Enjoei (usados).
- **Fotografia:** lojas especializadas, OLX/ML para usados.

## 3. Comparadores de preço e histórico

- **Google Shopping:** `https://www.google.com/search?tbm=shop&q=termo` — visão ampla de lojas.
- **Buscapé:** `https://www.buscape.com.br/search?q=termo` — compara lojas e mostra **histórico de preço**.
- **Zoom:** `https://www.zoom.com.br/search?q=termo` — idem, com histórico.
- **Keepa / CamelCamelCamel:** histórico de preço da Amazon.
- **Pelando, Promobit:** comunidades de promoções — bom para ver se há cupom ativo e se "a promoção" é real (os usuários comentam o histórico).

Use os comparadores para descobrir lojas e checar se o preço atual é bom, mas **abra o anúncio na loja** antes de recomendar: o preço do comparador pode estar desatualizado.

## 4. Usados

- **OLX:** `https://www.olx.com.br/brasil?q=termo` ou por estado `https://www.olx.com.br/estado-sp?q=termo` (troque a sigla). Filtre por região próxima para retirada.
- **Mercado Livre usados:** filtro "Usado"; tem a proteção da Compra Garantida se pagar pela plataforma.
- **Facebook Marketplace:** `https://www.facebook.com/marketplace/search/?query=termo` — normalmente exige login; se não tiver acesso, diga isso e sugira que a pessoa olhe lá.
- **Enjoei:** `https://www.enjoei.com.br/s?q=termo` — moda, casa, alguns eletrônicos; pagamento pela plataforma.
- **Estante Virtual:** livros usados.
- **Grupos/fóruns especializados** (ex.: fóruns de hardware, grupos de instrumentos) — mencione como opção, sem prometer acesso.

Antes de recomendar qualquer usado: `references/usados-e-golpes.md`.

## 5. Internacional

- **AliExpress:** `https://pt.aliexpress.com/w/wholesale-termo-com-hifens.html`; **Shein/Temu** para itens simples.
- Compras internacionais pagam imposto de importação + ICMS; confira se o preço exibido já inclui os tributos ("impostos inclusos"/Remessa Conforme) e o prazo de entrega. Garantia e devolução são mais difíceis. Para eletrônicos, verifique compatibilidade (tomada, voltagem, bandas de celular, homologação Anatel).

## 6. Como identificar quem vende de verdade

Marketplaces misturam a própria loja com milhares de lojistas. Sempre registre na tabela:
- **Plataforma (1P):** "Vendido e entregue por Amazon/Magalu/Casas Bahia" — política de troca da própria empresa.
- **Lojista parceiro (3P):** nome da loja, reputação, tempo na plataforma, volume de vendas. Pode ser ótimo ou ruim — a reputação decide.
- **Loja oficial da marca no marketplace:** em geral segura.
- **Pessoa física:** usado ou revenda informal; risco maior.

## 7. Verificando se uma loja desconhecida é confiável

Se um comparador apontar uma loja que você não conhece com preço muito bom:
- Domínio exato (sites clonados usam nomes parecidos), CNPJ no rodapé e consulta do CNPJ (ativo? endereço coerente?).
- Reputação no Reclame Aqui (nota, índice de solução, reclamações recentes).
- Idade do domínio e presença em comparadores.
- Formas de pagamento: loja que só aceita Pix e tem preço muito abaixo do mercado é forte sinal de golpe.
