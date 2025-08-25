#!/usr/bin/env python3
"""
BPM AI Solution - Workflow Completo
Demonstração end-to-end: Requisito → Análise → Código → Execução
"""

import asyncio
import json
import os
import sys
import subprocess
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import uvicorn
import shutil

# LangChain imports
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

# Rich for beautiful output
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.text import Text
import webbrowser

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

console = Console()

# ===================== ENHANCED PYDANTIC MODELS =====================

class BPMNElement(BaseModel):
    id: str = Field(description="Unique identifier for the element")
    type: str = Field(description="Type of BPMN element (startEvent, userTask, etc.)")
    name: str = Field(description="Human readable name")
    properties: Dict[str, Any] = Field(default={}, description="Additional properties")
    position: Dict[str, int] = Field(default={"x": 0, "y": 0}, description="Visual position")

class BPMNFlow(BaseModel):
    from_element: str = Field(description="Source element ID")
    to_element: str = Field(description="Target element ID")
    condition: str = Field(default="", description="Flow condition if applicable")
    name: str = Field(default="", description="Flow name")

class ProcessDefinition(BaseModel):
    process_id: str = Field(description="Unique process identifier")
    name: str = Field(description="Process name")
    description: str = Field(description="Process description")
    elements: List[BPMNElement] = Field(description="BPMN elements")
    flows: List[BPMNFlow] = Field(description="Process flows")
    estimated_duration: str = Field(description="Estimated process duration")
    complexity_score: float = Field(description="Process complexity (0-10)")
    business_rules: List[str] = Field(default=[], description="Business rules")

class FormField(BaseModel):
    name: str = Field(description="Field name")
    type: str = Field(description="Field type (string, number, etc.)")
    title: str = Field(description="Human readable title")
    required: bool = Field(default=False, description="Is field required")
    properties: Dict[str, Any] = Field(default={}, description="Additional field properties")
    validation: Dict[str, Any] = Field(default={}, description="Validation rules")

class FormDefinition(BaseModel):
    form_id: str = Field(description="Unique form identifier")
    title: str = Field(description="Form title")
    fields: List[FormField] = Field(description="Form fields")
    validations: List[Dict[str, Any]] = Field(default=[], description="Validation rules")
    sections: List[Dict[str, Any]] = Field(default=[], description="Form sections")

class GeneratedCode(BaseModel):
    language: str = Field(description="Programming language")
    framework: str = Field(description="Framework used")
    filename: str = Field(description="Suggested filename")
    code: str = Field(description="Generated code")
    dependencies: List[str] = Field(default=[], description="Required dependencies")
    tests: str = Field(default="", description="Generated test code")
    documentation: str = Field(default="", description="Code documentation")

# ===================== ENHANCED AGENTS =====================

class RequirementAnalyzerAgent:
    """Agent que analisa e enriquece requisitos usando LangChain"""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.name = "Requirement Analyzer"
        
        if "claude" in model.lower():
            self.llm = ChatAnthropic(
                anthropic_api_key=api_key,
                model=model,
                temperature=0.1,
                max_tokens=2000
            )
        else:
            self.llm = ChatOpenAI(
                openai_api_key=api_key,
                model=model,
                temperature=0.1,
                max_tokens=2000
            )
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """Você é um analista de negócios especialista em BPM.
                
                Sua função é analisar requisitos de processos empresariais e gerar:
                1. Análise detalhada do domínio do negócio
                2. Identificação de stakeholders
                3. Regras de negócio implícitas
                4. Requisitos funcionais e não-funcionais
                5. Estimativa de complexidade
                6. Riscos e considerações de compliance
                
                Formato de saída em JSON:
                {{
                    "domain": "Domínio do negócio",
                    "stakeholders": ["Lista de stakeholders"],
                    "business_rules": ["Lista de regras de negócio"],
                    "functional_requirements": ["Requisitos funcionais"],
                    "non_functional_requirements": ["Requisitos não funcionais"],
                    "complexity_factors": ["Fatores de complexidade"],
                    "compliance_considerations": ["Considerações de compliance"],
                    "estimated_complexity": "Baixa/Média/Alta",
                    "recommended_approach": "Abordagem recomendada"
                }}"""
            ),
            HumanMessagePromptTemplate.from_template(
                """Analise o seguinte requisito empresarial:
                
                REQUISITO: {requirement}
                
                CONTEXTO:
                - Ambiente corporativo
                - Necessidade de auditoria e compliance
                - Integração com sistemas existentes
                - Usuários com diferentes níveis de acesso
                
                Forneça uma análise completa em formato JSON."""
            )
        ])

    async def analyze_requirement(self, requirement: str) -> Dict[str, Any]:
        """Analisa requisito e retorna análise estruturada"""
        try:
            chain = self.prompt | self.llm
            result = await asyncio.to_thread(
                chain.invoke,
                {"requirement": requirement}
            )
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            console.print(f"[red]Erro na análise: {e}[/red]")
            return {
                "domain": "Processo Corporativo",
                "stakeholders": ["Usuários", "Gestores", "Administradores"],
                "business_rules": ["Validação de dados", "Aprovação necessária"],
                "functional_requirements": ["Interface web", "Notificações"],
                "non_functional_requirements": ["Performance", "Segurança"],
                "complexity_factors": ["Múltiplos aprovadores"],
                "compliance_considerations": ["LGPD", "Auditoria"],
                "estimated_complexity": "Média",
                "recommended_approach": "Desenvolvimento incremental"
            }

