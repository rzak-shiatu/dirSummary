import subprocess
import os
from openai import OpenAI

# 環境変数からAPIキーを取得
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# --- 入力 ---
print("=== 解析したいフォルダのパスを入力してください ===")
print("入力例:")
print("  C:\\Users\\YourName\\Documents")
print("  C:\\pythonProjects\\test-keiba")
print("  \\\\ServerName\\SharedFolder  (ネットワークドライブの場合)")
print("※ 何も入力せずにEnterでカレントディレクトリを解析します")
print("============================================")

folder_path = input("フォルダパス: ").strip()
if not folder_path:
    folder_path = os.getcwd()
    print(f"\n入力が空なので、カレントディレクトリを解析します: {folder_path}")

# --- dir /s 実行（サブフォルダ含む全出力） ---
result = subprocess.run(
    ["cmd", "/c", f"dir \"{folder_path}\" /s"], 
    capture_output=True, text=True, shell=True
)
dir_output = result.stdout

# --- 出力を行ごとに分割 ---
lines = dir_output.splitlines()
block_size = 300  # 1ブロックあたりの行数（調整可能）
blocks = [lines[i:i+block_size] for i in range(0, len(lines), block_size)]

summaries = []

# --- 各分割ブロックを解析 ---
for idx, block in enumerate(blocks, start=1):
    block_text = "\n".join(block)
    prompt = f"""
以下はフォルダ {folder_path} の一部（分割ブロック {idx}/{len(blocks)}）のdir出力です。
ファイルやフォルダを整理して、この部分の特徴を文章で要約してください。
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはフォルダ構成を解析して用途を推測するアシスタントです。"},
            {"role": "user", "content": prompt + block_text}
        ]
    )
    summary = response.choices[0].message.content
    print(f"\n=== 分割ブロック {idx}/{len(blocks)} の要約 ===\n{summary}\n")
    summaries.append(summary)

# --- 最後に全体を統合要約 ---
final_prompt = f"""
以下はフォルダ {folder_path} を分割ブロックごとに解析した要約結果です。
これらを踏まえて、このフォルダ全体が何のために使われているかを文章でまとめてください。

{chr(10).join(summaries)}
"""

final_response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "あなたはフォルダ全体の構成を要約するアシスタントです。"},
        {"role": "user", "content": final_prompt}
    ]
)

print("\n=== フォルダ全体の最終要約 ===\n")
print(final_response.choices[0].message.content)
