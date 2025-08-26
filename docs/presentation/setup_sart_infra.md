# Setup da Infraestrutura Inicial - POC
*Versão 1.0 - 26/08/2025*

## 🎯 Objetivo

Configurar toda a infraestrutura necessária para o desenvolvimento da POC do sistema BPM com IA, garantindo que a equipe tenha um ambiente funcional desde o dia 1.

---

## 🏗️ Arquitetura da Infraestrutura POC

```bash
┌─────────────────────────────────────────────────────────┐
│                    Development Environment              │
├─────────────────────────────────────────────────────────┤
│  Frontend (React)    │     AI Agents       │  Services  │
│  ├── BPMN Editor     │    ├── Process      │  ├── API   │
│  ├── Form Builder    │    ├── Form         │  ├── Auth  │
│  └── Dashboard       │    └── Orchestrator │  └── Engine│
├─────────────────────────────────────────────────────────┤
│                     Data Layer                          │
│  PostgreSQL  │  Redis Cache  │  MinIO Storage           │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Componentes da Infraestrutura

### 1. Ambiente de Desenvolvimento

#### 1.1 Containers Docker
**Arquivo: `docker-compose.yml`**
- **PostgreSQL 15:** Banco principal
- **Redis 7:** Cache e sessões
- **MinIO:** Object storage para arquivos
- **Nginx:** Proxy reverso
- **Grafana + Prometheus:** Monitoramento básico

#### 1.2 Variáveis de Ambiente
**Arquivo: `.env`**
```env
# Database
POSTGRES_DB=bpm_poc
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure_password
DATABASE_URL=postgresql://admin:secure_password@postgres:5432/bpm_poc

# Redis
REDIS_URL=redis://redis:6379/0

# MinIO
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET=bpm-attachments

# AI Services
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=...

# Application
SECRET_KEY=your-super-secret-key-here
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 2. Repositório e Versionamento

#### 2.1 Estrutura Git
```
main (branch de produção)
├── develop (branch de desenvolvimento)
├── feature/process-designer
├── feature/form-builder
├── feature/frontend-ui
└── release/poc-v1.0
```

#### 2.2 Configuração CI/CD Básica
**GitHub Actions / GitLab CI:**
- Testes automatizados
- Build de containers
- Deploy automático para desenvolvimento
- Verificações de qualidade de código

### 3. Banco de Dados

#### 3.1 Schema Inicial - PostgreSQL
```sql
-- Usuários e autenticação
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Processos BPMN
CREATE TABLE processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    version INTEGER DEFAULT 1,
    bpmn_xml TEXT NOT NULL,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- Instâncias de processo (chamados)
CREATE TABLE process_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID REFERENCES processes(id),
    started_by UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'active',
    current_task VARCHAR(255),
    form_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tarefas em andamento
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_id UUID REFERENCES process_instances(id),
    task_name VARCHAR(255) NOT NULL,
    assigned_to UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP NULL
);

-- Formulários dinâmicos
CREATE TABLE form_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    schema JSONB NOT NULL,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Anexos
CREATE TABLE attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_id UUID REFERENCES process_instances(id),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    uploaded_by UUID REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT NOW()
);
```

#### 3.2 Dados de Teste
```sql
-- Usuários de teste
INSERT INTO users (email, name, role) VALUES
('admin@company.com', 'Administrador Sistema', 'admin'),
('supervisor@company.com', 'Supervisor TI', 'supervisor'),
('gerente@company.com', 'Gerente Operações', 'manager'),
('diretor@company.com', 'Diretor Executivo', 'director'),
('user1@company.com', 'João Silva', 'user'),
('user2@company.com', 'Maria Santos', 'user');
```

---

## 📦 Setup de Desenvolvimento

### 1. Requisitos do Sistema
**Mínimo por desenvolvedor:**
- **CPU:** 8 cores / 16 threads
- **RAM:** 16GB (32GB recomendado)
- **Storage:** 500GB SSD
- **OS:** Windows 11 / macOS / Ubuntu 22.04+

### 2. Ferramentas Necessárias
```bash
# Ferramentas base
├── Docker Desktop 4.20+
├── Node.js 18+ (com npm/yarn)
├── Python 3.11+
├── Git 2.40+
├── VSCode + Extensions recomendadas

# Extensions VSCode
├── Python
├── Vue Language Features (Volar)
├── TypeScript Vue Plugin (Volar)
├── Docker
├── GitLens
├── Thunder Client (API testing)
└── PostgreSQL (database management)
```

### 3. Configuração do Ambiente Local

#### 3.1 Clone e Setup Inicial
```bash
# Clone do repositório
git clone https://github.com/company/bpm-ai-poc.git
cd bmp-ai-poc

# Setup das variáveis de ambiente
cp .env.example .env
# Editar .env com as configurações específicas

# Subir containers de desenvolvimento
docker-compose up -d

# Verificar se todos os serviços estão rodando
docker-compose ps
```

#### 3.2 Setup Backend (Python)
```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar migrações
alembic upgrade head

# Carregar dados de teste
python scripts/seed_data.py

# Executar testes
pytest

# Iniciar servidor de desenvolvimento
uvicorn src.main:app --reload --port 8000
```

#### 3.3 Setup Frontend (Vue.js)
```bash
cd src/frontend

# Instalar dependências
npm install

# Executar em modo desenvolvimento
npm run dev

# Executar testes
npm run test

# Build para produção (quando necessário)
npm run build
```

### 4. APIs e Chaves Necessárias

#### 4.1 OpenAI / Claude
```bash
# OpenAI (GPT-4)
OPENAI_API_KEY=sk-proj-...
OPENAI_ORG_ID=org-...

# Anthropic (Claude)
CLAUDE_API_KEY=sk-ant-...
```

