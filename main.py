from http.client import HTTPException
import uuid
from fastapi import FastAPI, Form, Request, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from models import *

app = FastAPI()


@app.get("/")
async def index(request: Request):
    print('Request for index page received')
    return "hello world"

'''Loja Online'''
virtual_store_router = APIRouter(tags=["Loja Online"])

@virtual_store_router.post("/virtual_store/cea/process_payment", response_model=PagamentoLojaOutput)
async def a(input_data: PagamentoLojaInput):
    transacao_id = f"TXN-cea-{uuid.uuid4()}"
    cartao_token = f"TOKEN-CC-{uuid.uuid4()}"
    output = PagamentoLojaOutput(
        transacao_id=transacao_id,
        pedido_id=input_data.pedido_id,
        valor=input_data.valor_total,
        cliente_id=input_data.cliente.id,
        cartao_token=cartao_token
    )
    return output

@virtual_store_router.post("/virtual_store/riachuelo/process_payment", response_model=PagamentoLojaOutput)
async def b(input_data: PagamentoLojaInput):
    transacao_id = f"TXN-riachuelo-{uuid.uuid4()}"
    cartao_token = f"TOKEN-CC-{uuid.uuid4()}"
    output = PagamentoLojaOutput(
        transacao_id=transacao_id,
        pedido_id=input_data.pedido_id,
        valor=input_data.valor_total,
        cliente_id=input_data.cliente.id,
        cartao_token=cartao_token
    )
    return output

@virtual_store_router.post("/virtual_store/cea/delivery_product", response_model=EntregaLojaOutput)
async def c(input_data: EntregaLojaInput):
    id_entrega = f"ENT-cea-{uuid.uuid4()}"
    
    output = EntregaLojaOutput(
        id_entrega=id_entrega,
        pedido_id=input_data.pedido_id,
    )
    
    return output

@virtual_store_router.post("/virtual_store/riachuelo/delivery_product", response_model=EntregaLojaOutput)
async def d(input_data: EntregaLojaInput):
    id_entrega = f"ENT-riachuelo-{uuid.uuid4()}"
    
    output = EntregaLojaOutput(
        id_entrega=id_entrega,
        pedido_id=input_data.pedido_id,
    )
    
    return output

@virtual_store_router.post("/virtual_store/cea/end_buy", response_model=LojaFinalOutput)
async def aa(input_data: LojaFinalInput):
    output = LojaFinalOutput(
        status=input_data.status_entrega,
        output="site atualizado"
    )
    return output

@virtual_store_router.post("/virtual_store/riachuelo/end_buy", response_model=LojaFinalOutput)
async def bb(input_data: LojaFinalInput):
    output = LojaFinalOutput(
        status=input_data.status_entrega,
        output="site atualizado"
    )
    return output

'''Gateway de Pagamento'''
gateway_router = APIRouter(tags=["Gateway de Pagamento"])

@gateway_router.post("/gateway_payment/paypal/process_payment", response_model=GatewayPagamentoOutput)
async def e(input_data: GatewayPagamentoInput):
    id_gateway = f"GW-paypal-{uuid.uuid4()}"
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

@gateway_router.post("/gateway_payment/pagarme/process_payment", response_model=GatewayPagamentoOutput)
async def f(input_data: GatewayPagamentoInput):
    id_gateway = f"GW-pagarme-{uuid.uuid4()}"
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

@gateway_router.post("/gateway_payment/paypal/analysis", response_model=GatewayAnaliseOutput)
async def ee(input_data: GatewayAnaliseInput):
    id_analise = f"ANALY-paypal-{uuid.uuid4()}"
    
    output = GatewayAnaliseOutput(
        id_analise_gateway=id_analise,
        status_preliminar="aprovado"
    )
    return output

@gateway_router.post("/gateway_payment/pagarme/analysis", response_model=GatewayAnaliseOutput)
async def ff(input_data: GatewayAnaliseInput):
    id_analise = f"ANALY-pagarme-{uuid.uuid4()}"
    
    output = GatewayAnaliseOutput(
        id_analise_gateway=id_analise,
        status_preliminar="aprovado"
    )
    return output

@gateway_router.post("/gateway_payment/pagarme/end", response_model=GatewayFinalOutput)
async def ee(input_data: GatewayFinalInput):
    output = GatewayFinalOutput(
        output="Validação completa"
    )
    return output

@gateway_router.post("/gateway_payment/paypal/end", response_model=GatewayFinalOutput)
async def ee(input_data: GatewayFinalInput):
    output = GatewayFinalOutput(
        output="Validação completa"
    )
    return output

