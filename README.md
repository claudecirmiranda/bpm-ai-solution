# Sistema de Chamados com Agentes de IA

Sistema avançado de gerenciamento de chamados com fluxos BPMN automatizados e agentes de IA especializados para criação de processos e formulários.

## 🏗️ Arquitetura

### Agentes de IA Especializados
- **Orchestrator Agent**: Coordena outros agentes e analisa requisições
- **Process Designer Agent**: Cria fluxos BPMN a partir de linguagem natural
- **Form Builder Agent**: Gera formulários dinâmicos com validações inteligentes

### Serviços Core
- **Process Engine**: Executa processos BPMN e gerencia instâncias
- **Form Service**: Renderiza e processa formulários
- **User Management**: Autenticação e autorização

### Infraestrutura
- **PostgreSQL**: Banco de dados principal
- **Redis**: Cache e sessões
- **NGINX**: API Gateway e proxy reverso
- **Prometheus + Grafana**: Monitoramento

## 🚀 Setup Rápido

### Pré-requisitos
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM disponível
- Portas 3000, 8000-8005, 9090 livres

### 1. Clone e Configure

```bash
# Clone o repositório
git clone <repository_url>
cd ticket-system-ai

# Torna o script executável
chmod +x setup.sh

# Execute o setup automático
./setup.sh
```

### 2. Configure API Keys

Edite o arquivo `.env` criado automaticamente:

```bash
# Substitua pelas suas chaves reais
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here  # Opcional
```

### 3. Inicie os Serviços

```bash
# Inicia todos os serviços
docker-compose up -d

# Verifica status
docker-compose ps

# Acompanha logs
docker-compose logs -f orchestrator
```

### 4. Teste o Sistema

```bash
# Execute os testes automatizados
python test_agents.py

# Ou acesse as URLs diretamente:
# Frontend: http://localhost:3000
# Orchestrator: http://localhost:8000
# Grafana: http://localhost:3001 (admin/admin)
```

## 🧪 Validação do Setup

### Teste de Conectividade
```bash
# Verifica se todos os agentes estão respondendo
curl http://localhost:8000/health  # Orchestrator
curl http://localhost:8001/health  # Process Designer  
curl http://localhost:8002/health  # Form Builder
```

### Teste de Funcionalidade
```bash
# Teste de criação de processo via Orchestrator
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "CREATE_PROCESS",
    "user_input": "Criar processo de aprovação de férias",
    "context": {"category": "RH"}
  }'
```

### Teste de Análise de Agentes
```bash
# Verifica status de todos os agentes
curl http://localhost:8000/agents/status
```

## 📊 Database Schema

O sistema utiliza PostgreSQL com as seguintes tabelas principais:

### Tabelas Core
- `users` - Usuários do sistema
- `ticket_categories` - Categorias de chamados
- `tickets` - Chamados/solicitações
- `ticket_history` - Histórico de ações

### Tabelas BPMN
- `bpmn_processes` - Definições de processo
- `bpmn_elements` - Elementos dos processos
- `process_instances` - Instâncias em execução
- `process_tasks` - Tarefas ativas

### Tabelas de Formulários
- `forms` - Definições de formulários
- `form_fields` - Campos dos formulários

### Tabelas de Aprovação
- `approval_levels` - Níveis de aprovação
- `level_approvers` - Aprovadores por nível
- `ticket_approvals` - Aprovações específicas

## 🤖 Como Usar os Agentes

### Orchestrator Agent

O ponto central para todas as requisições:

```python
# Exemplo de uso via API
import httpx

async def create_vacation_process():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/orchestrate",
            json={
                "task_type": "CREATE_PROCESS",
                "user_input": "Preciso de um processo para solicitação de férias que passe por aprovação do supervisor e depois do RH",
                "context": {
                    "department": "TI",
                    "user_role": "employee"
                }
            }
        )
        return response.json()
```

### Process Designer Agent

Especializado em criar fluxos BPMN:

```python
# Criação direta de processo
async def design_process():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/execute",
            json={
                "task": "Criar processo de compra com 3 níveis de aprovação",
                "parameters": {
                    "category": "Compras",
                    "approval_levels": 3,
                    "sla_hours": 72
                }
            }
        )
        return response.json()
```

### Form Builder Agent

Especializado em criar formulários:

```python
# Criação de formulário
async def build_form():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8002/execute", 
            json={
                "task": "Criar formulário para solicitação de equipamento",
                "parameters": {
                    "fields": ["tipo_equipamento", "justificativa", "orcamento"],
                    "category": "TI"
                }
            }
        )
        return response.json()
```

## 🛠️ Desenvolvimento

### Estrutura de Arquivos
```
backend/
├── ai-agents/
│   ├── orchestrator/        # Agente coordenador
│   ├── process-designer/    # Criação de processos BPMN
│   └── form-builder/        # Criação de formulários
└── services/
    ├── process-engine/      # Execução de processos
    ├── form-builder/        # Renderização de forms
    └── user-management/     # Usuários e auth
```

### Logs e Debugging
```bash
# Logs específicos por serviço
docker-compose logs -f orchestrator
docker-compose logs -f process-designer
docker-compose logs -f form-builder

# Logs de todos os agentes
docker-compose logs -f orchestrator process-designer form-builder

# Debug mode (mais verbose)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Reinicialização Durante Desenvolvimento
```bash
# Rebuild apenas um serviço
docker-compose up --build -d orchestrator

# Reinicia com rebuild completo
docker-compose down && docker-compose up --build -d

