#!/usr/bin/env python3
"""
build_html.py
JSONコンテンツからHTML教材を生成する。
Usage: python build_html.py [--day N] [--all]
"""

import json
import os
import sys
import argparse
from pathlib import Path
from html import escape as h

BASE_DIR = Path(__file__).parent
CONTENT_DIR = BASE_DIR / "content"
DOCS_DIR = BASE_DIR / "docs"
TOTAL_DAYS = 30
TOTAL_SECTIONS = 11


# ── Menu definition (for index page when JSON not available) ──
MENU = {
    1: ("Scones", "🫖"), 2: ("Lamington", "🍫"), 3: ("Pavlova", "🎂"),
    4: ("Anzac Biscuits", "🍪"), 5: ("Tim Tam Slam", "☕"),
    6: ("Banana Bread", "🍌"), 7: ("Fairy Bread", "🌈"),
    8: ("Vanilla Slice", "🍰"), 9: ("Pumpkin Scones", "🎃"),
    10: ("Sticky Date Pudding", "🍯"), 11: ("Apple Crumble", "🍎"),
    12: ("Lemon Tart", "🍋"), 13: ("Chocolate Brownie", "🍫"),
    14: ("Carrot Cake", "🥕"), 15: ("Blueberry Muffin", "🫐"),
    16: ("Banana Split", "🍌"), 17: ("Fruit Tart", "🍓"),
    18: ("Coconut Macaroons", "🥥"), 19: ("Lemon Meringue Pie", "🍋"),
    20: ("Rocky Road", "🍫"), 21: ("Churros", "🥖"),
    22: ("Crème Brûlée", "🍮"), 23: ("Chia Pudding", "🥄"),
    24: ("Smoothie Bowl", "🥣"), 25: ("Granola Bars", "🥜"),
    26: ("Chocolate Mousse", "🍫"), 27: ("Waffles", "🧇"),
    28: ("Tiramisu", "☕"), 29: ("Mango Sorbet", "🥭"),
    30: ("Ice Cream Sundae", "🍨"),
}


def yamada_avatar_html():
    """山田涼介のアバターHTML（実画像版）"""
    return '<img src="assets/ryosuke.jpg" alt="Ryosuke" style="width:36px;height:36px;border-radius:50%;object-fit:cover;flex-shrink:0;box-shadow:0 2px 8px rgba(194,24,91,0.3);">'


def yamada_comment_html(comment_text: str) -> str:
    """山田涼介コメントブロックのHTML"""
    return f'''    <div class="yamada-comment">
      {yamada_avatar_html()}
      <div class="yamada-text">
        <div class="yamada-name">Ryosuke</div>
        {h(comment_text)}
      </div>
    </div>'''


def vocab_list_html(vocab: list, section_id: str) -> str:
    """単語リストのHTML"""
    items = ""
    for v in vocab:
        items += f'''      <div class="vocab-item" onclick="this.classList.toggle('checked')"><div class="vocab-check">✓</div><span class="vocab-en">{h(v["en"])}</span><span class="vocab-ja">{h(v["ja"])}</span></div>\n'''
    return f'''    <button class="vocab-toggle" onclick="toggleVocab(this)">📚 単語リストを見る</button>
    <div class="vocab-list">
      <p style="font-size:0.75rem;color:var(--text-light);margin-bottom:0.5rem;">💡 わからなかった単語にチェック ✓</p>
{items}    </div>'''


def quiz_html(quiz: dict, quiz_id: str) -> str:
    """クイズのHTML"""
    options = ""
    for i, opt in enumerate(quiz["options"]):
        is_correct = "true" if i == quiz["correct_index"] else "false"
        options += f'      <div class="quiz-option" onclick="checkQuiz(this, {is_correct})">{h(opt)}</div>\n'
    return f'''    <div class="quiz-question">Q: {h(quiz["question_ja"])}</div>
    <div class="quiz-options">
{options}    </div>
    <div class="quiz-feedback correct">⭕ 正解！{h(quiz["explanation_correct"])}</div>
    <div class="quiz-feedback wrong">❌ {h(quiz["explanation_wrong"])}</div>'''


def build_recipe_text(data: dict) -> str:
    """レシピのプレーンテキスト（コピー/TTS用）"""
    r = data["recipe"]
    steps = " ".join(f"{i+1}. {s}" for i, s in enumerate(r["steps"]))
    return f'{r["title"]}. {r["intro"]} Ingredients: {r["ingredients"]}. Steps: {steps}'


def build_recipe_tts(data: dict) -> str:
    """レシピのTTS用テキスト"""
    r = data["recipe"]
    steps = " ".join(f"Step {i+1}. {s}" for i, s in enumerate(r["steps"]))
    return f'{r["title"]}. {r["intro"]} {steps}'


def section_recipe(data: dict) -> str:
    """Section 1: Recipe"""
    r = data["recipe"]
    steps_html = ""
    for step in r["steps"]:
        # Convert **word** to <strong>word</strong>
        import re
        step_formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', step)
        steps_html += f"        <li>{step_formatted}</li>\n"

    recipe_text = build_recipe_text(data)
    recipe_tts = build_recipe_tts(data)
    yamada = yamada_comment_html(data["yamada_comments"]["recipe"])
    vocab = vocab_list_html(data["recipe_vocab"], "recipe")

    return f'''<div class="section-card sec-recipe open" data-index="0">
  <div class="section-header" onclick="toggleSection(this)">
    <div class="section-number">1</div>
    <div class="section-title"><div class="label">Recipe</div><div class="name">{h(data["sweet"])}のレシピを読んでみよう</div></div>
    <div class="section-chevron">▾</div>
  </div>
  <div class="section-body">
{yamada}
    <div class="recipe-box">
      <h3>{h(r["title"])}</h3>
      <p>{h(r["intro"])}</p>
      <div class="ingredients">
        <strong>Ingredients:</strong><br>
        {h(r["ingredients"])}
      </div>
      <ol class="recipe-steps">
{steps_html}      </ol>
    </div>
    <div class="action-row">
      <button class="action-btn" onclick="copyText('recipe-text')">📋 コピー</button>
      <button class="action-btn tts-btn" onclick="speakText('recipe-tts', this)">🔊 読み上げ</button>
      <a class="action-btn" href="https://www.naturalreaders.com/online/" target="_blank">🔊 Natural Reader</a>
    </div>
    <div id="recipe-text" style="display:none">{h(recipe_text)}</div>
    <div id="recipe-tts" style="display:none">{h(recipe_tts)}</div>
{vocab}
  </div>
</div>'''


def section_quiz1(data: dict) -> str:
    """Section 2: Quiz 1"""
    q = quiz_html(data["quiz1"], "quiz1")
    return f'''<div class="section-card sec-quiz1" data-index="1">
  <div class="section-header" onclick="toggleSection(this)">
    <div class="section-number">2</div>
    <div class="section-title"><div class="label">Quiz 1</div><div class="name">レシピの内容チェック</div></div>
    <div class="section-chevron">▾</div>
  </div>
  <div class="section-body">
{q}
  </div>
</div>'''


def section_review(data: dict) -> str:
    """Section 3: Review"""
    rv = data["review"]
    stars = "⭐" * rv.get("stars", 5)
    yamada = yamada_comment_html(data["yamada_comments"]["review"])
    vocab = vocab_list_html(data["review_vocab"], "review")
    review_plain = rv["text"]

    return f'''<div class="section-card sec-review" data-index="2">
  <div class="section-header" onclick="toggleSection(this)">
    <div class="section-number">3</div>
    <div class="section-title"><div class="label">Review</div><div class="name">カフェのお客さんレビュー</div></div>
    <div class="section-chevron">▾</div>
  </div>
  <div class="section-body">
{yamada}
    <div class="review-card">
      <div class="review-header"><span>☕</span><h4>{h(rv["cafe_name"])} — {h(rv["location"])}</h4></div>
      <div class="review-stars">{stars}</div>
      <div class="review-text" style="margin-top:0.5rem;">
        {h(rv["text"])}
      </div>
    </div>
    <div class="action-row">
      <button class="action-btn" onclick="copyText('review-text')">📋 コピー</button>
      <button class="action-btn tts-btn" onclick="speakText('review-tts', this)">🔊 読み上げ</button>
      <a class="action-btn" href="https://www.naturalreaders.com/online/" target="_blank">🔊 Natural Reader</a>
    </div>
    <div id="review-text" style="display:none">{h(review_plain)}</div>
    <div id="review-tts" style="display:none">{h(review_plain)}</div>
{vocab}
  </div>
</div>'''


