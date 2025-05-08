from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
import subprocess
import tempfile
import os
import logging
import shutil

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

class LatexRequest(BaseModel):
    tex_content: str

def setup_fonts(tmpdir: str):
    """Setup fonts in the temporary directory"""
    assets_dir = "/app/assets"  # This is the mounted assets directory in Docker
    fonts_dir = os.path.join(tmpdir, "fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    
    # Copy fonts from assets to temporary directory
    font_files = ["THSarabunIT9.ttf", "THSarabunIT9Bold.ttf"]
    for font_file in font_files:
        src = os.path.join(assets_dir, font_file)
        dst = os.path.join(fonts_dir, font_file)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            logger.debug(f'Copied font {font_file} to {dst}')
        else:
            logger.warning(f'Font file not found: {src}')
    
    return fonts_dir

@app.post("/compile")
def compile_latex(req: LatexRequest):
    with tempfile.TemporaryDirectory() as tmpdir:
        logger.debug(f'Created temporary directory: {tmpdir}')
        tex_path = os.path.join(tmpdir, "main.tex")
        pdf_path = os.path.join(tmpdir, "main.pdf")
        
        # Setup fonts
        fonts_dir = setup_fonts(tmpdir)
        
        # Create assets directory for other assets
        assets_dir = os.path.join(tmpdir, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        logger.debug(f'Created assets directory: {assets_dir}')

        # Copy other assets if needed
        if "assets/" in req.tex_content:
            src_assets = "/app/assets"
            for item in os.listdir(src_assets):
                if item.endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                    shutil.copy2(
                        os.path.join(src_assets, item),
                        os.path.join(assets_dir, item)
                    )
            logger.debug(f'Copied assets to {assets_dir}')

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(req.tex_content)
            logger.debug(f'Written TeX content to: {tex_path}')
            logger.debug(f'Content: {req.tex_content}')

        try:
            logger.debug(f'Starting xelatex compilation in directory: {tmpdir}')
            # First run to generate aux files
            result = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", "main.tex"],
                cwd=tmpdir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                text=True
            )
            logger.debug(f'First LaTeX compilation completed')
            
            # Second run to resolve references
            result = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", "main.tex"],
                cwd=tmpdir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                text=True
            )
            logger.debug(f'Second LaTeX compilation completed')
            logger.debug(f"STDOUT: {result.stdout}")
            logger.debug(f"STDERR: {result.stderr}")
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stdout or e.stderr
            if "fontspec error" in error_msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail="Font error: Required fonts are not properly accessible. Please check font files in assets directory."
                )
            logger.error(f'LaTeX compilation failed with error: {e}')
            logger.error(f'STDOUT: {e.stdout}')
            logger.error(f'STDERR: {e.stderr}')
            raise HTTPException(
                status_code=400,
                detail=f"LaTeX compilation failed:\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}"
            )
        except subprocess.TimeoutExpired as e:
            logger.error(f'LaTeX compilation timed out: {e}')
            raise HTTPException(status_code=408, detail="LaTeX compilation timed out.")
        except Exception as e:
            logger.error(f'Unexpected error during LaTeX compilation: {e}')
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

        if not os.path.exists(pdf_path):
            logger.error(f'PDF file not found at: {pdf_path}')
            raise HTTPException(status_code=500, detail="PDF not generated.")
            
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        return Response(content=pdf_bytes, media_type="application/pdf") 