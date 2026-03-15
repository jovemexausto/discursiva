# Discursiva — Correção de Respostas Discursivas

Micro-serviço serverless para registrar e consultar correções de respostas
discursivas, com persistência SQL, fila assíncrona (SQS) e armazenamento S3.

---

## Arquitetura

```
                         ┌──────────────┐
   Browser ──► Next.js ──► API Gateway  │
                         └──────┬───────┘
                                │ invoke
                         ┌──────▼───────┐
                         │  Lambda: API │  (FastAPI + Mangum em prod)
                         └──┬───┬───┬───┘
                            │   │   │
                  ┌─────────┘   │   └─────────┐
                  ▼             ▼             ▼
             ┌────────┐   ┌────────┐   ┌──────────┐
             │Postgres│   │   S3   │   │    SQS   │
             └────────┘   └────────┘   └────┬─────┘
                                            │ trigger
                                     ┌──────▼───────┐
                                     │Lambda: Worker│
                                     └──┬───────┬───┘
                                        │       │
                                   ┌────▼──┐ ┌──▼──────┐
                                   │  S3   │ │Postgres │
                                   └───────┘ └─────────┘
```

### Fluxo

1. `POST /submissions` — salva o texto no S3, cria registro `PENDING` no Postgres, publica no SQS
2. Worker consome a fila, baixa o texto do S3, calcula nota, atualiza para `DONE`
3. `GET /submissions/{id}` — retorna detalhes + status + nota
4. `GET /submissions?student_id=abc` — lista paginada por aluno

### Estrutura

```
discursiva/
├── apps/
│   ├── api/           # Lambda handlers + FastAPI app (testes/dev)
│   ├── worker/        # Lambda handler (SQS) + worker de polling standalone
│   └── frontend/      # Next.js
├── packages/
│   ├── domain/        # Entidades, Use Cases, Ports — zero dependências externas
│   └── infra/         # Postgres (asyncpg), S3, SQS (boto3)
├── serverless.yml     # Lambdas + recursos AWS (API Gateway, SQS, S3)
├── docker-compose.yml # LocalStack + Postgres + API + Worker + Frontend
└── pyproject.toml     # UV workspace
```

---

