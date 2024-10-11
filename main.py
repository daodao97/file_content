import os
import shutil
import tempfile

import pandas as pd
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import PlainTextResponse

from utils_e2m import MultiE2MParser
from utils_mega import PdfMegaParser

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

        if file_ext in ['.doc', '.docx', '.ppt', '.pptx']:
            result["extracted_content"] = e2m.parse_file(file_path, temp_dir)
        elif file_ext in ['.pdf']:
            result["extracted_content"] = await mega.parse_file(file_path)
        elif file_ext in ['.xls', '.xlsx']:
            result["extracted_content"] = pd.read_excel(file_path).to_csv()
        else:
            raise HTTPException(status_code=500, detail=f"Error type: [{file_ext}]")

    return result


@app.exception_handler(HTTPException)
async def exception_handler(request: Request, exc: HTTPException):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


if __name__ == '__main__':
    e2m = MultiE2MParser()
    mega = PdfMegaParser()
    uvicorn.run(app, host="0.0.0.0")
