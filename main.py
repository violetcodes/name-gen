from name_generator import get_new_name as _get_new_name 
from time import time 
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from collections import defaultdict 
from fastapi import HTTPException


app = FastAPI()
templates = Jinja2Templates(directory="templates")

def serve_index(request: Request, message: str, subtitle: str = None):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "message": message,
        "subtitle": subtitle or '',
    })

def get_new_name(starts_with: str = None, category: str = None): 
    """
    Generate a name based on the provided starting letters and category.
    :param starts_with: Starting letters for the name.
    :param category: Category to match.
    :return: Generated name.
    """
    name, category = _get_new_name(starts_with, category).split(": ", 1) 
    return name, category  
    

app = FastAPI()

RATE_LIMIT = 10
WINDOW_SIZE = 60  # in seconds

# IP -> list of timestamps
ip_request_log = defaultdict(list)

ip_blocked_until = {}

@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    client_ip = request.client.host
    current_time = time()

    if client_ip in ip_blocked_until and current_time < ip_blocked_until[client_ip]:
        return JSONResponse(status_code=429, content={"detail": "You are temporarily blocked. Try again later."})

    recent_requests = [t for t in ip_request_log[client_ip] if current_time - t < WINDOW_SIZE]
    ip_request_log[client_ip] = recent_requests

    if len(recent_requests) >= RATE_LIMIT:
        ip_blocked_until[client_ip] = current_time + 60  # Block for 60 seconds
        return JSONResponse(status_code=429, content={"detail": "Too many requests. Blocked for 60 seconds."})

    ip_request_log[client_ip].append(current_time)

    return await call_next(request)



@app.get("/")
def read_root(request: Request):
    """
    Root endpoint to return a simple message.
    :return: Simple message.
    """

    link_cat = "<a href='/categories'>/categories</a>" 
    link_gen = "<a href='/generate'>/generate</a>" 

    endpoint = f"Endpoints: {link_cat}, {link_gen}"
    subtitle = """For generate, 
    <br>* /generate 
    <br>* /generate/{starts_with}/{category}
    <br>* /generate/?starts_with=any&category=any 
    <br>Parameters:
    <br>* `starts_with` should be comma seperated A-Z, 
    <br>* any category word should be matching with one of list of categories at /categories
    <br>Examples: 
    <br>* /generate/A,B,C/Scientists,Cities,Countries
    <br>* /generate/A,B,C/Scientists
    <br>* /generate/any/Scientists
    <br>* /generate/any/any
    <br>* /generate/?starts_with=G,S,Y&category=Anime
    """

    return serve_index(request, endpoint, subtitle)
    # return serve_index(request, "endpints: /generate, /categories")



@app.get("/categories", response_class=HTMLResponse)
def get_categories(request: Request):
    """
    Endpoint to get all available categories.
    :return: List of categories.
    """
    link_gen = "<a href='/generate'>/generate</a>" 
    out = "<br>".join([f"<a href='/generate/any/{w}'>{w}</a>" for w in _get_new_name._available_category])

    return serve_index(request, out, link_gen) 

@app.get("/generate")
@app.get("/generate/{starts_with}/{category}")
def generate_name_path(request: Request, starts_with: str="any", category: str="any"):
    """
    Endpoint to generate a name based on the provided starting letters and category.
    :param starts_with: Starting letters for the name.
    :param category: Category to match.
    :return: Generated name.
    """
    parse_starts_with = starts_with.replace("%2C", ",") 
    parse_category = category.replace("%2C", ",") 

    link_cat = "<a href='/categories'>/categories</a>" 
    link_gen = "<a href='/generate'>/generate</a>" 

    endpoint = f"Endpoints: {link_cat}, {link_gen}"
    

    starts_with = None if starts_with == "any" else starts_with
    category = None if category == "any" else category

    a, b = get_new_name(starts_with, category)
    return serve_index(request, a, f"{b}<br>{endpoint}") 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)