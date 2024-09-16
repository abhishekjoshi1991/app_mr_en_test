from fastapi import FastAPI
from const import (
    TITLE,
    DESCRIPTION,
)
from routers import routes
from version import __version__

app = FastAPI(
    title=TITLE,
    description=DESCRIPTION,
    version=__version__,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)
app.include_router(routes.router)