def section_quiz2(data: dict) -> str:
    """Section 4: Quiz 2"""
    q = quiz_html(data["quiz2"], "quiz2")
    return f'''<div class="section-card sec-quiz2" data-index="3">
  <div class="section-header" onclick="toggleSection(this)">
    <div class="section-number">4</div>
    <div class="section-title"><div class="label">Quiz 2</div><div class="name">レビューの内容チェック</div></div>
    <div class="section-chevron">▾</div>
  </div>
  <div class="section-body">
{q}
  </div>
</div>'''


def section_tips(data: dict) -> str:
    """Section 5: Australia Tips"""
    tips = ""
    for tip in data["australia_tips"]:
        # Convert **text** to <strong>text</strong>
        import re
        tip_formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', tip)
        tips += f"      <p>{tip_formatted}</p>\n"

    return f'''<div class="section-card sec-tips" data-index="4">
  <div class="section-header" onclick="toggleSection(this)">
    <div class="section-number">5</div>
    <div class="section-title"><div class="label">🦘 Australia Tips</div><div class="name">オーストラリアで{h(data["sweet"])}を楽しむなら</div></div>
    <div class="section-chevron">▾</div>
  </div>
  <div class="section-body">
    <div class="tips-box">
{tips}    </div>
  </div>
</div>'''


def section_conversation(data: dict) -> str:
    """Section 6: Conversation"""
    conv = data["conversation"]
    yamada = yamada_comment_html(data["yamada_comments"]["conversation"])
    vocab = vocab_list_html(data["conversation_vocab"], "convo")

    lines_html = ""
    convo_plain_parts = []
    convo_tts_parts = []
    for line in conv["lines"]:
        speaker = line["speaker"]
        text = line["text"]
        speaker_class = "you" if speaker.lower() == "you" else "emma"
        lines_html += f'    <div class="convo-line"><span class="convo-speaker {speaker_class}">{h(speaker)}:</span><span class="convo-text">{h(text)}</span></div>\n'
        convo_plain_parts.append(f"{speaker}: {text}")
        convo_tts_parts.append(text)

    convo_plain = " ".join(convo_plain_parts)
    convo_tts = " ... ".join(convo_tts_parts)

    return f'''<div class="section-card sec-convo" data-index="5">
  <div class="section-header" onclick="toggleSection(this)">
    <div class="section-number">6</div>
    <div class="section-title"><div class="label">Conversation</div><div class="name">カフェでの接客場面</div></div>
    <div class="section-chevron">▾</div>
  </div>
  <div class="section-body">
{yamada}
    <div class="conversation-scene">☕ {h(conv["scene"])}</div>
{lines_html}    <div class="action-row">
      <button class="action-btn" onclick="copyText('convo-text')">📋 コピー</button>
      <button class="action-btn tts-btn" onclick="speakText('convo-tts', this)">🔊 読み上げ</button>
      <a class="action-btn" href="https://www.naturalreaders.com/online/" target="_blank">🔊 Natural Reader</a>
    </div>
    <div id="convo-text" style="display:none">{h(convo_plain)}</div>
    <div id="convo-tts" style="display:none">{h(convo_tts)}</div>
{vocab}
  </div>
</div>'''


def section_quiz3(data: dict) -> str:
    """Section 7: Quiz 3"""
    q = quiz_html(data["quiz3"], "quiz3")
    return f'''<div class="section-card sec-quiz3" data-index="6">
  <div class="section-header" onclick="toggleSection(this)">
    <div class="section-number">7</div>
    <div class="section-title"><div class="label">Quiz 3</div><div class="name">会話の内容チェック</div></div>
    <div class="section-chevron">▾</div>
  </div>
  <div class="section-body">
{q}
  </div>
</div>'''


def section_listening(data: dict) -> str:
    """Section 8: Listening Challenge"""
    ls = data["listening"]
    yamada = yamada_comment_html(data["yamada_comments"]["listening"])

    # Part A: gap fill
    pa = ls["part_a"]
    gaps_html = ""
    for i, gap in enumerate(pa["gaps"], 1):
        gaps_html += f'      <div class="gap-fill">{i}. {h(gap["before"])} <input type="text" data-answer="{h(gap["answer"])}" placeholder="____"> {h(gap["after"])}</div>\n'

    answers_html = " ".join(f'{i+1}. <strong>{h(g["answer"])}</strong>' for i, g in enumerate(pa["gaps"]))

    # Part A script
    pa_script = h(pa["full_text"]).replace(". ", ".<br>\n        ")

    # Part B: comprehension quiz
    pb = ls["part_b"]
    pb_questions = ""
    for i, q in enumerate(pb["questions"]):
        margin = 'style="margin-top:0.5rem;"' if i == 0 else 'style="margin-top:1.2rem;"'
        options = ""
        for j, opt in enumerate(q["options"]):
            is_correct = "true" if j == q["correct_index"] else "false"
            options += f'        <div class="quiz-option" onclick="checkQuiz(this, {is_correct})">{h(opt)}</div>\n'
        pb_questions += f'''
      <div class="quiz-question" {margin}>Q{i+1}: {h(q["question_ja"])}</div>
      <div class="quiz-options">
{options}      </div>
      <div class="quiz-feedback correct">⭕ 正解！{h(q["explanation_correct"])}</div>
      <div class="quiz-feedback wrong">❌ {h(q["explanation_wrong"])}</div>
'''

    pb_script = h(pb["full_text"]).replace(". ", ".<br>\n        ")

    return f'''<div class="section-card sec-listening" data-index="7">
  <div class="section-header" onclick="toggleSection(this)">
    <div class="section-number">8</div>
    <div class="section-title"><div class="label">🎧 Listening Challenge</div><div class="name">リスニングに挑戦しよう</div></div>
    <div class="section-chevron">▾</div>
  </div>
  <div class="section-body">
{yamada}

    <!-- Part A -->
    <div class="listening-box">
      <h4>🔊 Part A: {h(pa["title_ja"])}（穴埋め）</h4>
      <p class="listening-instruction">音声を聴いて、空欄に入る単語を書いてみよう。最初はわからなくて当然！何回でも聴いてOK。</p>
      <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.8rem;">
        <button class="tts-btn" onclick="speakText('listening-a-tts', this)">🔊 再生</button>
        <span class="tts-speed">速度: <select id="speed-a" onchange="currentSpeed=parseFloat(this.value)">
          <option value="0.7">🐢 ゆっくり</option>
          <option value="0.85" selected>普通</option>
          <option value="1">速い</option>
        </select></span>
        <span class="repeat-count" id="repeat-a">再生回数: 0</span>
      </div>
      <div id="listening-a-tts" style="display:none">{h(pa["full_text"])}</div>
{gaps_html}      <button class="listening-check-btn" onclick="checkAllGaps(this)">✅ 答えを確認</button>
      <div class="listening-answer" id="gap-answer-a">
        <strong>答え:</strong> {answers_html}
      </div>
      <button class="listening-script-toggle" onclick="toggleScript(this)">📝 スクリプトを見る</button>
      <div class="listening-script">
        {pa_script}
      </div>
    </div>

    <!-- Part B -->
    <div class="listening-box">
      <h4>🔊 Part B: {h(pb["title_ja"])}（内容理解）</h4>
      <p class="listening-instruction">音声を聴いてから、質問に答えてみよう。先に質問を読んでから聴くのもOK！</p>
      <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.8rem;">
        <button class="tts-btn" onclick="speakText('listening-b-tts', this)">🔊 再生</button>
        <span class="tts-speed">速度: <select id="speed-b" onchange="currentSpeed=parseFloat(this.value)">
          <option value="0.7">🐢 ゆっくり</option>
          <option value="0.85" selected>普通</option>
          <option value="1">速い</option>
        </select></span>
        <span class="repeat-count" id="repeat-b">再生回数: 0</span>
      </div>
      <div id="listening-b-tts" style="display:none">{h(pb["full_text"])}</div>
{pb_questions}
      <button class="listening-script-toggle" onclick="toggleScript(this)" style="margin-top:0.8rem;">📝 スクリプトを見る</button>
      <div class="listening-script">
        {pb_script}
      </div>
    </div>
  </div>
</div>'''


