# Discursiva: Correção de Redações

Micro-serviço para submissão e correção assíncrona de textos discursivos. Stack: Python (asyncio) + Postgres + SQS + S3, com um frontend Next.js. Tudo sobe localmente com um único `docker compose up`.

## Contexto

O desafio pedia um back-end funcional em ~60 minutos. Como o tempo permitiu, optei por uma estrutura um pouco mais cuidadosa: separação de camadas, testes unitários sem I/O, schema SQL com tipos nativos e índices adequados. Nada que não estaria no projeto de produção real.

## Como rodar

Primeiro, certifique-se de que você tem o docker rodando e execute o comando:

```bash
docker compose up
```

Então é só esperar subir tudo. O front será o último, então aguarde até que ele esteja disponível.

_Optei por manter '.env.local' no versionamento, pois contém apenas informações locais e facilita a execução do projeto, para um projeto real devemos evitar o versionamento de arquivos .env._

| Serviço    | URL                     |
|------------|-------------------------|
| API        | <http://localhost:8000> |
| Frontend   | <http://localhost:3000> |
| LocalStack | <http://localhost:4566> |

**Rodar os testes:**

```bash
uv sync --all-groups
uv run pytest
```

A collection do Postman/Bruno está em `collection.json` na raiz.

## Endpoints

| Método | Rota                        | Descrição                              |
|--------|-----------------------------|----------------------------------------|
| POST   | `/submissions`              | Cria submissão, retorna `201` imediato |
| GET    | `/submissions/{id}`         | Detalhe, status e nota                 |
| GET    | `/submissions?student_id=X` | Lista paginada por aluno               |

**Exemplo:**

```bash
curl -s -X POST http://localhost:8000/submissions \
  -H "Content-Type: application/json" \
  -d '{"student_id": "aluno_01", "text": "Texto da redação..."}'
```

## Arquitetura

```mermaid
sequenceDiagram
    actor C as Client
    participant A as API Handler<br/>(Lambda)
    participant S as S3
    participant DB as Postgres
    participant Q as SQS
    participant W as Worker<br/>(Lambda / polling)

    C->>A: POST /submissions
    A->>S: upload texto (s3_key)
    A->>DB: INSERT status=PENDING
    A->>Q: publish {submission_id, s3_key}
    A-->>C: 201 Created

    Note over Q,W: assíncrono: dev usa polling loop,<br/>prod usa SQS Event Source Mapping

    Q->>W: mensagem
    W->>S: download texto
    W->>W: compute_score()
    W->>DB: UPDATE status=DONE, score=X
    W->>Q: delete message

    Note over Q,W: falha 3x? vai para DLQ (corrections-dlq)
```

O fluxo de uma submissão percorre quatro passos em sequência, mas a API responde `201` antes de qualquer processamento:

1. **Upload do texto** para S3 (LocalStack em dev, bucket real em prod).
2. **Insert** na tabela `submissions` com `status = PENDING`.
3. **Publish** na fila SQS with `submission_id` e `s3_key`.
4. **Worker** consome a mensagem, baixa o texto, calcula a nota e atualiza o registro para `DONE`.

### Por que polling em dev e trigger em prod?

Em produção, a Lambda worker é acionada automaticamente pela própria fila: SQS Event Source Mapping cuida disso, sem polling manual. Em desenvolvimento, esse mecanismo não existe localmente: a Lambda não está rodando como um runtime gerenciado, só existe como um container Python comum. Por isso o `worker/main.py` implementa um loop `asyncio` com long-polling (5 s de `WaitTimeSeconds` no `receive_message`). O código de processamento é o mesmo em ambos os ambientes, só o ponto de entrada muda (`handler.py` para Lambda, `main.py` para dev).

## Estrutura do projeto

```mermaid
graph LR
    subgraph apps["Serviços (apps/)"]
        API["<b>api/</b><br/><small>handlers · tests</small>"]
        WORKER["<b>worker/</b><br/><small>main.py</small>"]
        FRONT["<b>frontend/</b><br/><small>Next.js</small>"]
    end

    subgraph packages["Domínio & Infra (packages/)"]
        DOMAIN["<b>domain/</b><br/><small>Entidades · Use Cases<br/>Zero I/O, Unit Tests</small>"]
        INFRA["<b>infra/</b><br/><small>S3 · SQS · Postgres<br/>Migrations</small>"]
    end

    API ----> DOMAIN
    API ----> INFRA
    WORKER ----> DOMAIN
    WORKER ----> INFRA
    INFRA -.->|implements| DOMAIN
```

O projeto segue Clean Architecture em dois pacotes compartilhados:

- **`packages/domain`**: entidades, value objects, use cases e ports (interfaces). Zero dependências externas, zero I/O. Os testes unitários rodam 100% em memória com fakes injetados.
- **`packages/infra`**: implementações concretas: `S3Storage`, `SQSQueue`, `PostgresSubmissionRepository`. Usa `boto3` com `run_in_executor` para não bloquear o event loop, e `asyncpg` para conexões assíncronas com Postgres.

Os serviços em `apps/` importam os dois pacotes acima e não contêm lógica de negócio, só wiring e I/O.

## Scoring

Cinco critérios ortogonais, cada um valendo até 2 pontos (máximo 10):

