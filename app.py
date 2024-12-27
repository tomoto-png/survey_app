from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # 安全な秘密鍵を設定
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # セッションの有効期限を30分に設定

# Flask-Sessionの初期化（オプション：より堅牢なセッション管理が必要な場合）
# from flask_session import Session
# Session(app)
# 健康スコアを計算する関数
def calculate_health_score(entry):
    score = 0
    
    exercise_score = {"毎日": 10, "週に3-4回": 7, "週に1-2回": 5, "ほとんどしない": 2}
    score += exercise_score.get(entry['exercise'], 0)
    
    diet_score = {"非常に良い": 10, "良い": 7, "普通": 5, "悪い": 2}
    score += diet_score.get(entry['diet'], 0)
    
    stress_score = {"ほとんどない": 10, "少しある": 7, "普通": 5, "高い": 2}
    score += stress_score.get(entry['stress'], 0)

    sleep_score = {"7時間以上": 10, "5-7時間": 7, "4-6時間": 5, "4時間未満": 2}
    score += sleep_score.get(entry['sleep'], 0)

    eating_out_score = {"ほとんどしない": 10, "週に1回": 7, "週に2-3回": 5, "ほとんど毎日": 2}
    score += eating_out_score.get(entry['eating_out'], 0)
    
    water_intake_score = {'1リットル未満': 2, '1-2リットル': 5, '2-3リットル': 7, '3リットル以上': 10}
    score += water_intake_score.get(entry['water_intake'], 0)
    
    smoking_score = {'なし': 10, '時々': 5, '毎日': 2}
    score += smoking_score.get(entry['smoking'], 0)

    return score

# コメント生成関数
def generate_comments(entry):
    return {
        'eating_out_comment': generate_eating_out_comment(entry['eating_out']),
        'exercise_comment': generate_exercise_comment(entry['exercise']),
        'sleep_comment': generate_sleep_comment(entry['sleep']),
        'water_intake_comment': generate_water_intake_comment(entry['water_intake']),
        'smoking_comment': generate_smoking_comment(entry['smoking']),
    }

def generate_eating_out_comment(eating_out):
    comments = {
        "ほとんどしない": "素晴らしい！外食が少ないです。",
        "週に1回": "バランスの取れた頻度ですね。",
        "週に2-3回": "少し外食が多いかも。",
        "ほとんど毎日": "外食を減らすことを考えましょう。"
    }
    return comments.get(eating_out, "外食頻度に関する情報が不足しています。")

def generate_water_intake_comment(water_intake):
    comments = {
        '1リットル未満': '水分が不足しています。もっと飲みましょう！',
        '1-2リットル': '適量ですが、もう少し増やしても良いかも。',
        '2-3リットル': '水分摂取が理想的です！',
        '3リットル以上': '水分は十分です。体調に合わせて調整を。',
        '不明': '水分摂取量についての情報がありません。'
    }
    return comments.get(water_intake, '情報がありません')

def generate_smoking_comment(smoking):
    comments = {
        'なし': '素晴らしいです！健康的な生活習慣を維持しています。',
        '時々': '喫煙習慣があります。健康のために減らすことを検討してください。',
        '毎日': '喫煙は健康に悪影響を及ぼします。禁煙を考えてみてください。',
        '不明': '喫煙習慣について確認が必要です。'
    }
    return comments.get(smoking, '情報がありません')

def generate_exercise_comment(exercise):
    comments = {
        "毎日": "毎日運動していて素晴らしいです！",
        "週に3-4回": "良いペースで運動しています！",
        "週に1-2回": "少し運動を増やすと良いかも。",
        "ほとんどしない": "もっと運動を心がけましょう。"
    }
    return comments.get(exercise, "運動習慣に関する情報が不足しています。")

def generate_sleep_comment(sleep):
    comments = {
        "7時間以上": "十分な睡眠が取れていますね！",
        "5-7時間": "もう少し睡眠時間を増やしましょう。",
        "4-6時間": "睡眠時間を改善しましょう。",
        "4時間未満": "もっと睡眠を取ることをお勧めします。"
    }
    return comments.get(sleep, "睡眠に関する情報が不足しています。")

