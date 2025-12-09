from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, HttpUrl
import uuid
import os
import requests
import time
from .jobs_db import jobs_db, create_job, update_job
from .face_swapper import perform_face_swap

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "static", "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "output")
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(title="Face-Swap Service")

class CreateJobRequest(BaseModel):
    base_image_url: HttpUrl
    selfie_url: HttpUrl

# --- NEW ROOT ROUTE ADDED HERE ---
@app.get("/")
def read_root():
    return {
        "message": "Face-Swap Service is running!",
        "documentation": "/docs",
        "health": "ok"
    }
# ---------------------------------

@app.post("/api/v1/face-swap/jobs")
async def create_face_swap_job(req: CreateJobRequest, background_tasks: BackgroundTasks):
    # Validate and download images
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    base_path = os.path.join(INPUT_DIR, f"{job_id}_base")
    selfie_path = os.path.join(INPUT_DIR, f"{job_id}_selfie")

    try:
        # Download and save images
        def download_image(url, path):
            r = requests.get(str(url), timeout=15)
            if r.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Failed to download image from {url}")
            content_type = r.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail=f"URL does not point to an image: {url}")
            # Guess extension
            ext = content_type.split("/")[-1].split(";")[0]
            full_path = f"{path}.{ext}"
            with open(full_path, "wb") as f:
                f.write(r.content)
            return full_path

        base_file = download_image(req.base_image_url, base_path)
        selfie_file = download_image(req.selfie_url, selfie_path)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch images: {e}")

    # create job record
    create_job(job_id, {
        "reference_id": job_id,
        "status": "pending",
        "base_image_path": base_file,
        "selfie_image_path": selfie_file,
        "result_image_url": None,
        "error": None,
        "processing_ms": None,
    })

    # start background processing
    background_tasks.add_task(process_job, job_id)

    return JSONResponse(status_code=202, content={
        "reference_id": job_id,
        "status": "pending",
        "message": "Face-swap job accepted"
    })


async def process_job(reference_id: str):
    job = jobs_db.get(reference_id)
    if not job:
        return
    update_job(reference_id, {"status": "processing"})
    start = time.time()
    try:
        out_name = f"{reference_id}.png"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        perform_face_swap(job["base_image_path"], job["selfie_image_path"], out_path)
        elapsed_ms = int((time.time() - start) * 1000)
        # In a real deployment you'd upload to S3/CDN and return public URL.
        # For this demo, we serve from /static/output
        # Note: Ideally, include the full domain, but relative works for browsers
        public_url = f"/static/output/{out_name}"
        update_job(reference_id, {
            "status": "completed",
            "result_image_url": public_url,
            "processing_ms": elapsed_ms,
        })
    except Exception as e:
        update_job(reference_id, {"status": "failed", "error": str(e)})


@app.get("/api/v1/face-swap/jobs/{reference_id}")
async def get_job(reference_id: str):
    job = jobs_db.get(reference_id)
    if not job:
        raise HTTPException(status_code=404, detail="reference_id not found")
    # return the canonical response shape
    resp = {
        "reference_id": job["reference_id"],
        "status": job["status"],
    }
    if job["status"] == "completed":
        resp.update({
            "result_image_url": job["result_image_url"],
            "processing_ms": job.get("processing_ms"),
        })
    if job["status"] == "failed":
        resp.update({"error": job.get("error")})
    return resp


# Static files serving: using raw FileResponse for results
@app.get("/static/output/{filename}")
async def serve_output(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(path, media_type="image/png")
