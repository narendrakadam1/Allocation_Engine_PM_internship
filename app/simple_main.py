"""
Simple FastAPI Application for Testing

This is a simplified version of the main application for testing purposes.
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import time

# Create FastAPI app
app = FastAPI(
    title="PM Internship AI Engine",
    description="Advanced AI-Powered Internship Allocation System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with welcome message"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PM Internship AI Engine</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 800px; margin: 0 auto; text-align: center; }
            .header { font-size: 2.5em; margin-bottom: 20px; }
            .subtitle { font-size: 1.2em; margin-bottom: 30px; opacity: 0.9; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 40px 0; }
            .feature { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; backdrop-filter: blur(10px); }
            .links { margin-top: 40px; }
            .links a { color: #FFD700; text-decoration: none; margin: 0 15px; font-weight: bold; }
            .links a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🚀 PM Internship AI Engine</h1>
            <p class="subtitle">Advanced AI-Powered Internship Allocation System for the PM Internship Scheme</p>
            
            <div class="features">
                <div class="feature">
                    <h3>🤖 AI Matching</h3>
                    <p>Multi-modal AI engine with explainable recommendations</p>
                </div>
                <div class="feature">
                    <h3>⚡ Real-time Automation</h3>
                    <p>Automated workflows and smart notifications</p>
                </div>
                <div class="feature">
                    <h3>📊 Advanced Analytics</h3>
                    <p>Comprehensive insights for all stakeholders</p>
                </div>
                <div class="feature">
                    <h3>🛡️ Enterprise Security</h3>
                    <p>End-to-end encryption and blockchain audit</p>
                </div>
            </div>
            
            <div class="links">
                <a href="/docs">📚 API Documentation</a>
                <a href="/health">🏥 Health Check</a>
                <a href="/status">📊 System Status</a>
            </div>
            
            <p style="margin-top: 40px; opacity: 0.7;">
                Made with ❤️ for India's future workforce 🇮🇳
            </p>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": "development",
        "message": "PM Internship AI Engine is running successfully!"
    }


@app.get("/status")
async def system_status():
    """System status endpoint"""
    return {
        "system": "PM Internship AI Engine",
        "status": "operational",
        "components": {
            "api": "healthy",
            "database": "not_configured",
            "ai_engine": "not_loaded",
            "cache": "not_configured",
            "queue": "not_configured"
        },
        "features": {
            "ai_matching": "available",
            "workflow_automation": "available", 
            "analytics": "available",
            "multi_language": "available",
            "security": "enabled"
        },
        "statistics": {
            "total_users": 0,
            "active_internships": 0,
            "successful_matches": 0,
            "uptime": "just_started"
        }
    }


@app.get("/api/v1/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "PM Internship AI Engine API",
        "version": "1.0.0",
        "description": "Advanced AI-powered internship allocation system",
        "endpoints": {
            "authentication": "/api/v1/auth/*",
            "matching": "/api/v1/matching/*",
            "analytics": "/api/v1/analytics/*",
            "health": "/health",
            "docs": "/docs"
        },
        "features": [
            "Multi-modal AI matching",
            "Explainable AI recommendations", 
            "Real-time workflow automation",
            "Advanced analytics dashboard",
            "Enterprise-grade security",
            "Multi-language support"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)