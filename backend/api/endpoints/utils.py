from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import requests

router = APIRouter()

@router.get("/stream-proxy")
async def stream_proxy(url: str):
    """
    Proxies external video content to bypass CORS or mix content issues.
    Used by VideoRelay.jsx
    """
    if not url:
        raise HTTPException(status_code=400, detail="Missing URL parameter")

    def iterfile():
        # Stream content in 4KB chunks
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=4096):
                yield chunk

    # We guess content type or default to mp4
    return StreamingResponse(iterfile(), media_type="video/mp4")