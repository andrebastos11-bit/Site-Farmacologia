"""Rebuild local preview reports without changing imported source files."""
import collections
import hashlib
import json
import pathlib
import re
import unicodedata
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / 'reports'
OUT.mkdir(exist_ok=True)
def norm(v):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFKD', str(v or '').lower()) if not unicodedata.combining(c)).split())
def text(v):
    return '' if v is None else str(v)
data = json.loads((ROOT / 'medicamentos.json').read_text(encoding='utf-8'))
workbook = openpyxl.load_workbook(ROOT / 'medicamentos.xlsx', read_only=True, data_only=True)
sheet = workbook.active
rows = list(sheet.values)
headers = [norm(h) for h in rows[0]]
def col(row, name):
    return text(row[headers.index(norm(name))])
# Keep the Excel's rows separate: it may be newer than the site's JSON.
xdata = []
for line, row in enumerate(rows[1:], 2):
    if not any(v is not None for v in row):
        continue
    xdata.append(dict(numero_registo=col(row,'numero_registo'), nome_medicamento=col(row,'Nome do medicamento'),
        substancia_ativa=col(row,'Substância ativa'), forma_farmaceutica=col(row,'Forma Farmacêutica'), dosagem=col(row,'Dosagem'),
        atc=col(row,'ATC'), composicao=col(row,'composicao'),
        atc_niveis=[{'codigo': col(row,'ATC')[:n], 'nome': col(row,f'{i}º Nível')} for i,n in enumerate([1,3,4,5,7],1)], linha_excel=line))
workbook.close()

source_url = 'https://www.fhi.no/en/fi/who-collaborating-centre-for-drug-statistics-methodology/atcddd-handbook/atc/structure-and-principles/'
wb = openpyxl.Workbook()
meta = wb.active
meta.title = 'Metodologia'
for row in [
    ['Auditoria estrutural ATC — ProPharma V2', '2026-11-08'],
    ['Âmbito', 'Todas as linhas não vazias do Excel e todas as apresentações do JSON, em folhas separadas.'],
    ['Medicamento distinto', 'Nome comercial normalizado; apresentação = linha do ficheiro.'],
    ['Composição distinta', 'Conjunto normalizado das substâncias declaradas no campo substancia_ativa; não é o texto quantitativo da composição.'],
    ['Regra', 'Sinais lexicais/estruturais são alertas para revisão, nunca prova de erro clínico.'],
    ['Substâncias diferentes', 'Podem partilhar legitimamente um ATC. Sais, combinações e indicações exigem verificação oficial individual.'],
    ['Confronto com composição', 'Verificação lexical conservadora; sinónimos, sais e abreviaturas podem produzir falsos alertas.'],
    ['Fonte metodológica consultada', source_url],
    ['Limite', 'Sem validação individual em RCM/índice ATC oficial; zero erros clínicos confirmados.'],
    ['Dados clínicos', 'Não alterados. Os dados JSON do catálogo não foram regenerados a partir do Excel.'],
]: meta.append(row)

audit_headers = ['Código ATC','Nome comercial','Substância ativa','Forma farmacêutica','Dosagem','Número de registo',
    'N.º medicamentos distintos no código','N.º composições distintas no código','Tipo de situação identificada','Observações',
    'Estado da auditoria','Composição declarada','Linha de origem']

def substances(m):
    return tuple(sorted(set(norm(p) for p in re.split(r'\s*(?:\+|;)\s*',m.get('substancia_ativa','')) if norm(p))))

def audit(records, title):
    ws = wb.create_sheet(title)
    ws.append(audit_headers)
    groups = collections.defaultdict(list)
    for m in records: groups[m.get('atc','').strip()].append(m)
    counts = collections.Counter()
    suspicious = 0
    for line,m in enumerate(records,2):
        code = m.get('atc','').strip()
        group = groups[code]
        variants = {substances(g) for g in group}
        names = {norm(g.get('nome_medicamento')) for g in group}
        alerts, notes = [], []
        state = 'Informação insuficiente'
        if not code: alerts.append('ATC em falta')
        elif re.fullmatch(r'[ABCDGHJLMNPRSV](?:\d{2}(?:[A-Z](?:[A-Z])?)?)?',code):
            alerts.append('ATC de grupo — nível terminal não disponível')
            notes.append('Código hierárquico com menos de 7 caracteres; não é necessariamente malformado.')
        elif not re.fullmatch(r'[ABCDGHJLMNPRSV]\d{2}[A-Z]{2}\d{2}',code): alerts.append('Formato ATC inesperado')
        if len(variants)>1:
            alerts.append('Substâncias/composições distintas no mesmo ATC')
            notes.append('Não constitui erro por si só; confirmar sais, combinações e âmbito terapêutico.')
            state = 'Situação potencialmente legítima'
        if not m.get('substancia_ativa'): alerts.append('Substância ativa em falta')
        levels=m.get('atc_niveis') or []
        if levels and [(l or {}).get('codigo') for l in levels] != [code[:n] for n in [1,3,4,5,7]]:
            alerts.append('Divergência entre ATC e caminho da árvore')
        if len(variants)>1 and levels:
            alerts.append('Rótulo de grupo potencialmente indevido na árvore')
            notes.append('A interface original substitui o nome do nível terminal pela primeira substância ativa; a preview usa um rótulo neutro para grupos heterogéneos.')
        label_variants={norm(((g.get('atc_niveis') or [{}])[-1] or {}).get('nome')) for g in group}
        if len(label_variants)>1:
            alerts.append('Designações divergentes para o mesmo nível ATC')
        composition=norm(m.get('composicao'))
        parts=substances(m)
        if composition in ['', 'nao disponivel', 'n/d', 'nd', 'n/a']:
            alerts.append('Composição não disponível para confronto')
        elif parts and any(p not in composition for p in parts):
            alerts.append('Composição requer confronto lexical')
            notes.append('Pelo menos uma substância declarada não ocorre literalmente na composição. Pode ser sinónimo/sal; revisão manual obrigatória.')
        mixed = {len(substances(g))>1 for g in group}
        if len(mixed)>1:
            alerts.append('Substância isolada e associação no mesmo ATC')
            notes.append('Identificação de associação apenas pelo separador + ou ;. Validar no RCM.')
        serious = any(a in alerts for a in ['ATC em falta','Formato ATC inesperado','Divergência entre ATC e caminho da árvore','Substância isolada e associação no mesmo ATC','Designações divergentes para o mesmo nível ATC'])
        if serious: state='Situação suspeita'; suspicious+=1
        if not alerts: alerts=['Sem alerta estrutural']; notes.append('Ausência de alerta não comprova correção clínica nem validação oficial.')
        for a in alerts: counts[a]+=1
        ws.append([code,m.get('nome_medicamento'),m.get('substancia_ativa'),m.get('forma_farmaceutica'),m.get('dosagem'),
            m.get('numero_registo'),len(names),len(variants),'; '.join(alerts),' '.join(notes),state,m.get('composicao'),m.get('linha_excel',line)])
    return dict(apresentacoes=len(records), nomes_distintos=len({norm(m['nome_medicamento']) for m in records}),
        codigos=len(groups),codigos_multiplas_composicoes=sum(len({substances(g) for g in group})>1 for group in groups.values()),
        apresentacoes_suspeitas=suspicious, erros_clinicos_confirmados=0, alertas=dict(counts))

