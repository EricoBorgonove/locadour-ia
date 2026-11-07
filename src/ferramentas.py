"""Consultas SQL fixas, somente leitura. Nunca execute SQL gerado pela IA."""
from datetime import date
from decimal import Decimal
import mysql.connector
from .config import DB

FERRAMENTAS = {
    'contar_clientes', 'listar_veiculos', 'consultar_disponibilidade',
    'locacoes_ativas', 'receita_mensal', 'pagamentos_pendentes',
    'ranking_veiculos', 'custos_manutencao', 'listar_filiais',
}

def sql(query, params=()):
    conn = mysql.connector.connect(**DB)
    try:
        conn.start_transaction(readonly=True)
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(query, params)
            rows = cur.fetchmany(21)
            return [{k: (float(v) if isinstance(v, Decimal) else v.isoformat() if isinstance(v, (date,)) else str(v) if hasattr(v,'isoformat') else v) for k,v in r.items()} for r in rows]
        finally:
            cur.close()
    finally:
        conn.close()

def inteiro(v, minimo, maximo, padrao=None):
    if v is None:
        if padrao is None:
            raise ValueError('Parâmetro numérico obrigatório.')
        return padrao
    try:
        n = int(v)
    except (TypeError, ValueError):
        raise ValueError('Parâmetro numérico inválido.')
    if not minimo <= n <= maximo:
        raise ValueError(f'Parâmetro deve estar entre {minimo} e {maximo}.')
    return n

def texto(v):
    return str(v or '').strip()[:60]

def data(v):
    try:
        return date.fromisoformat(str(v))
    except ValueError:
        raise ValueError('Data inválida; use AAAA-MM-DD.')

def executar(nome: str, params: dict):
    if nome not in FERRAMENTAS:
        raise ValueError('Ferramenta não autorizada.')
    if not isinstance(params, dict):
        raise ValueError('Parâmetros inválidos.')
    limite = inteiro(params.get('limite'), 1, 10, 5)
    if nome == 'contar_clientes':
        return sql('SELECT COUNT(*) AS total_clientes FROM clientes')
    if nome == 'listar_filiais':
        return sql('SELECT nome, cidade, uf, bairro FROM filiais ORDER BY cidade, nome LIMIT 10')
    if nome == 'listar_veiculos':
        categoria, cidade = texto(params.get('categoria')), texto(params.get('cidade'))
        return sql('''SELECT v.marca, v.modelo, v.categoria, v.ano, v.diaria_base, v.status, f.cidade, f.nome AS filial
           FROM veiculos v JOIN filiais f ON f.id=v.filial_id
           WHERE (%s='' OR v.categoria LIKE CONCAT('%%',%s,'%%'))
             AND (%s='' OR f.cidade LIKE CONCAT('%%',%s,'%%'))
           ORDER BY v.diaria_base LIMIT %s''', (categoria,categoria,cidade,cidade,limite))
    if nome == 'consultar_disponibilidade':
        inicio, fim = data(params.get('inicio')), data(params.get('fim'))
        if fim <= inicio:
            raise ValueError('A data final deve ser posterior à data inicial.')
        categoria, cidade = texto(params.get('categoria')), texto(params.get('cidade'))
        return sql('''SELECT v.marca, v.modelo, v.categoria, v.ano, v.diaria_base, f.cidade, f.nome AS filial
           FROM veiculos v JOIN filiais f ON f.id=v.filial_id
           WHERE v.status='disponivel'
             AND (%s='' OR v.categoria LIKE CONCAT('%%',%s,'%%'))
             AND (%s='' OR f.cidade LIKE CONCAT('%%',%s,'%%'))
             AND NOT EXISTS (
               SELECT 1 FROM locacoes l WHERE l.veiculo_id=v.id
               AND l.status IN ('ativa','reservada')
               AND l.retirada_em < %s AND l.devolucao_prevista_em > %s
             )
             AND NOT EXISTS (
               SELECT 1 FROM manutencoes m WHERE m.veiculo_id=v.id
               AND m.data_entrada < %s
               AND (m.data_saida IS NULL OR m.data_saida >= %s)
             )
           ORDER BY v.diaria_base LIMIT %s''', (categoria,categoria,cidade,cidade,fim.isoformat(),inicio.isoformat(),fim.isoformat(),inicio.isoformat(),limite))
    if nome == 'locacoes_ativas':
        return sql('''SELECT l.id AS locacao, v.marca, v.modelo, l.retirada_em, l.devolucao_prevista_em, l.valor_total
            FROM locacoes l JOIN veiculos v ON v.id=l.veiculo_id
            WHERE l.status='ativa' ORDER BY l.devolucao_prevista_em LIMIT %s''', (limite,))
    if nome == 'receita_mensal':
        mes = inteiro(params.get('mes'), 1, 12)
        ano = inteiro(params.get('ano'), 2000, 2100)
        # Receita contratada = soma de locações concluídas/ativas pela data de retirada.
        return sql('''SELECT COUNT(*) AS quantidade_locacoes, COALESCE(SUM(valor_total),0) AS receita_contratada
            FROM locacoes WHERE status IN ('concluida','ativa') AND YEAR(retirada_em)=%s AND MONTH(retirada_em)=%s''', (ano,mes))
    if nome == 'pagamentos_pendentes':
        return sql('''SELECT COUNT(*) AS quantidade, COALESCE(SUM(valor),0) AS valor_pendente
           FROM pagamentos WHERE status='pendente' ''')
    if nome == 'ranking_veiculos':
        return sql('''SELECT v.marca,v.modelo,v.categoria,COUNT(*) AS numero_locacoes
            FROM locacoes l JOIN veiculos v ON v.id=l.veiculo_id
            WHERE l.status IN ('concluida','ativa')
            GROUP BY v.id,v.marca,v.modelo,v.categoria ORDER BY numero_locacoes DESC LIMIT %s''', (limite,))
    if nome == 'custos_manutencao':
        return sql('''SELECT v.marca,v.modelo, COUNT(*) AS manutencoes,
            ROUND(SUM(m.custo),2) AS custo_total
            FROM manutencoes m JOIN veiculos v ON v.id=m.veiculo_id
            GROUP BY v.id,v.marca,v.modelo ORDER BY custo_total DESC LIMIT %s''', (limite,))
    raise ValueError('Ferramenta desconhecida.')
