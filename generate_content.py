#!/usr/bin/env python3
"""
generate_content.py
Claude API (Sonnet) を使って30日分のJSONコンテンツを自動生成する。
Usage: python generate_content.py [--day N] [--all]
"""

import json
import os
import sys
import argparse
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("Error: anthropic パッケージが必要です。")
    print("  pip install anthropic")
    sys.exit(1)

# ── Month 1 メニュー定義（AUスイーツ） ──
MENU = {
    1: "Scones", 2: "Lamington", 3: "Pavlova", 4: "Anzac Biscuits",
    5: "Tim Tam Slam", 6: "Banana Bread", 7: "Fairy Bread",
    8: "Vanilla Slice", 9: "Pumpkin Scones", 10: "Sticky Date Pudding",
    11: "Apple Crumble", 12: "Lemon Tart", 13: "Chocolate Brownie",
    14: "Carrot Cake", 15: "Blueberry Muffin", 16: "Banana Split",
    17: "Fruit Tart", 18: "Coconut Macaroons", 19: "Lemon Meringue Pie",
    20: "Rocky Road", 21: "Churros", 22: "Crème Brûlée",
    23: "Chia Pudding", 24: "Smoothie Bowl", 25: "Granola Bars",
    26: "Chocolate Mousse", 27: "Waffles", 28: "Tiramisu",
    29: "Mango Sorbet", 30: "Ice Cream Sundae",
}

EMOJI_MAP = {
    "Scones": "🫖", "Lamington": "🍫", "Pavlova": "🎂", "Anzac Biscuits": "🍪",
    "Tim Tam Slam": "☕", "Banana Bread": "🍌", "Fairy Bread": "🌈",
    "Vanilla Slice": "🍰", "Pumpkin Scones": "🎃", "Sticky Date Pudding": "🍯",
    "Apple Crumble": "🍎", "Lemon Tart": "🍋", "Chocolate Brownie": "🍫",
    "Carrot Cake": "🥕", "Blueberry Muffin": "🫐", "Banana Split": "🍌",
    "Fruit Tart": "🍓", "Coconut Macaroons": "🥥", "Lemon Meringue Pie": "🍋",
    "Rocky Road": "🍫", "Churros": "🥖", "Crème Brûlée": "🍮",
    "Chia Pudding": "🥄", "Smoothie Bowl": "🥣", "Granola Bars": "🥜",
    "Chocolate Mousse": "🍫", "Waffles": "🧇", "Tiramisu": "☕",
    "Mango Sorbet": "🥭", "Ice Cream Sundae": "🍨",
}