def section_pronunciation(data: dict) -> str:
    """Section 9: Pronunciation Check"""
    yamada = yamada_comment_html(data["yamada_comments"]["pronunciation"])
    sentences = data["pronunciation"]["sentences"]
    sentences_json = json.dumps(sentences, ensure_ascii=False)

    return f'''<div class="section-card sec-pronun" data-index="8">
  <div class="section-header" onclick="toggleSection(this)">
    <div class="section-number">9</div>
    <div class="section-title"><div class="label">🎤 Pronunciation Check</div><div class="name">発音チェックに挑戦しよう</div></div>
    <div class="section-chevron">▾</div>
  </div>
  <div class="section-body">
{yamada}

    <div class="pronun-box">
      <h4>🎤 文を声に出して読んでみよう</h4>
      <p style="font-size:0.85rem;color:var(--text-light);margin-bottom:0.5rem;">マイクボタンを押して、表示された文を読み上げてください。音声認識であなたの発音をチェックします。</p>

      <div class="pronun-sentence" id="pronun-target"></div>

      <div style="display:flex;align-items:center;gap:0.8rem;flex-wrap:wrap;">
        <button class="pronun-record-btn" id="pronun-btn" onclick="togglePronunRecording()">
          🎤 録音スタート
        </button>
        <button class="tts-btn" onclick="speakPronunSentence()" style="background:var(--navy);">🔊 お手本を聴く</button>
      </div>

      <div class="pronun-result" id="pronun-result">
        <div class="pronun-score">
          <div class="pronun-score-circle" id="pronun-score-circle">-</div>
          <div>
            <div style="font-weight:700;color:var(--navy);" id="pronun-score-label">判定中...</div>
            <div style="font-size:0.75rem;color:var(--text-light);" id="pronun-score-detail"></div>
          </div>
        </div>
        <div class="pronun-heard" id="pronun-heard"></div>
        <ul class="pronun-tips" id="pronun-tips"></ul>
      </div>

      <div class="pronun-nav">
        <button class="pronun-nav-btn" id="pronun-prev" onclick="changePronunSentence(-1)">← 前の文</button>
        <span class="pronun-counter" id="pronun-counter">1 / {len(sentences)}</span>
        <button class="pronun-nav-btn" id="pronun-next" onclick="changePronunSentence(1)">次の文 →</button>
      </div>

      <div class="pronun-browser-note">
        💡 Chrome推奨。マイクの許可が必要です。静かな場所で、はっきり声に出して読んでください。
      </div>
    </div>
  </div>
</div>
<script>
const pronunSentences = {sentences_json};
</script>'''


def section_tryit(data: dict) -> str:
    """Section 10: Try It"""
    yamada = yamada_comment_html(data["yamada_comments"]["try_it"])
    ti = data["try_it"]

    return f'''<div class="section-card sec-tryit" data-index="9">
  <div class="section-header" onclick="toggleSection(this)">
    <div class="section-number">10</div>
    <div class="section-title"><div class="label">✏️ Try It!</div><div class="name">今日のことを3行で書いてみよう</div></div>
    <div class="section-chevron">▾</div>
  </div>
  <div class="section-body">
{yamada}
    <div class="try-it-box">
      <h4>✏️ {h(ti["prompt_ja"])}</h4>
      <p>💡 今日の会話や文をマネしてOK！わからない英語は日本語のままで大丈夫。</p>
      <p><strong>例:</strong> {h(ti["example"])}</p>
      <textarea class="try-it-textarea" id="tryit-text" placeholder="ここに英語で書いてみよう..."></textarea>
    </div>
  </div>
</div>'''


def section_summary(data: dict) -> str:
    """Section 11: Summary"""
    day = data["day"]
    sweet = data["sweet"]
    return f'''<div class="section-card sec-summary" data-index="10">
  <div class="section-header" onclick="toggleSection(this)">
    <div class="section-number">11</div>
    <div class="section-title"><div class="label">📊 Summary</div><div class="name">学習サマリー</div></div>
    <div class="section-chevron">▾</div>
  </div>
  <div class="section-body">
    <div class="summary-box">
      <p style="font-size:0.85rem;color:var(--text-light);margin-bottom:0.8rem;">ChatGPTやClaudeにコピペして解説をもらおう</p>
      <button class="summary-btn" onclick="generateSummary()">📋 サマリーを生成する</button>
      <div class="summary-output" id="summary-output"></div>
      <div class="action-row" style="justify-content:center;margin-top:0.5rem;">
        <button class="action-btn" onclick="copySummary()">📋 コピー</button>
        <a class="action-btn" href="https://chat.openai.com" target="_blank">🤖 ChatGPT</a>
        <a class="action-btn" href="https://claude.ai" target="_blank">🤖 Claude</a>
      </div>
    </div>
  </div>
</div>'''


