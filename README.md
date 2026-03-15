# Discursiva — Correção de Redações (Teste Técnico)

E aí! Este é um micro-serviço serverless desenvolvido em Python para gerenciar a submissão e correção de textos discursivos. Ele usa S3 para armazenar os textos, SQS para processamento assíncrono e Postgres para manter o status e as notas.

## Como rodar localmente

A forma mais rápida é usar o Docker Compose, que já sobe o banco, o LocalStack (emulando S3/SQS) e os serviços.

```bash
# 1. Prepare as variáveis de ambiente
cp .env.example .env

# 2. Suba tudo
docker compose up --build
```

- **API:** `http://localhost:8000`
- **Frontend:** `http://localhost:3000`
- **Docs (Swagger):** `http://localhost:8000/docs`

---

## Endpoints Principais

- **`POST /submissions`**: Envia uma redação. 
  - Ex: `{"student_id": "aluno_123", "text": "Meu texto..."}`
- **`GET /submissions/{id}`**: Vê o status e a nota.
- **`GET /submissions?student_id=abc`**: Lista submissões de um aluno.

---

## Arquitetura AWS (Produção)

Para levar esse projeto para o mundo real na AWS, usaríamos:

1.  **API Gateway + Lambda**: Cada endpoint da API seria uma função Lambda. O API Gateway cuida do roteamento, throttling e segurança (JWT/Cognito).
2.  **S3**: O texto original das redações vai direto para um bucket S3. As Lambdas usam permissões de IAM para ler/escrever.
3.  **SQS**: A Lambda de "criação" apenas joga um evento na fila SQS e responde 201 pro usuário. Isso garante que a API seja rápida e resiliente a picos de carga.
4.  **Lambda Worker**: Uma função Lambda configurada para ser triggada pela fila SQS. Ela processa a mensagem, baixa o texto do S3, calcula a nota e atualiza o banco.
5.  **RDS Postgres**: Banco de dados relacional para persistência, preferencialmente com um **RDS Proxy** na frente para gerenciar o pool de conexões das Lambdas.

### Escalabilidade e Observabilidade

-   **Escalabilidade**: Como tudo é serverless (Lambda/SQS/S3), o sistema escala automaticamente conforme o volume de redações aumenta.
-   **Logs**: Centralizados no **CloudWatch Logs** para todas as funções.
-   **Retries e DLQ**: O SQS está configurado com uma **Dead Letter Queue (DLQ)**. Se um worker falhar 3 vezes em processar uma redação (ex: erro inesperado ou timeout), a mensagem vai para a DLQ para não perdermos dados e podermos investigar o erro.
-   **Rastreamento**: Usamos **AWS X-Ray** para monitorar o caminho completo da requisição (API -> SQS -> Worker -> DB) e identificar gargalos.

---

## Design e Organização

O projeto segue princípios de **Clean Architecture**. O domínio (`packages/domain`) não conhece frameworks ou banco de dados. Toda a implementação técnica (S3, SQS, Postgres) vive na camada de infraestrutura (`packages/infra`). Isso facilitou muito os testes unitários, que rodam 100% em memória sem precisar de infraestrutura real.

```bash
# Rodar testes
uv run pytest
```
**Scoring determinístico:** 5 critérios ortogonais (comprimento, parágrafos,
vocabulário rico, pontuação, diversidade lexical), cada um valendo até 2
pontos. Lógica pura, sem I/O, 100% testável.
