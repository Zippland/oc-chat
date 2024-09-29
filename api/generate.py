import json
import openai
import os
from flask import Flask, request

app = Flask(__name__)

# 从环境变量中读取 OpenAI API 密钥
openai.api_key = os.getenv('OPENAI_API_KEY')

# 设置角色性格和对话目的
roles = {
    "角色A": {
        "名称": "哈利·波特",
        "性格": "勇敢坚定，富有同情心，善于团结朋友，面对困难时不轻言放弃，有时显得冲动。在危机时刻能保持冷静，具备良好的领导能力，能激励身边的人。",
        "对话目的": "分享自己在与伏地魔斗争中的经历，表达对友谊和勇气的重视，激励他人团结一致，共同面对困难，同时寻求理解和支持。"
    },
    "角色B": {
        "名称": "德拉科·马尔福",
        "性格": "傲慢自信，常常表现出冷酷与优越感，内心深处渴望认可和爱的同时又害怕被孤立。他非常聪明，善于操控局势，表面冷静，内心却有着脆弱的一面。",
        "对话目的": "通过挑衅和质疑哈利的观点，测试对方的决心，同时在无意间表达自己对家族期待的抗拒，试图寻找自我定位和价值。"
    }
}

def call_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"发生错误: {str(e)}"

def summarize_dialogue(cha, dialogue):
    summary_prompt = f"请详细地概括出 {cha} 表达了什么内容，越详细越好，字数越多越好，注意：概括前要加名字标注，一句话就行，不要任何格式。：\n" + "\n" + str(dialogue)
    return call_gpt(summary_prompt)

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    
    # 获取用户传入的自定义角色名称和对话
    role_a_name = data.get('roleA_name', roles['角色A']['名称'])
    role_b_name = data.get('roleB_name', roles['角色B']['名称'])
    first_sentence = data.get('first_sentence', "")
    dialogue = data.get('dialogue', [])
    turn_count = len(dialogue)  # 已进行的对话轮次
    
    roles['角色A']['名称'] = role_a_name
    roles['角色B']['名称'] = role_b_name
    
    if first_sentence:
        dialogue.append({"role": role_a_name, "content": first_sentence})
    
    system_prompt_a = (
        f"系统提示: 你现在扮演的是{roles['角色A']}。你的每一句话都要符合人设，且专注于自己的目的，现在请继续向{roles['角色B']['名称']}表达你的观点，不用在开头打出自己的名字。一句话就行，不要任何格式。"
    )
    system_prompt_b = (
        f"系统提示: 你现在扮演的是{roles['角色B']}。你的每一句话都要符合人设，且专注于自己的目的，现在请继续向{roles['角色A']['名称']}表达你的观点，不用在开头打出自己的名字。一句话就行，不要任何格式。"
    )

    # 生成角色A的回应，只基于最新的一句话
    response_a = call_gpt(f"{system_prompt_a}\n\n{role_a_name}: {first_sentence}" if first_sentence else system_prompt_a)
    dialogue.append({"role": roles['角色A']['名称'], "content": response_a})
    
    # 生成角色B的回应，只基于角色A的最新回应
    response_b = call_gpt(f"{system_prompt_b}\n\n{roles['角色A']['名称']}: {response_a}\n{roles['角色B']['名称']}:")
    dialogue.append({"role": roles['角色B']['名称'], "content": response_b})

    # 每10轮生成总结并清除历史
    if len(dialogue) >= 20:
        summary = summarize_dialogue(roles['角色A']['名称'],dialogue) + "\n" + summarize_dialogue(roles['角色B']['名称'],dialogue)
        dialogue = [{"role": "系统总结", "content": summary}]  # 清空对话历史，只保留总结

    return json.dumps(dialogue)

if __name__ == "__main__":
    app.run()
