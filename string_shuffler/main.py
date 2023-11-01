from typing import Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import string_utils

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class ShuffleState(BaseModel):
    input: str = "FavouriteName"
    amount: str = "10"
    output: Optional[list[str]] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.output is None:
            self.output = ["..."]

shuffle_state = ShuffleState()


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Root</title>
        </head>
        <body>
            <h1>Hello New World!</h1>
        </body>
    </html>
    """


def shuffle(input: str, amount: int = 1) -> list[str]:
    return [string_utils.shuffle(input).title() for _ in range(amount)]

@app.get("/shuffle/{input}")
async def page_shuffle(input: str, amount: int = 1):
    return {
        "input": input,
        "shuffled": shuffle(input, amount),
    }

@app.get("/shuffler", response_class=HTMLResponse)
async def page_shuffler(request: Request):
    return templates.TemplateResponse(
        "shuffler.html", {
            "request": request, 
            "output": shuffle_state.output, 
            "input": shuffle_state.input, 
            "amount": shuffle_state.amount}
        )

@app.post("/shuffler/go")
async def page_shuffler_go(input: str = Form(...), amount: str = Form(...)):
    output = shuffle(input, int(amount))
    shuffle_state.output = output
    shuffle_state.input = input 
    shuffle_state.amount = amount
    response = RedirectResponse(
        url="/shuffler", 
        status_code=303,  # to enable redirect from POST to GET
    )
    return response