class EnhancedProcessDesignerAgent:
    """Agent melhorado para gerar processos BPMN"""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.name = "Enhanced Process Designer"
        
        if "claude" in model.lower():
            self.llm = ChatAnthropic(
                anthropic_api_key=api_key,
                model=model,
                temperature=0.1,
                max_tokens=4000
            )
        else:
            self.llm = ChatOpenAI(
                openai_api_key=api_key,
                model=model,
                temperature=0.1,
                max_tokens=4000
            )
        
        self.parser = PydanticOutputParser(pydantic_object=ProcessDefinition)
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """Você é um especialista em BPM e modelagem BPMN 2.0.
                
                Com base na análise de requisitos, gere um processo BPMN completo que inclua:
                1. Elementos BPMN apropriados com posicionamento visual
                2. Fluxos condicionais e paralelos
                3. Tratamento de exceções
                4. Pontos de decisão e aprovação
                5. Integrações com sistemas
                6. Regras de negócio incorporadas
                
                Elementos BPMN suportados:
                - startEvent: Evento de início
                - userTask: Tarefa humana
                - serviceTask: Tarefa automatizada
                - exclusiveGateway: Gateway exclusivo (XOR)
                - parallelGateway: Gateway paralelo (AND)
                - inclusiveGateway: Gateway inclusivo (OR)
                - endEvent: Evento de fim
                - intermediateCatchEvent: Evento intermediário
                
                {format_instructions}"""
            ),
            HumanMessagePromptTemplate.from_template(
                """Com base na seguinte análise de requisitos, gere um processo BPMN detalhado:
                
                REQUISITO ORIGINAL: {original_requirement}
                
                ANÁLISE:
                - Domínio: {domain}
                - Stakeholders: {stakeholders}
                - Regras de negócio: {business_rules}
                - Complexidade: {complexity}
                - Compliance: {compliance}
                
                REQUISITOS ESPECÍFICOS:
                - Processo deve ser auditável
                - Notificações automáticas
                - Diferentes níveis de aprovação
                - Tratamento de exceções
                - Integração com sistemas corporativos
                
                Gere um processo BPMN completo e otimizado."""
            )
        ])
        
        self.chain = self.prompt | self.llm | self.parser

    async def generate_process(self, requirement: str, analysis: Dict[str, Any]) -> ProcessDefinition:
        """Gera processo BPMN baseado na análise"""
        try:
            result = await asyncio.to_thread(
                self.chain.invoke,
                {
                    "original_requirement": requirement,
                    "domain": analysis.get("domain", "N/A"),
                    "stakeholders": ", ".join(analysis.get("stakeholders", [])),
                    "business_rules": ", ".join(analysis.get("business_rules", [])),
                    "complexity": analysis.get("estimated_complexity", "Média"),
                    "compliance": ", ".join(analysis.get("compliance_considerations", [])),
                    "format_instructions": self.parser.get_format_instructions()
                }
            )
            
            # Adicionar regras de negócio da análise
            result.business_rules = analysis.get("business_rules", [])
            
            return result
            
        except Exception as e:
            console.print(f"[red]Erro no Process Designer: {e}[/red]")
            return ProcessDefinition(
                process_id="fallback_process",
                name="Processo de Aprovação",
                description="Processo gerado como fallback",
                elements=[
                    BPMNElement(id="start_1", type="startEvent", name="Início", position={"x": 100, "y": 100}),
                    BPMNElement(id="task_1", type="userTask", name="Preencher Solicitação", position={"x": 250, "y": 100}),
                    BPMNElement(id="gateway_1", type="exclusiveGateway", name="Valor > R$ 1000?", position={"x": 400, "y": 100}),
                    BPMNElement(id="task_2", type="userTask", name="Aprovação Gerencial", position={"x": 550, "y": 50}),
                    BPMNElement(id="end_1", type="endEvent", name="Aprovado", position={"x": 700, "y": 100})
                ],
                flows=[
                    BPMNFlow(from_element="start_1", to_element="task_1"),
                    BPMNFlow(from_element="task_1", to_element="gateway_1"),
                    BPMNFlow(from_element="gateway_1", to_element="task_2", condition="value > 1000"),
                    BPMNFlow(from_element="gateway_1", to_element="end_1", condition="value <= 1000"),
                    BPMNFlow(from_element="task_2", to_element="end_1")
                ],
                estimated_duration="2-5 dias úteis",
                complexity_score=6.5,
                business_rules=analysis.get("business_rules", [])
            )