## Como rodar localmente

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e Docker Compose
- [uv](https://docs.astral.sh/uv/) — gerenciador de pacotes Python
- [Node.js](https://nodejs.org/) >= 18 — apenas se quiser rodar o
  `serverless-offline` fora do Docker

### Opção A — Docker Compose (recomendado)

Sobe tudo: Postgres, LocalStack (S3 + SQS), API, Worker e Frontend.

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env

# 2. Subir todos os serviços
docker compose up --build

# API disponível em http://localhost:8000
# Frontend disponível em http://localhost:3000
```

O `init-localstack.sh` cria automaticamente o bucket S3 e as filas SQS
assim que o LocalStack fica saudável.

### Opção B — serverless-offline (emula API Gateway + Lambda localmente)

```bash
# 1. Dependências Python
uv sync

# 2. Dependências Node
npm install

# 3. Subir infraestrutura (Postgres + LocalStack)
docker compose up postgres localstack -d

# 4. Aguardar LocalStack
docker compose logs -f localstack   # espere "Ready."

# 5. Deploy no LocalStack
npx serverless deploy --stage local

# 6. Iniciar API Gateway + Lambda emulados
npx serverless offline --stage local

# API em http://localhost:8000
```

> **Nota:** o `serverless-offline-sqs` faz polling da fila e invoca o worker
> Lambda automaticamente. Se preferir o worker standalone (mais simples):
> ```bash
> uv run python -m worker.main
> ```

---

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/submissions` | Cria submissão. Body: `{"student_id": "abc", "text": "..."}` |
| `GET`  | `/submissions/{id}` | Retorna detalhes + status + nota |
| `GET`  | `/submissions?student_id=abc&limit=20&offset=0` | Lista paginada por aluno |
| `GET`  | `/health` | Health check |

### Exemplos curl

```bash
# Criar submissão
curl -s -X POST http://localhost:8000/submissions \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "aluno-42",
    "text": "A educação brasileira enfrenta desafios significativos.\n\nEntre os principais problemas está a desigualdade de acesso.\n\nInvestimentos em infraestrutura e tecnologia são fundamentais."
  }' | jq

# Consultar por ID
curl -s http://localhost:8000/submissions/<id> | jq

# Listar por aluno
curl -s "http://localhost:8000/submissions?student_id=aluno-42" | jq
```

Uma **Postman collection** está em [`collection.json`](collection.json).

---

## Testes

```bash
uv run pytest          # 27 testes: domínio (16) + API (11)
uv run pytest -v       # verbose
```

Todos os testes usam fakes in-memory — não precisam de Postgres, S3 ou SQS.

---

## Arquitetura AWS (Produção)

**API Gateway + Lambda:** Cada endpoint é uma função Lambda independente
(`createSubmission`, `getSubmission`, `listSubmissions`). O API Gateway REST
roteia cada `path/method` para a Lambda correta, com throttling, autenticação
(Cognito/JWT) e logging automático no CloudWatch. Cada função escala
independentemente.

**S3:** Textos armazenados com versionamento e lifecycle policies. Acesso via
IAM Roles nas Lambdas — sem credenciais hardcoded. Para textos grandes,
presigned URLs permitem upload direto do frontend sem passar pela Lambda.

**SQS + Lambda Worker:** O SQS desacopla a criação de submissões do
processamento assíncrono. O Lambda Service faz polling da fila automaticamente
e invoca o worker ao receber mensagens. `batchSize: 1` garante isolamento entre
mensagens. A **DLQ** (`corrections-dlq`) captura mensagens que falharam 3
vezes consecutivas (`maxReceiveCount: 3`), evitando loops infinitos de retry.

**RDS Postgres + RDS Proxy:** Em produção o Postgres fica em RDS com Multi-AZ.
Um RDS Proxy na frente gerencia o pool de conexões — essencial para Lambda, que
pode abrir centenas de conexões simultâneas sem o Proxy. Cada Lambda cria uma
conexão (max_size=1) e fecha no `finally` — o Proxy multiplexa upstream.

**Observabilidade:** CloudWatch Logs automático por Lambda. Alarme no tamanho
da DLQ para detectar falhas de processamento. AWS X-Ray habilitável com
`tracing: true` no `serverless.yml` para tracing distribuído ponta a ponta:
API Gateway → Lambda → SQS → Worker → RDS.

---

## Decisões técnicas

**Clean Architecture (Ports & Adapters):** O domínio (`packages/domain`) é
Python puro, sem dependências externas. Use Cases dependem de Protocols
(`SubmissionRepository`, `StoragePort`, `QueuePort`), implementados em
`packages/infra`. Trocar DynamoDB por Postgres, ou RabbitMQ por SQS, não toca
na lógica de negócio.

**`asyncio.run()` por invocação Lambda:** Cada handler cria um event loop
novo via `asyncio.run()` (Python 3.12+). O pool asyncpg é criado e fechado
dentro do mesmo loop — evita o problema de pool inválido entre invocações, que
ocorre quando se reutiliza um pool criado em um loop destruído.

**UV Workspace Monorepo:** Cada pacote tem seu próprio `pyproject.toml` e
dependências declaradas explicitamente, mas compartilham lockfile e virtualenv.
Importações entre pacotes (`discursiva-domain`, `discursiva-infra`) funcionam
como pacotes instalados — sem `sys.path` hacks no código de produção.

**Idempotência no worker:** Antes de processar, o worker verifica se o status
é `PENDING`. Mensagens duplicadas (redelivery do SQS) são descartadas
silenciosamente — a submissão não é reprocessada.

**Scoring determinístico:** 5 critérios ortogonais (comprimento, parágrafos,
vocabulário rico, pontuação, diversidade lexical), cada um valendo até 2
pontos. Lógica pura, sem I/O, 100% testável.
