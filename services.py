from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import date, timedelta
import uvicorn

app = FastAPI()

# Armazenamento em memória para simular persistência de dados
transacoes = {}
autorizacoes = {}
entregas = {}

# --- Modelos Pydantic ---

# Passo 1: Processamento do pagamento pela Loja Virtual
class ItemPedido(BaseModel):
    produto_id: str
    quantidade: int

class Cliente(BaseModel):
    id: str
    email: str

class Cartao(BaseModel):
    numero: str
    validade: str

class PagamentoLojaInput(BaseModel):
    pedido_id: str
    valor_total: float
    itens: List[ItemPedido]
    cliente: Cliente
    cartao: Cartao

class PagamentoLojaOutput(BaseModel):
    transacao_id: str
    pedido_id: str
    valor: float
    cliente_id: str
    cartao_token: str

# Passo 2: Gateway-de-Pagamento
class GatewayPagamentoInput(BaseModel):
    transacao_id: str
    valor: float
    cartao_token: str
    parcelas: int

class GatewayPagamentoOutput(BaseModel):
    id_gateway: str
    status: str
    detalhes: dict

# Passo 3: Adquirente
class AdquirenteInput(BaseModel):
    id_gateway: str
    valor: float

class AdquirenteOutput(BaseModel):
    codigo_resposta_adq: str
    autorizacao_adq: str
    id_gateway: str

# Passo 4: Bandeira
class BandeiraInput(BaseModel):
    codigo_autorizacao: str
    dados_cartao: str

class BandeiraOutput(BaseModel):
    status_bandeira: str
    autorizacao_bandeira: str

# Passo 5: Emissor
class EmissorInput(BaseModel):
    autorizacao_bandeira: str
    valor_parcela: float

class EmissorOutput(BaseModel):
    status_emissor: str
    codigo_autorizacao_final: str

# Passo 6: Análise Gateway
class GatewayAnaliseInput(BaseModel):
    id_gateway: str
    autorizacao_emissor: str

class GatewayAnaliseOutput(BaseModel):
    id_analise_gateway: str
    status_preliminar: str

# Passo 7: Antifraude
class AntifraudeInput(BaseModel):
    id_gateway: str
    email_cliente: str

class AntifraudeOutput(BaseModel):
    status_antifraude: str
    score_risco: int
    recomendacao: str

# Passo 8: Entrega Loja
class EnderecoEntrega(BaseModel):
    cep: str
    logradouro: str

class EntregaLojaInput(BaseModel):
    pedido_id: str
    id_gateway: str
    endereco_entrega: EnderecoEntrega
    itens: List[ItemPedido]

class EntregaLojaOutput(BaseModel):
    id_entrega: str
    pedido_id: str
    transportadora: str

# Passo 9: Transportadora
class Dimensoes(BaseModel):
    peso_kg: float
    largura_cm: int

class TransportadoraInput(BaseModel):
    id_entrega: str
    dimensoes: Dimensoes

class TransportadoraOutput(BaseModel):
    status: str
    codigo_rastreio: str
    previsao_entrega: date

# --- Endpoints ---

@app.post("/loja/pagamento", response_model=PagamentoLojaOutput)
async def processar_pagamento_loja(input_data: PagamentoLojaInput):
    transacao_id = f"TXN-LOJA-{uuid.uuid4().hex[:6]}"
    cartao_token = f"TOKEN-CC-{uuid.uuid4().hex[:4]}"
    
    output = PagamentoLojaOutput(
        transacao_id=transacao_id,
        pedido_id=input_data.pedido_id,
        valor=input_data.valor_total,
        cliente_id=input_data.cliente.id,
        cartao_token=cartao_token
    )
    
    # Armazena para uso posterior
    transacoes[transacao_id] = {
        "input": input_data.dict(),
        "output": output.dict()
    }
    
    return output

