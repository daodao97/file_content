import os
import shutil
import tempfile

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import PlainTextResponse

from markitdown import MarkItDown

app = FastAPI()


@app.post("/")
async def upload_file(file: UploadFile = File(...)):
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_ext = os.path.splitext(file.filename)[-1].lower()
        file_size = os.path.getsize(file_path)
        
        result = {
            "file_name": file.filename,
            "file_size": file_size,
            "file_type": file_ext[1:],  # 去掉开头的点
            "extracted_content": ""
        }

        # router
        md = MarkItDown()
        if file_ext in ['.doc', '.docx', '.ppt', '.pptx', ".xls", ".xlsx", ".csv", ".pdf"]:
            result["extracted_content"] = md.convert(file_path).text_content
        else:
            raise HTTPException(status_code=500, detail=f"Error type: [{file_ext}]")

    return result


@app.exception_handler(HTTPException)
async def exception_handler(request: Request, exc: HTTPException):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)