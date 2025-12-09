# 🎭 Face-Swap API Service

A robust, asynchronous **Face-Swap REST API** built with **FastAPI**, **OpenCV**, and **Docker**. This service implements a two-step process (Job Creation → Result Polling) to handle image processing efficiently.

---

## 🚀 Live Deployment
The API is currently deployed and publicly accessible:

| Service | URL |
| :--- | :--- |
| **Interactive Docs (Swagger)** | [**https://test1-ju64.onrender.com/docs**](https://test1-ju64.onrender.com/docs) |
| **Base URL** | `https://test1-ju64.onrender.com` |

---

## 💰 Cost Per API Call Analysis

This service utilizes an optimized **OpenCV (CPU-based)** approach. Unlike Deep Learning models (GANs) that require expensive GPUs, this solution runs efficiently on standard CPU instances, significantly reducing costs.

### 1. Resource & Pricing Model
*Based on a standard General Purpose Cloud Instance (e.g., AWS t3.medium or Render Standard).*

| Metric | Value | Notes |
| :--- | :--- | :--- |
| **Instance Cost** | **$0.06 / hour** | Standard CPU Instance (2 vCPU, 4GB RAM) |
| **Avg. Processing Time** | **1.5 seconds** | Measured average per face-swap operation |
| **Data Transfer** | **$0.09 / GB** | Approx. $0.00001 per image pair |

### 2. Cost Calculation Formula

$$ \text{Cost Per Job} = \left( \frac{\text{Instance Cost per Hour}}{3600 \text{ sec}} \right) \times \text{Processing Duration} + \text{Network/Storage} $$

### 3. Final Breakdown

| Component | Calculation | Cost per Job |
| :--- | :--- | :--- |
| **Compute** | `($0.06 / 3600) * 1.5s` | **$0.000025** |
| **Network/Storage** | Estimate (Images < 2MB) | **$0.000010** |
| **TOTAL COST** | | **$0.000035** |

> **Summary:** You can process approximately **28,500 face-swaps for $1.00**.

---

## 📚 API Documentation

### 1. Create Face-Swap Job
**Endpoint:** `POST /api/v1/face-swap/jobs`

Initiates a background job. Returns a `reference_id` immediately.

**Request Body:**
```json
{
  "base_image_url": "https://raw.githubusercontent.com/vipulj462/Test/main/test_images/base.jpg",
  "selfie_url": "https://raw.githubusercontent.com/vipulj462/Test/main/test_images/selfie.jpg"
}

Response (202 Accepted):
JSON
{
  "reference_id": "job_8f2a1c9e4b",
  "status": "pending",
  "message": "Face-swap job accepted"
}


2. Get Job Status / Result
Endpoint: GET /api/v1/face-swap/jobs/{reference_id}

Poll this endpoint to check status or retrieve the final image.
Response (Processing):
JSON
{
  "reference_id": "job_8f2a1c9e4b",
  "status": "processing"
}

Response (Completed):
JSON
{
  "reference_id": "job_8f2a1c9e4b",
  "status": "completed",
  "result_image_url": "/static/output/job_8f2a1c9e4b.png",
  "processing_ms": 1520
}


🛠️ Technical Stack
Language: Python 3.11
Framework: FastAPI (Asynchronous)
Computer Vision: OpenCV (Haar Cascades + Seamless Cloning)

