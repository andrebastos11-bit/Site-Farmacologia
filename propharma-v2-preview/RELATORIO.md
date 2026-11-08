# ProPharma V2 — relatório da versão experimental

Data de execução: 8 de novembro de 2026.

## Abrir a preview

Pasta: `C:\Users\User\Desktop\ProPharma\propharma-v2-preview`

Endereço: http://localhost:8001 (também disponível em http://127.0.0.1:8001).

Se o servidor estiver parado, executar nesta pasta:

```powershell
powershell -ExecutionPolicy Bypass -File .\start-preview.ps1
```

O servidor serve apenas a pasta experimental e aceita ligações no computador local. Se a porta 8001 já estiver ocupada, não terminar processos desconhecidos: confirmar se a preview já está disponível.

## Proteção da versão oficial

Foi analisado o site estático: `index.html`, `medicamentos.json`, `medicamentos.xlsx`, `conversor.py`, `indexador` e imagens. Todos os ficheiros necessários foram copiados, sem `.git`, identidade de alojamento ou ficheiros temporários Excel. O site original, os dados e os ficheiros de produção não foram editados. Não foram executados `git add`, `git commit`, `git push` ou publicação. Não foi alterado qualquer domínio ou configuração Vercel.

O manifesto `reports/original-sha256.json` permite comparar os ficheiros originais com o snapshot inicial. O JSON copiado permanece byte a byte igual ao original. O Excel copiado preserva o hash inicial.

**Alteração externa detetada durante a execução:** o Excel original foi guardado por outro processo às 18:23:47, passando de 723 592 para 725 360 bytes. O seu hash mudou de `42604c50e49550bfd5c04c7574bdb8d84b0aa9c01fc3e56216d4c724b9110d76` para `5445a4bd726ba51bfc5bedb3219f99aed405e8e6472a99e5ec685c91485dd45f`. A cópia mantém o hash inicial. Nenhuma operação desta implementação escreveu no Excel original. A auditoria deste relatório refere-se ao snapshot inicial copiado, não ao Excel guardado posteriormente. Os restantes 25 ficheiros originais mantiveram os hashes iniciais.

## Alterações e componentes

- Identidade ProPharma, título do separador solicitado, subtítulo e favicon SVG com cápsula. Identificação visível da versão experimental.
- Painéis com altura limitada à área útil, scroll independente, estado vazio de altura integral e ausência de scroll horizontal nos tamanhos testados.
- Árvore ATC retrátil; a ficha ocupa a largura libertada. Em grupos heterogéneos, rótulo neutro em vez de usar a primeira substância como identidade de todo o grupo. Os códigos e substâncias originais não foram alterados.
- Cabeçalho da ficha, registo, dispensa, indicação resumida, forma/dose, seletor de apresentações e cartões de consulta rápida preservados e harmonizados.
- Componentes globais reutilizáveis para blocos clínicos com títulos explícitos, grupos etários, instruções numeradas, advertências, listas de contraindicações, subseções de fertilidade/gravidez/aleitamento, condução e listas de excipientes em duas colunas quando possível.
- Tabelas de grupos etários e de reações adversas apenas quando a estrutura permite associação explícita. A infraestrutura de tabelas com delimitadores originais foi preservada. Texto ambíguo mantém o componente de texto original; não foram inferidas doses, categorias ou títulos.
- Os três grupos de informação continuam disponíveis: Informações Clínicas, Propriedades Farmacológicas e Informações Farmacêuticas.
- A reconstrução por intervalos do texto de origem verifica a preservação antes de aceitar componentes estruturados. O texto importado completo continua acessível no fim da ficha.
- Rastreabilidade por campo: origem importada, fonte oficial, URL, secção, versão documental, última verificação, estado e observações. Valores desconhecidos ficam como «Não disponível» e os dados importados têm revisão pendente.
- O sidecar `rastreabilidade.json` separa metadados e conteúdo clínico. As chaves usam `json:índice` com confirmação da identidade da apresentação; não usam apenas números de registo, que não são únicos nesta base.
- Componente «Consultar RCM oficial ↗» preparado com nova aba e `rel="noopener noreferrer"`. Só é apresentado com URL HTTPS INFARMED/EMA e evidência da associação à apresentação. Sem evidência, permanece a consulta discreta do texto importado. Não foram criadas ligações fictícias.
- Não foram atribuídos indicadores clínicos de segurança por palavras-chave. Nenhuma classificação de segurança nova foi apresentada como validada.

## Auditoria ATC

Relatório: [reports/auditoria-atc.xlsx](reports/auditoria-atc.xlsx).

Foram analisadas todas as 4 846 apresentações do JSON e todas as 4 844 linhas de apresentações do Excel. As duas origens têm folhas separadas; a preview usa o mesmo JSON do site original. Não foi regenerado o catálogo a partir do Excel, que diverge do JSON.

| Resultado | JSON do site | Excel atual |
| --- | ---: | ---: |
| Apresentações | 4 846 | 4 844 |
| Nomes comerciais distintos, normalizados | 3 185 | 3 185 |
| Valores de código ATC distintos | 1 617 | 1 631 |
| Códigos associados a composições/substâncias distintas | 97 | 92 |
| Apresentações com sinais classificados como suspeitos | 707 | 671 |
| ATC de grupo, sem nível terminal | 152 | 149 |
| Divergência entre campo ATC e caminho importado | 71 | 0* |
| Erros clínicos confirmados por fonte oficial | 0 | 0 |