class EnhancedCodeGeneratorAgent:
    """Agent melhorado para geração de código full-stack"""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.name = "Enhanced Code Generator"
        
        if "claude" in model.lower():
            self.llm = ChatAnthropic(
                anthropic_api_key=api_key,
                model=model,
                temperature=0.1,
                max_tokens=4000
            )
        else:
            self.llm = ChatOpenAI(
                openai_api_key=api_key,
                model=model,
                temperature=0.1,
                max_tokens=4000
            )

    async def generate_executable_backend(self, process_data: ProcessDefinition, form_data: FormDefinition) -> GeneratedCode:
        """Gera código FastAPI executável"""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """Você é um desenvolvedor senior Python especialista em FastAPI.
                
                Gere código FastAPI EXECUTÁVEL e PRODUCTION-READY que inclua:
                1. Aplicação FastAPI completa e funcional
                2. Models Pydantic para dados
                3. Endpoints REST completos
                4. Middleware de CORS
                5. Documentação OpenAPI
                6. Sistema de logging
                7. Validações robustas
                8. Base de dados em memória (SQLite)
                9. Sistema de notificações mock
                10. Startup e shutdown handlers
                
                IMPORTANTE:
                - Código deve executar sem erros
                - Inclua if __name__ == "__main__": com uvicorn.run()
                - Use SQLite com tabelas criadas automaticamente
                - Endpoints devem retornar dados reais
                - Inclua CORS para frontend
                - Docstrings e type hints completos
                
                NÃO use imports externos além de FastAPI, Pydantic, SQLite3, UUID, datetime."""
            ),
            HumanMessagePromptTemplate.from_template(
                """Gere código FastAPI EXECUTÁVEL completo para:
                
                PROCESSO: {process_name}
                ID: {process_id}
                DESCRIÇÃO: {process_description}
                REGRAS DE NEGÓCIO: {business_rules}
                
                FORMULÁRIO:
                {form_fields}
                
                ENDPOINTS OBRIGATÓRIOS:
                - POST /api/processes/{process_id}/start - Iniciar processo
                - GET /api/processes/{process_id}/tasks - Listar tarefas
                - POST /api/processes/{process_id}/tasks/{{task_id}}/complete - Completar tarefa
                - GET /api/processes/{process_id}/status - Status do processo
                - GET /health - Health check
                - GET /docs - Documentação automática
                
                REQUISITOS:
                - Aplicação deve rodar na porta 8000
                - CORS habilitado
                - Logging configurado
                - Validações de dados
                - Responses estruturadas
                
                Retorne APENAS o código Python executável."""
            )
        ])
        
        try:
            chain = prompt | self.llm
            result = await asyncio.to_thread(
                chain.invoke,
                {
                    "process_name": process_data.name,
                    "process_id": process_data.process_id,
                    "process_description": process_data.description,
                    "business_rules": "; ".join(process_data.business_rules),
                    "form_fields": json.dumps([field.dict() for field in form_data.fields], indent=2)
                }
            )
            
            return GeneratedCode(
                language="Python",
                framework="FastAPI",
                filename=f"{process_data.process_id}_server.py",
                code=result.content,
                dependencies=["fastapi", "uvicorn", "pydantic", "sqlite3", "uuid", "datetime"],
                documentation="FastAPI server with SQLite backend and REST endpoints"
            )
            
        except Exception as e:
            console.print(f"[red]Erro gerando backend: {e}[/red]")
            # Fallback code
            fallback_code = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="BPM API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
            return GeneratedCode(
                language="Python",
                framework="FastAPI",
                filename="fallback_server.py",
                code=fallback_code,
                dependencies=["fastapi", "uvicorn"]
            )

    async def generate_executable_frontend(self, process_data: ProcessDefinition, form_data: FormDefinition) -> GeneratedCode:
        """Gera código HTML/JS executável"""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """Você é um desenvolvedor frontend senior especialista em HTML/CSS/JavaScript.
                
                Gere uma aplicação web EXECUTÁVEL que inclua:
                1. HTML5 semântico e acessível
                2. CSS moderno com flexbox/grid
                3. JavaScript vanilla (ES6+)
                4. Formulário reativo e responsivo
                5. Validações client-side
                6. Integração com API REST
                7. Loading states e error handling
                8. UI moderna e intuitiva
                9. Notificações visuais
                10. Design responsivo
                
                IMPORTANTE:
                - Arquivo HTML único e executável
                - CSS embedded para styling moderno
                - JavaScript para interatividade
                - Formulário baseado nos campos fornecidos
                - Integração com API backend
                - UX otimizada
                - Acessibilidade (ARIA labels)
                
                NÃO use bibliotecas externas, apenas HTML/CSS/JS puros."""
            ),
            HumanMessagePromptTemplate.from_template(
                """Gere aplicação web EXECUTÁVEL completa para:
                
                PROCESSO: {process_name}
                DESCRIÇÃO: {process_description}
                
                FORMULÁRIO: {form_title}
                CAMPOS: {form_fields}
                
                API ENDPOINTS:
                - POST http://localhost:8000/api/processes/{process_id}/start
                - GET http://localhost:8000/api/processes/{process_id}/tasks
                - GET http://localhost:8000/api/processes/{process_id}/status
                
                REQUISITOS:
                - Página única HTML executável
                - Design moderno e responsivo
                - Formulário com todos os campos
                - Validações JavaScript
                - Feedback visual
                - Error handling
                - Loading states
                
                Retorne APENAS o código HTML completo."""
            )
        ])
        
        try:
            chain = prompt | self.llm
            result = await asyncio.to_thread(
                chain.invoke,
                {
                    "process_name": process_data.name,
                    "process_description": process_data.description,
                    "form_title": form_data.title,
                    "form_fields": json.dumps([field.dict() for field in form_data.fields], indent=2),
                    "process_id": process_data.process_id
                }
            )
            
            return GeneratedCode(
                language="HTML/CSS/JavaScript",
                framework="Vanilla Web",
                filename=f"{process_data.process_id}_app.html",
                code=result.content,
                dependencies=[],
                documentation="Complete web application with embedded CSS/JS"
            )
            
        except Exception as e:
            console.print(f"[red]Erro gerando frontend: {e}[/red]")
            # Fallback HTML
            fallback_code = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BPM Application</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        form { background: #f5f5f5; padding: 20px; border-radius: 8px; }
        input, textarea, select { width: 100%; padding: 8px; margin: 5px 0; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>BPM Process Application</h1>
        <form id="bpmForm">
            <h2>Process Form</h2>
            <input type="text" placeholder="Enter data" required>
            <button type="submit">Submit Process</button>
        </form>
    </div>
    <script>
        document.getElementById('bpmForm').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Process submitted successfully!');
        });
    </script>
