import os
import shutil
import tempfile

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import PlainTextResponse

from markitdown import MarkItDown
import pymupdf4llm
import pandas
app = FastAPI()

def convertDocToDocx(doc_path, docx_path):
    """
    使用 unoconv 或 LibreOffice 将 doc 文件转换为 docx 文件
    
    参数:
        doc_path: doc 文件路径
        docx_path: 转换后的 docx 文件保存路径
    """
    import subprocess
    import os
    import sys
    
    # 确保输出目录存在
    output_dir = os.path.dirname(docx_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 方法1: 使用 LibreOffice 直接转换（更可靠）
    try:
        # 尝试使用 LibreOffice 直接转换
        libreoffice_paths = ['libreoffice', 'soffice', '/usr/bin/libreoffice', '/usr/bin/soffice']
        
        for cmd in libreoffice_paths:
            try:
                # 检查命令是否存在
                subprocess.run(['which', cmd], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # 执行转换
                result = subprocess.run(
                    [cmd, '--headless', '--convert-to', 'docx', '--outdir', output_dir, doc_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
                
                # 检查转换后的文件是否存在
                base_name = os.path.basename(doc_path)
                base_name_without_ext = os.path.splitext(base_name)[0]
                converted_file = os.path.join(output_dir, f"{base_name_without_ext}.docx")
                
                print(111, cmd, converted_file)
                
                if os.path.exists(converted_file):
                    # 如果输出路径不是我们想要的，重命名文件
                    if converted_file != docx_path:
                        os.rename(converted_file, docx_path)
                    return
                
                break  # 如果命令存在但转换失败，尝试下一个方法
            except subprocess.CalledProcessError:
                continue  # 如果命令不存在，尝试下一个
            except Exception as e:
                continue  # 如果其他错误，尝试下一个
    except Exception:
         raise RuntimeError(f"文档转换失败: {str(e)}")

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

        # 如果是.doc文件，先转换为.docx
        if file_ext == '.doc':
            docx_path = os.path.join(temp_dir, os.path.splitext(file.filename)[0] + '.docx')
            try:
                convertDocToDocx(file_path, docx_path)
                file_path = docx_path
                file_ext = '.docx'
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error converting doc to docx: {e}")

        # router
        md = MarkItDown()
        if file_ext in ['.doc', '.docx', '.ppt', '.pptx', ".csv", ".pdf"]:
            content = md.convert(file_path).text_content
            result["extracted_content"] = content
            if file_ext == ".pdf" and content == "":
                md_read = pymupdf4llm.LlamaMarkdownReader()
                data = md_read.load_data(file_path)
                result["extracted_content"] = data
        elif file_ext in [".xlsx", ".xls"]:
            df = pandas.read_excel(file_path)
            result["extracted_content"] = df.to_csv()
        else:
            raise HTTPException(status_code=500, detail=f"Error type: [{file_ext}]")

    return result


@app.exception_handler(HTTPException)
async def exception_handler(request: Request, exc: HTTPException):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)