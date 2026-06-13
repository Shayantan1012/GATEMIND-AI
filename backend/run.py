import os

from app import create_app

app = create_app()
# EC2 instances configure the environment variables for HOST, PORT, and FLASK_DEBUG in the .env file or through the EC2 instance's environment variable settings. This allows for flexible configuration without modifying the codebase directly
if __name__ == "__main__":
    
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
        use_reloader=False,
    )
