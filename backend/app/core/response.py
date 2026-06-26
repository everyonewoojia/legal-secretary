from typing import Any
from fastapi.responses import JSONResponse


def success(data: Any = None, message: str = "success") -> JSONResponse:
    return JSONResponse(content={"code": 0, "message": message, "data": data})


def error(code: int = 40001, message: str = "error", data: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=400 if code < 50000 else 500,
        content={"code": code, "message": message, "data": data},
    )
