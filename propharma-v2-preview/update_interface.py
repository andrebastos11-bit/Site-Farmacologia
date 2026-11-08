"""One-time transformation of the copied interface only."""
from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'index.html'
s=p.read_text(encoding='utf-8')
s=s.replace('<title>Vademecum | Consulta de Medicamentos</title>', '<title>ProPharma | Base de Dados de Medicamentos</title>\n<meta name="description" content="ProPharma — Consulta rápida de informação farmacológica e clínica. Versão experimental local.">\n<link rel="icon" href="favicon.svg" type="image/svg+xml">')
s=s.replace('        Base de Dados de Medicamentos\n    </h1>', '        ProPharma <span class="preview-label">V2 · Experimental</span>\n    </h1>')
s=s.replace('Explore a classificação ATC e selecione uma substância para consultar os medicamentos.', 'Explore os grupos ATC e selecione uma apresentação. Classificação importada, pendente de revisão.')
start=s.index('    if (\n        eSubstancia &&')
end=s.index('    row.innerHTML', start)
s=s[:start]+'''    if (eSubstancia && no.medicamentos.length) {
        const composicoes = new Set(no.medicamentos.map(m => norm(m.substancia_ativa || "")));
        nomeVisivel = composicoes.size > 1
            ? "Grupo com diferentes substâncias/composições"
            : (no.nome || "Designação não disponível");
    }

'''+s[end:]
# Never substitute a clinical field with another field's content.
s=s.replace('        if (!apresentado && id === "forma-farmaceutica") apresentado = med.forma_farmaceutica || "";\n','')
s=s.replace('        if (!apresentado && id === "composicao") apresentado = med.substancia_ativa || "";\n','')
s=s.replace('acesso.textContent = "Consultar texto original do RCM"', 'acesso.textContent = "Consultar texto original importado"')
s=s.replace('    detalhe.querySelector(".sections").appendChild(arquivo);', '    detalhe.querySelector(".sections").appendChild(arquivo);\n    adicionarRastreabilidade(med, detalhe);')
# More explicit headings accepted, without introducing labels or rewriting source text.
s=s.replace('(?:Posologia|Modo de administração|Forma pura|Forma diluída|Adultos|Crianças|Adolescentes|Idosos|População pediátrica|Insuficiência renal|Insuficiência hepática)(?:\\s*\\([^:\\r\\n]{1,90}\\))?\\s*:\\s*', '(?:Posologia|Modo de administração|Forma pura|Forma diluída|Adultos|Crianças|Adolescentes|Idosos|População pediátrica|Insuficiência renal|Insuficiência hepática)(?:\\s*\\([^:\\r\\n]{1,90}\\))?(?:[ \\t]*:[ \\t]*|[ \\t]*(?:\\r\\n|\\n|\\r))')
# Connect generation of field metadata after the catalogue is loaded.
s=s.replace('        construirDadosATC();', '        await carregarRastreabilidade();\n        construirDadosATC();')
s=s.replace('    <script>', '    <script>')
s=s.replace('</head>', '<link rel="stylesheet" href="preview.css">\n<script src="provenance.js"></script>\n</head>')
s=s.replace('class="search-box"', 'class="search-box" aria-label="Pesquisar medicamentos por nome, substância ativa ou número de registo"')
# Keep errors visible when the local data file cannot load.
s=s.replace('        console.error(\n            erro\n        );', '        console.error(erro);\n        document.getElementById("atcTree").textContent = "Não foi possível carregar o catálogo. Abra este site pelo servidor local na porta 8001.";')
p.write_text(s,encoding='utf-8')
(root/'favicon.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#263b50"/><g transform="rotate(-40 32 32)"><rect x="20" y="9" width="24" height="46" rx="12" fill="white"/><path d="M20 32h24v11a12 12 0 0 1-24 0z" fill="#75b4d3"/><path d="M20 32h24" stroke="#263b50" stroke-width="2"/></g></svg>''',encoding='utf-8')
print('Interface updated in preview only')
