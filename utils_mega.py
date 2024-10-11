import asyncio

from fastapi import HTTPException
from megaparse import MegaParse


# 文档和 PDF 都还行，但文档不支持旧版的
class PdfMegaParser:
    @staticmethod
    async def parse_file(file_path):
        data = await MegaParse(file_path=file_path).aload()
        if data is None:
            raise HTTPException(status_code=500, detail=f"Empty file")
        return data.page_content


if __name__ == '__main__':
    pdf_parser = PdfMegaParser()
    result = asyncio.run(pdf_parser.parse_file('archive/aabbcc.pdf'))
    print(result)
