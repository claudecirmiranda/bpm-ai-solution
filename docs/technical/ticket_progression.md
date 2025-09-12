# Progressão do Ticket

Proposta de um **baseline prático** (modelo de dados + endpoints + UI + passos de implementação) para tornar o fluxo de progresso de tickets funcional e simples, mas com portas abertas para integrar BPMN/aprovações complexas depois.

Dividido em: visão geral, modelos de dados (tabelas novas / reuso), endpoints FastAPI sugeridos, exemplos cURL para testar ponta-a-ponta, componentes/UX front-end sugeridos, e um plano de implementação incremental (prioridades para MVP).

## 1) Visão geral (objetivo do baseline)
* * * 

*   Mostrar tickets abertos / por responsável / por setor.
    
*   Mostrar **histórico / timeline** com todas as ações realizadas.
    
*   Permitir “progredir” o ticket: enviar ação (ex: iniciar análise, reprovar, aprovar, concluir), comentário, e opcionalmente trocar status/assignee.
    
*   Persistir cada passo com metadados (quem, quando, comentário, dados de formulário).
    
*   Ter estrutura que possa suportar níveis de aprovação e integração BPM no futuro.
    

## 2) Modelos de dados — reuso e extensão
* * * 

Já tem tabelas importantes: `tickets`, `ticket_history`, `approval_levels`, `ticket_approvals`, `bpmn_processes`, `process_instances`. Sugestão de **duas tabelas novas** e indicado reuso:
**Opção leve (recomendada para MVP)** — nova tabela `ticket_progressions` ligada a `tickets`:

```sql
CREATE TABLE ticket_progressions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_id uuid NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
  step_name varchar(150) NOT NULL,           -- ex: "review_started", "approved", "closed"
  action varchar(100) NOT NULL,              -- ex: "start_review", "approve", "reject", "close"
  performed_by uuid,                         -- FK para users.id (nullable se sistema)
  previous_status varchar(50),
  new_status varchar(50),
  comments text,
  metadata jsonb,                            -- informações extras (ex: form snapshot)
  created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ticket_progressions_ticket ON ticket_progressions(ticket_id);

```

> **Por que nova tabela?** `ticket_history` já existe e cumpre parte do papel — mas ter `ticket_progressions` com link a `step_name`/`action` e `metadata` facilita buscas por workflow e integração a `workflow_steps`. Pode manter `ticket_history` para auditoria, e gravar paralelo nele (ou fazer triggers).

**(Opcional)** Tabelas para definir workflows reutilizáveis:

```sql
CREATE TABLE workflows (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name varchar(255) NOT NULL,
  description text,
  category_id uuid,
  metadata jsonb,
  is_active boolean DEFAULT true,
  created_by uuid,
  created_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workflow_steps (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id uuid REFERENCES workflows(id) ON DELETE CASCADE,
  step_number integer NOT NULL,
  name varchar(150) NOT NULL,        -- ex: "triagem", "análise", "aprovacao_nivel_1"
  action_type varchar(30) DEFAULT 'manual', -- 'manual' | 'auto' | 'approval'
  required_role varchar(60),
  timeout_hours integer,
  metadata jsonb
);

```

## 3) Endpoints FastAPI sugeridos (MVP)
* * * 

Endpoints novos/alterados e breve Pydantic shapes.

Endpoints para gerenciar progressão (MVP)
-----------------------------------------

*   `GET /tickets/` — já existente — listar (filtrar por status, category, assigned_to).
    
*   `GET /tickets/{ticket_id}` — já existente — retorna `form_id` e `form_data`.
    
*   `GET /tickets/{ticket_id}/progressions` — retorna lista de progressões (ticket_progressions).
    
*   `POST /tickets/{ticket_id}/progress` — registrar ação de progresso (principal).
    
*   `GET /workflows/` & `POST /workflows/` — opcional (para criar workflows reutilizáveis).
    
*   `GET /workflows/{id}/steps` — opcional.
    

### Exemplo Pydantic + endpoint (simplificado)

```python
# schemas.py (excertos)
from pydantic import BaseModel
from typing import Optional, Dict

class TicketProgressCreate(BaseModel):
    action: str               # ex: "start_review", "approve", "close"
    performed_by: Optional[str]  # uuid string
    comments: Optional[str] = None
    new_status: Optional[str] = None
    metadata: Optional[Dict] = None

class TicketProgressOut(BaseModel):
    id: str
    ticket_id: str
    action: str
    performed_by: Optional[str]
    previous_status: Optional[str]
    new_status: Optional[str]
    comments: Optional[str]
    metadata: Optional[Dict]
    created_at: str

```

```python
# app.py (endpoints)
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.future import select
import uuid, datetime

router = APIRouter()

@router.get("/tickets/{ticket_id}/progressions")
async def list_progressions(ticket_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(TicketProgression).where(TicketProgression.ticket_id == ticket_id).order_by(TicketProgression.created_at))
    rows = res.scalars().all()
    return [row_to_dict(r) for r in rows]

@router.post("/tickets/{ticket_id}/progress", response_model=TicketProgressOut)
async def progress_ticket(ticket_id: uuid.UUID, payload: TicketProgressCreate, db: AsyncSession = Depends(get_db)):
    # 1) load ticket
    res = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = res.scalar_one_or_none()
    if not ticket:
        raise HTTPException(404, "Ticket não encontrado")

    prev_status = ticket.status
    # 2) update ticket status (if provided)
    if payload.new_status:
        ticket.status = payload.new_status
        ticket.updated_at = datetime.utcnow()

    # 3) build progression record
    prog = TicketProgression(
        ticket_id=ticket.id,
        step_name=payload.action,
        action=payload.action,
        performed_by=payload.performed_by,
        previous_status=prev_status,
        new_status=payload.new_status,
        comments=payload.comments,
        metadata=payload.metadata or {}
    )
    db.add(prog)
    db.add(ticket)
    await db.commit()
    await db.refresh(prog)
    # optional: also insert into ticket_history for auditing
    return row_to_dict(prog)

```

