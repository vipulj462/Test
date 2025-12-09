from pydantic import BaseModel, HttpUrl


class CreateJobRequest(BaseModel):
    base_image_url: HttpUrl
    selfie_url: HttpUrl