from fastapi.encoders import jsonable_encoder
import logging
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse

from schemas import ApiResponse


def generate_response(
    code=status.HTTP_200_OK,
    message=None,
    data=[],
    headers={},
    success=True,
    media_type="application/json",
):
    try:
        if code not in [200, 201, 202, 204]:
            return HTTPException(
                status_code=code,
                detail=jsonable_encoder(
                    ApiResponse(
                        status_code=code,
                        data=data,
                        message=str(message),
                        success=success,
                    ).__dict__
                ),
            )
        else:
            return JSONResponse(
                status_code=code,
                media_type=media_type,
                headers=headers,
                content=jsonable_encoder(
                    ApiResponse(
                        status_code=code, data=data, message=message, success=success
                    ).__dict__
                ),
            )
    except Exception as e:
        return "Error occurred in generate_response:"
