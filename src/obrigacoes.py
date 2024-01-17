from sql import sqlPool
from email import envioDoEmail
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

fornecedores = sqlPool("SELECT", "exec voucherzero.relacaoFornecedores")

for i, fornecedor in enumerate(fornecedores):
    codFornecedor = fornecedor[0]
    nomeFornecedor = fornecedor[1]
    codEmpresa = fornecedor[2]
    empresa = fornecedor[3]
    email = fornecedor[4]

    obrigacoes = sqlPool("SELECT", f"EXEC voucherzero.obrigacoes_fornecedor '{codFornecedor}', '{codEmpresa}'")
    notas = []
    parcelas = []
    totalBruto = 0
    totalJuros = 0
    totalDescontos = 0

    for obrigacao in obrigacoes:
        totalBruto += obrigacao[6]
        totalJuros += obrigacao[11]
        totalDescontos += obrigacao[13]
        notas.append(obrigacao[9])
        parcelas.append({
            'referencia': obrigacao[5],
            'dataPagamento': obrigacao[4],
            'valorTitulo': locale.currency(obrigacao[6], grouping=True)
        })

    notas_str = ', '.join(map(str, notas))
    impostos = sqlPool("SELECT", f"""
                        SELECT                                                                                                                                                      
                            ROUND(ISNULL(sum(nfed.nf_vliss),0),2) as ISS,                                           
                            ROUND(ISNULL(sum(nfed.nf_vlinss),0),2) as INSS,                                                    
                            ROUND(ISNULL(sum(nfed.nf_vlirrf),0),2) as IRRF,                                           
                            ROUND(ISNULL(sum(ISNULL(nfed.nf_vlicms,0)+ISNULL(nfei.nf_vlicms,0)+ISNULL(nfed.nf_vlicmsret,0)+ISNULL(nfei.nf_vlicmsret,0)),0),2) as ICMS,                                             
                            ROUND(ISNULL(sum(ISNULL(nfed.nf_vlipi,0)+ISNULL(nfei.nf_vlipi,0)),0),2) as IPI,                                                    
                            ROUND(ISNULL(sum(nfe.nf_vlfcp),0),2) as FECOP                                                    
                        FROM [BD_LOG_MTZ]..ger_nfe nfe                                                    
                        LEFT JOIN [BD_LOG_MTZ]..ger_nfed nfed ON nfed.nf_lanc = nfe.nf_lanc                            
                        LEFT JOIN [BD_LOG_MTZ]..ger_nfei nfei ON nfei.nf_lanc = nfe.nf_lanc                                                    
                        WHERE 
                            nfe.nf_lanc in ({notas_str})
                            AND nfe.nf_dtcanc IS NULL 
                        """)

    totalImpostos = sum(impostos[0])

    dados = {
        'para': 'guilherme.rabelo@grupofornecedora.com.br',
        'dataEmail': '20/12/2023',
        'empresa': empresa,
        'fornecedor': nomeFornecedor,
        'totalBruto': locale.currency(totalBruto, grouping=True),
        'totalJuros': locale.currency(totalJuros, grouping=True),
        'deducoesImpostos': locale.currency(totalImpostos, grouping=True),
        'descontos': locale.currency(totalDescontos, grouping=True),
        'totalLiquido': locale.currency((totalBruto - totalDescontos - totalImpostos), grouping=True),
        'parcelas': parcelas
    }

    envioDoEmail('lancamento', dados)

