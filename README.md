# Web Crypto Combat

## 安裝教學

推薦版本 python 3.13

在 command line 輸入以下命令
```bash
python -m venv .venv

source .venv/bin/activate # Linux
.\.venv\Scripts\activate  # Windows

pip install -r requirements.txt
cd homO_chAT
python app.py
```

## 使用步驟

> 因為專案可能還有很多未預期 bug、因此強烈建議按照以下步驟操作

1. 打開 [http://localhost:5000/](http://localhost:5000/)
2. 打開監控室
3. 回到首頁、用戶名稱選擇 Alice
4. 登入聊天室
5. 回到首頁、用戶名稱選擇 Bob
6. 登入聊天室

## 檔案結構

```
web-crypto-combat
├── homO_chAT
│   ├── app.py
│   ├── encryption.py
│   ├── __pycache__
│   │   └── encryption.cpython-313.pyc
│   ├── static
│   │   ├── image
│   │   │   ├── explosion.gif
│   │   │   ├── neuro.png
│   │   │   └── yaju-senpai.png
│   │   └── music
│   │       └── beast_noice.mp3
│   └── templates
│       ├── chat.html
│       ├── index.html
│       └── monitor.html
├── README.md
└── requirements.txt
```