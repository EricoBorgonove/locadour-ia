# WhatsApp + MySQL + Ollama: Locadora com 3 agentes

Projeto didático independente do Langflow. **Não utiliza API oficial do WhatsApp**. Neonize é uma biblioteca não oficial, sujeita a falhas/bloqueios; use um número de testes e não utilize para disparos em massa.

## Arquitetura

1. **Decisor** (Ollama): classifica intenção e decide o domínio.
2. **Executor** (Ollama + Python): escolhe operação/argumentos; Python valida e executa SQL fixo com conta somente leitura.
3. **Intérprete** (Ollama): transforma resultados comprovados em mensagem natural para WhatsApp.

## Preparação

Use Python 3.10+ e MySQL 8+. Importar **uma única vez** o banco `locadora_veiculos_mysql.sql` que acompanha este ZIP. **CUIDADO: a importação apaga e recria a base `locadora_ia_demo`**. Não rode novamente se já houver alterações que queira preservar.

```bash
mysql -u root -p < locadora_veiculos_mysql.sql
```

Em seguida, edite a senha no arquivo `sql/criar_usuario_bot.sql` e execute:

```bash
mysql -u root -p < sql/criar_usuario_bot.sql
```

Esse usuário terá apenas `SELECT` sobre a base de demonstração. Em instalação MySQL remota, ajuste o host do usuário e restrinja a rede; o exemplo utiliza `localhost`.

## Instalação Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
ollama pull qwen2.5:3b
```

No Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
ollama pull qwen2.5:3b
```

Edite `.env`: inclua a senha do banco, o nome do modelo instalado e o endereço do Ollama. `pypdf` é incluído por compatibilidade com a experiência anterior, mas o projeto atual não consulta PDFs.

## Teste sem WhatsApp

Com Ollama funcionando (`ollama serve`, se necessário) e o MySQL iniciado:

```bash
python terminal.py
```

Perguntas sugeridas:
- Quantos clientes cadastrados?
- Liste cinco SUVs.
- Quanto foi a receita contratada em outubro de 2026?
- Quais os cinco veículos mais alugados?
- Quais os custos mais altos de manutenção?
- Quais veículos parecem disponíveis entre 2026-11-12 e 2026-11-15?
