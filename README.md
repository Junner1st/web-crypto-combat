# Web Crypto Combat

## 使用教學

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