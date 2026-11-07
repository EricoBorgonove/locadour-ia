import json
import logging
from pathlib import Path
from .llm import conversa, objeto_json, LLMError
from .ferramentas import executar, FERRAMENTAS

ROOT = Path(__file__).resolve().parents[1]

def prompt(arquivo):
    return (ROOT / 'prompts' / arquivo).read_text(encoding='utf-8')

MAPA = {
    'clientes_total': 'contar_clientes',
    'veiculos_lista': 'listar_veiculos',
    'disponibilidade': 'consultar_disponibilidade',
    'locacoes_ativas': 'locacoes_ativas',
    'receita_mensal': 'receita_mensal',
    'pagamentos_pendentes': 'pagamentos_pendentes',
    'ranking_veiculos': 'ranking_veiculos',
    'manutencao_custos': 'custos_manutencao',
    'filiais_lista': 'listar_filiais',
}

class SistemaTresAgentes:
    def responder(self, pergunta: str, administrativo: bool = True) -> str:
        pergunta = pergunta.strip()[:1000]
        if not pergunta:
            return 'Envie uma pergunta sobre a locadora.'
        try:
            # Agente 1: classifica a intenção.
            decisao = objeto_json(conversa(prompt('01_decisor.txt'), pergunta, json_mode=True))
            categoria = decisao.get('categoria')
            logging.info('Agente 1: %s', categoria)
            if categoria in ('saudacao', 'ajuda'):
                return ('Olá! 🚗 Posso informar veículos, diárias, filiais, locações ativas, '
                        'receita mensal, pagamentos pendentes e manutenção da frota. O que deseja consultar?')
            if categoria in ('receita_mensal', 'pagamentos_pendentes', 'locacoes_ativas', 'manutencao_custos') and not administrativo:
                return 'Esse relatório está disponível apenas para administradores autorizados.'
            if categoria not in MAPA:
                return 'Posso ajudar com consultas à locadora. Não faço alterações, reservas ou divulgo dados pessoais pelo WhatsApp.'

            # Agente 2: escolhe parâmetros e ferramenta. A aplicação valida a escolha.
            pedido = {'pergunta': pergunta, 'categoria': categoria,
                      'ferramenta_obrigatoria': MAPA[categoria],
                      'data_atual': __import__('datetime').date.today().isoformat()}
            ordem = objeto_json(conversa(prompt('02_executor.txt'), json.dumps(pedido, ensure_ascii=False), json_mode=True))
            ferramenta = ordem.get('ferramenta')
            parametros = ordem.get('parametros') or {}
            if ferramenta == 'nenhuma':
                return str(ordem.get('motivo') or 'Informe os dados necessários para realizar a consulta.')[:350]
            if ferramenta != MAPA[categoria] or ferramenta not in FERRAMENTAS:
                return 'Não consegui identificar uma operação segura para essa pergunta. Pode reformular?'
            logging.info('Agente 2: ferramenta=%s parametros=%s', ferramenta, parametros)
            try:
                dados = executar(ferramenta, parametros)
                resultado = {'ferramenta': ferramenta, 'dados': dados, 'parametros': parametros,
                             'descricao': 'Receita mensal representa valores contratados, não valores pagos.' if ferramenta == 'receita_mensal' else ''}
            except ValueError as exc:
                resultado = {'erro': str(exc)}

            # Agente 3: somente interpreta resultado, sem autorização para consultar nem modificar o banco.
            contexto = json.dumps({'pergunta': pergunta, 'resultado': resultado}, ensure_ascii=False, default=str)
            logging.info('Agente 3: interpretando dados')
            return conversa(prompt('03_interprete.txt'), contexto)[:3500]
        except LLMError:
            logging.exception('Erro ao acessar o modelo local')
            return 'O assistente está temporariamente indisponível. Tente novamente mais tarde.'
        except Exception:
            logging.exception('Erro no processamento')
            return 'Não consegui concluir a consulta agora. Verifique a conexão com o banco e tente novamente.'
