import unittest
from unittest.mock import patch
from src.ferramentas import executar

class FerramentasTest(unittest.TestCase):
    def test_nao_aceita_sql_livre(self):
        with self.assertRaises(ValueError):
            executar('DROP TABLE clientes', {})

    def test_data_invalida(self):
        with self.assertRaises(ValueError):
            executar('consultar_disponibilidade', {'inicio': '2026-11-20', 'fim': '2026-11-19'})

    @patch('src.ferramentas.sql', return_value=[{'total_clientes': 500}])
    def test_contagem(self, fake_sql):
        self.assertEqual(executar('contar_clientes', {}), [{'total_clientes': 500}])
        fake_sql.assert_called_once()

    @patch('src.ferramentas.sql', return_value=[])
    def test_limite(self, fake_sql):
        with self.assertRaises(ValueError):
            executar('listar_veiculos', {'limite': 1000})
        fake_sql.assert_not_called()

if __name__ == '__main__':
    unittest.main()
