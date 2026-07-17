FROM python:3.11-slim

WORKDIR /app

# Manim 系统依赖（Cairo + Pango + ffmpeg + 中文字体）
# 注意：不装 texlive（项目禁用 Tex/MathTex，改用 Text/MarkupText），避免镜像过大
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    pkg-config \
    default-libmysqlclient-dev \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf-2.0-dev \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    && rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用代码
COPY . .

# 持久化目录
RUN mkdir -p data/videos data/chroma_db

# Zeabur 注入 PORT，默认 8000
ENV PORT=8000
EXPOSE 8000

# 直接用 uvicorn 启动
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
