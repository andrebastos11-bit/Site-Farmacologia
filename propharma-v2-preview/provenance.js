/* Sidecar metadata never mutates the imported medicine records. */
let rastreabilidade = {schema_version: 1, apresentacoes: {}};
async function carregarRastreabilidade() {
    try {
        const resposta = await fetch('rastreabilidade.json');
        if (!resposta.ok) throw new Error('Metadados indisponíveis');
        rastreabilidade = await resposta.json();
    } catch (e) { console.warn(e.message); }
}
function metadadosCampo(med, campo) {
    const registro = registroRastreabilidade(med);
    return {origem_importacao: 'medicamentos.json', fonte_oficial: null, url_rcm: null, secao_rcm: null,
        data_versao_documento: null, data_ultima_verificacao: null, estado_validacao: 'importado',
        observacoes: 'Pendente de revisão por fonte oficial.', ...(registro.campos?.[campo] || {})};
}
function urlOficialSegura(valor) {
    try {
        const url = new URL(valor);
        return url.protocol === 'https:' && /(^|\.)(infarmed\.pt|ema\.europa\.eu)$/.test(url.hostname) ? url.href : null;
    } catch { return null; }
}
function registroRastreabilidade(med) {
    // Registration numbers are not unique in the imported catalogue.
    const registro = rastreabilidade.apresentacoes['json:'+med._id];
    if (!registro || registro.identidade !== JSON.stringify([med.numero_registo,med.nome_medicamento,med.forma_farmaceutica,med.dosagem])) return {};
    return registro;
}
function adicionarRastreabilidade(med, detalhe) {
    const painel = document.createElement('aside'); painel.className = 'provenance-overview';
    const titulo = document.createElement('strong'); titulo.textContent = 'Dados importados · Revisão oficial pendente';
    const nota = document.createElement('p'); nota.textContent = 'O texto clínico é preservado tal como consta do catálogo. Não existe evidência de validação oficial associada a estes dados.';
    painel.append(titulo, nota);
    const registro = registroRastreabilidade(med);
    // A URL is displayed only after the specific presentation/document association is verified.
    const url = registro.associacao_rcm_verificada === true && registro.evidencia_associacao
        ? urlOficialSegura(registro.url_rcm) : null;
    if (url) {
        const link = document.createElement('a'); link.className = 'official-rcm'; link.href = url;
        link.target = '_blank'; link.rel = 'noopener noreferrer'; link.textContent = 'Consultar RCM oficial ↗'; painel.append(link);
    } else {
        const ausencia = document.createElement('p'); ausencia.textContent = 'Ligação ao RCM oficial não disponível. O texto original importado encontra-se no fim da ficha.'; painel.append(ausencia);
    }
    detalhe.querySelector('.trading-card-header').after(painel);
    const rotulos = {origem_importacao:'Origem importada', fonte_oficial:'Fonte oficial', url_rcm:'URL do RCM', secao_rcm:'Secção do RCM', data_versao_documento:'Versão do documento', data_ultima_verificacao:'Última verificação', estado_validacao:'Estado da validação', observacoes:'Observações'};
    for (const [id,campo] of Object.entries(CAMPOS_RCM)) {
        const alvo = detalhe.querySelector('#'+id+' .rcm-field'); if (!alvo) continue;
        const info = metadadosCampo(med,campo);
        const bloco = document.createElement('details'); bloco.className='field-provenance';
        const summary = document.createElement('summary'); summary.textContent='Rastreabilidade · '+({'importado':'Importado','pendente_revisao':'Pendente de revisão','verificado':'Verificado'}[info.estado_validacao] || 'Pendente de revisão');
        // Verification requires documentary evidence and a verification date.
        if (info.estado_validacao === 'verificado' && !(info.evidencia_validacao && info.data_ultima_verificacao && urlOficialSegura(info.url_rcm))) {
            info.estado_validacao = 'pendente_revisao'; summary.textContent='Rastreabilidade · Pendente de revisão';
        }
        const dl = document.createElement('dl');
        for (const [key,label] of Object.entries(rotulos)) {
            const dt=document.createElement('dt'), dd=document.createElement('dd');
            dt.textContent=label; dd.textContent=info[key] || 'Não disponível'; dl.append(dt,dd);
        }
        bloco.append(summary,dl); alvo.append(bloco);
    }
}