def build_prompt(day: int, sweet: str) -> str:
    """Claude API に送るプロンプトを構築する。"""
    return f"""あなたは英語教材のコンテンツライターです。以下の仕様に従い、Day {day} のコンテンツを **JSON** で出力してください。

## 対象者
- 日本人女性、オーストラリア・ケアンズでワーホリ中、カフェ勤務
- 英語レベル: A2（英検3級〜準2級）
- 興味: 陸上競技、フィギュアスケート、Snow Man、山田涼介

## Day {day}: {sweet}

## 出力JSON構造（厳密に守ること）

```json
{{
  "day": {day},
  "sweet": "{sweet}",
  "recipe": {{
    "title": "How to Make {sweet}",
    "intro": "(1-2文の導入。A2レベルの簡単な英語)",
    "ingredients": "(材料リスト、カンマ区切りの文字列)",
    "steps": [
      "(各ステップ1文。重要動詞を**太字**にする。6ステップ程度)"
    ]
  }},
  "recipe_vocab": [
    {{"en": "英単語", "ja": "日本語訳"}}
  ],
  "quiz1": {{
    "question_ja": "(レシピの内容に関する日本語の質問)",
    "options": ["選択肢1", "選択肢2", "選択肢3"],
    "correct_index": 0,
    "explanation_correct": "(正解時の解説。英文引用を含む)",
    "explanation_wrong": "(不正解時のヒント)"
  }},
  "review": {{
    "cafe_name": "(オーストラリアのカフェ名を創作)",
    "location": "(ケアンズ周辺の地名)",
    "stars": 5,
    "text": "(カフェでその日のスイーツを食べた感想レビュー。5-7文。A2レベル)"
  }},
  "review_vocab": [
    {{"en": "英単語", "ja": "日本語訳"}}
  ],
  "quiz2": {{
    "question_ja": "(レビューの内容に関する日本語の質問)",
    "options": ["選択肢1", "選択肢2", "選択肢3"],
    "correct_index": 0,
    "explanation_correct": "(正解時の解説)",
    "explanation_wrong": "(不正解時のヒント)"
  }},
  "australia_tips": [
    "(オーストラリアでこのスイーツに関連する豆知識。日本語で3段落。各段落に英語フレーズを含める)"
  ],
  "conversation": {{
    "scene": "(カフェでの接客場面の説明。日本語)",
    "lines": [
      {{"speaker": "You", "text": "(英語のセリフ)"}},
      {{"speaker": "Customer", "text": "(英語のセリフ)"}}
    ]
  }},
  "conversation_vocab": [
    {{"en": "英単語", "ja": "日本語訳"}}
  ],
  "quiz3": {{
    "question_ja": "(会話の内容に関する日本語の質問)",
    "options": ["選択肢1", "選択肢2", "選択肢3"],
    "correct_index": 0,
    "explanation_correct": "(正解時の解説)",
    "explanation_wrong": "(不正解時のヒント)"
  }},
  "listening": {{
    "part_a": {{
      "title_ja": "(Part Aのタイトル。日本語)",
      "full_text": "(穴埋め用の新しい文章。レシピ/レビューとは完全に別の内容。同じスイーツに関連するが別のシーン。6-8文)",
      "gaps": [
        {{"before": "文の穴の前の部分", "answer": "正解の単語", "after": "文の穴の後の部分"}}
      ]
    }},
    "part_b": {{
      "title_ja": "(Part Bのタイトル。日本語)",
      "full_text": "(内容理解クイズ用の新しい文章。これもレシピ/レビューとは別。8-10文)",
      "questions": [
        {{
          "question_ja": "(日本語の質問)",
          "options": ["選択肢1", "選択肢2", "選択肢3"],
          "correct_index": 0,
          "explanation_correct": "(正解時の解説)",
          "explanation_wrong": "(不正解時のヒント)"
        }}
      ]
    }}
  }},
  "pronunciation": {{
    "sentences": [
      {{
        "text": "(その日の教材から抜き出した重要フレーズ。5つ)",
        "tip": "(発音のコツ。リンキング、ストレス等。日本語)"
      }}
    ]
  }},
  "try_it": {{
    "prompt_ja": "(ライティングのお題。日本語)",
    "example": "(英語の例文。2-3文)"
  }},
  "yamada_comments": {{
    "recipe": "(セクション1冒頭の山田涼介コメント。推しネタ絡め。日本語で2-3文)",
    "review": "(セクション3冒頭のコメント)",
    "conversation": "(セクション6冒頭のコメント)",
    "listening": "(セクション8冒頭のコメント。陸上やフィギュア等のネタを自然に絡める)",
    "pronunciation": "(セクション9冒頭のコメント)",
    "try_it": "(セクション10冒頭のコメント)"
  }}
}}
```

## 重要なルール
1. **英語レベルはA2**（英検3級〜準2級）。難しい単語は使わない。1文は短く。
2. **リスニング（listening）のfull_textは、レシピ・レビュー・会話とは完全に別の新しい文章**にすること。同じスイーツをテーマにするが、シーンは異なる（例：友達との会話、お店での注文、料理教室など）。
3. **recipe_vocabは7-9個**、review_vocabは5-7個、conversation_vocabは5-7個にする。
4. **quiz**は全て3択。日本語で質問し、日本語で選択肢を作る。
5. **Part Bのquestionsは3問**作る。
6. **Part Aのgapsは5問**作る。
7. **pronunciationのsentencesは5つ**。その日のレシピ・会話・リスニングから重要フレーズを選ぶ。
8. **yamada_comments**は山田涼介（Snow Manメンバー）のキャラで、親しみやすい先輩口調。推しネタ（陸上、フィギュア、Snow Man）を自然に絡める。
9. **カフェ名**はオーストラリア風に。場所はケアンズ周辺で。
10. **会話のcustomer名**は英語名（Emma, Jack, Lily等、毎日変える）。
11. JSONのみ出力。マークダウンのコードブロックで囲まないこと。説明文も不要。"""


def generate_day(client, day: int) -> dict:
    """1日分のコンテンツを生成する。"""
    sweet = MENU[day]
    prompt = build_prompt(day, sweet)

    print(f"  Generating Day {day}: {sweet}...", end=" ", flush=True)

    message = client.messages.create(
        model="claude-sonnet-4-5-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    )

    text = message.content[0].text.strip()
    # Strip markdown code block if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]

    data = json.loads(text)
    print("OK")
    return data


def main():
    parser = argparse.ArgumentParser(description="30日分のコンテンツJSON生成")
    parser.add_argument("--day", type=int, help="特定の日だけ生成 (1-30)")
    parser.add_argument("--all", action="store_true", help="30日分すべて生成")
    parser.add_argument("--range", type=str, help="範囲指定 (例: 1-5)")
    args = parser.parse_args()

    if not args.day and not args.all and not args.range:
        print("Usage: python generate_content.py --day 1    (1日分)")
        print("       python generate_content.py --range 1-5 (範囲)")
        print("       python generate_content.py --all       (全30日)")
        sys.exit(0)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY 環境変数を設定してください。")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    output_dir = Path(__file__).parent / "content"
    output_dir.mkdir(exist_ok=True)

    # Determine which days to generate
    if args.day:
        days = [args.day]
    elif args.range:
        start, end = map(int, args.range.split("-"))
        days = list(range(start, end + 1))
    else:
        days = list(range(1, 31))

    print(f"Generating {len(days)} day(s) of content...")

    for day in days:
        if day < 1 or day > 30:
            print(f"  Skipping Day {day} (out of range)")
            continue
        try:
            data = generate_day(client, day)
            # Add emoji
            data["emoji"] = EMOJI_MAP.get(MENU[day], "🍰")
            out_path = output_dir / f"day{day}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  Saved: {out_path}")
        except json.JSONDecodeError as e:
            print(f"  ERROR (JSON parse): Day {day} - {e}")
        except Exception as e:
            print(f"  ERROR: Day {day} - {e}")

    print("\nDone!")


if __name__ == "__main__":
    main()
