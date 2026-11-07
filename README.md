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

## WhatsApp

```bash
python whatsapp.py
```

Na primeira conexão, escaneie o QR Code no WhatsApp > Dispositivos conectados > Conectar dispositivo. A sessão fica armazenada localmente. O bot ignora grupos por padrão (`ALLOW_GROUPS=false`) e mensagens sem texto. Não compartilhe o banco de sessão.

## Testes

```bash
python -m unittest discover -s tests -v
```

## Limitações

- Somente leitura: não cadastra clientes, não altera locações, não confirma reservas nem recebe pagamentos.
- Relatórios administrativos são bloqueados por padrão no WhatsApp. Para testá-los, inclua os JIDs exatos dos remetentes autorizados em `ADMIN_JIDS`, separados por vírgula; o formato de JID depende da versão do Neonize. Ainda é um exemplo didático e não substitui autenticação forte nem controles de privacidade. Nunca conecte dados pessoais reais a um número público sem revisão de segurança.
- Disponibilidade é aproximação baseada nos registros existentes e no status atual, não é garantia de reserva ou preço final.
- A classificação/extração de parâmetros depende da qualidade do modelo Ollama; quando dados estiverem faltando, o bot pede esclarecimento.
- A execução foi validada estaticamente e com testes unitários simulados; integração real exige Ollama, MySQL e login WhatsApp em execução no computador do usuário.