#### 4.2 LangChain (Observability)
```bash
# LangSmith para debug
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=bpm-poc
```

---

## 🔧 Configurações dos Microserviços

### 1. Process Engine Service
**Porta:** 8001  
**Framework:** FastAPI + Camunda (ou engine própria)  
**Responsabilidades:**
- Execução de workflows BPMN
- Gerenciamento de tarefas
- APIs de processo

### 2. Form Builder Service
**Porta:** 8002  
**Framework:** FastAPI + SQLAlchemy  
**Responsabilidades:**
- CRUD de formulários
- Validação de schemas
- Rendering de formulários

### 3. User Management Service
**Porta:** 8003  
**Framework:** FastAPI + JWT  
**Responsabilidades:**
- Autenticação/autorização
- Gerenciamento de usuários
- Controle de acesso

### 4. AI Agents Orchestrator
**Porta:** 8004  
**Framework:** FastAPI + LangChain + CrewAI  
**Responsabilidades:**
- Coordenação entre agentes
- Processamento de linguagem natural
- Geração de fluxos e formulários

---

## 🔒 Segurança e Compliance

### 1. Autenticação
- JWT tokens com expiração
- Refresh tokens
- Rate limiting (100 req/min por usuário)
- CORS configurado para domínios específicos

### 2. Banco de Dados
- Conexões SSL
- Passwords criptografadas (bcrypt)
- Logs de auditoria
- Backup diário automático

### 3. APIs Externas
- API keys em variáveis de ambiente
- Rate limiting para APIs de IA
- Fallbacks para indisponibilidade
- Logs de uso e custos

---

## 📊 Monitoramento e Observabilidade

### 1. Métricas Básicas
**Prometheus + Grafana:**
- Tempo de resposta das APIs
- Uso de CPU/RAM dos containers
- Latência do banco de dados
- Número de requests por endpoint
- Taxa de erro das APIs de IA

### 2. Logs Estruturados
**ELK Stack (básico):**
- Logs centralizados em JSON
- Correlação por request ID
- Alertas para erros críticos
- Dashboard de logs em tempo real

### 3. Health Checks
- Endpoint `/health` em todos os serviços
- Verificação de dependências externas
- Status do banco e cache
- Disponibilidade das APIs de IA

---

## 🚀 Plano de Deploy

### 1. Ambiente Local (Semana 1)
- Docker Compose completo
- Todos os serviços funcionando
- Dados de teste carregados
- Testes automatizados passando

### 2. Ambiente de Desenvolvimento (Semana 2)
- Deploy automatizado via CI/CD
- URLs públicas para validação
- Integração com APIs de IA reais
- Monitoramento básico ativo

### 3. Ambiente de Demo (Semana 3)
- Infraestrutura estável
- Dados de demonstração
- Performance otimizada
- Backup e recovery testados

---

## 📋 Checklist de Setup

### ✅ Semana Atual (Setup)
- [ ] Repositório Git criado e configurado
- [ ] Docker Compose funcionando localmente
- [ ] Banco PostgreSQL com schema inicial
- [ ] APIs de IA configuradas e testadas
- [ ] Ambiente de desenvolvimento de cada dev
- [ ] CI/CD pipeline básico
- [ ] Documentação de setup atualizada

### 🔄 Próxima Semana (Desenvolvimento)
- [ ] Todos os microserviços rodando
- [ ] Testes automatizados implementados
- [ ] Monitoramento básico ativo
- [ ] Deploy automático para dev
- [ ] Performance baseline estabelecida

### 🎯 Semana 3 (Pre-Demo)
- [ ] Ambiente de demo estável
- [ ] Dados de teste realísticos
- [ ] Monitoramento completo
- [ ] Backup e recovery testados
- [ ] Documentação final

---

## 💰 Custos Estimados (3 semanas)

### Infraestrutura
- **Cloud VMs:** R$ 1.500 (3 instâncias médias)
- **Storage:** R$ 200 (500GB SSD)
- **Bandwidth:** R$ 300 (estimativa)
- **Monitoramento:** R$ 400 (ferramentas)

### APIs de IA
- **OpenAI (GPT-4):** R$ 800 (estimativa de tokens)
- **Claude (Anthropic):** R$ 600 (estimativa de tokens)
- **LangChain Plus:** R$ 200 (observabilidade)

### Ferramentas
- **GitHub Actions:** R$ 0 (uso gratuito)
- **Docker Registry:** R$ 100 (armazenamento)
- **SSL Certificates:** R$ 0 (Let's Encrypt)

**Total Infraestrutura: R$ 4.200** (10% do budget POC)

---

## 🚨 Riscos e Contingências

### Risco Alto
**APIs de IA indisponíveis ou com limite**
- *Contingência:* Multiple providers + fallback local

### Risco Médio  
**Performance abaixo do esperado**
- *Contingência:* Profile desde semana 1 + otimizações

### Risco Baixo
**Problemas de rede/conectividade**
- *Contingência:* Ambiente local completo

---

## 📞 Contatos e Responsabilidades

### Infrastructure Team
- **Tech Lead:** [Nome] - Setup geral e arquitetura
- **DevOps:** [Nome] - CI/CD e deploy
- **Backend:** [Nome] - APIs e banco
- **Frontend:** [Nome] - Interface e integração

### External Support
- **Cloud Provider:** [AWS/Azure/GCP] - Suporte técnico
- **OpenAI/Anthropic:** APIs de IA
- **Monitoramento:** [Ferramenta] - Observabilidade

---

*Este documento será atualizado conforme o progresso do setup e feedback da equipe.*
