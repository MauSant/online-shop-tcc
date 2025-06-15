from fastapi import FastAPI, Form, Request, status
import uvicorn


app = FastAPI()

@app.get("/")
async def index(request: Request):
    print('Request for index page received')
    return "hello world"
'''Loja Online'''
@app.get("/virtual_store/cea/process_payment")
async def index():
    return "Pagamento processado pela C & A"

@app.get("/virtual_store/riachuelo/process_payment")
async def index():
    return "Pagamento processado pela riachuelo"

@app.get("/virtual_store/cea/delivery_product")
async def index():
    return "Produto entregue pela C & A"

@app.get("/virtual_store/riachuelo/delivery_product")
async def index():
    return "Produto entregue pela Riachuelo"

'''Gateway de Pagamento'''
@app.get("/gateway_payment/paypal/process_payment")
async def index():
    return "Pagamento processado pela paypal"

@app.get("/gateway_payment/pagarme/process_payment")
async def index():
    return "Pagamento processado pela pagar.me"

'''Adquirente'''
@app.get("/aquirer/cielo/validate_payment")
async def index():
    return "Pagamento validado pela CIELO"

@app.get("/aquirer/stone/validate_payment")
async def index():
    return "Pagamento validado pela STONE"


'''Anti fraude'''
@app.get("/atifraud/rudder/validate_payment")
async def index():
    return "Pagamento validado pela RUDDER"

@app.get("/atifraud/rudder/validate_payment")
async def index():
    return "Pagamento validado pela RUDDER"


'''Bandeira''' #TODO
@app.get("/flag/rudder/validate_payment")
async def index():
    return "Pagamento validado pela RUDDER"

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)