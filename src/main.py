from obrigacoes import envioObrigacoes
from faturas import envioFaturas
import logging

execucao_handler = logging.FileHandler('../log/logsDeExecucao.log')
execucao_handler.setLevel(logging.INFO)
execucao_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
erro_handler = logging.FileHandler('../log/logsDeErro.log')
erro_handler.setLevel(logging.ERROR)
erro_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[execucao_handler, erro_handler]
)
logger = logging.getLogger(__name__)

logger.info("=-=-=-=-=-=-=-=-INICIO DA EXECUCAO=-=-=-=-=-=-=-=-")
    
# try:
#     envioObrigacoes()
# except Exception as err:
#     logging.error(f'Há erros no envio de obrigacoes {err}')

try:
    envioFaturas()
except Exception as err:
    logging.error(f'Há erros no envio de faturas {err}')


logger.info("=-=-=-=-=-=-=-=-FIM DA EXECUCAO=-=-=-=-=-=-=-=-")
