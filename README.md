## 起動

以下の画像を配置

- ./src/icon.ico (128x128)
- ./src/img/button.png (20x20)
- ./src/img/logo.png (350x320)

```bash
$ pip install -r requirements.txt
$ cd src
$ python main.py
```

## EXE化

./src/LiViewer.specの${WD}をワーキングディレクトリの絶対パス（区切り文字は"\\\\"）に変更

```bash
$ pyinstaller LiViewer.spec --noconsole
```

./src/dist/LiViewer/にcsv/, img/, icon.icoをコピー

LiViewer.exeで起動