'''Adquirente'''
aquirer_router = APIRouter(tags=["Adquirente"])

@aquirer_router.post("/aquirer/cielo/validate_payment", response_model=AdquirenteOutput)
async def g(input_data: AdquirenteInput):
    autorizacao_adq = f"AUTH-cielo-{uuid.uuid4()}"
    output = AdquirenteOutput(
        codigo_resposta_adq="00",
        autorizacao_adq=autorizacao_adq,
        id_gateway=input_data.id_gateway
    )
    return output

@aquirer_router.post("/aquirer/stone/validate_payment", response_model=AdquirenteOutput)
async def h(input_data: AdquirenteInput):
    autorizacao_adq = f"AUTH-stone-{uuid.uuid4()}"
    output = AdquirenteOutput(
        codigo_resposta_adq="00",
        autorizacao_adq=autorizacao_adq,
        id_gateway=input_data.id_gateway
    )
    return output


'''Anti fraude'''
antifraud_router = APIRouter(tags=["Anti Fraude"])

@antifraud_router.post("/atifraud/rudder/validate_payment", response_model=AntifraudeOutput)
async def i(input_data: AntifraudeInput):
    output = AntifraudeOutput(
        status_antifraude="aprovado/rudder",
        score_risco=20,
        recomendacao="liberar"
    )
    return output

@antifraud_router.post("/atifraud/netrin/validate_payment", response_model=AntifraudeOutput)
async def j(input_data: AntifraudeInput):
    output = AntifraudeOutput(
        status_antifraude="aprovado/netrin",
        score_risco=15,
        recomendacao="liberar"
    )
    return output


'''Bandeira''' 
flag_router = APIRouter(tags=["Bandeira"])

@flag_router.post("/flag/visa/validate_payment", response_model=BandeiraOutput)
async def l(input_data: BandeiraInput):
    autorizacao_bandeira = f"AUTH-BAND-{uuid.uuid4()}"
    
    output = BandeiraOutput(
        status_bandeira="aprovado",
        autorizacao_bandeira=autorizacao_bandeira
    )
    
    return output

@flag_router.post("/flag/mastercard/validate_payment", response_model=BandeiraOutput)
async def m(input_data: BandeiraInput):
    autorizacao_bandeira = f"AUTH-BAND-{uuid.uuid4()}"
    
    output = BandeiraOutput(
        status_bandeira="aprovado",
        autorizacao_bandeira=autorizacao_bandeira
    )
    
    return output

'''Emissor'''
emissor_router = APIRouter(tags=["Emissor"])

@emissor_router.post("/issuing/bradesco/validate_payment", response_model=EmissorOutput)
async def n(input_data: EmissorInput):
    codigo_autorizacao_final = f"AUTH-bradesco-{uuid.uuid4()}"
    
    output = EmissorOutput(
        status_emissor="aprovado",
        codigo_autorizacao_final=codigo_autorizacao_final
    )
    
    return output

@emissor_router.post("/issuing/santander/validate_payment", response_model=EmissorOutput)
async def o(input_data: EmissorInput):
    codigo_autorizacao_final = f"AUTH-santander-{uuid.uuid4()}"
    
    output = EmissorOutput(
        status_emissor="aprovado",
        codigo_autorizacao_final=codigo_autorizacao_final
    )
    
    return output

'''Transportadora'''
transporter_router = APIRouter(tags=["Transportadora"])

@transporter_router.post("/transporter/correios/delivery_item", response_model=TransportadoraOutput)
async def p(input_data: TransportadoraInput):
    output = TransportadoraOutput(
        status="entregue",
        codigo_rastreio=f"TRACK-correios-{uuid.uuid4()}",
        previsao_entrega=date.today() + timedelta(days=7),
        id_entrega=input_data.id_entrega
    )
    return output

@transporter_router.post("/transporter/loggi/delivery_item", response_model=TransportadoraOutput)
async def q(input_data: TransportadoraInput):
    
    output = TransportadoraOutput(
        status="entregue",
        codigo_rastreio=f"TRACK-loggi-{uuid.uuid4()}",
        previsao_entrega=date.today() + timedelta(days=7),
        id_entrega=input_data.id_entrega
    )
    
    return output

app.include_router(virtual_store_router)
app.include_router(gateway_router)
app.include_router(aquirer_router)
app.include_router(antifraud_router)
app.include_router(flag_router)
app.include_router(emissor_router)
app.include_router(transporter_router)


origins = [
    "http://127.0.0.1:8000",
    "https://127.0.0.1:8000 ",
    "http://localhost"
    "http://localhost:8000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8003)