# ── CSS (extracted from day1-v3.html) ──
CSS = """:root {
  --primary: #E8792F;
  --primary-light: #FDF0E6;
  --primary-dark: #C45A1A;
  --navy: #1B3A5C;
  --blue: #2E75B6;
  --blue-light: #D6E8F7;
  --green: #4CAF50;
  --green-light: #E8F5E9;
  --purple: #7B1FA2;
  --purple-light: #F3E5F5;
  --listening-color: #00897B;
  --listening-light: #E0F2F1;
  --bg: #FAFAF7;
  --card-bg: #FFFFFF;
  --text: #333333;
  --text-light: #666666;
  --border: #E8E5DF;
  --shadow: 0 2px 12px rgba(27,58,92,0.08);
  --shadow-hover: 0 4px 20px rgba(27,58,92,0.14);
  --radius: 16px;
  --radius-sm: 10px;
  --yamada-bg: linear-gradient(135deg, #FFF5F5 0%, #FFF0F5 50%, #F5F0FF 100%);
  --yamada-border: #E8B4B8;
  --yamada-accent: #C2185B;
  --pronun-color: #E65100;
  --pronun-light: #FFF3E0;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Noto Sans JP', 'Zen Maru Gothic', sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.8;
  min-height: 100vh;
}

.header {
  background: linear-gradient(135deg, var(--navy) 0%, #2A5080 100%);
  color: white;
  padding: 2rem 1.5rem 1.5rem;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(232,121,47,0.15) 0%, transparent 70%);
  border-radius: 50%;
}
.header-badge {
  display: inline-block;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  padding: 0.3rem 1rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-family: 'Quicksand', sans-serif;
  font-weight: 600;
  letter-spacing: 0.05em;
  margin-bottom: 0.8rem;
  border: 1px solid rgba(255,255,255,0.2);
}
.header h1 {
  font-family: 'Quicksand', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
}
.header p { font-size: 0.85rem; opacity: 0.8; }

.progress-bar {
  background: white;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.progress-dots { display: flex; gap: 4px; justify-content: center; align-items: center; }
.progress-dot {
  width: 28px; height: 6px; border-radius: 3px;
  background: var(--border); transition: all 0.3s; cursor: pointer;
}
.progress-dot.active { background: var(--primary); }
.progress-dot.complete { background: var(--green); }
.progress-label {
  text-align: center; font-size: 0.7rem; color: var(--text-light);
  margin-top: 0.4rem; font-family: 'Quicksand', sans-serif; font-weight: 600;
}

.main { max-width: 640px; margin: 0 auto; padding: 1rem 1rem 4rem; }

.section-card {
  background: var(--card-bg); border-radius: var(--radius);
  margin-bottom: 1.2rem; box-shadow: var(--shadow);
  overflow: hidden; border: 1px solid var(--border);
  transition: box-shadow 0.3s;
  animation: fadeIn 0.4s ease both;
}
.section-card:hover { box-shadow: var(--shadow-hover); }
.section-card:nth-child(1) { animation-delay: 0.05s; }
.section-card:nth-child(2) { animation-delay: 0.1s; }
.section-card:nth-child(3) { animation-delay: 0.15s; }
.section-card:nth-child(4) { animation-delay: 0.2s; }
.section-card:nth-child(5) { animation-delay: 0.25s; }
.section-card:nth-child(6) { animation-delay: 0.3s; }
.section-card:nth-child(7) { animation-delay: 0.35s; }
.section-card:nth-child(8) { animation-delay: 0.4s; }
.section-card:nth-child(9) { animation-delay: 0.45s; }
.section-card:nth-child(10) { animation-delay: 0.5s; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.section-header {
  display: flex; align-items: center; gap: 0.8rem;
  padding: 1rem 1.2rem; cursor: pointer; user-select: none;
  transition: background 0.2s;
}
.section-header:hover { background: rgba(0,0,0,0.02); }
.section-number {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Quicksand', sans-serif; font-weight: 700;
  font-size: 0.85rem; color: white; flex-shrink: 0;
}
.section-title { flex: 1; }
.section-title .label {
  font-size: 0.65rem; font-family: 'Quicksand', sans-serif;
  font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.08em; opacity: 0.7;
}
.section-title .name { font-size: 1rem; font-weight: 700; }
.section-chevron { font-size: 1.2rem; transition: transform 0.3s; opacity: 0.4; }
.section-card.open .section-chevron { transform: rotate(180deg); }
.section-body { padding: 0 1.2rem 1.2rem; display: none; }
.section-card.open .section-body { display: block; }

.yamada-comment {
  background: var(--yamada-bg); border: 1px solid var(--yamada-border);
  border-radius: var(--radius-sm); padding: 0.8rem 1rem;
  margin-bottom: 1rem; display: flex; gap: 0.6rem;
  align-items: flex-start; font-size: 0.85rem; line-height: 1.6;
}
.yamada-text { flex: 1; }
.yamada-name {
  font-size: 0.7rem; font-weight: 700; color: var(--yamada-accent);
  font-family: 'Quicksand', sans-serif; margin-bottom: 0.15rem;
}

.recipe-box {
  background: #FFFDF9; border: 1px solid #F0E8D8;
  border-radius: var(--radius-sm); padding: 1.2rem; margin-bottom: 1rem;
}
.recipe-box h3 { font-family: 'Quicksand', sans-serif; font-size: 1.1rem; color: var(--navy); margin-bottom: 0.8rem; }
.recipe-box .ingredients {
  font-size: 0.85rem; color: var(--text-light); margin-bottom: 1rem;
  padding: 0.6rem; background: rgba(232,121,47,0.05); border-radius: 8px;
}
.recipe-box .ingredients strong { color: var(--primary-dark); }
.recipe-steps { counter-reset: step; list-style: none; }
.recipe-steps li {
  counter-increment: step; padding: 0.5rem 0 0.5rem 2.2rem;
  position: relative; font-size: 0.9rem; border-bottom: 1px solid #F5F0E8;
}
.recipe-steps li:last-child { border-bottom: none; }
.recipe-steps li::before {
  content: counter(step); position: absolute; left: 0; top: 0.5rem;
  width: 24px; height: 24px; background: var(--primary); color: white;
  border-radius: 50%; font-size: 0.75rem; font-family: 'Quicksand', sans-serif;
  font-weight: 700; display: flex; align-items: center; justify-content: center;
}
.recipe-steps li strong { color: var(--navy); }

.action-row { display: flex; gap: 0.5rem; margin: 0.8rem 0; flex-wrap: wrap; }
.action-btn {
  display: inline-flex; align-items: center; gap: 0.3rem;
  padding: 0.4rem 0.8rem; border: 1px solid var(--border);
  border-radius: 20px; font-size: 0.75rem; background: white;
  cursor: pointer; transition: all 0.2s; font-family: 'Noto Sans JP', sans-serif;
  color: var(--text-light); text-decoration: none;
}
.action-btn:hover { background: var(--blue-light); border-color: var(--blue); color: var(--navy); }

.vocab-toggle {
  display: inline-flex; align-items: center; gap: 0.3rem;
  padding: 0.4rem 0.8rem; border: 1px solid var(--border);
  border-radius: 20px; font-size: 0.75rem; background: white;
  cursor: pointer; transition: all 0.2s; color: var(--text-light); margin-bottom: 0.5rem;
}
.vocab-toggle:hover { background: var(--green-light); border-color: var(--green); }
.vocab-list { display: none; margin-top: 0.5rem; }
.vocab-list.show { display: block; }
.vocab-item {
  display: flex; align-items: center; gap: 0.8rem;
  padding: 0.5rem 0.8rem; border-radius: 8px; font-size: 0.85rem;
  transition: background 0.2s; cursor: pointer;
}
.vocab-item:hover { background: rgba(0,0,0,0.03); }
.vocab-check {
  width: 18px; height: 18px; border: 2px solid var(--border);
  border-radius: 4px; flex-shrink: 0; display: flex;
  align-items: center; justify-content: center;
  transition: all 0.2s; font-size: 0.7rem; color: transparent;
}
.vocab-item.checked .vocab-check { background: var(--primary); border-color: var(--primary); color: white; }
.vocab-en { font-weight: 700; color: var(--navy); min-width: 100px; }
.vocab-ja { color: var(--text-light); font-size: 0.8rem; }

.quiz-question { font-weight: 700; font-size: 0.95rem; margin-bottom: 0.8rem; color: var(--navy); padding-left: 0.3rem; }
.quiz-options { display: flex; flex-direction: column; gap: 0.5rem; }
.quiz-option {
  padding: 0.7rem 1rem; border: 2px solid var(--border);
  border-radius: var(--radius-sm); cursor: pointer; font-size: 0.9rem;
  transition: all 0.2s; background: white;
}
.quiz-option:hover { border-color: var(--blue); background: var(--blue-light); }
.quiz-option.correct { border-color: var(--green); background: var(--green-light); }
.quiz-option.wrong { border-color: #E53935; background: #FFEBEE; }
.quiz-feedback { margin-top: 0.8rem; padding: 0.6rem 0.8rem; border-radius: 8px; font-size: 0.85rem; display: none; }
.quiz-feedback.show { display: block; }
.quiz-feedback.correct { background: var(--green-light); color: #2E7D32; }
.quiz-feedback.wrong { background: #FFEBEE; color: #C62828; }

.review-card {
  background: linear-gradient(135deg, #FFFDF7 0%, #FFF8F0 100%);
  border: 1px solid #F0E0C8; border-radius: var(--radius-sm);
  padding: 1.2rem; margin-bottom: 1rem;
}
.review-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.6rem; }
.review-header h4 { font-family: 'Quicksand', sans-serif; font-size: 0.95rem; color: var(--navy); }
.review-stars { color: #F9A825; font-size: 0.9rem; }
.review-text { font-size: 0.9rem; line-height: 1.9; color: var(--text); }

.tips-box {
  background: linear-gradient(135deg, #F0F8FF 0%, #E8F5E9 100%);
  border: 1px solid #C8E6C9; border-radius: var(--radius-sm); padding: 1.2rem;
}
.tips-box p { font-size: 0.85rem; margin-bottom: 0.8rem; line-height: 1.8; }
.tips-box p:last-child { margin-bottom: 0; }

.conversation-scene {
  background: var(--blue-light); border-radius: var(--radius-sm);
  padding: 0.6rem 1rem; font-size: 0.8rem; color: var(--navy);
  margin-bottom: 1rem; font-weight: 500;
}
.convo-line { display: flex; gap: 0.6rem; margin-bottom: 0.6rem; align-items: flex-start; }
.convo-speaker { font-weight: 700; font-size: 0.8rem; min-width: 50px; padding-top: 0.1rem; flex-shrink: 0; }
.convo-speaker.you { color: var(--primary); }
.convo-speaker.emma { color: var(--blue); }
.convo-text { font-size: 0.9rem; }

/* ===== LISTENING ===== */
.listening-box {
  background: var(--listening-light); border: 1px solid #B2DFDB;
  border-radius: var(--radius-sm); padding: 1.2rem; margin-bottom: 1rem;
}
.listening-box h4 { font-family: 'Quicksand', sans-serif; color: var(--listening-color); font-size: 0.95rem; margin-bottom: 0.8rem; }
.listening-instruction { font-size: 0.85rem; color: var(--text-light); margin-bottom: 0.6rem; }

.tts-btn {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.5rem 1.2rem; background: var(--listening-color);
  color: white; border: none; border-radius: 20px;
  font-size: 0.8rem; font-family: 'Noto Sans JP', sans-serif;
  font-weight: 700; cursor: pointer; transition: all 0.2s;
  margin-bottom: 0.8rem;
}
.tts-btn:hover { background: #00695C; transform: translateY(-1px); }
.tts-btn.playing { background: #E53935; }
.tts-btn.playing:hover { background: #C62828; }

.tts-speed {
  display: inline-flex; align-items: center; gap: 0.3rem;
  margin-left: 0.5rem; font-size: 0.75rem; color: var(--text-light);
}
.tts-speed select {
  border: 1px solid var(--border); border-radius: 12px;
  padding: 0.2rem 0.4rem; font-size: 0.75rem;
  background: white; cursor: pointer;
}

.gap-fill { margin: 0.5rem 0; font-size: 0.9rem; line-height: 2.4; }
.gap-fill input {
  border: none; border-bottom: 2px solid var(--listening-color);
  background: rgba(0,137,123,0.05); border-radius: 4px 4px 0 0;
  padding: 0.1rem 0.3rem; font-size: 0.9rem;
  font-family: 'Quicksand', sans-serif; font-weight: 600;
  width: 100px; text-align: center; outline: none;
  color: var(--listening-color);
}
.gap-fill input:focus { border-bottom-color: var(--primary); background: rgba(232,121,47,0.08); }
.gap-fill input.correct-input { border-bottom-color: #4CAF50; background: rgba(76,175,80,0.1); }
.gap-fill input.wrong-input { border-bottom-color: #E53935; background: rgba(229,57,53,0.1); }

.listening-check-btn {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.5rem 1.2rem; background: var(--listening-color);
  color: white; border: none; border-radius: 20px;
  font-size: 0.8rem; font-family: 'Noto Sans JP', sans-serif;
  font-weight: 700; cursor: pointer; transition: all 0.2s; margin-top: 0.5rem;
}
.listening-check-btn:hover { background: #00695C; transform: translateY(-1px); }
.listening-answer {
  margin-top: 0.8rem; padding: 0.6rem 0.8rem; background: white;
  border-radius: 8px; font-size: 0.85rem; display: none; border: 1px solid #B2DFDB;
}
.listening-answer.show { display: block; }

.listening-script-toggle {
  display: inline-flex; align-items: center; gap: 0.3rem;
  padding: 0.4rem 0.8rem; border: 1px dashed var(--listening-color);
  border-radius: 20px; font-size: 0.75rem; background: white;
  cursor: pointer; color: var(--listening-color); margin-top: 0.5rem;
}
.listening-script { display: none; margin-top: 0.6rem; padding: 0.8rem; background: white; border-radius: 8px; font-size: 0.85rem; border: 1px solid #B2DFDB; line-height: 1.8; }
.listening-script.show { display: block; }

.try-it-box {
  background: var(--purple-light); border: 1px solid #CE93D8;
  border-radius: var(--radius-sm); padding: 1.2rem;
}
.try-it-box h4 { color: var(--purple); font-family: 'Quicksand', sans-serif; margin-bottom: 0.5rem; }
.try-it-box p { font-size: 0.85rem; margin-bottom: 0.6rem; }
.try-it-textarea {
  width: 100%; min-height: 100px; border: 1px solid #CE93D8;
  border-radius: 8px; padding: 0.8rem; font-size: 0.9rem;
  font-family: 'Noto Sans JP', sans-serif; line-height: 1.8;
  resize: vertical; outline: none; transition: border-color 0.2s;
}
.try-it-textarea:focus { border-color: var(--purple); }

.summary-box {
  background: white; border: 2px dashed var(--border);
  border-radius: var(--radius-sm); padding: 1.2rem; text-align: center;
}
.summary-btn {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.6rem 1.5rem; background: var(--navy); color: white;
  border: none; border-radius: 20px; font-size: 0.85rem;
  font-family: 'Noto Sans JP', sans-serif; font-weight: 700;
  cursor: pointer; transition: all 0.2s; margin-bottom: 0.5rem;
}
.summary-btn:hover { background: #2A5080; transform: translateY(-1px); }
.summary-output {
  margin-top: 0.8rem; text-align: left; font-size: 0.8rem;
  color: var(--text-light); padding: 0.8rem; background: #F5F5F5;
  border-radius: 8px; display: none; white-space: pre-wrap;
}
.summary-output.show { display: block; }

.day-nav {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1rem 0; margin-top: 1rem; border-top: 1px solid var(--border);
}
.nav-btn {
  display: inline-flex; align-items: center; gap: 0.3rem;
  padding: 0.5rem 1rem; border: 1px solid var(--border);
  border-radius: 20px; font-size: 0.85rem; background: white;
  cursor: pointer; transition: all 0.2s; text-decoration: none;
  color: var(--text); font-family: 'Noto Sans JP', sans-serif;
}
.nav-btn:hover { background: var(--blue-light); border-color: var(--blue); }
.nav-btn.disabled { opacity: 0.4; pointer-events: none; }
.home-btn {
  padding: 0.5rem 1rem; background: var(--primary); color: white;
  border: none; border-radius: 20px; font-size: 0.8rem; cursor: pointer;
  text-decoration: none; font-family: 'Quicksand', sans-serif; font-weight: 700;
}

.sec-recipe .section-number { background: var(--primary); }
.sec-quiz1 .section-number { background: var(--blue); }
.sec-review .section-number { background: #F9A825; }
.sec-quiz2 .section-number { background: var(--blue); }
.sec-tips .section-number { background: var(--green); }
.sec-convo .section-number { background: var(--navy); }
.sec-quiz3 .section-number { background: var(--blue); }
.sec-listening .section-number { background: var(--listening-color); }
.sec-tryit .section-number { background: var(--purple); }
.sec-summary .section-number { background: var(--text-light); }
.sec-pronun .section-number { background: var(--pronun-color); }

/* ===== PRONUNCIATION CHECK ===== */
.pronun-box {
  background: var(--pronun-light);
  border: 1px solid #FFB74D;
  border-radius: var(--radius-sm);
  padding: 1.2rem;
  margin-bottom: 1rem;
}
.pronun-box h4 {
  font-family: 'Quicksand', sans-serif;
  color: var(--pronun-color);
  font-size: 0.95rem;
  margin-bottom: 0.6rem;
}
.pronun-sentence {
  background: white;
  border: 2px solid #FFB74D;
  border-radius: var(--radius-sm);
  padding: 1rem;
  margin: 0.8rem 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--navy);
  text-align: center;
  line-height: 1.8;
}
.pronun-sentence .word {
  display: inline-block;
  padding: 0.1rem 0.2rem;
  border-radius: 4px;
  transition: all 0.3s;
  margin: 0 1px;
}
.pronun-sentence .word.correct { background: rgba(76,175,80,0.2); color: #2E7D32; }
.pronun-sentence .word.wrong { background: rgba(229,57,53,0.2); color: #C62828; text-decoration: underline wavy #E53935; }
.pronun-sentence .word.missed { background: rgba(255,152,0,0.2); color: #E65100; }

.pronun-record-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 1.5rem;
  background: var(--pronun-color);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 0.9rem;
  font-family: 'Noto Sans JP', sans-serif;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.pronun-record-btn:hover { background: #BF360C; transform: translateY(-1px); }
.pronun-record-btn.recording {
  background: #E53935;
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(229,57,53,0.4); }
  50% { box-shadow: 0 0 0 12px rgba(229,57,53,0); }
}

.pronun-result {
  margin-top: 1rem;
  padding: 0.8rem 1rem;
  border-radius: var(--radius-sm);
  display: none;
  font-size: 0.85rem;
}
.pronun-result.show { display: block; }
.pronun-result.good { background: var(--green-light); border: 1px solid #A5D6A7; }
.pronun-result.needs-work { background: #FFF3E0; border: 1px solid #FFB74D; }
.pronun-result.try-again { background: #FFEBEE; border: 1px solid #EF9A9A; }

.pronun-score {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 0.5rem;
}
.pronun-score-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Quicksand', sans-serif;
  font-weight: 700;
  font-size: 1.1rem;
  color: white;
  flex-shrink: 0;
}
.pronun-score-circle.high { background: var(--green); }
.pronun-score-circle.mid { background: #FF9800; }
.pronun-score-circle.low { background: #E53935; }

.pronun-heard {
  margin-top: 0.5rem;
  padding: 0.5rem 0.8rem;
  background: rgba(0,0,0,0.03);
  border-radius: 8px;
  font-size: 0.8rem;
  color: var(--text-light);
}
.pronun-heard strong { color: var(--navy); }

.pronun-tips {
  margin-top: 0.6rem;
  font-size: 0.8rem;
  color: var(--text-light);
  padding-left: 0.5rem;
}
.pronun-tips li { margin-bottom: 0.3rem; }

.pronun-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.8rem;
}
.pronun-nav-btn {
  padding: 0.4rem 1rem;
  border: 1px solid var(--border);
  border-radius: 20px;
  font-size: 0.8rem;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}
.pronun-nav-btn:hover { background: var(--pronun-light); border-color: #FFB74D; }
.pronun-nav-btn.disabled { opacity: 0.3; pointer-events: none; }
.pronun-counter {
  font-size: 0.75rem;
  color: var(--text-light);
  font-family: 'Quicksand', sans-serif;
  font-weight: 600;
}
.pronun-browser-note {
  font-size: 0.7rem;
  color: var(--text-light);
  margin-top: 0.5rem;
  padding: 0.4rem 0.6rem;
  background: rgba(0,0,0,0.03);
  border-radius: 6px;
}

.repeat-count { font-size: 0.75rem; color: var(--text-light); margin-left: 0.5rem; }

@media (max-width: 480px) {
  .header h1 { font-size: 1.6rem; }
  .main { padding: 0.8rem 0.6rem 4rem; }
  .section-body { padding: 0 0.8rem 1rem; }
}"""


