from fastapi import FastAPI, HTTPException, Request  # Importa HTTPException
from fastapi.responses import JSONResponse

from app.api.v1.auth import router as login_router
from app.api.v1.orders import router as orders_router
from app.api.v1.products import router as products_router
from app.api.v1.users import router as users_router

app = FastAPI()

app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(products_router, prefix="/api/v1/products", tags=["products"])
app.include_router(orders_router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(login_router, prefix="/api/v1/auth", tags=["auth"])

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # PASO CRÍTICO: Si el error ya es una HTTPException (nuestra lógica de negocio),
    # dejamos que FastAPI lo maneje normal o lo relanzamos.
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    # Solo para errores verdaderamente desconocidos (crashes de Python), devolvemos 500
    print(f"🔥 ERROR 500 NO CONTROLADO: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error_real": str(exc)},
    )

@app.get("/")
async def root():
    return {"message": "Welcome to the DevCris80's E-commerce API"}
