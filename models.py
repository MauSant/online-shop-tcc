from pydantic import BaseModel
from datetime import date, timedelta


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
    itens: list[ItemPedido]
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
    ip: str

class AntifraudeOutput(BaseModel):
    status_antifraude: str
    score_risco: int
    recomendacao: str

# Passo 8: Fim gateway
class GatewayFinalInput(BaseModel):
    status_antifraude: str

class GatewayFinalOutput(BaseModel):
    output: str


# Passo 9: Entrega Loja
class EnderecoEntrega(BaseModel):
    cep: str
    logradouro: str

class EntregaLojaInput(BaseModel):
    pedido_id: str
    id_gateway: str
    endereco_entrega: EnderecoEntrega
    itens: list[ItemPedido]

class EntregaLojaOutput(BaseModel):
    id_entrega: str
    pedido_id: str

# Passo 10: Transportadora
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
    id_entrega: str

# Passo 11: Loja online final

class LojaFinalInput(BaseModel):
    id_entrega: str
    pedido_id: str
    status_entrega: str

class LojaFinalOutput(BaseModel):
    status: str
    output: str