def build_js(day: int, sweet: str) -> str:
    """JavaScriptコード（day1-v3.htmlベース）"""
    return f'''let currentSpeed = 0.85;
let repeatCounts = {{}};

function toggleSection(header) {{
  const card = header.parentElement;
  card.classList.toggle('open');
  const index = parseInt(card.dataset.index);
  const dots = document.querySelectorAll('.progress-dot');
  if (card.classList.contains('open')) {{
    dots[index].classList.add('active');
    for (let i = 0; i < index; i++) {{ dots[i].classList.add('complete'); dots[i].classList.remove('active'); }}
  }}
  const openCards = document.querySelectorAll('.section-card.open');
  document.querySelector('.progress-label').textContent = openCards.length + ' / {TOTAL_SECTIONS} セクション';
}}

function toggleVocab(btn) {{
  const list = btn.nextElementSibling;
  list.classList.toggle('show');
  btn.textContent = list.classList.contains('show') ? '📚 単語リストを隠す' : '📚 単語リストを見る';
}}

function checkQuiz(option, isCorrect) {{
  const parent = option.parentElement;
  if (parent.dataset.answered) return;
  parent.dataset.answered = 'true';
  const allOptions = parent.querySelectorAll('.quiz-option');
  allOptions.forEach(opt => opt.style.pointerEvents = 'none');
  if (isCorrect) {{
    option.classList.add('correct');
    parent.nextElementSibling.classList.add('show');
  }} else {{
    option.classList.add('wrong');
    parent.nextElementSibling.nextElementSibling.classList.add('show');
  }}
}}

// Web Speech API TTS
function speakText(elementId, btn) {{
  if (window.speechSynthesis.speaking) {{
    window.speechSynthesis.cancel();
    btn.textContent = '🔊 再生';
    btn.classList.remove('playing');
    return;
  }}
  const text = document.getElementById(elementId).textContent;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'en-AU';
  utterance.rate = currentSpeed;
  utterance.pitch = 1;

  const voices = window.speechSynthesis.getVoices();
  const enVoice = voices.find(v => v.lang.startsWith('en-AU')) ||
                  voices.find(v => v.lang.startsWith('en-GB')) ||
                  voices.find(v => v.lang.startsWith('en'));
  if (enVoice) utterance.voice = enVoice;

  btn.textContent = '⏹ 停止';
  btn.classList.add('playing');

  if (!repeatCounts[elementId]) repeatCounts[elementId] = 0;
  repeatCounts[elementId]++;
  const repeatEl = btn.parentElement.querySelector('.repeat-count');
  if (repeatEl) repeatEl.textContent = '再生回数: ' + repeatCounts[elementId];

  utterance.onend = () => {{ btn.textContent = '🔊 再生'; btn.classList.remove('playing'); }};
  utterance.onerror = () => {{ btn.textContent = '🔊 再生'; btn.classList.remove('playing'); }};
  window.speechSynthesis.speak(utterance);
}}

window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();

function checkAllGaps(btn) {{
  const box = btn.closest('.listening-box');
  const inputs = box.querySelectorAll('input[data-answer]');
  inputs.forEach(input => {{
    const correct = input.dataset.answer.toLowerCase();
    const val = input.value.trim().toLowerCase();
    input.classList.remove('correct-input', 'wrong-input');
    if (val === correct) {{ input.classList.add('correct-input'); }}
    else {{ input.classList.add('wrong-input'); }}
  }});
  const answer = box.querySelector('.listening-answer');
  if (answer) answer.classList.add('show');
}}

function toggleScript(btn) {{
  const script = btn.nextElementSibling;
  script.classList.toggle('show');
  btn.textContent = script.classList.contains('show') ? '📝 スクリプトを隠す' : '📝 スクリプトを見る';
}}

function copyText(id) {{
  const text = document.getElementById(id).textContent;
  navigator.clipboard.writeText(text).then(() => alert('コピーしました！'));
}}

function generateSummary() {{
  const checked = document.querySelectorAll('.vocab-item.checked');
  const vocabList = Array.from(checked).map(i => i.querySelector('.vocab-en').textContent);
  const tryIt = document.getElementById('tryit-text').value;
  const listeningPlays = Object.entries(repeatCounts).map(([k,v]) => k + ': ' + v + '回').join(', ');

  let s = `【Day {day}: {sweet} 学習サマリー】\\n\\n`;
  s += `■ チェックした単語 (${{vocabList.length}}個):\\n${{vocabList.length > 0 ? vocabList.join(', ') : 'なし'}}\\n\\n`;
  s += `■ リスニング再生回数:\\n${{listeningPlays || '未再生'}}\\n\\n`;

  const pronunSummary = pronunResults.filter(r => r).map((r, i) =>
    `  ${{i+1}}. "${{r.target}}" → ${{r.score}}% (認識: "${{r.heard}}")`
  ).join('\\n');
  s += `■ 発音チェック結果:\\n${{pronunSummary || '(未実施)'}}\\n\\n`;

  s += `■ Today's Writing:\\n${{tryIt || '(未記入)'}}\\n\\n`;
  s += `---\\n上の内容をもとに、以下を教えてください：\\n1. チェックした単語の使い方（例文付き）\\n2. 発音チェックで間違えた部分のアドバイス\\n3. Today's Writingの添削\\n4. 今日学んだフレーズの発展表現`;

  const output = document.getElementById('summary-output');
  output.textContent = s;
  output.classList.add('show');
}}

function copySummary() {{
  const text = document.getElementById('summary-output').textContent;
  navigator.clipboard.writeText(text).then(() => alert('コピーしました！'));
}}

document.querySelectorAll('.progress-dot').forEach(dot => {{
  dot.addEventListener('click', () => {{
    const index = parseInt(dot.dataset.section);
    const cards = document.querySelectorAll('.section-card');
    if (cards[index]) {{
      cards[index].scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      if (!cards[index].classList.contains('open')) toggleSection(cards[index].querySelector('.section-header'));
    }}
  }});
}});

// ===== PRONUNCIATION CHECK =====
// pronunSentences is defined in the HTML before this script

let currentPronunIndex = 0;
let pronunResults = [];
let pronunRecognition = null;
let isRecording = false;

function initPronun() {{
  renderPronunSentence();
  updatePronunNav();
}}

function renderPronunSentence() {{
  const target = document.getElementById('pronun-target');
  const sentence = pronunSentences[currentPronunIndex];
  const words = sentence.text.split(' ');
  target.innerHTML = words.map((w, i) => `<span class="word" data-index="${{i}}">${{w}}</span>`).join(' ');

  const result = document.getElementById('pronun-result');
  result.classList.remove('show', 'good', 'needs-work', 'try-again');
}}

function updatePronunNav() {{
  document.getElementById('pronun-counter').textContent =
    `${{currentPronunIndex + 1}} / ${{pronunSentences.length}}`;
  document.getElementById('pronun-prev').classList.toggle('disabled', currentPronunIndex === 0);
  document.getElementById('pronun-next').classList.toggle('disabled', currentPronunIndex === pronunSentences.length - 1);
}}

function changePronunSentence(dir) {{
  const newIndex = currentPronunIndex + dir;
  if (newIndex < 0 || newIndex >= pronunSentences.length) return;
  currentPronunIndex = newIndex;
  renderPronunSentence();
  updatePronunNav();
}}

function speakPronunSentence() {{
  if (window.speechSynthesis.speaking) {{
    window.speechSynthesis.cancel();
    return;
  }}
  const text = pronunSentences[currentPronunIndex].text;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'en-AU';
  utterance.rate = 0.85;
  const voices = window.speechSynthesis.getVoices();
  const enVoice = voices.find(v => v.lang.startsWith('en-AU')) ||
                  voices.find(v => v.lang.startsWith('en-GB')) ||
                  voices.find(v => v.lang.startsWith('en'));
  if (enVoice) utterance.voice = enVoice;
  window.speechSynthesis.speak(utterance);
}}

function togglePronunRecording() {{
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
    alert('お使いのブラウザは音声認識に対応していません。Chrome をお使いください。');
    return;
  }}

  if (isRecording) {{
    stopPronunRecording();
    return;
  }}

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  pronunRecognition = new SpeechRecognition();
  pronunRecognition.lang = 'en-AU';
  pronunRecognition.interimResults = false;
  pronunRecognition.maxAlternatives = 3;
  pronunRecognition.continuous = false;

  const btn = document.getElementById('pronun-btn');
  btn.textContent = '⏹ 録音中...';
  btn.classList.add('recording');
  isRecording = true;

  pronunRecognition.onresult = (event) => {{
    const results = event.results[0];
    const heard = results[0].transcript;
    const confidence = results[0].confidence;
    const alternatives = [];
    for (let i = 0; i < results.length; i++) {{
      alternatives.push(results[i].transcript.toLowerCase());
    }}
    evaluatePronunciation(heard, confidence, alternatives);
    stopPronunRecording();
  }};

  pronunRecognition.onerror = (event) => {{
    stopPronunRecording();
    if (event.error === 'no-speech') {{
      alert('音声が検出されませんでした。もう少し大きな声ではっきり話してみてください。');
    }} else if (event.error === 'not-allowed') {{
      alert('マイクの使用が許可されていません。ブラウザの設定でマイクを許可してください。');
    }} else {{
      alert('音声認識エラー: ' + event.error);
    }}
  }};

  pronunRecognition.onend = () => {{
    stopPronunRecording();
  }};

  pronunRecognition.start();
}}

function stopPronunRecording() {{
  const btn = document.getElementById('pronun-btn');
  btn.textContent = '🎤 もう一回';
  btn.classList.remove('recording');
  isRecording = false;
  if (pronunRecognition) {{
    try {{ pronunRecognition.stop(); }} catch(e) {{}}
  }}
}}

function normalizeText(text) {{
  return text.toLowerCase()
    .replace(/[.,!?;:'"()\\-]/g, '')
    .replace(/\\s+/g, ' ')
    .trim();
}}

function evaluatePronunciation(heard, confidence, alternatives) {{
  const target = pronunSentences[currentPronunIndex].text;
  const tip = pronunSentences[currentPronunIndex].tip;

  const targetWords = normalizeText(target).split(' ');
  const heardWords = normalizeText(heard).split(' ');

  const allHeardWords = new Set();
  alternatives.forEach(alt => {{
    normalizeText(alt).split(' ').forEach(w => allHeardWords.add(w));
  }});

  let correctCount = 0;
  const wordElements = document.querySelectorAll('#pronun-target .word');

  targetWords.forEach((targetWord, i) => {{
    const el = wordElements[i];
    if (!el) return;

    el.classList.remove('correct', 'wrong', 'missed');

    const targetClean = targetWord.toLowerCase();

    if (heardWords.includes(targetClean) || allHeardWords.has(targetClean)) {{
      el.classList.add('correct');
      correctCount++;
    }} else {{
      const similar = heardWords.some(hw => levenshtein(hw, targetClean) <= 1) ||
                      [...allHeardWords].some(hw => levenshtein(hw, targetClean) <= 1);
      if (similar) {{
        el.classList.add('correct');
        correctCount++;
      }} else {{
        el.classList.add('wrong');
      }}
    }}
  }});

  const score = Math.round((correctCount / targetWords.length) * 100);

  pronunResults[currentPronunIndex] = {{ score, heard, target }};

  const resultEl = document.getElementById('pronun-result');
  const scoreCircle = document.getElementById('pronun-score-circle');
  const scoreLabel = document.getElementById('pronun-score-label');
  const scoreDetail = document.getElementById('pronun-score-detail');
  const heardEl = document.getElementById('pronun-heard');
  const tipsEl = document.getElementById('pronun-tips');

  scoreCircle.textContent = score + '%';
  scoreCircle.classList.remove('high', 'mid', 'low');
  resultEl.classList.remove('good', 'needs-work', 'try-again');

  if (score >= 80) {{
    scoreCircle.classList.add('high');
    scoreLabel.textContent = '🎉 Great!';
    scoreDetail.textContent = 'しっかり通じる発音です！';
    resultEl.classList.add('good');
  }} else if (score >= 50) {{
    scoreCircle.classList.add('mid');
    scoreLabel.textContent = '👍 Almost!';
    scoreDetail.textContent = 'もう少し！赤い単語を意識してみよう。';
    resultEl.classList.add('needs-work');
  }} else {{
    scoreCircle.classList.add('low');
    scoreLabel.textContent = '💪 Keep trying!';
    scoreDetail.textContent = 'お手本を聴いてからもう一回チャレンジ！';
    resultEl.classList.add('try-again');
  }}

  heardEl.innerHTML = `<strong>🎧 認識された音声:</strong> "${{heard}}"`;
  tipsEl.innerHTML = `<li>💡 ${{tip}}</li>`;

  const wrongWords = [];
  wordElements.forEach((el, i) => {{
    if (el.classList.contains('wrong') && targetWords[i]) {{
      wrongWords.push(targetWords[i]);
    }}
  }});
  if (wrongWords.length > 0) {{
    tipsEl.innerHTML += `<li>🔴 認識されなかった単語: <strong>${{wrongWords.join(', ')}}</strong> — ゆっくりはっきり発音してみよう</li>`;
  }}

  resultEl.classList.add('show');
}}

// Simple Levenshtein distance for fuzzy matching
function levenshtein(a, b) {{
  if (a.length === 0) return b.length;
  if (b.length === 0) return a.length;
  const matrix = [];
  for (let i = 0; i <= b.length; i++) matrix[i] = [i];
  for (let j = 0; j <= a.length; j++) matrix[0][j] = j;
  for (let i = 1; i <= b.length; i++) {{
    for (let j = 1; j <= a.length; j++) {{
      if (b.charAt(i - 1) === a.charAt(j - 1)) {{
        matrix[i][j] = matrix[i - 1][j - 1];
      }} else {{
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }}
    }}
  }}
  return matrix[b.length][a.length];
}}

document.addEventListener('DOMContentLoaded', initPronun);'''