# Reset completo (limpa volumes)
docker-compose down -v && docker-compose up --build -d
```

## 🔧 Configurações Avançadas

### Variáveis de Ambiente Importantes

```bash
# Performance dos Agentes
AGENT_TIMEOUT_SECONDS=30        # Timeout para chamadas entre agentes
AGENT_MAX_RETRIES=3            # Tentativas em caso de falha
AGENT_MEMORY_SIZE=100          # Tamanho do buffer de memória

# Configurações de IA
ANTHROPIC_API_KEY=sk-ant-...   # Chave da Anthropic (obrigatório)
OPENAI_API_KEY=sk-...          # Chave OpenAI (opcional, para futura integração)

# Database
DATABASE_POOL_SIZE=10          # Pool de conexões
DATABASE_MAX_OVERFLOW=20       # Conexões extras permitidas
```

### Monitoramento e Métricas

O sistema inclui monitoramento completo via Prometheus + Grafana:

- **Grafana Dashboard**: http://localhost:3001
  - Username: `admin`
  - Password: `admin`
  - Dashboards pré-configurados para agentes de IA

- **Prometheus**: http://localhost:9090
  - Métricas detalhadas de performance
  - Alertas configuráveis

- **Métricas Coletadas**:
  - Tempo de resposta dos agentes
  - Taxa de sucesso/falha
  - Uso de memória e CPU
  - Throughput de requests

## 🧩 Extensibilidade

### Adicionando Novos Agentes

1. **Crie o diretório**: `backend/ai-agents/novo-agente/`

2. **Implemente a interface padrão**:
```python
class NovoAgent:
    async def execute_task(self, request: AgentRequest):
        # Sua lógica aqui
        pass
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "agent": "novo-agente"}
    
    @app.get("/capabilities") 
    async def get_capabilities():
        return {"capabilities": ["capability1", "capability2"]}
```

3. **Registre no Orchestrator**:
```python
# Em orchestrator/app.py
self.agents[AgentType.NOVO_AGENTE] = AgentConfig(
    name="Novo Agente",
    endpoint="http://novo-agente:8000",
    capabilities=["nova_funcionalidade"]
)
```

4. **Adicione ao docker-compose.yml**

### Customizando Prompts dos Agentes

Os prompts dos agentes estão centralizados e podem ser facilmente customizados:

```python
# Exemplo: Customizando o Process Designer
class ProcessDesignerAgent:
    def __init__(self):
        self.system_prompt = """
        Seu prompt customizado aqui...
        Especializado em processos da sua empresa...
        """
```

## 📚 API Reference

### Orchestrator Endpoints

- `POST /orchestrate` - Orquestra execução de tarefas
- `GET /agents/status` - Status de todos os agentes
- `GET /health` - Health check

### Process Designer Endpoints

- `POST /execute` - Executa criação de processo
- `GET /capabilities` - Lista capacidades
- `GET /templates` - Templates de processo
- `POST /validate` - Valida BPMN XML

### Form Builder Endpoints

- `POST /execute` - Executa criação de formulário
- `GET /capabilities` - Lista capacidades  
- `GET /templates` - Templates de campos
- `POST /preview` - Preview HTML do formulário

## 🐛 Troubleshooting

### Problemas Comuns

**1. Agente não responde**
```bash
# Verifica logs
docker-compose logs agente-name

# Reinicia serviço específico
docker-compose restart agente-name
```

**2. Erro de API Key**
```bash
# Verifica se a chave está configurada
docker-compose exec orchestrator env | grep ANTHROPIC

# Atualiza variável sem restart
docker-compose exec orchestrator sh -c 'export ANTHROPIC_API_KEY=nova-chave'
```

**3. Banco de dados não conecta**
```bash
# Verifica status do postgres
docker-compose logs postgres

# Testa conexão manual
docker-compose exec postgres psql -U admin -d ticket_system -c "SELECT 1;"
```

**4. Performance lenta dos agentes**
```bash
# Verifica uso de recursos
docker stats

# Aumenta timeout se necessário
# No .env: AGENT_TIMEOUT_SECONDS=60
```

### Debug Mode

Para desenvolvimento ativo, use o modo debug:

```bash
# Inicia com rebuild automático e logs verbosos
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Ou apenas os agentes em modo debug
docker-compose up --build orchestrator process-designer form-builder
```

## 📈 Próximos Passos

Após o setup inicial bem-sucedido:

1. **Semana 1 - Dias 3-5**: Implementar Core Engine
   - Process Engine MVP
   - Form Builder API básica
   - Interface base do frontend

2. **Semana 2**: Desenvolvimento dos agentes
   - Refinamento dos prompts de IA
   - Editor BPMN visual
   - Interface drag-and-drop

3. **Semana 3**: Integração e validação
   - Testes end-to-end
   - Polimento da interface
   - Preparação da demo

## 🤝 Contribuição

### Testando Mudanças
```bash
# Executa testes automatizados
python test_agents.py

# Testes específicos de um agente
curl -X POST http://localhost:8001/execute -d '{"task":"test"}'
```

### Estrutura de Commits
- `feat(agent):` - Nova funcionalidade em agente
- `fix(orchestrator):` - Correção no orchestrator
- `docs:` - Atualizações de documentação
- `test:` - Adição ou correção de testes

---

## 📞 Suporte

- **Logs**: `docker-compose logs -f`
- **Health Check**: `curl http://localhost:8000/health`
- **Testes**: `python test_agents.py`
- **Monitoramento**: http://localhost:3001

**Status do Setup**: ✅ Pronto para desenvolvimento da Semana 1!