*No Excel o código dos níveis é derivado do campo ATC; o confronto independente de códigos de caminho aplica-se ao JSON. O Excel contém os nomes dos níveis, não códigos independentes para cada nível.*

Não foram identificados códigos em falta ou códigos de formato malformado pela regra estrutural aplicada. Os códigos de grupo não foram considerados automaticamente malformados.

Há 163 entradas de diferenças nos campos comparados entre Excel e JSON. O confronto usa nome, forma, dosagem e registo com multiplicidade, porque o registo isolado não é uma chave única. A folha «Registos duplicados» documenta o valor `9999999`, partilhado por 4 827 apresentações no JSON.

No JSON, 188 apresentações partilham código entre substâncias isoladas e associações identificadas pelos separadores explícitos; 609 pertencem a códigos com designações terminais divergentes. Estes conjuntos podem sobrepor-se. São alertas de revisão, não contagens de erros clínicos.

O confronto lexical com composição quantitativa produziu dois alertas no JSON; 4 831 composições estão indisponíveis e não permitem esse confronto. Sinónimos e sais podem explicar divergências lexicais. «Composições distintas» na contagem por código significa conjuntos das substâncias do campo substância ativa, normalizados; não significa diferenças de dose no texto quantitativo da composição.

A metodologia respeita a possibilidade de diferentes combinações partilharem legitimamente um código, descrita pelo [WHO Collaborating Centre](https://www.fhi.no/en/fi/who-collaborating-centre-for-drug-statistics-methodology/atcddd-handbook/atc/structure-and-principles/). Essa fonte fundamenta a metodologia; não valida individualmente os medicamentos deste catálogo. Não foram confirmados erros ATC individuais nem aplicadas correções automáticas.

## Ligações RCM e qualidade dos dados

Todas as 4 846 apresentações do catálogo, correspondentes a 3 185 nomes comerciais normalizados (3 191 grafias exatas), estão sem URL oficial de RCM nos dados. A folha «Sem RCM oficial» lista cada apresentação e inclui também a origem Excel.

Os dados contêm lacunas importantes: 4 830 apresentações têm posologia «Não Disponível». Eutirox permite testar pesquisa, apresentações e campos indisponíveis, mas não fornece conteúdo clínico completo para avaliar todas as novas estruturas. Existem textos aparentemente truncados ou com lapsos nos dados importados; por exemplo, a posologia de Duraphat termina em «Uso denta». Estes textos foram preservados e precisam de revisão no RCM, não de correção editorial nesta fase.

## Testes e evidências

Testes automatizados em Chrome e Edge instalados, ambos em modo headless. Computador: 1440×1000; tablet simulado: 768×1024; telemóvel simulado: 390×844. Não são testes em dispositivos físicos.

- Carregamento HTTP local e catálogo completo.
- Pesquisa por Tantum Verde, Eutirox, Fluoreto de sódio e número de registo 4781688; seleção por teclado.
- Navegação real pela árvore, expansão/recolha, seleção de apresentação e seletor de outras apresentações.
- Fichas de Tantum Verde, Duraphat 5000 e Eutirox, cartões de consulta rápida e texto original acessível.
- Estado vazio com preenchimento da altura útil, scroll independente, árvore visível/oculta e expansão da ficha.
- Layout nas três resoluções, sem overflow horizontal da página.
- Comparação integral dos 92 074 campos clínicos do catálogo com a saída dos componentes, em cada navegador; zero diferenças de conteúdo.
- Ausência de ligações oficiais inventadas e filtro de domínios. Não foi possível verificar documentos RCM correspondentes porque não existem URLs associadas.
- Zero erros JavaScript nos percursos testados.
- Comparação dos originais com o snapshot, preservação do JSON e do Excel copiados; alteração externa do Excel original identificada e registada.

Evidência executável: `test_preview.py`; resultados: `reports/browser-tests.json`; capturas: `reports/*.png`. Os testes requerem a dependência Playwright em `.test-deps`, instalada apenas para QA. O site não depende de Playwright.

## Pendências explícitas

- Chromium autónomo e Firefox não estavam disponíveis: testes pendentes. Chrome/Edge usam Chromium, mas não substituem o teste da distribuição Chromium autónoma.
- Revisão visual manual e testes em tablets/telemóveis físicos.
- Validação clínica individual por fonte oficial, confirmação de alertas ATC e preenchimento de ligações RCM, datas documentais e verificações reais.
- Estruturação adicional dos textos sem delimitação inequívoca só após melhor qualidade/estrutura dos dados. Não se prometem tabelas ou advertências separadas onde o texto original não permite uma conversão segura.
- Integração no site oficial e publicação dependem de decisão posterior do utilizador; não foram realizadas.

## Ficheiros de manutenção

`preview.css`: apresentação experimental; `provenance.js`: leitura e apresentação da rastreabilidade; `rastreabilidade.json`: sidecar; `prepare_preview.py`: reconstrução da auditoria, requer openpyxl; `update_interface.py`: registo da transformação inicial, para execução única sobre uma cópia limpa, não voltar a executar sobre a preview já transformada.
