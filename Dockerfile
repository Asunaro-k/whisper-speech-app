# ベースイメージ
FROM python:3.9-slim

# 作業ディレクトリを設定
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*


# 必要なPythonライブラリをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリコードをコピー
COPY . .

# Streamlitアプリを起動
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
