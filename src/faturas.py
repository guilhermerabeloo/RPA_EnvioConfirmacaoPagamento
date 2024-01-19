from sql import sqlPool
from email import envioDoEmail
import locale

def envioFaturas():
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    fornecedores = sqlPool("SELECT", "exec voucherzero.relacaoFornecedoresFatura ")

    for i, fornecedor in enumerate(fornecedores):
        try:
            codFornecedor = fornecedor[0]
            nomeFornecedor = fornecedor[1]
            codEmpresa = fornecedor[2]
            empresa = fornecedor[3]
            email = fornecedor[4]
            fatura = fornecedor[5]

            faturas = sqlPool("SELECT", f"EXEC voucherzero.faturasDoDia '{fatura}'")
            notas = []
            lancamentos = []
            parcelas = []
            totalLiquido = 0
            totalJuros = 0
            totalDescontos = 0

            for fatura in faturas:
                totalLiquido += fatura[8]
                totalJuros += fatura[10]
                totalDescontos += fatura[12]
                notas.append(fatura[4])
                lancamentos.append(fatura[0])
                parcelas.append({
                    'nota': fatura[6],
                    'parcela': fatura[7],
                    'dataPagamento': fatura[9],
                    'valorTitulo': locale.currency(fatura[8], grouping=True)
                })

            notas_str = ', '.join(map(str, notas))
            lancamentos_str = ', '.join(map(str, lancamentos))
            impostosEad = sqlPool("SELECT", f"""
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
            
            impostosScr = sqlPool("SELECT", f"""
                                SELECT 
                                    (SELECT SUM(cdo_vl) FROM BD_MTZ_FOR..scp_cdo WHERE cdo_cd = 'R2' and ob_lanc IN ({lancamentos_str})) AS PIS,
                                    (SELECT SUM(cdo_vl) FROM BD_MTZ_FOR..scp_cdo WHERE cdo_cd = 'R3' and ob_lanc IN ({lancamentos_str})) AS COFINS,
                                    (SELECT SUM(cdo_vl) FROM BD_MTZ_FOR..scp_cdo WHERE cdo_cd = 'R4' and ob_lanc IN ({lancamentos_str})) AS CSLL
                                """)
            totalImpostos = sum(impostosEad[0]) + sum(impostosScr[0])


            dados = {
                'para': 'guilherme.rabelo@grupofornecedora.com.br',
                'dataEmail': '20/12/2023',
                'empresa': empresa,
                'fornecedor': nomeFornecedor,
                'totalBruto': locale.currency((totalLiquido + totalImpostos), grouping=True),
                'totalJuros': locale.currency(totalJuros, grouping=True),
                'deducoesImpostos': locale.currency(totalImpostos, grouping=True),
                'descontos': locale.currency(totalDescontos, grouping=True),
                'totalLiquido': locale.currency((totalLiquido), grouping=True),
                'parcelas': parcelas
            }

            envioDoEmail('fatura', dados)
            sqlPool("INSERT", f"""
                    INSERT INTO [voucherzero].[log_execucoes]
                    (empresa, fornecedor, fatura, sucesso)
                    VALUES
                    ('{codEmpresa}', '{codFornecedor}', '1', '1')
                    """)
        except Exception as err:
            sqlPool("INSERT", f"""
                    INSERT INTO [voucherzero].[log_execucoes]
                    (empresa, fornecedor, fatura, sucesso)
                    VALUES
                    ('{codEmpresa}', '{codFornecedor}', '1', '0')
                    """)
            continue