def build_day_html(data: dict) -> str:
    """1日分のHTMLを生成する。"""
    day = data["day"]
    sweet = data["sweet"]
    emoji = data.get("emoji", "🍰")

    # Navigation links
    prev_link = f'<a class="nav-btn" href="day{day-1}.html">← Day {day-1}</a>' if day > 1 else '<span class="nav-btn disabled">← 前の日</span>'
    next_link = f'<a class="nav-btn" href="day{day+1}.html">Day {day+1} →</a>' if day < TOTAL_DAYS else '<span class="nav-btn disabled">次の日 →</span>'

    # Progress dots
    dots = "\n    ".join(
        f'<div class="progress-dot{" active" if i == 0 else ""}" data-section="{i}"></div>'
        for i in range(TOTAL_SECTIONS)
    )

    # Build sections
    sections = "\n\n".join([
        section_recipe(data),
        section_quiz1(data),
        section_review(data),
        section_quiz2(data),
        section_tips(data),
        section_conversation(data),
        section_quiz3(data),
        section_listening(data),
        section_pronunciation(data),
        section_tryit(data),
        section_summary(data),
    ])

    js = build_js(day, sweet)

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{emoji} Day {day}: {h(sweet)} — Cooking English Custom</title>
<link href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500;700&family=Quicksand:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<style>
{CSS}
</style>
</head>
<body>

