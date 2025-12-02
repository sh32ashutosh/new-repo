from fastapi import APIRouter, HTTPException, Query
import requests
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/stream-proxy")
def stream_proxy(url: str = Query(...)):
    try:
        r = requests.get(url, stream=True)
        return StreamingResponse(r.iter_content(chunk_size=1024*1024), media_type="video/mp4")
    except:
        raise HTTPException(status_code=500, detail="Failed to fetch URL")
