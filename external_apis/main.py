from fastapi_stubs import app

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=3629, log_level='info')