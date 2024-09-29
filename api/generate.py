import json
import subprocess
from flask import Flask, request

app = Flask(__name__)

# 设置角色性格和对话目的，注意：不要修改"角色A""角色B"和"名称"这几个关键字
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

def call_ollama(prompt):
    result = subprocess.run(
        ["ollama", "run", "llama3.1:8b", prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8',
        errors='ignore'
    )

    if result.returncode != 0:
        return "发生错误"
    
    output = result.stdout.strip()
    if "failed to get console mode" in output:
        return output.split("\n")[-1]  # 只返回有效输出

    return output

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    
    # 获取用户传入的自定义角色名称和对话
    role_a_name = data.get('roleA_name', roles['角色A']['名称'])
    role_b_name = data.get('roleB_name', roles['角色B']['名称'])
    first_sentence = data.get('first_sentence', "")
    
    roles['角色A']['名称'] = role_a_name
    roles['角色B']['名称'] = role_b_name
    
    dialogue = []
    if first_sentence:
        dialogue = [{"role": role_a_name, "content": first_sentence}]
    
    cnt = 0  # 对话轮次
    
    system_prompt_a = (
        f"系统提示: 你现在扮演的是{roles['角色A']['名称']}。你的每一句话都要符合人设，且专注于自己的目的，现在请继续向{roles['角色B']['名称']}表达你的观点，不用在开头打出自己的名字。"
    )
    system_prompt_b = (
        f"系统提示: 你现在扮演的是{roles['角色B']['名称']}。你的每一句话都要符合人设，且专注于自己的目的，现在请继续向{roles['角色A']['名称']}表达你的观点，不用在开头打出自己的名字。"
    )

    context_a = f"\n\n{system_prompt_a}" + "\n\n" + str(dialogue) + f"\n\n{roles['角色A']['名称']}:"
    response_a = call_ollama(context_a)
    dialogue.append({"role": roles['角色A']['名称'], "content": response_a})
    
    context_b = f"\n\n{system_prompt_b}" + "\n\n" + str(dialogue) + f"\n\n{roles['角色B']['名称']}:"
    response_b = call_ollama(context_b)
    dialogue.append({"role": roles['角色B']['名称'], "content": response_b})

    return json.dumps(dialogue)

if __name__ == "__main__":
    app.run()
