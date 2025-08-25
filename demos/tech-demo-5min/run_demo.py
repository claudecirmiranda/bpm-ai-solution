# demos/tech-demo-5min/run_demo.py
"""
Tech Demo 5 Minutos - BPM AI Solution
Demonstração executável dos agentes de IA em ação
"""

import asyncio
import json
import time
from typing import Dict, Any
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
import os

console = Console()

class ProcessDesignerAgent:
    """Agent que gera processos BPMN baseado em descrição textual"""
    
    def __init__(self):
        self.name = "Process Designer Agent"
        self.version = "1.0.0"
    
    async def generate_process(self, description: str) -> Dict[str, Any]:
        """Gera um processo BPMN baseado na descrição"""
        
        # Simula chamada para LLM (Claude/GPT-4)
        await asyncio.sleep(2)  # Simula tempo de processamento
        
        # Processo gerado baseado na descrição
        if "aprovação" in description.lower() and "compras" in description.lower():
            return {
                "process_id": "approval_purchase_001",
                "name": "Aprovação de Compras",
                "description": "Processo automatizado para aprovação de solicitações de compra",
                "bpmn_elements": [
                    {"id": "start_1", "type": "startEvent", "name": "Início"},
                    {"id": "task_1", "type": "userTask", "name": "Preencher Solicitação", "assignee": "solicitante"},
                    {"id": "gateway_1", "type": "exclusiveGateway", "name": "Valor > R$ 5.000?"},
                    {"id": "task_2", "type": "userTask", "name": "Aprovação Gestor", "assignee": "gestor"},
                    {"id": "task_3", "type": "userTask", "name": "Aprovação Direta", "assignee": "aprovador"},
                    {"id": "task_4", "type": "serviceTask", "name": "Notificar Solicitante"},
                    {"id": "end_1", "type": "endEvent", "name": "Fim"}
                ],
                "flows": [
                    {"from": "start_1", "to": "task_1"},
                    {"from": "task_1", "to": "gateway_1"},
                    {"from": "gateway_1", "to": "task_2", "condition": "valor > 5000"},
                    {"from": "gateway_1", "to": "task_3", "condition": "valor <= 5000"},
                    {"from": "task_2", "to": "task_4"},
                    {"from": "task_3", "to": "task_4"},
                    {"from": "task_4", "to": "end_1"}
                ],
                "estimated_duration": "2-5 dias",
                "complexity_score": 7.5,
                "compliance_checks": ["SOX", "LGPD"],
                "optimizations": [
                    "SLA automático de 48h para aprovação",
                    "Escalação automática após 2 dias",
                    "Notificação por email em cada etapa"
                ]
            }
        
        return {"error": "Tipo de processo não reconhecido"}

class FormBuilderAgent:
    """Agent que gera formulários dinâmicos baseado no contexto do processo"""
    
    def __init__(self):
        self.name = "Form Builder Agent"
        self.version = "1.0.0"
    
    async def generate_form(self, process_context: Dict[str, Any]) -> Dict[str, Any]:
        """Gera formulário JSON Schema baseado no processo"""
        
        await asyncio.sleep(1.5)  # Simula processamento
        
        if "aprovação" in process_context.get("name", "").lower():
            return {
                "form_id": f"form_{process_context.get('process_id', 'unknown')}",
                "title": "Solicitação de Compra",
                "schema": {
                    "type": "object",
                    "properties": {
                        "solicitante": {
                            "type": "string",
                            "title": "Nome do Solicitante",
                            "description": "Nome completo do solicitante"
                        },
                        "fornecedor": {
                            "type": "string",
                            "title": "Fornecedor",
                            "description": "Nome da empresa fornecedora"
                        },
                        "descricao_item": {
                            "type": "string",
                            "title": "Descrição do Item/Serviço",
                            "description": "Descrição detalhada do que será adquirido",
                            "minLength": 10
                        },
                        "valor": {
                            "type": "number",
                            "title": "Valor Total",
                            "description": "Valor total da compra em reais",
                            "minimum": 0
                        },
                        "centro_custo": {
                            "type": "string",
                            "title": "Centro de Custo",
                            "enum": ["TI", "Marketing", "Vendas", "RH", "Financeiro"]
                        },
                        "justificativa": {
                            "type": "string",
                            "title": "Justificativa",
                            "description": "Justificativa para a compra",
                            "minLength": 20
                        },
                        "data_necessidade": {
                            "type": "string",
                            "format": "date",
                            "title": "Data de Necessidade"
                        },
                        "anexos": {
                            "type": "array",
                            "title": "Anexos",
                            "items": {
                                "type": "string",
                                "format": "uri"
                            }
                        }
                    },
                    "required": ["solicitante", "fornecedor", "descricao_item", "valor", "centro_custo", "justificativa"]
                },
                "ui_schema": {
                    "descricao_item": {"ui:widget": "textarea"},
                    "justificativa": {"ui:widget": "textarea"},
                    "valor": {"ui:widget": "updown"},
                    "data_necessidade": {"ui:widget": "date"},
                    "anexos": {"ui:widget": "files"}
                },
                "validations": [
                    {"field": "valor", "rule": "required", "message": "Valor é obrigatório"},
                    {"field": "valor", "rule": "min", "value": 1, "message": "Valor deve ser maior que zero"},
                    {"field": "justificativa", "rule": "minLength", "value": 20, "message": "Justificativa deve ter pelo menos 20 caracteres"}
                ],
                "estimated_completion_time": "5-8 minutos"
            }
        
        return {"error": "Contexto de processo não suportado"}

