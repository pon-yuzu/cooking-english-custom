# Cooking English Custom Edition — もものちゃん専用

オーストラリアワーホリ中のもものちゃん（カフェ勤務）向けに、30日間のクッキング英語教材をカスタマイズした英語学習HTML教材。

## 概要

| 項目 | 値 |
|------|-----|
| レベル | A2（英検3級〜準2級） |
| テーマ | Month 1: お菓子・AUスイーツ |
| セクション数 | 11（リスニング+発音チェック含む） |
| ナビゲーター | 山田涼介（実画像アイコン使用） |

## ファイル構成

```
もものちゃん/
├── README.md                ← このファイル
├── day1-v3.html             ← Day 1 プロトタイプ（テンプレート元）
├── generate_content.py      ← Claude API で30日分のJSON生成
├── build_html.py            ← JSONからHTML生成
├── assets/
│   └── ryosuke.jpg          ← 山田涼介ナビゲーター画像
├── content/                 ← 生成されたJSONファイル
│   ├── day1.json
│   ├── day2.json
│   └── ...
└── docs/                    ← 生成されたHTML（GitHub Pages用）
    ├── index.html           ← 30日分グリッド一覧
    ├── day1.html
    ├── day2.html
    ├── ...
    └── assets/
        └── ryosuke.jpg
```

## 使い方

### 1. コンテンツ生成（Claude API使用）

```bash
# 環境変数にAPIキーを設定
export ANTHROPIC_API_KEY="sk-ant-..."

# 1日分だけ
python generate_content.py --day 1

# 範囲指定
python generate_content.py --range 1-5

# 全30日分
python generate_content.py --all
```

### 2. HTML生成

```bash
# 1日分
python build_html.py --day 1

# 全日分
python build_html.py --all
```

### 3. ローカルで確認

```bash
open docs/index.html
# または
python -m http.server 8000 --directory docs
```

## 11セクション構成

| # | セクション | 内容 |
|---|-----------|------|
| 1 | Recipe | スイーツのレシピ読解 + TTS + 単語チェック |
| 2 | Quiz 1 | レシピ内容チェック |
| 3 | Review | カフェのお客さんレビュー |
| 4 | Quiz 2 | レビュー内容チェック |
| 5 | Australia Tips | オーストラリア生活情報 |
| 6 | Conversation | カフェ接客場面 |
| 7 | Quiz 3 | 会話内容チェック |
| 8 | Listening | リスニング（穴埋め + 内容理解）※別文章 |
| 9 | Pronunciation | 発音チェック（Web Speech API） |
| 10 | Try It! | ライティング練習 |
| 11 | Summary | 学習サマリー生成 |

## Month 1 メニュー（AUスイーツ）

| Day | スイーツ | Day | スイーツ |
|-----|---------|-----|---------|
| 1 | Scones | 16 | Banana Split |
| 2 | Lamington | 17 | Fruit Tart |
| 3 | Pavlova | 18 | Coconut Macaroons |
| 4 | Anzac Biscuits | 19 | Lemon Meringue Pie |
| 5 | Tim Tam Slam | 20 | Rocky Road |
| 6 | Banana Bread | 21 | Churros |
| 7 | Fairy Bread | 22 | Crème Brûlée |
| 8 | Vanilla Slice | 23 | Chia Pudding |
| 9 | Pumpkin Scones | 24 | Smoothie Bowl |
| 10 | Sticky Date Pudding | 25 | Granola Bars |
| 11 | Apple Crumble | 26 | Chocolate Mousse |
| 12 | Lemon Tart | 27 | Waffles |
| 13 | Chocolate Brownie | 28 | Tiramisu |
| 14 | Carrot Cake | 29 | Mango Sorbet |
| 15 | Blueberry Muffin | 30 | Ice Cream Sundae |

## 技術仕様

- **静的HTML/CSS/JS**（フレームワーク不使用）
- Web Speech API: TTS読み上げ + 音声認識（Chrome推奨、HTTPS必須）
- 発音チェック: Levenshtein距離でファジーマッチ
- GitHub Pages でホスティング

## 依存パッケージ

```bash
pip install anthropic  # generate_content.py のみ
```

build_html.py は標準ライブラリのみ使用。