> `row_to_dict` = função util para serializar SQLAlchemy model -> dict.

## 4) Exemplo cURL (ponta-a-ponta MVP)
* * * 

1.  Criar ticket (já tem):
    

```curl
curl -X POST 'http://localhost:8003/tickets/' -H 'Content-Type: application/json' \
-d '{
  "title":"Pedido de Férias",
  "description":"Solicitação inicial",
  "category_id":"0b206ba5-1783-46d9-9de2-5c1befe9bc8e",
  "requester_id":"25f4f8eb-ff36-4564-9144-3dc2880fb058",
  "form_id":"84ae93ad-a492-4954-a48d-b0b442373363",
  "priority":"medium",
  "status":"open"
}'

```

2.  Submeter form (JSON puro sem arquivos — MVP):
    

```curl
curl -X POST 'http://localhost:8003/tickets/<TICKET_ID>/submit-form' \
-H 'Content-Type: application/json' \
-d '{"name":"Fulano","employee_id":"EMP001","start_date":"2025-09-10","end_date":"2025-10-10"}'

```

3.  Progredir ticket (adicionar passo):
    

```curl
curl -X POST 'http://localhost:8003/tickets/<TICKET_ID>/progress' \
-H 'Content-Type: application/json' \
-d '{
  "action":"start_review",
  "performed_by":"25f4f8eb-ff36-4564-9144-3dc2880fb058",
  "comments":"Iniciando análise",
  "new_status":"in_progress"
}'

```

4.  Listar progressões:
    

```curl
curl 'http://localhost:8003/tickets/<TICKET_ID>/progressions'
```

## 5) Frontend — componentes e fluxo
* * * 

Componentes mínimos a implementar:
1.  **TicketList** — lista tickets (GET /tickets) com filtros (status, category, assigned_to).
    
2.  **TicketDetail** — mostra ticket, histórico (GET /tickets/{id}) e botão “Progredir”.
    
3.  **ProgressForm** — small form com `action`, `comments`, `new_status`, botão enviar. Envia POST `/tickets/{id}/progress`.
    
4.  **ProgressTimeline** — renderiza `ticket.form_data` preenchido no formulário (reusar `TicketForm` com `initialValues`) e lista `progressions` como timeline.
    
**Comportamento quando o usuário escolher um ticket**:
*   buscar `/tickets/{id}` -> devolve `form_id` e `form_data`.
    
*   buscar `/forms/{form_id}/schema` -> carregar schema (reutilizar `getFormSchema`).
    
*   renderizar `TicketForm` com `initialValues = ticket.form_data`.
    
*   abaixo do formulário, renderizar `ProgressForm` (action + comments + submit) e `ProgressTimeline` (GET `/tickets/{id}/progressions`).
    

## 6) Integração com aprovações / BPM — notas de arquitetura
* * * 

*   Para MVP, `ticket_progressions` + `approval_levels` + `ticket_approvals` oferecem rastreabilidade e condição de aprovação.
    
*   Quando for integrar BPMN:
    *   cada `progression` pode disparar um `process_instance` (criar `process_instances` entry).
        
    *   `workflow_steps` podem mapear para `bpmn_elements`.
        
*   Implementar um “executor” (microservice) que consome `ticket_progressions` com `action_type == 'auto'` para executar passos automáticos (notificações, timeouts).
    

## 7) Plano incremental (prático)
* * * 

Prioridade e tarefas:
**Sprint 1 (MVP core)** — 1–2 dias
*   Criar tabela `ticket_progressions`.
    
*   Implementar endpoints:
    *   `POST /tickets/{ticket_id}/progress`
        
    *   `GET /tickets/{ticket_id}/progressions`
        
*   Frontend:
    *   `TicketList` e `TicketDetail` (show form + form_data).
        
    *   `ProgressForm` (action/comments/new_status).
        
    *   `ProgressTimeline`.
        
**Sprint 2 (apoio / QA)** — 1–2 dias
*   Audit: gravar também `ticket_history` ao avançar.
    
*   Permissões: checar `performed_by` tem role apropriada (backend).
    
*   Notificações/email quando status mudar.
    
**Sprint 3 (integração BPMN/aprovações)** — 2–4 dias
*   Mapear workflows → `workflows` + `workflow_steps`.
    
*   Integrar com `bpmn_processes` / disparar `process_instances`.
    
*   Implementar `auto` steps e timeouts.
    

## 8) SQL de migração (exemplo)
* * * 

```sql
-- migration: create ticket_progressions
CREATE TABLE IF NOT EXISTS ticket_progressions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_id uuid NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
  step_name varchar(150) NOT NULL,
  action varchar(100) NOT NULL,
  performed_by uuid,
  previous_status varchar(50),
  new_status varchar(50),
  comments text,
  metadata jsonb,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ticket_progressions_ticket ON ticket_progressions(ticket_id);

```

## 9) Observações práticas e recomendadas
* * * 

*   **Para auditabilidade**, sempre salve `form_data` snapshot no `metadata` do progression quando a ação depender do formulário.
    
*   **Validações/authorizations**: backend deve confirmar `performed_by` existe e tem permissão.
    
*   **Files**: MVP envia JSON; tratar multipart/upload em `submit-form` depois e persistir arquivos em uma tabela `ticket_attachments` (referenciar `ticket_id`, `file_path`, `metadata`).
    
*   **IDs**: gerar UUID no backend (não confiar no front).
    
*   **Teste ponta-a-ponta**: crie collection Postman com os cURL de exemplo acima.