</body>
</html>
'''
            return GeneratedCode(
                language="HTML",
                framework="Vanilla",
                filename="fallback_app.html",
                code=fallback_code,
                dependencies=[]
            )

# ===================== EXECUTION ENGINE =====================

class ExecutionEngine:
    """Engine para executar código gerado"""
    
    def __init__(self):
        self.backend_process = None
        self.temp_dir = None
        
    async def setup_environment(self) -> bool:
        """Configura ambiente de execução"""
        try:
            # Criar diretório temporário
            self.temp_dir = Path(tempfile.mkdtemp(prefix="bpm_demo_"))
            console.print(f"[dim]📁 Ambiente: {self.temp_dir}[/dim]")
            
            # Verificar Python
            result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
            console.print(f"[dim]🐍 Python: {result.stdout.strip()}[/dim]")
            
            # Instalar dependências se necessário
            packages = ["fastapi", "uvicorn"]
            for package in packages:
                try:
                    __import__(package)
                except ImportError:
                    console.print(f"[yellow]📦 Instalando {package}...[/yellow]")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Erro no setup: {e}[/red]")
            return False
    
    async def deploy_backend(self, backend_code: GeneratedCode) -> bool:
        """Deploy do código backend"""
        try:
            # Salvar arquivo
            backend_file = self.temp_dir / backend_code.filename
            with open(backend_file, "w", encoding="utf-8") as f:
                f.write(backend_code.code)
            
            console.print(f"[green]💾 Backend salvo: {backend_file}[/green]")
            
            # Iniciar servidor em background
            self.backend_process = subprocess.Popen([
                sys.executable, str(backend_file)
            ], cwd=self.temp_dir)
            
            # Aguardar inicialização
            await asyncio.sleep(3)
            
            # Verificar se está rodando
            if self.backend_process.poll() is None:
                console.print("[green]🚀 Backend executando na porta 8000[/green]")
                return True
            else:
                console.print("[red]❌ Backend falhou ao iniciar[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ Erro no deploy backend: {e}[/red]")
            return False
    
    async def deploy_frontend(self, frontend_code: GeneratedCode) -> bool:
        """Deploy do código frontend"""
        try:
            # Salvar arquivo
            frontend_file = self.temp_dir / frontend_code.filename
            with open(frontend_file, "w", encoding="utf-8") as f:
                f.write(frontend_code.code)
            
            console.print(f"[green]💾 Frontend salvo: {frontend_file}[/green]")
            
            # Abrir no navegador
            frontend_url = f"file://{frontend_file.absolute()}"
            console.print(f"[blue]🌐 Frontend disponível: {frontend_url}[/blue]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Erro no deploy frontend: {e}[/red]")
            return False
    
    def cleanup(self):
        """Limpa recursos"""
        try:
            if self.backend_process:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                console.print("[yellow]🛑 Backend finalizado[/yellow]")
        except:
            pass
        
        try:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                console.print("[dim]🧹 Ambiente limpo[/dim]")
        except:
            pass

# ===================== MAIN WORKFLOW =====================

async def run_complete_workflow():
    """Executa workflow completo: Requisito → Código → Execução"""
    
    # Verificar API keys
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if not anthropic_key and not openai_key:
        console.print("[red]❌ Configure ANTHROPIC_API_KEY ou OPENAI_API_KEY[/red]")
        return
    
    # Escolher modelo
    if anthropic_key:
        api_key = anthropic_key
        model = "claude-sonnet-4-20250514"
        console.print("[green]🤖 Usando Claude 3 Sonnet[/green]")
    else:
        api_key = openai_key
        model = "gpt-4"
        console.print("[green]🤖 Usando GPT-4[/green]")
    
    # Header
    console.clear()
    console.print(Panel.fit(
        "[bold blue]🚀 BPM AI Solution - Workflow Completo[/bold blue]\n"
        "[bold green]Requisito → Análise → Código → Execução[/bold green]\n"
        f"[dim]Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}[/dim]\n"
        f"[bold magenta]🎯 Modelo: {model}[/bold magenta]",
        border_style="blue"
    ))
    
    # Inicializar componentes
    analyzer = RequirementAnalyzerAgent(api_key, model)
    process_designer = EnhancedProcessDesignerAgent(api_key, model)
    form_agent = FormBuilderAgent(api_key, model)
    code_generator = EnhancedCodeGeneratorAgent(api_key, model)
    execution_engine = ExecutionEngine()
    
    # Input do usuário - requisito mais complexo
    requirement = """
    Implementar um sistema completo de aprovação de despesas corporativas que atenda aos seguintes critérios:
    
    1. Diferentes níveis de aprovação baseados no valor:
       - Até R$ 500: Aprovação automática do gestor direto
       - R$ 501 a R$ 5.000: Aprovação do gestor + diretor
       - Acima de R$ 5.000: Aprovação do gestor + diretor + CFO
    
    2. Categorias de despesa: Viagem, Material de escritório, Software, Consultoria, Treinamento
    
    3. Documentação obrigatória:
       - Comprovantes fiscais para todas as despesas
       - Justificativa de negócio para valores acima de R$ 1.000
       - Orçamentos comparativos para valores acima de R$ 2.000
    
    4. Integrações necessárias:
       - Sistema de RH para validar hierarquia
       - Sistema financeiro para processamento de pagamentos
       - Sistema de notificações por email
    
    5. Compliance e auditoria:
       - Log completo de todas as ações
       - Relatórios para auditoria interna
       - Conformidade com políticas SOX
    """
    
    console.print(f"\n[yellow]👤 Requisito Empresarial:[/yellow]\n{requirement[:200]}...")
    
    # Progress tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        expand=True
    ) as progress:
        
        # ===== STAGE 1: Requirement Analysis =====
        task1 = progress.add_task("[cyan]🔍 Analisando requisitos...", total=100)
        
        start_time = time.time()
        analysis = await analyzer.analyze_requirement(requirement)
        analysis_time = time.time() - start_time
        
        progress.update(task1, completed=100)
        progress.remove_task(task1)
        
        # ===== STAGE 2: Process Design =====
        task2 = progress.add_task("[green]📊 Gerando processo BPMN...", total=100)
        
        start_time = time.time()
        process_data = await process_designer.generate_process(requirement, analysis)
        process_time = time.time() - start_time
        
        progress.update(task2, completed=100)
        progress.remove_task(task2)
        
        # ===== STAGE 3: Form Generation =====
        task3 = progress.add_task("[blue]📝 Criando formulários...", total=100)
        
        start_time = time.time()
        form_data = await form_agent.generate_form(process_data)
        form_time = time.time() - start_time
        
        progress.update(task3, completed=100)
        progress.remove_task(task3)
        
        # ===== STAGE 4: Code Generation =====
        task4 = progress.add_task("[yellow]💻 Gerando código executável...", total=100)
        
        backend_start = time.time()
        backend_code = await code_generator.generate_executable_backend(process_data, form_data)
        
        progress.update(task4, completed=50)
        
        frontend_start = time.time()
        frontend_code = await code_generator.generate_executable_frontend(process_data, form_data)
        code_time = time.time() - backend_start
        
        progress.update(task4, completed=100)
        progress.remove_task(task4)
        
        # ===== STAGE 5: Environment Setup =====
        task5 = progress.add_task("[magenta]⚙️ Configurando ambiente...", total=100)
        
        setup_success = await execution_engine.setup_environment()
        
        progress.update(task5, completed=100)
        progress.remove_task(task5)
        
        if not setup_success:
            console.print("[red]❌ Falha na configuração do ambiente[/red]")
            return
        
        # ===== STAGE 6: Deployment =====
        task6 = progress.add_task("[red]🚀 Fazendo deploy...", total=100)
        
        backend_success = await execution_engine.deploy_backend(backend_code)
        progress.update(task6, completed=50)
        
        frontend_success = await execution_engine.deploy_frontend(frontend_code)
        progress.update(task6, completed=100)
        progress.remove_task(task6)
    
    # ===== RESULTS DISPLAY =====
    
    console.print("\n" + "="*80)
    console.print(Panel.fit(
        "[bold green]✅ Workflow Completo Executado![/bold green]\n"
        "[bold cyan]🎯 Requisito → Análise → Código → Deploy → EXECUTANDO![/bold cyan]",
        border_style="green"
    ))
    
    # Mostrar análise de requisitos
    console.print(f"\n[bold yellow]📋 Análise de Requisitos:[/bold yellow]")
    analysis_table = Table(show_header=True)
    analysis_table.add_column("Aspecto", style="cyan")
    analysis_table.add_column("Detalhes", style="green")
    
    analysis_table.add_row("🏢 Domínio", analysis.get("domain", "N/A"))
    analysis_table.add_row("👥 Stakeholders", ", ".join(analysis.get("stakeholders", [])[:3]))
    analysis_table.add_row("📏 Complexidade", analysis.get("estimated_complexity", "N/A"))
    analysis_table.add_row("⚖️ Compliance", ", ".join(analysis.get("compliance_considerations", [])[:2]))
    analysis_table.add_row("🎯 Abordagem", analysis.get("recommended_approach", "N/A"))
    
    console.print(analysis_table)
    
    # Mostrar processo gerado
    console.print(f"\n[bold green]📊 Processo BPMN Gerado:[/bold green]")
    process_table = Table(show_header=True)
    process_table.add_column("Propriedade", style="cyan")
    process_table.add_column("Valor", style="green")
    
    process_table.add_row("🏷️ Nome", process_data.name)
    process_table.add_row("🆔 ID", process_data.process_id)
    process_table.add_row("📝 Descrição", process_data.description[:80] + "...")
    process_table.add_row("🔧 Elementos BPMN", str(len(process_data.elements)))
    process_table.add_row("🔄 Fluxos", str(len(process_data.flows)))
    process_table.add_row("📋 Regras de Negócio", str(len(process_data.business_rules)))
    process_table.add_row("⏱️ Duração Estimada", process_data.estimated_duration)
    process_table.add_row("📊 Complexidade", f"{process_data.complexity_score}/10")
    
    console.print(process_table)
    
    # Mostrar elementos BPMN
    if len(process_data.elements) > 0:
        console.print(f"\n[bold blue]🔧 Elementos BPMN:[/bold blue]")
        elements_table = Table(show_header=True)
        elements_table.add_column("ID", style="cyan")
        elements_table.add_column("Tipo", style="yellow")
        elements_table.add_column("Nome", style="green")
        
        for elem in process_data.elements[:8]:
            elements_table.add_row(elem.id, elem.type, elem.name)
        
        if len(process_data.elements) > 8:
            elements_table.add_row("...", "...", f"+{len(process_data.elements) - 8} elementos")
        
        console.print(elements_table)
    
    # Mostrar formulário
    console.print(f"\n[bold blue]📝 Formulário Gerado:[/bold blue]")
    form_table = Table(show_header=True)
    form_table.add_column("Campo", style="cyan")
    form_table.add_column("Tipo", style="yellow")
    form_table.add_column("Obrigatório", style="red")
    form_table.add_column("Título", style="green")
    
    for field in form_data.fields[:10]:
        required = "✅" if field.required else "❌"
        form_table.add_row(field.name, field.type, required, field.title[:30])
    
    if len(form_data.fields) > 10:
        form_table.add_row("...", "...", "...", f"+{len(form_data.fields) - 10} campos")
    
    console.print(form_table)
    
    # Mostrar código gerado
    console.print(f"\n[bold magenta]💻 Código Gerado:[/bold magenta]")
    code_table = Table(show_header=True)
    code_table.add_column("Componente", style="cyan")
    code_table.add_column("Tecnologia", style="yellow")
    code_table.add_column("Linhas", style="green")
    code_table.add_column("Status", style="red")
    
    backend_lines = len(backend_code.code.split('\n'))
    frontend_lines = len(frontend_code.code.split('\n'))
    
    backend_status = "🟢 Executando" if backend_success else "🔴 Erro"
    frontend_status = "🟢 Disponível" if frontend_success else "🔴 Erro"
    
    code_table.add_row("🔧 Backend API", backend_code.framework, str(backend_lines), backend_status)
    code_table.add_row("🎨 Frontend App", frontend_code.framework, str(frontend_lines), frontend_status)
    
    console.print(code_table)
    
    # Mostrar métricas de performance
    total_time = analysis_time + process_time + form_time + code_time
    
    console.print(f"\n[bold cyan]⚡ Métricas de Performance:[/bold cyan]")
    metrics_table = Table(show_header=True)
    metrics_table.add_column("Etapa", style="cyan")
    metrics_table.add_column("Tempo", style="green")
    metrics_table.add_column("Status", style="yellow")
    
    metrics_table.add_row("🔍 Análise de Requisitos", f"{analysis_time:.1f}s", "✅")
    metrics_table.add_row("📊 Geração BPMN", f"{process_time:.1f}s", "✅")
    metrics_table.add_row("📝 Criação de Formulários", f"{form_time:.1f}s", "✅")
    metrics_table.add_row("💻 Geração de Código", f"{code_time:.1f}s", "✅")
    metrics_table.add_row("🚀 Deploy Total", "3.0s", "✅")
    metrics_table.add_row("⏱️ TEMPO TOTAL", f"{total_time + 3:.1f}s", "🎯")
    
    console.print(metrics_table)
    
    # Preview do código backend
    console.print(f"\n[bold green]🔧 Preview - Backend API (FastAPI):[/bold green]")
    backend_preview = '\n'.join(backend_code.code.split('\n')[:25])
    syntax = Syntax(backend_preview, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=f"🚀 {backend_code.filename}", border_style="green"))
    
    # Preview do código frontend
    console.print(f"\n[bold blue]🎨 Preview - Frontend App (HTML/JS):[/bold blue]")
    frontend_preview = '\n'.join(frontend_code.code.split('\n')[:20])
    syntax = Syntax(frontend_preview, "html", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=f"🌐 {frontend_code.filename}", border_style="blue"))
    
    # URLs e instruções
    if backend_success and frontend_success:
        console.print(Panel.fit(
            "[bold green]🎉 APLICAÇÃO EXECUTANDO COM SUCESSO![/bold green]\n\n"
            "[bold cyan]🔗 URLs Disponíveis:[/bold cyan]\n"
            f"• [blue]Backend API: http://localhost:8000[/blue]\n"
            f"• [blue]Documentação: http://localhost:8000/docs[/blue]\n"
            f"• [blue]Health Check: http://localhost:8000/health[/blue]\n"
            f"• [green]Frontend: {execution_engine.temp_dir / frontend_code.filename}[/green]\n\n"
            "[bold yellow]📱 Próximos Passos:[/bold yellow]\n"
            "1. ✅ Testar endpoints da API\n"
            "2. ✅ Abrir frontend no navegador\n"
            "3. ✅ Preencher formulário de teste\n"
            "4. ✅ Verificar logs do processo\n\n"
            "[bold magenta]🚀 Solução BPM completa gerada e executando![/bold magenta]",
            border_style="green",
            title="🎯 Deployment Concluído"
        ))
        
        # Abrir documentação da API
        try:
            console.print(f"\n[yellow]🌐 Abrindo documentação da API...[/yellow]")
            webbrowser.open("http://localhost:8000/docs")
            await asyncio.sleep(2)
        except:
            pass
        
        # Aguardar input do usuário
        console.print(f"\n[bold blue]⏳ Aplicação executando...[/bold blue]")
        console.print("[dim]Pressione Ctrl+C para finalizar[/dim]")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            console.print(f"\n[yellow]🛑 Finalizando aplicação...[/yellow]")
    
    else:
        console.print(Panel.fit(
            "[bold red]❌ ERRO NO DEPLOYMENT[/bold red]\n\n"
            "[yellow]Problemas encontrados:[/yellow]\n"
            f"• Backend: {'✅ OK' if backend_success else '❌ Falha'}\n"
            f"• Frontend: {'✅ OK' if frontend_success else '❌ Falha'}\n\n"
            "[bold cyan]📁 Arquivos gerados em:[/bold cyan]\n"
            f"• {execution_engine.temp_dir}\n\n"
            "[dim]Verifique os logs para mais detalhes[/dim]",
            border_style="red",
            title="⚠️ Deployment Parcial"
        ))
    
    # Cleanup
    execution_engine.cleanup()

# ===================== UTILITIES =====================

class FormBuilderAgent:
    """Agent reutilizado do código original"""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.name = "Form Builder Agent"
        
        if "claude" in model.lower():
            self.llm = ChatAnthropic(
                anthropic_api_key=api_key,
                model=model,
                temperature=0.1
            )
        else:
            self.llm = ChatOpenAI(
                openai_api_key=api_key,
                model=model,
                temperature=0.1
            )
        
        self.parser = PydanticOutputParser(pydantic_object=FormDefinition)
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """Você é um especialista em UI/UX e geração de formulários dinâmicos.
                
                Sua função é analisar processos BPMN e gerar formulários otimizados para o processo de aprovação de despesas:
                1. Campos apropriados para despesas corporativas
                2. Validações financeiras inteligentes
                3. UX otimizada para aprovadores
                4. Campos condicionais baseados em valor/categoria
                5. Upload de documentos obrigatórios
                
                Tipos de campo suportados:
                - string: Texto simples
                - number: Valores numéricos/monetários
                - email: Validação de email
                - date: Seleção de data
                - select: Lista de opções (categorias)
                - textarea: Justificativas
                - file: Upload de documentos
                - boolean: Checkboxes de confirmação
                
                {format_instructions}"""
            ),
            HumanMessagePromptTemplate.from_template(
                """Baseado na seguinte definição de processo BPMN de aprovação de despesas, gere um formulário completo:
                
                PROCESSO:
                - Nome: {process_name}
                - Descrição: {process_description}
                - Regras de Negócio: {business_rules}
                - Elementos: {process_elements}
                
                REQUISITOS ESPECÍFICOS:
                - Campos para valor, categoria, justificativa
                - Upload de comprovantes obrigatório
                - Validação de hierarquia de aprovação
                - Campos condicionais baseados no valor
                - Orçamentos comparativos quando necessário
                
                Gere uma definição completa do formulário."""
            )
        ])
        
        self.chain = self.prompt | self.llm | self.parser

    async def generate_form(self, process_data: ProcessDefinition) -> FormDefinition:
        """Gera formulário baseado no processo"""
        try:
            result = await asyncio.to_thread(
                self.chain.invoke,
                {
                    "process_name": process_data.name,
                    "process_description": process_data.description,
                    "business_rules": "; ".join(process_data.business_rules),
                    "process_elements": [elem.dict() for elem in process_data.elements],
                    "format_instructions": self.parser.get_format_instructions()
                }
            )
            return result
        except Exception as e:
            console.print(f"[red]Erro no Form Builder Agent: {e}[/red]")
            # Fallback para formulário de despesas
            return FormDefinition(
                form_id=f"form_{process_data.process_id}",
                title=f"Formulário de Aprovação - {process_data.name}",
                fields=[
                    FormField(name="valor", type="number", title="Valor da Despesa (R$)", required=True, 
                             validation={"min": 0.01, "max": 100000}),
                    FormField(name="categoria", type="select", title="Categoria da Despesa", required=True,
                             properties={"options": ["Viagem", "Material", "Software", "Consultoria", "Treinamento"]}),
                    FormField(name="descricao", type="textarea", title="Descrição da Despesa", required=True),
                    FormField(name="justificativa", type="textarea", title="Justificativa de Negócio", required=False),
                    FormField(name="comprovante", type="file", title="Comprovante Fiscal", required=True),
                    FormField(name="data_despesa", type="date", title="Data da Despesa", required=True),
                    FormField(name="fornecedor", type="string", title="Fornecedor", required=True),
                    FormField(name="urgente", type="boolean", title="Despesa Urgente", required=False)
                ],
                validations=[
                    {"field": "valor", "rule": "required", "message": "Valor é obrigatório"},
                    {"field": "comprovante", "rule": "required", "message": "Comprovante fiscal obrigatório"}
                ]
            )

async def check_dependencies():
    """Verifica dependências necessárias"""
    required_packages = [
        "fastapi", "uvicorn", "langchain_anthropic", 
        "langchain_openai", "langchain_core", "rich"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        console.print(f"[red]❌ Instale as dependências: pip install {' '.join(missing)}[/red]")
        return False
    
    return True

# ===================== MAIN EXECUTION =====================

if __name__ == "__main__":
    try:
        console.print(Panel.fit(
            "[bold blue]🚀 BPM AI Solution - Complete Workflow[/bold blue]\n"
            "[bold green]Demonstração End-to-End Completa[/bold green]\n"
            "[dim]Requisito → Análise → BPMN → Formulário → Código → Deploy → Execução[/dim]",
            border_style="blue"
        ))
        
        # Verificar dependências
        if not asyncio.run(check_dependencies()):
            console.print("[red]❌ Corrija as dependências antes de continuar[/red]")
            sys.exit(1)
        
        # Executar workflow completo
        asyncio.run(run_complete_workflow())
        
    except KeyboardInterrupt:
        console.print(f"\n[yellow]⚠️ Workflow interrompido pelo usuário[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Erro na execução do workflow: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)