| Critério            | Threshold                    |
|---------------------|------------------------------|
| Comprimento         | >= 50 palavras = 2 pts       |
| Parágrafos          | >= 3 parágrafos = 2 pts      |
| Vocabulário rico    | >= 5 palavras longas = 2 pts |
| Pontuação           | >= 3 sinais = 2 pts          |
| Diversidade lexical | palavra top < 10% = 2 pts    |

Lógica pura em `packages/domain/services/corrector.py`. 100% testável de forma isolada.

## Schema SQL

Schema completo em [`packages/infra/src/discursiva_infra/postgres/migrations/schema.sql`](packages/infra/src/discursiva_infra/postgres/migrations/schema.sql).

O campo `updated_at` é mantido por um trigger Postgres (`set_updated_at`), não pela aplicação.

O `schema.sql` atende ao requisito do desafio diretamente e é suficiente para um schema que não vai evoluir. Em um produto real com deploys contínuos, a primeira alteração de schema expõe a limitação: o arquivo não carrega histórico, então não há como saber o que já foi aplicado em cada ambiente nem aplicar só o delta. O Alembic resolve exatamente isso: cada alteração vira uma revisão versionada, o `alembic upgrade head` no CI leva qualquer ambiente ao estado correto a partir de onde ele está, e dá para reverter uma migration específica se necessário. O custo de adotar seria baixo dado que o projeto já usa `asyncpg`, e o Alembic tem suporte nativo a async via `run_sync`.

## AWS em produção

```mermaid
flowchart TD
    GW[API Gateway] --> L_CREATE(Lambda: createSubmission)
    GW --> L_GET(Lambda: getSubmission)
    GW --> L_LIST(Lambda: listSubmissions)
    
    subgraph Storage ["Camada de Dados"]
        S3[(S3 Bucket)]
        RDS[(RDS Proxy)]
    end

    subgraph Messaging ["Mensageria"]
        SQS[[SQS Queue]]
        DLQ[[SQS DLQ]]
    end

    L_CREATE --> S3
    L_CREATE --> RDS
    L_CREATE --> SQS

    L_GET --> RDS
    L_LIST --> RDS

    SQS -->|Trigger| L_WORKER(Lambda: Worker)
    SQS -.->|3 falhas| DLQ
    
    L_WORKER --> S3
    L_WORKER --> RDS
```

O `serverless.yml` já define tudo: funções, permissões IAM, bucket S3, fila SQS e DLQ. Para subir em produção seria só `sls deploy --stage prod`, sem tocar no código.

Sobre as decisões de infra que tomei: a API retorna `201` antes do worker processar porque não faz sentido deixar o cliente esperando uma correção que pode levar segundos. O SQS garante que a mensagem não se perde mesmo se o worker cair no meio do caminho, e a DLQ captura o que falhou três vezes para não perder dados silenciosamente.

O único gargalo real em escala seria o pool de conexões do Postgres com muitas Lambdas concorrentes. O RDS Proxy resolve isso sem mudança de código.

Para observabilidade: os logs já saem estruturados em JSON via `logging_config.py`, então no CloudWatch ficam indexáveis sem parser adicional. Para rastrear o caminho completo de uma requisição (API -> SQS -> Worker -> DB) colocaria AWS X-Ray. E um alarme no CloudWatch Metrics monitorando o tamanho da DLQ é o primeiro sinal de que algo está quebrando no worker.

## CI

GitHub Actions (`.github/workflows/ci.yml`) roda `uv run pytest` em todo push para `dev`. O workflow de deploy (`.github/workflows/deploy.yml`), que ocorre em push para `master`, está estruturado mas requer configuração de secrets AWS para execução real.

## Simulando Deploy

É possível simular o comportamento de produção (Lambda + SQS Event Source Mapping) localmente usando o Serverless Framework e LocalStack.
Para isso, você precisa ter o docker rodando, o [UV](https://docs.astral.sh/uv/getting-started/installation/) e o nodejs instalados.

1. **Instale as dependências:**

   ```bash
   npm run sync
   ```

2. **Derrube o ambiente padrão:**

   ```bash
   docker compose down -v
   ```

3. **Execute o deploy local:**

   ```bash
   npm run deploy:local
   ```

Isso iniciará o Postgres e o LocalStack (via `packages/infra/compose.sls.yml`) e realizará o deploy das funções. A API ficará disponível nos endpoints gerados pelo `serverless-offline`.

Para testar, utilize a collection do Postman ou Bruno, atualizando o endpoint para o endereço fornecido pelo `serverless-offline`. Como alternativa, é possível usar `curl` (substitua `XXXXXXXXXX` pelo identificador do endpoint gerado):

```bash
curl -s -X POST http://localhost:4566/restapis/XXXXXXXXXX/local/_user_request_/submissions \
  -H "Content-Type: application/json" \
  -d '{"student_id": "aluno_01", "text": "Texto da redação..."}'
```

Para inciar o frontend utilizando este deploy local, basta inciar o frontend em paralelo definindo `INTERNAL_API_URL` para o endpoint gerado pelo `serverless-offline`.  

```bash
export INTERNAL_API_URL="http://localhost:4566/restapis/XXXXXXXXXX/local/_user_request_"
npm --prefix apps/frontend run dev
```

---

> "A simplicidade é o último grau de sofisticação." — **Leonard Thiessen**
