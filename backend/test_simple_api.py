from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Test API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {"message": "Test API is working", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running correctly"}

@app.get("/test/drivers")
async def test_drivers():
    return {
        "success": True,
        "data": {
            "total_drivers": 118,
            "active_drivers": 8,
            "total_rides": 13,
            "cancelled_rides": 2,
            "avg_hours_online": 25.5,
            "avg_rating": 4.2,
            "total_revenue": 195.0,
            "acceptance_rate": 84.6,
            "revenue_per_hour": 7.65,
            "total_distance": 156.8
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