stats={'json':audit(data,'Auditoria JSON'), 'excel':audit(xdata,'Auditoria Excel')}
missing=wb.create_sheet('Sem RCM oficial')
missing.append(['Origem','Nome comercial','Número de registo','ATC','Estado'])
for origin,records in [('JSON',data),('Excel',xdata)]:
    for m in records: missing.append([origin,m['nome_medicamento'],m['numero_registo'],m['atc'],'URL oficial não disponível'])

diff=wb.create_sheet('Diferenças Excel JSON')
diff.append(['Número registo','Campo','Valor JSON','Valor Excel','Situação'])
def identity(m):
    return tuple(norm(m.get(f)) for f in ['numero_registo','nome_medicamento','forma_farmaceutica','dosagem'])
jmap=collections.defaultdict(list); xmap=collections.defaultdict(list)
for m in data: jmap[identity(m)].append(m)
for m in xdata: xmap[identity(m)].append(m)
for key in sorted(set(jmap)|set(xmap)):
    jrows,xrows=jmap[key],xmap[key]
    for i in range(max(len(jrows),len(xrows))):
        j=jrows[i] if i<len(jrows) else None
        x=xrows[i] if i<len(xrows) else None
        if j is None or x is None:
            item=j or x
            diff.append([item['numero_registo'],'Apresentação',json.dumps(j,ensure_ascii=False) if j else '',json.dumps(x,ensure_ascii=False) if x else '', 'Apenas Excel' if j is None else 'Apenas JSON'])
        else:
            for field in ['substancia_ativa','atc','composicao']:
                if norm(j.get(field))!=norm(x.get(field)):
                    diff.append([j['numero_registo'],j['nome_medicamento']+' / '+field,j.get(field),x.get(field),'Divergência — não corrigida'])
dups=wb.create_sheet('Registos duplicados')
dups.append(['Origem','Número de registo','Número de apresentações','Observação'])
for origin,records in [('JSON',data),('Excel',xdata)]:
    for reg,count in collections.Counter(m['numero_registo'] for m in records).items():
        if count>1: dups.append([origin,reg,count,'Não identifica univocamente uma apresentação. Não corrigido.'])
stats['registos_duplicados_json']={reg:c for reg,c in collections.Counter(m['numero_registo'] for m in data).items() if c>1}
stats['diferencas_excel_json']=diff.max_row-1
stats['sem_rcm_json']=len(data)
stats['sem_rcm_nomes_distintos']=len({norm(m['nome_medicamento']) for m in data})
for ws in wb:
    ws.freeze_panes='A2'; ws.auto_filter.ref=ws.dimensions
    ws.row_dimensions[1].height=32
    for cell in ws[1]: cell.font=Font(color='FFFFFF',bold=True); cell.fill=PatternFill('solid',fgColor='263B50')
    for col_cells in ws.columns:
        letter=col_cells[0].column_letter
        ws.column_dimensions[letter].width=min(62,max(18,len(str(col_cells[0].value or ''))+2))
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment=Alignment(vertical='top',wrap_text=True)
            # Imported clinical text is always stored as literal text, never an Excel formula.
            if isinstance(cell.value,str): cell.data_type='s'
wb.save(OUT/'auditoria-atc.xlsx')
(OUT/'audit-summary.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
manifest={}
for p in ROOT.parent.rglob('*'):
    if not p.is_file() or '.git' in p.parts or ROOT in p.parents: continue
    manifest[str(p.relative_to(ROOT.parent))]=hashlib.sha256(p.read_bytes()).hexdigest()
if not (OUT/'original-sha256.json').exists():
    (OUT/'original-sha256.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(stats,ensure_ascii=True,indent=2))