<div class="header">
  <div class="header-badge">COOKING ENGLISH — CUSTOM EDITION</div>
  <h1>{emoji} Day {day}: {h(sweet)}</h1>
  <p>30日間クッキング英語 — {day}日目</p>
</div>

<div class="progress-bar">
  <div class="progress-dots">
    {dots}
  </div>
  <div class="progress-label">1 / {TOTAL_SECTIONS} セクション</div>
</div>

<div class="main">

{sections}

<div class="day-nav">
  {prev_link}
  <a class="home-btn" href="index.html">🏠 ホーム</a>
  {next_link}
</div>

</div>

<script>
{js}
</script>
</body>
</html>'''


def build_index_html(available_days: list) -> str:
    """index.html（30日分のグリッド一覧）を生成する。"""
    cards = ""
    for day in range(1, TOTAL_DAYS + 1):
        sweet, emoji = MENU[day]
        exists = day in available_days
        if exists:
            cards += f'''    <a href="day{day}.html" class="day-card">
      <div class="day-emoji">{emoji}</div>
      <div class="day-number">Day {day}</div>
      <div class="day-name">{h(sweet)}</div>
    </a>\n'''
        else:
            cards += f'''    <div class="day-card locked">
      <div class="day-emoji">{emoji}</div>
      <div class="day-number">Day {day}</div>
      <div class="day-name">{h(sweet)}</div>
      <div class="day-lock">🔒 準備中</div>
    </div>\n'''

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🍰 Cooking English Custom Edition — Month 1: AUスイーツ</title>
<link href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500;700&family=Quicksand:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root {{
  --primary: #E8792F;
  --navy: #1B3A5C;
  --bg: #FAFAF7;
  --card-bg: #FFFFFF;
  --text: #333333;
  --text-light: #666666;
  --border: #E8E5DF;
  --shadow: 0 2px 12px rgba(27,58,92,0.08);
  --shadow-hover: 0 4px 20px rgba(27,58,92,0.14);
  --radius: 16px;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: 'Noto Sans JP', 'Zen Maru Gothic', sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.8;
  min-height: 100vh;
}}

.header {{
  background: linear-gradient(135deg, var(--navy) 0%, #2A5080 100%);
  color: white;
  padding: 2.5rem 1.5rem 2rem;
  text-align: center;
  position: relative;
  overflow: hidden;
}}
.header::before {{
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(232,121,47,0.15) 0%, transparent 70%);
  border-radius: 50%;
}}
.header-badge {{
  display: inline-block;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  padding: 0.3rem 1rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-family: 'Quicksand', sans-serif;
  font-weight: 600;
  letter-spacing: 0.05em;
  margin-bottom: 0.8rem;
  border: 1px solid rgba(255,255,255,0.2);
}}
.header h1 {{
  font-family: 'Quicksand', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
}}
.header p {{ font-size: 0.9rem; opacity: 0.8; }}
.header .subtitle {{ font-size: 0.8rem; opacity: 0.6; margin-top: 0.3rem; }}

.grid {{
  max-width: 720px;
  margin: 1.5rem auto;
  padding: 0 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 1rem;
}}

.day-card {{
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.2rem 0.8rem;
  text-align: center;
  text-decoration: none;
  color: var(--text);
  box-shadow: var(--shadow);
  transition: all 0.3s;
  cursor: pointer;
  position: relative;
}}
.day-card:hover {{
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
  border-color: var(--primary);
}}
.day-card.locked {{
  opacity: 0.5;
  cursor: default;
}}
.day-card.locked:hover {{
  transform: none;
  box-shadow: var(--shadow);
  border-color: var(--border);
}}
.day-emoji {{ font-size: 2rem; margin-bottom: 0.3rem; }}
.day-number {{
  font-family: 'Quicksand', sans-serif;
  font-weight: 700;
  font-size: 0.75rem;
  color: var(--primary);
  margin-bottom: 0.1rem;
}}
.day-name {{
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--navy);
}}
.day-lock {{
  font-size: 0.65rem;
  color: var(--text-light);
  margin-top: 0.3rem;
}}

.footer {{
  text-align: center;
  padding: 2rem 1rem;
  font-size: 0.75rem;
  color: var(--text-light);
}}

@media (max-width: 480px) {{
  .header h1 {{ font-size: 1.6rem; }}
  .grid {{ grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 0.8rem; }}
}}
</style>
</head>
<body>

<div class="header">
  <div class="header-badge">COOKING ENGLISH — CUSTOM EDITION</div>
  <h1>🍰 Month 1: AUスイーツ</h1>
  <p>30日間クッキング英語</p>
  <div class="subtitle">もものちゃん専用 — A2レベル</div>
</div>

<div class="grid">
{cards}</div>

<div class="footer">
  Cooking English Custom Edition — Made with ❤️
</div>

</body>
</html>'''


