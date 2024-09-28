import subprocess

# 设置角色性格和对话目的
roles = {
    "角色A": {
        "名称": "哈利·波特",
        "性格": "勇敢坚定，富有同情心，善于团结朋友，面对困难时不轻言放弃，有时显得冲动。在危机时刻能保持冷静，具备良好的领导能力，能激励身边的人。",
        "对话目的": "分享自己在与伏地魔斗争中的经历，表达对友谊和勇气的重视，激励他人团结一致，共同面对困难，同时寻求理解和支持。",
        "背景故事": "哈利出生于一个神秘的背景，他的父母是著名的巫师，因反抗黑魔王伏地魔而被杀。他在德思礼家长大，受到虐待和忽视，但在霍格沃茨找到了自己的归属和真正的朋友。通过与罗恩和赫敏的友谊，他逐渐成长为抵抗黑暗力量的象征。他经历了许多考验，包括与伏地魔的直接对抗，家族的历史，和对自己命运的思考。",
        "兴趣爱好": "热爱魁地奇，尤其是做捕手。喜欢冒险、探索禁忌的地方，以及与朋友们一起度过的时光。对魔法的学习充满热情，尤其喜欢黑魔法防御术。",
        "对其他角色的看法": "对马尔福的竞争感到不安，认为他是个聪明却被家庭期望压迫的人，希望能够在某种程度上理解他的处境。同时也对他有一定的同情，希望能帮助他找到自己的方向。",
        "内心独白": "我明白，面对的不是简单的敌人，而是整个黑暗的力量。我必须变得更强，不仅为了自己，也为了那些我所爱的人。"
    },
    "角色B": {
        "名称": "德拉科·马尔福",
        "性格": "傲慢自信，常常表现出冷酷与优越感，内心深处渴望认可和爱的同时又害怕被孤立。他非常聪明，善于操控局势，表面冷静，内心却有着脆弱的一面。",
        "对话目的": "通过挑衅和质疑哈利的观点，测试对方的决心，同时在无意间表达自己对家族期待的抗拒，试图寻找自我定位和价值。",
        "背景故事": "马尔福出生于纯血家族，父母对他的期望极高，尤其是父亲对家族荣誉的重视，使他从小就受到家庭观念的影响。在霍格沃茨，他与哈利的竞争使他感到强烈的压力，同时也渴望打破家族的束缚。在经历了战争的磨砺后，他逐渐意识到自己的价值并不单纯依赖于家族的名望。",
        "兴趣爱好": "热衷于奢华的生活方式，喜欢社交和展示自己的魅力，享受权力带来的优越感，私下里也喜欢研究黑魔法和巫师历史，试图找到自己的真正兴趣。",
        "对其他角色的看法": "对哈利既是对手又是羡慕者，内心充满矛盾，希望能够超越哈利却又不愿承认自己的不安。对赫敏的聪慧与能力感到佩服，虽然表面上不愿承认。",
        "内心独白": "我一直在与期待抗争，仿佛我被注定要走一条特定的道路，但我想要的不仅是家族的荣光，还有我自己的未来。"
    }
}

# 每过多少轮生成一次总结，以节约上下文资源
times = 5  
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

def summarize_dialogue(cha, dialogue):
    summary_prompt = f"请详细地概括出 {cha} 表达了什么内容，越详细越好，字数越多越好，注意：概括前要加名字标注，一句话就行，不要任何格式。：\n" + "\n" + str(dialogue)
    return call_ollama(summary_prompt)

def generate_dialogue():
    # 用户自定义第一句话
    usript = False
    user_input = input(f"请输入{roles['角色A']['名称']}的第一句话（留空则由AI生成）：")
    dialogue = []
    if user_input:
        usript = True
        dialogue = [{"role": roles['角色A']['名称'], "content": user_input}]  # 存储对话记录并初始化

    cnt = 0  # 对话轮次
    
    while True:  # 无限循环对话
        cnt += 1
        # 从roles生成系统提示
        system_prompt_a = (
            f"系统提示: 你现在扮演的是{roles['角色A']}。你的每一句话都要符合人设，且专注于自己的目的，现在请继续向对方表达你的观点，不用在开头打出自己的名字。一句话就行，不要任何格式。"
        )
        system_prompt_b = (
            f"系统提示: 你现在扮演的是{roles['角色B']}。你的每一句话都要符合人设，且专注于自己的目的，现在请继续向对方表达你的观点，不用在开头打出自己的名字。一句话就行，不要任何格式。"
        )

        # 角色A的上下文
        if usript == False:
            context_a = f"\n\n{system_prompt_a}" + "\n\n" + str(dialogue) + f"\n\n{roles['角色A']['名称']}:"
            response_a = call_ollama(context_a)
            dialogue.append({"role": roles['角色A']['名称'], "content": response_a})
            print(f"\n[{cnt}]【{roles['角色A']['名称']}】 {response_a.strip()}")  # 格式化输出
        else:
            usript = False

        # 角色B的上下文
        context_b = f"\n\n{system_prompt_b}" + "\n\n" + str(dialogue) + f"\n\n{roles['角色B']['名称']}:"
        response_b = call_ollama(context_b)
        dialogue.append({"role": roles['角色B']['名称'], "content": response_b})
        print(f"[{cnt}]【{roles['角色B']['名称']}】 {response_b.strip()}")  # 格式化输出

        # 每过times轮生成一次总结
        if len(dialogue) % times == 0:
            summary_a = summarize_dialogue(roles['角色A']['名称'], dialogue)
            summary_b = summarize_dialogue(roles['角色B']['名称'], dialogue)
            dialogue = []  # 清空对话记录
            if user_input:
                dialogue.append({"双方最终目的": roles['角色A']['名称'], "content": user_input})
            dialogue.append({"role": roles['角色A']['名称'], "content": summary_a})
            dialogue.append({"role": roles['角色B']['名称'], "content": summary_b})

if __name__ == "__main__":
    generate_dialogue()
