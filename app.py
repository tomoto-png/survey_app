from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
import os

app = Flask(__name__)

# アプリ設定
app.config['SECRET_KEY'] = os.urandom(24)  # セキュアな秘密鍵
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# 健康スコアの計算
def calculate_health_score(entry):
    scores = {
        "exercise": {"毎日": 10, "週に3-4回": 7, "週に1-2回": 5, "ほとんどしない": 2},
        "diet": {"非常に良い": 10, "良い": 7, "普通": 5, "悪い": 2},
        "stress": {"ほとんどない": 10, "少しある": 7, "普通": 5, "高い": 2},
        "sleep": {"7時間以上": 10, "5-7時間": 7, "4-6時間": 5, "4時間未満": 2},
        "eating_out": {"ほとんどしない": 10, "週に1回": 7, "週に2-3回": 5, "ほとんど毎日": 2},
        "water_intake": {'1リットル未満': 2, '1-2リットル': 5, '2-3リットル': 7, '3リットル以上': 10},
        "smoking": {'なし': 10, '時々': 5, '毎日': 2},
    }
    return sum(scores[category].get(entry.get(category, '不明'), 0) for category in scores)

# コメント生成
def generate_comments(entry):
    categories = {
        "eating_out": {"ほとんどしない": "素晴らしい！外食が少ないです。",
                       "週に1回": "バランスの取れた頻度ですね。",
                       "週に2-3回": "少し外食が多いかも。",
                       "ほとんど毎日": "外食を減らすことを考えましょう。"},
        "water_intake": {'1リットル未満': '水分が不足しています。もっと飲みましょう！',
                         '1-2リットル': '適量ですが、もう少し増やしても良いかも。',
                         '2-3リットル': '水分摂取が理想的です！',
                         '3リットル以上': '水分は十分です。体調に合わせて調整を。'},
        "smoking": {'なし': '素晴らしいです！健康的な生活習慣を維持しています。',
                    '時々': '喫煙習慣があります。健康のために減らすことを検討してください。',
                    '毎日': '喫煙は健康に悪影響を及ぼします。禁煙を考えてみてください。'},
        "exercise": {"毎日": "毎日運動していて素晴らしいです！",
                     "週に3-4回": "良いペースで運動しています！",
                     "週に1-2回": "少し運動を増やすと良いかも。",
                     "ほとんどしない": "もっと運動を心がけましょう。"},
        "sleep": {"7時間以上": "十分な睡眠が取れていますね！",
                  "5-7時間": "もう少し睡眠時間を増やしましょう。",
                  "4-6時間": "睡眠時間を改善しましょう。",
                  "4時間未満": "もっと睡眠を取ることをお勧めします。"}
    }
    return {key: categories[key].get(entry.get(key, '不明'), "情報が不足しています。") for key in categories}

# 健康評価
def evaluate_health(score):
    if score >= 45:
        return "非常に健康的です"
    elif score >= 35:
        return "健康的です"
    elif score >= 25:
        return "注意が必要です"
    return "健康に問題があります"

# BMI計算
def calculate_bmi(weight, height):
    return round(weight / (height / 100) ** 2, 1) if height > 0 else 0

# BMI評価
def evaluate_bmi(bmi):
    if bmi < 18.5:
        return "低体重"
    elif bmi < 25:
        return "正常体重"
    elif bmi < 30:
        return "過体重"
    return "肥満"

@app.route('/', methods=['GET', 'POST'])
def health_survey():
    if request.method == 'POST':
        # フォームデータの取得
        entry = {key: request.form.get(key, '不明') for key in [
            'name', 'age', 'gender', 'height', 'weight',
            'exercise', 'diet', 'stress', 'sleep',
            'eating_out', 'water_intake', 'smoking'
        ]}
        entry['height'] = float(entry['height'])
        entry['weight'] = float(entry['weight'])

        # スコア計算と評価
        entry['score'] = calculate_health_score(entry)
        entry['evaluation'] = evaluate_health(entry['score'])
        entry['bmi'] = calculate_bmi(entry['weight'], entry['height'])
        entry['bmi_evaluation'] = evaluate_bmi(entry['bmi'])

        # セッションに保存
        if 'survey_data' not in session:
            session['survey_data'] = []
        session['survey_data'].append(entry)
        session.modified = True
        
        return redirect(url_for('comments'))

    return render_template('health_survey.html')

@app.route('/comments')
def comments():
    # セッションから最新データを取得
    survey_data = session.get('survey_data', [])
    if not survey_data:
        return "セッションデータがありません。"

    latest_entry = survey_data[-1]
    comments = generate_comments(latest_entry)

    # キーが重複しないようにデータを整理
    context = {**latest_entry}
    for key, value in comments.items():
        if key not in context:  # 重複キーを避ける
            context[key] = value
        else:
            context[f"{key}_comment"] = value

    # デバッグ用に表示
    print("コンテキスト:", context)

    return render_template('comments.html', **context)

@app.route('/result')
def result():
    survey_data = session.get('survey_data', [])
    return render_template('result.html', survey_data=survey_data)

if __name__ == '__main__':
    app.run(debug=True)