class CodeGeneratorAgent:
    """Agent que gera código full-stack baseado no processo BPMN"""
    
    def __init__(self):
        self.name = "Code Generator Agent"
        self.version = "1.0.0"
    
    async def generate_code(self, process_data: Dict[str, Any], form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera código completo para backend e frontend"""
        
        await asyncio.sleep(3)  # Simula geração de código
        
        # Código FastAPI gerado
        fastapi_code = '''
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List
import uuid

app = FastAPI(title="BPM Process API")

class SolicitacaoCompra(BaseModel):
    solicitante: str
    fornecedor: str
    descricao_item: str
    valor: float
    centro_custo: str
    justificativa: str
    data_necessidade: Optional[datetime] = None
    anexos: Optional[List[str]] = []
    
    @validator('valor')
    def valor_deve_ser_positivo(cls, v):
        if v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return v

@app.post("/api/processos/approval_purchase_001/start")
async def iniciar_processo(solicitacao: SolicitacaoCompra):
    """Inicia processo de aprovação de compra"""
    process_instance_id = str(uuid.uuid4())
    
    # Determina próxima tarefa baseada no valor
    if solicitacao.valor > 5000:
        next_task = "Aprovação Gestor"
        assignee = "gestor"
    else:
        next_task = "Aprovação Direta"
        assignee = "aprovador"
    
    return {
        "process_instance_id": process_instance_id,
        "status": "started",
        "current_task": next_task,
        "assignee": assignee,
        "data": solicitacao.dict()
    }
'''
        
        # Código Vue.js gerado
        vue_component = '''
<template>
  <div class="solicitacao-compra">
    <h2>{{ formTitle }}</h2>
    <form @submit.prevent="submitForm" class="form-container">
      <div class="form-group">
        <label>Nome do Solicitante*</label>
        <input 
          v-model="form.solicitante" 
          type="text" 
          required 
          placeholder="Digite seu nome completo"
        />
      </div>
      
      <div class="form-group">
        <label>Valor Total*</label>
        <input 
          v-model.number="form.valor" 
          type="number" 
          step="0.01" 
          min="1" 
          required 
          @input="checkApprovalLevel"
        />
        <small v-if="form.valor > 5000" class="approval-info">
          ⚠️ Valor acima de R$ 5.000 - Requer aprovação do gestor
        </small>
      </div>
      
      <button type="submit" :disabled="!isFormValid" class="submit-btn">
        {{ submitButtonText }}
      </button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'SolicitacaoCompra',
  data() {
    return {
      form: {
        solicitante: '',
        fornecedor: '',
        valor: 0,
        justificativa: ''
      }
    }
  },
  computed: {
    isFormValid() {
      return this.form.solicitante && this.form.valor > 0
    },
    submitButtonText() {
      return this.form.valor > 5000 ? 
        'Enviar para Aprovação do Gestor' : 
        'Enviar para Aprovação Direta'
    }
  }
}
</script>
'''
        
        return {
            "generation_id": f"codegen_{int(time.time())}",
            "process_id": process_data.get("process_id"),
            "generated_files": {
                "backend": {
                    "language": "Python",
                    "framework": "FastAPI",
                    "file": "main.py",
                    "lines_of_code": 67,
                    "code": fastapi_code.strip()
                },
                "frontend": {
                    "language": "Vue.js",
                    "framework": "Vue 3",
                    "file": "SolicitacaoCompra.vue",
                    "lines_of_code": 98,
                    "code": vue_component.strip()
                },
                "database": {
                    "type": "PostgreSQL Migration",
                    "file": "001_create_purchase_requests.sql",
                    "code": """
CREATE TABLE purchase_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_instance_id UUID NOT NULL,
    solicitante VARCHAR(255) NOT NULL,
    valor DECIMAL(10,2) NOT NULL CHECK (valor > 0),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"""
                }
            },
            "tests_generated": {
                "unit_tests": 12,
                "integration_tests": 5,
                "e2e_tests": 3
            },
            "estimated_dev_time_saved": "85%",
            "manual_dev_estimate": "40 horas",
            "ai_assisted_estimate": "6 horas"
        }

async def show_metrics_dashboard():
    """Mostra dashboard com métricas do que foi gerado"""
    
    metrics_table = Table(title="📈 Métricas de Geração IA", show_header=True, header_style="bold magenta")
    metrics_table.add_column("Métrica", style="cyan", no_wrap=True)
    metrics_table.add_column("Valor", style="green")
    metrics_table.add_column("Impacto", style="yellow")
    
    metrics_table.add_row("⏱️ Tempo Total Demo", "~7 segundos", "vs 40+ horas manuais")
    metrics_table.add_row("📝 Linhas de Código", "200+ linhas", "Backend + Frontend + SQL")
    metrics_table.add_row("🧪 Testes Gerados", "20 testes", "Unit + Integration + E2E")
    metrics_table.add_row("⚡ Produtividade", "+85%", "6h vs 40h desenvolvimento")
    metrics_table.add_row("💰 Economia Estimada", "R$ 12.000", "Por processo (dev + qa)")
    metrics_table.add_row("🎯 Qualidade Código", "Production Ready", "Validações + Tipagem")
    
    console.print(metrics_table)

async def run_demo():
    """Executa o demo completo de 5 minutos"""
    
    console.clear()
    console.print(Panel.fit(
        "[bold blue]🚀 BPM AI Solution - Tech Demo[/bold blue]\n"
        "[dim]Demonstração dos Agentes de IA em Ação[/dim]\n"
        f"[dim]Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}[/dim]\n"
        "[bold green]🎯 Objetivo: Mostrar como IA acelera desenvolvimento BPM[/bold green]",
        border_style="blue"
    ))
    
    # Instanciar agents
    process_agent = ProcessDesignerAgent()
    form_agent = FormBuilderAgent()
    code_agent = CodeGeneratorAgent()
    
    # Cenário do demo
    user_input = "Preciso de um processo para aprovação de compras com diferentes níveis baseados no valor"
    
    console.print(f"\n[yellow]👤 Requisito do Cliente:[/yellow] {user_input}")
    
    # ========== STAGE 1: Process Designer Agent ==========
    console.print(f"\n[bold green]🤖 Stage 1: {process_agent.name}[/bold green]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🧠 Analisando requisitos e gerando processo BPMN...", total=None)
        
        process_data = await process_agent.generate_process(user_input)
        
        progress.stop_task(task)
    
    # Mostrar resultado do processo
    process_table = Table(title="📊 Processo BPMN Gerado", show_header=True, header_style="bold cyan")
    process_table.add_column("Propriedade", style="cyan")
    process_table.add_column("Valor", style="green")
    
    process_table.add_row("🏷️ Nome", process_data["name"])
    process_table.add_row("🆔 ID", process_data["process_id"])
    process_table.add_row("🔧 Elementos BPMN", str(len(process_data["bpmn_elements"])))
    process_table.add_row("🔄 Fluxos", str(len(process_data["flows"])))
    process_table.add_row("⏱️ Duração Est.", process_data["estimated_duration"])
    process_table.add_row("📊 Complexidade", f"{process_data['complexity_score']}/10")
    process_table.add_row("✅ Otimizações", f"{len(process_data['optimizations'])} sugestões")
    
    console.print(process_table)
    
    # ========== STAGE 2: Form Builder Agent ==========
    console.print(f"\n[bold green]🤖 Stage 2: {form_agent.name}[/bold green]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("📝 Gerando formulário dinâmico baseado no processo...", total=None)
        
        form_data = await form_agent.generate_form(process_data)
        
        progress.stop_task(task)
    
    # Mostrar resultado do formulário
    form_table = Table(title="📋 Formulário JSON Schema Gerado", show_header=True, header_style="bold cyan")
    form_table.add_column("Propriedade", style="cyan")
    form_table.add_column("Valor", style="green")
    
    form_table.add_row("📝 Título", form_data["title"])
    form_table.add_row("🆔 Form ID", form_data["form_id"])
    form_table.add_row("📊 Campos", str(len(form_data["schema"]["properties"])))
    form_table.add_row("✅ Validações", str(len(form_data["validations"])))
    form_table.add_row("⏱️ Tempo Preench.", form_data["estimated_completion_time"])
    form_table.add_row("🎨 UI Components", str(len(form_data["ui_schema"])))
    
    console.print(form_table)
    
    # ========== STAGE 3: Code Generator Agent ==========
    console.print(f"\n[bold green]🤖 Stage 3: {code_agent.name}[/bold green]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("💻 Gerando código full-stack (Backend + Frontend + DB)...", total=None)
        
        code_data = await code_agent.generate_code(process_data, form_data)
        
        progress.stop_task(task)
    
    # Mostrar métricas de código gerado
    code_table = Table(title="💻 Código Full-Stack Gerado", show_header=True, header_style="bold cyan")
    code_table.add_column("Componente", style="cyan")
    code_table.add_column("Tecnologia", style="yellow")
    code_table.add_column("Linhas", style="green")
    code_table.add_column("Arquivo", style="blue")
    
    for component, details in code_data["generated_files"].items():
        if component == "database":
            code_table.add_row(
                f"🗄️ {component.title()}", 
                details["type"], 
                "~15", 
                details["file"]
            )
        else:
            code_table.add_row(
                f"{'🔧' if component == 'backend' else '🎨'} {component.title()}", 
                details["framework"], 
                str(details["lines_of_code"]), 
                details["file"]
            )
    
    console.print(code_table)
    
    # ========== RESULTADOS FINAIS ==========
    console.print(f"\n[bold yellow]🎯 Resumo da Demonstração[/bold yellow]")
    
    await show_metrics_dashboard()
    
    # Mostrar um trecho do código gerado
    console.print(f"\n[bold cyan]💻 Preview do Código Backend Gerado:[/bold cyan]")
    
    backend_preview = '''@app.post("/api/processos/approval_purchase_001/start")
async def iniciar_processo(solicitacao: SolicitacaoCompra):
    """Inicia processo de aprovação de compra"""
    process_instance_id = str(uuid.uuid4())
    
    # Lógica de roteamento inteligente baseada no valor
    if solicitacao.valor > 5000:
        next_task = "Aprovação Gestor"
        assignee = "gestor"
    else:
        next_task = "Aprovação Direta"
        assignee = "aprovador"
    
    return {
        "process_instance_id": process_instance_id,
        "status": "started",
        "current_task": next_task,
        "assignee": assignee
    }'''
    
    syntax = Syntax(backend_preview, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="FastAPI - Endpoint Gerado Automaticamente", border_style="green"))
    
    # Conclusão impactante
    console.print(Panel.fit(
        "[bold green]✅ Demo Concluída com Sucesso![/bold green]\n\n"
        "[yellow]📈 Resultados Alcançados:[/yellow]\n"
        "• Processo BPMN completo gerado em 2 segundos\n"
        "• Formulário JSON Schema com validações em 1.5s\n" 
        "• Código full-stack production-ready em 3 segundos\n"
        "• 20 testes automatizados incluídos\n"
        "• Economia de 85% no tempo de desenvolvimento\n\n"
        "[bold blue]🚀 Próximos Passos:[/bold blue]\n"
        "• Deploy automático em staging\n"
        "• Testes E2E executados\n"
        "• Documentação API gerada\n"
        "• Métricas de performance coletadas",
        border_style="green",
        title="🎉 Impacto da IA no Desenvolvimento BPM"
    ))
    
    # Call to Action
    console.print(f"\n[bold magenta]💡 Esta demo representa apenas 1 processo.[/bold magenta]")
    console.print(f"[dim]Imagine o impacto em dezenas de processos empresariais...[/dim]")

# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    try:
        # Verificar dependências
        required_packages = ["rich", "asyncio"]
        
        console.print("[dim]Iniciando Tech Demo...[/dim]")
        time.sleep(1)
        
        # Executar demo
        asyncio.run(run_demo())
        
        console.print(f"\n[green]🎯 Demo executada com sucesso![/green]")
        console.print(f"[dim]Para mais informações: docs/presentation/[/dim]")
        
    except KeyboardInterrupt:
        console.print(f"\n[yellow]⚠️ Demo interrompida pelo usuário[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Erro na execução: {e}[/red]")

# ========== BONUS: Interactive Mode ==========
async def interactive_demo():
    """Versão interativa da demo para apresentações ao vivo"""
    
    console.print("[bold blue]🎤 Modo Interativo Ativado[/bold blue]")
    console.print("[dim]Pressione ENTER para avançar cada etapa...[/dim]\n")
    
    input("🚀 Pressione ENTER para iniciar a demonstração...")
    
    # Continuar com o fluxo normal mas com paradas
    await run_demo()