from fastapi import HTTPException, status


def credentials_exception(
    detail="authentication failed",
):
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detail)


def form_exception(detail="The form data has been compromised"):
    return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail)


def file_exception(detail="The file size is above the max limit"):
    return HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail)
