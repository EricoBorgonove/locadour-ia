# WhatsApp + MySQL + Ollama: Locadora com 3 agentes

Projeto didático independente do Langflow. **Não utiliza API oficial do WhatsApp**. Neonize é uma biblioteca não oficial, sujeita a falhas/bloqueios; use um número de testes e não utilize para disparos em massa.

## Arquitetura

1. **Decisor** (Ollama): classifica intenção e decide o domínio.
2. **Executor** (Ollama + Python): escolhe operação/argumentos; Python valida e executa SQL fixo com conta somente leitura.
3. **Intérprete** (Ollama): transforma resultados comprovados em mensagem natural para WhatsApp.