def build_day(day: int):
    """1日分のHTMLを生成してdocs/に保存する。"""
    json_path = CONTENT_DIR / f"day{day}.json"
    if not json_path.exists():
        print(f"  Skipping Day {day} (no JSON)")
        return False

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    html = build_day_html(data)
    out_path = DOCS_DIR / f"day{day}.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Built: {out_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="JSON → HTML生成")
    parser.add_argument("--day", type=int, help="特定の日だけ生成")
    parser.add_argument("--all", action="store_true", help="全日分生成")
    args = parser.parse_args()

    if not args.day and not args.all:
        print("Usage: python build_html.py --day 1  (1日分)")
        print("       python build_html.py --all     (全日分)")
        sys.exit(0)

    # Create output directories
    DOCS_DIR.mkdir(exist_ok=True)
    assets_src = BASE_DIR / "assets"
    assets_dst = DOCS_DIR / "assets"

    # Copy assets to docs/
    if assets_src.exists():
        assets_dst.mkdir(exist_ok=True)
        import shutil
        for f in assets_src.iterdir():
            if f.is_file():
                shutil.copy2(f, assets_dst / f.name)
        print(f"  Copied assets to {assets_dst}")

    # Build day pages
    available_days = []
    if args.day:
        days = [args.day]
    else:
        days = list(range(1, TOTAL_DAYS + 1))

    for day in days:
        if build_day(day):
            available_days.append(day)

    # Also scan for any previously built days
    if args.day:
        for d in range(1, TOTAL_DAYS + 1):
            if (CONTENT_DIR / f"day{d}.json").exists():
                available_days.append(d)
        available_days = sorted(set(available_days))

    # Build index
    index_html = build_index_html(available_days)
    index_path = DOCS_DIR / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"  Built: {index_path}")
    print(f"\nDone! {len(available_days)} day(s) built. Open docs/index.html to view.")


if __name__ == "__main__":
    main()
