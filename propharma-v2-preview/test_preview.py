"""Browser checks against the local experimental site; writes reproducible evidence."""
import hashlib
import json
import pathlib
import sys
import urllib.request
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent/'.test-deps'))
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parent
results=[]
def record(browser,name,details=True):
    results.append(dict(browser=browser,test=name,result=details))
    (ROOT/'reports'/'browser-tests.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(browser,name,json.dumps(details,ensure_ascii=True)[:600],flush=True)
assert urllib.request.urlopen('http://127.0.0.1:8001').status==200
with sync_playwright() as p:
    for name,exe in [('Chrome',r'C:\Program Files\Google\Chrome\Application\chrome.exe'),('Edge',r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')]:
        browser=p.chromium.launch(executable_path=exe,headless=True)
        page=browser.new_page(viewport={'width':1440,'height':1000})
        errors=[]
        page.on('pageerror',lambda e: errors.append(str(e)))
        page.goto('http://127.0.0.1:8001',wait_until='networkidle')
        page.wait_for_function('medicamentos.length === 4846 && document.querySelector(".atc-node")')
        assert page.title()=='ProPharma | Base de Dados de Medicamentos'
        record(name,'Catálogo carregado',page.evaluate('medicamentos.length'))
        # Full-height empty state and independent bounded panels at three resolutions.
        for w,h in [(1440,1000),(768,1024),(390,844)]:
            page.set_viewport_size({'width':w,'height':h})
            info=page.evaluate('''() => {
                const panel=document.querySelector('.medicine-panel'), detail=document.querySelector('#detalhe-medicamento');
                return {width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,
                    panelHeight:panel.clientHeight,detailHeight:detail.getBoundingClientRect().height,
                    panelBounded:panel.getBoundingClientRect().bottom<=innerHeight+1};
            }''')
            assert not info['overflow'] and info['panelBounded'] and info['detailHeight']>=info['panelHeight']-2,info
            record(name,f'Estado vazio {w}x{h}',info)
        page.set_viewport_size({'width':1440,'height':1000})
        for term in ['Tantum Verde','Fluoreto de sódio','4781688','Eutirox']:
            page.locator('#searchBar').fill(term)
            page.wait_for_timeout(350)
            assert page.locator('.search-result').count()>0,term
            record(name,'Pesquisa '+term,page.locator('.search-result').count())
        page.locator('#searchBar').fill('4781688')
        page.wait_for_timeout(350)
        page.locator('#searchBar').press('Enter')
        page.wait_for_function('medicamentoSelecionado && medicamentoSelecionado.nome_medicamento === "Duraphat 5000"')
        record(name,'Seleção pelo registo via teclado')
        for drug in ['Duraphat 5000','Tantum Verde','Eutirox']:
            selected=page.evaluate('''drug => {
                const med=medicamentos.find(m=>m.nome_medicamento===drug); selecionarMedicamento(med);
                return {nome:med.nome_medicamento,id:med._id,campos:document.querySelectorAll('.rcm-field').length};
            }''',drug)
            assert selected['campos']==19,selected
            for w,h in [(1440,1000),(768,1024),(390,844)]:
                page.set_viewport_size({'width':w,'height':h})
                page.locator('details.nivel-secao').first.evaluate('(e)=>e.open=true')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                page.screenshot(path=str(ROOT/'reports'/f'{name.lower()}-{drug.split()[0].lower()}-{w}.png'),full_page=True)
            page.set_viewport_size({'width':1440,'height':1000})
            record(name,'Ficha real responsiva '+drug,selected)
            source=page.evaluate('''() => {
                const originals=[...document.querySelectorAll('.rcm-original-all pre')].map(e=>e.textContent);
                return Object.values(CAMPOS_RCM).filter(k=>String(medicamentoSelecionado[k]??'').length).every(k=>originals.includes(String(medicamentoSelecionado[k])));
            }''')
            assert source
            record(name,'Texto original acessível '+drug,source)
            page.locator('.shortcut-posologia').click()
            page.wait_for_timeout(250)
            page.screenshot(path=str(ROOT/'reports'/f'{name.lower()}-{drug.split()[0].lower()}-posologia.png'))
        # Shortcuts open their target section.
        page.locator('.shortcut-posologia').click()
        page.wait_for_timeout(500)
        assert page.locator('#posologia').is_visible()
        record(name,'Cartão de consulta rápida')
        picker=page.locator('.presentation-option:not(.active)')
        if picker.count():
            old=page.evaluate('medicamentoSelecionado._id')
            picker.first.click()
            assert page.evaluate('medicamentoSelecionado._id')!=old
            record(name,'Seletor de apresentações')
        before=page.locator('.medicine-panel').bounding_box()['width']
        page.locator('#hideATC').click()
        assert page.locator('#atcPanel').is_hidden()
        assert page.locator('.medicine-panel').bounding_box()['width']>before
        page.locator('#showATC').click()
        assert page.locator('#atcPanel').is_visible()
        record(name,'Ocultar/mostrar árvore e expandir ficha')
        # Real tree navigation, not just API selection.
        page.evaluate('''() => { document.querySelectorAll('.atc-node.open,.atc-node.show-products').forEach(e=>e.classList.remove('open','show-products')); document.querySelector('.atc-panel').scrollTop=0; }''')
        row=page.locator('#atcTree > .atc-node').first
        row.locator(':scope > .atc-row').click()
        assert 'open' in row.get_attribute('class')
        row.locator(':scope > .atc-row').click()
        assert 'open' not in row.get_attribute('class')
        record(name,'Expandir/recolher nível ATC')
        page.evaluate('selecionarMedicamento(medicamentos[0])')
        tree=page.locator('.tree-product[data-med-id="0"]')
        tree.click()
        assert page.evaluate('medicamentoSelecionado._id')==0
        record(name,'Selecionar apresentação pela árvore')
        page.locator('details.nivel-secao').evaluate_all('(els)=>els.forEach(e=>e.open=true)')
        independent=page.evaluate('''() => {
            const a=document.querySelector('.atc-panel'),b=document.querySelector('.medicine-panel');
            a.scrollTop=0;b.scrollTop=0;b.scrollTop=400;
            const ok=b.scrollTop>0 && a.scrollTop===0;
            b.scrollTop=0;a.scrollTop=50;
            return ok && b.scrollTop===0 && a.scrollTop>0;
        }''')
        assert independent
        record(name,'Scroll independente',independent)
        # Test all clinical fields across the complete imported catalogue.
        preservation=page.evaluate('''() => {
            let total=0,structured=0; const failed=[];
            for(const med of medicamentos) for(const [id,key] of Object.entries(CAMPOS_RCM)) {
                const original=String(med[key]??'');
                const doc=id==='excipientes'?criarListaExcipientesSegura(original):renderizarComponentesClinicos(estruturarCampoClinico(original,id));
                const rebuilt=doc.classList.contains('rcm-components')?reconstruirComponenteClinico(doc):doc.textContent;
                total++; if(doc.classList.contains('rcm-components')) structured++;
                if(rebuilt!==original) failed.push({id:med._id,key});
            }
            return {total,structured,failed};
        }''')
        assert not preservation['failed'],preservation
        record(name,'Preservação integral de todos os campos clínicos',preservation)
        links=page.evaluate('''() => ({count:document.querySelectorAll('.official-rcm').length,
            invalid:urlOficialSegura('https://example.com/fake.pdf'),valid:urlOficialSegura('https://www.ema.europa.eu/test.pdf')})''')
        assert links['count']==0 and links['invalid'] is None
        record(name,'Ausência de ligações inventadas e filtro de domínio',links)
        record(name,'Erros JavaScript',errors)
        assert not errors,errors
        browser.close()
manifest=json.loads((ROOT/'reports'/'original-sha256.json').read_text())
changes=[rel for rel,sha in manifest.items() if hashlib.sha256((ROOT.parent/rel).read_bytes()).hexdigest()!=sha]
record('Ficheiros','Alterações externas nos originais desde o snapshot',changes)
assert (ROOT/'medicamentos.json').read_bytes()==(ROOT.parent/'medicamentos.json').read_bytes()
assert hashlib.sha256((ROOT/'medicamentos.xlsx').read_bytes()).hexdigest()==manifest['medicamentos.xlsx']
record('Ficheiros','Cópia Excel preserva snapshot inicial; JSON igual ao original',True)
(ROOT/'reports'/'browser-tests.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