@app.post("/gateway/pagamento", response_model=GatewayPagamentoOutput)
async def processar_gateway(input_data: GatewayPagamentoInput):
    
    id_gateway = f"GW-TXN-{uuid.uuid4().hex[:6]}"
    valor_parcela = input_data.valor / input_data.parcelas
    
    output = GatewayPagamentoOutput(
        id_gateway=id_gateway,
        status="pendente_validacao",
        detalhes={
            "transacao_origem": input_data.transacao_id,
            "valor_parcelado": valor_parcela
        }
    )
    
    return output

@app.post("/adquirente/validar", response_model=AdquirenteOutput)
async def validar_adquirente(input_data: AdquirenteInput):
    # Verifica se o gateway existe
    if input_data.id_gateway not in autorizacoes:
        raise HTTPException(status_code=404, detail="Transação Gateway não encontrada")
    
    autorizacao_adq = f"AUTH-ADQ-{uuid.uuid4().hex[:6]}"
    
    output = AdquirenteOutput(
        codigo_resposta_adq="00",
        autorizacao_adq=autorizacao_adq,
        id_gateway=input_data.id_gateway
    )
    
    return output

@app.post("/bandeira/validar", response_model=BandeiraOutput)
async def validar_bandeira(input_data: BandeiraInput):
    autorizacao_bandeira = f"AUTH-BAND-{uuid.uuid4().hex[:6]}"
    
    output = BandeiraOutput(
        status_bandeira="aprovado",
        autorizacao_bandeira=autorizacao_bandeira
    )
    
    return output

@app.post("/emissor/validar", response_model=EmissorOutput)
async def validar_emissor(input_data: EmissorInput):
    codigo_autorizacao_final = f"AUTH-EMI-{uuid.uuid4().hex[:6]}"
    
    output = EmissorOutput(
        status_emissor="aprovado",
        codigo_autorizacao_final=codigo_autorizacao_final
    )
    
    return output

@app.post("/gateway/analise", response_model=GatewayAnaliseOutput)
async def analisar_gateway(input_data: GatewayAnaliseInput):
    # Verifica se o gateway existe
    if input_data.id_gateway not in autorizacoes:
        raise HTTPException(status_code=404, detail="Transação Gateway não encontrada")
    
    id_analise = f"ANAL-GW-{uuid.uuid4().hex[:6]}"
    
    output = GatewayAnaliseOutput(
        id_analise_gateway=id_analise,
        status_preliminar="aprovado"
    )
    
    
    return output

@app.post("/antifraude/analisar", response_model=AntifraudeOutput)
async def analisar_antifraude(input_data: AntifraudeInput):
    # Verifica se o gateway existe
    if input_data.id_gateway not in autorizacoes:
        raise HTTPException(status_code=404, detail="Transação Gateway não encontrada")
    
    output = AntifraudeOutput(
        status_antifraude="aprovado",
        score_risco=20,
        recomendacao="liberar"
    )
    
    return output

@app.post("/loja/entrega", response_model=EntregaLojaOutput)
async def processar_entrega_loja(input_data: EntregaLojaInput):
    
    id_entrega = f"ENT-{uuid.uuid4().hex[:6]}"
    
    output = EntregaLojaOutput(
        id_entrega=id_entrega,
        pedido_id=input_data.pedido_id,
        transportadora="Correios"
    )
    
    # Armazena para uso posterior
    entregas[id_entrega] = {
        "input": input_data.dict(),
        "output": output.dict()
    }
    
    return output

@app.post("/transportadora/entregar", response_model=TransportadoraOutput)
async def processar_entrega_transportadora(input_data: TransportadoraInput):
    # Verifica se a entrega existe
    if input_data.id_entrega not in entregas:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")
    
    output = TransportadoraOutput(
        status="em_transito",
        codigo_rastreio=f"TRACK-{uuid.uuid4().hex[:6]}",
        previsao_entrega=date.today() + timedelta(days=7)
    )
    
    return output


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)