def evaluate_health(score):
    if score >= 45:
        return "非常に健康的です"
    elif score >= 35:
        return "健康的です"
    elif score >= 25:
        return "注意が必要です"
    else:
        return "健康に問題があります"

def calculate_bmi(weight, height):
    if height > 0:
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        return round(bmi, 1)
    return 0

def evaluate_bmi(bmi):
    if bmi < 18.5:
        return "低体重"
    elif 18.5 <= bmi < 25:
        return "正常体重"
    elif 25 <= bmi < 30:
        return "過体重"
    else:
        return "肥満"

@app.route('/', methods=['GET', 'POST'])
def health_survey():
    if request.method == 'POST':
        # フォームデータを取得
        survey_entry = {
            "name": request.form.get('name', 'No Name'),
            "age": int(request.form.get('age', 0)),
            "gender": request.form.get('gender', '不明'),
            "height": float(request.form.get('height', 0.0)),
            "weight": float(request.form.get('weight', 0.0)),
            "exercise": request.form.get('exercise', '不明'),
            "sleep": request.form.get('sleep', '不明'),
            "diet": request.form.get('diet', '不明'),
            "stress": request.form.get('stress', '不明'),
            "eating_out": request.form.get('eating_out', '不明'),
            "water_intake": request.form.get('water_intake', '不明'),
            "smoking": request.form.get('smoking', '不明')
        }

        # スコアとBMIの計算
        health_score = calculate_health_score(survey_entry)
        health_evaluation = evaluate_health(health_score)
        bmi = calculate_bmi(survey_entry['weight'], survey_entry['height'])
        bmi_evaluation = evaluate_bmi(bmi)

        # 計算結果をsurvey_entryに追加
        survey_entry['score'] = health_score
        survey_entry['evaluation'] = health_evaluation
        survey_entry['bmi'] = bmi
        survey_entry['bmi_evaluation'] = bmi_evaluation

        if 'survey_data' not in session:
            session['survey_data'] = []
        session['survey_data'].append(survey_entry)
        session.modified = True  # セッションの変更を確実に保存
        
        print("Saved to session:", session['survey_data'])  # デバッグ用
        
        return redirect(url_for('thank_you'))

    return render_template('health_survey.html')

@app.route('/thank_you')
def thank_you():
    # セッションから最新のデータを取得
    survey_data = session.get('survey_data', [])
    print("Retrieved from session:", survey_data)  # デバッグ用

    if not survey_data:
        return "No survey data found in session."

    # 最新のエントリを取得
    latest_entry = survey_data[-1]

    # データをテンプレートに渡す
    name = latest_entry.get('name', 'No Name')
    score = latest_entry.get('score', 0)
    evaluation = latest_entry.get('evaluation', '評価なし')
    bmi = latest_entry.get('bmi', 0)
    bmi_evaluation = latest_entry.get('bmi_evaluation', '評価なし')

    # コメント生成
    comments = generate_comments(latest_entry)

    print(f"Passing to template - Score: {score}, BMI: {bmi}, Evaluation: {evaluation}")  # デバッグ用

    return render_template('thank_you.html', name=name, score=score, evaluation=evaluation,
                           bmi=bmi, bmi_evaluation=bmi_evaluation, **comments)

@app.route('/analysis')
def analysis():
    survey_data = session.get('survey_data', [])
    print("Retrieved from session:", survey_data)  # デバッグ用
    return render_template('analysis.html', survey_data=survey_data)

@app.route('/set_session')
def set_session():
    session['test'] = 'This is a test'
    return 'Session data set'

@app.route('/get_session')
def get_session():
    test_data = session.get('test', 'No data found')
    return f'Session data: {test_data}'
@app.route('/debug_session')
def debug_session():
    session_data = session.get('survey_data', 'No data found')
    return f'Session data: {session_data}'

if __name__ == '__main__':
    app.run(debug=True)
