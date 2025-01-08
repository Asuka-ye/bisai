# -*- coding: utf-8 -*-
print("win")

import os
from volcenginesdkarkruntime import Ark
# 从环境变量中读取您的方舟API Key
client = Ark(api_key=os.environ.get("ARK_API_KEY_2"))
long="ep-20241226003315-lc9tw"

normal="ep-20241220225452-pj9hv"
char="ep-20241220225419-f7czx"

# stream = client.chat.completions.create(
#     # 替换为您的推理接入点ID，创建方法见 
#     model="<YOUR_ENDPOINT_ID>",
#     messages = [
#         {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
#         {"role": "user", "content": "常见的十字花科植物有哪些？"},
#     ],
#     stream=True
# )
# for chunk in stream:
#     if not chunk.choices:
#         continue
#     print(chunk.choices[0].delta.content, end="")

strs=["正在生成角色背景故事","正在生成角色时间线","正在生成证据","正在汇总证据字典"]
def llm_background_1(topic, location, relationship,nums):
    messages_background=[
        {"role": "system", "content": f"你将为一个文字驱动的剧本杀游戏中的每一个角色生成角色设定，他们各自都有自己独特的角色背景（保证这个独特的背景可以使角色使用一些特殊的手段）,所有角色跟死者都有纠葛,每个人都有杀死死者的动机，没有人直接目击到凶手的作案行为。只输出角色的角色设定"},
        {"role": "user", "content": f"{topic}主题的剧本杀总共有{nums}个游戏角色，第一个角色是凶手，地点：{location}，角色之间的关系：{relationship}"},
    ]
    result1n = client.chat.completions.create(
    
        model=long,
        messages=messages_background,
        stream=True
    )
    
    for chunk in result1n:
        if not chunk.choices:
            continue
        yield chunk.choices[0].delta.content
    # print(result1n.choices[0].message.content)

def llm_background_2(result1n):
    messages_add =[
        {"role": "system", "content": "丰富下面角色设定中背景故事的部分，如果角色没有自己的名字添加一个名字，然后输出最终版的角色设定"},
        {"role": "user", "content": f"{result1n}"},
    ]

    result2n = client.chat.completions.create(
    
        model=long,
        messages=messages_add ,
        stream=True
    )
    for chunk in result2n:
        if not chunk.choices:
            continue
        yield chunk.choices[0].delta.content
def to_role_list(result):
    
    messages_list =[
        {"role": "system", "content": " 你将提取用户输入的内容中不同角色的名字，输出一个字符串形式的python列表，只输出列表的内容，不要输出其他任何内容。"},
        {"role": "user", "content": f"{result}"},
    ]
    list_response = client.chat.completions.create(
  
    model=normal,
    messages=messages_list ,
)
    return list_response.choices[0].message.content
    # print(result2n.choices[0].message.content)

def get_introduct(i,back):
    messages_add =[
        {"role": "system", "content": f"你将根据下面的内容为角色{i}生成一个针对于这个角色外貌特征的介绍，只输出介绍，不要输出其他任何内容。"},
        {"role": "user", "content": f"{back}"},
    ]

    result = client.chat.completions.create(
    
        model=long,
        messages=messages_add ,
    )
    return result.choices[0].message.content


def timeline_1(back,location):
    
    messages_exp11n1 =[
            {"role": "system", "content": "你将为剧本杀游戏中的每一个角色生成时间线，时间线的输出就到大家发现死者的尸体这里截止"},
            {"role": "user", "content": f"""这个剧本杀时间线的跨度应为一天或两天，地点是在一个{location}。结合下面角色的背景故事和技能，为这个剧本杀的角色先生成一段从剧情开始到最后一次死者活着出现在所有人的视野
                    这段时间片段的有具体时刻的时间线。所有角色在这个时间片段各自都有一些其他人没有办法作证的不完全重合的自由时间，他们在自由
                    时间为他们自己对死者即将进行的杀害行为做准备，然后生成最后一次死者活着出现在所有人的视野到大家发现死者的尸体这一大段时间
                    内有具体时刻的时间线。所有角色在这个时间片段各自都有且只有一段独处的自由时间，凶手在自由时间进行致死者死亡的作案行为，作案方式的关键点隐晦地蕴含在凶手自己与其他角色的背景故事中，而且其他角色没有掌握任何有关凶手的作案线索。
                    其他角色在自由时间进行嫌疑行为或者无效的作案行为，作为红鲱鱼线索。角色的背景故事和手段{back}"""},
            {"role": "assistant", "content": ""}
        ]

    stream = client.chat.completions.create(
        # 替换为您的推理接入点ID，创建方法见 
        model=long,
        messages=messages_exp11n1,
        stream=True
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        messages_exp11n1[-1]["content"] +=chunk.choices[0].delta.content
        yield chunk.choices[0].delta.content
        while chunk.choices[0].finish_reason == "length":
            print("*****************************************")
            stream2 = client.chat.completions.create(
                model=long,
                messages=messages_exp11n1,
                stream=True
            )
            for chunk2 in stream2:
                if not chunk2.choices:
                    continue
                messages_exp11n1[-1]["content"] +=chunk2.choices[0].delta.content
                yield chunk2.choices[0].delta.content
def div_timeline(role,timeline):
    messages_role =[
        {"role": "system", "content": f"从下面的剧本杀时间线中分离出属于角色{role}视角的时间线，如果括号内的注解不是这个角色视角应该知道的内容，而是上帝视角才知道的内容，就不要输出括号内的部分,输出格式为角色名，时间线[]。人称改为第二人称，[]内的一段时间线结束后要换行"},
        {"role": "user", "content": f"""剧本杀时间线：{timeline}"""},
    ]
    fir_timeline=client.chat.completions.create(
        model=long,
        messages=messages_role,
    ).choices[0].message.content
    print(fir_timeline)
    messages_timeline_check =[
        {"role": "system", "content": f"检查下面剧本杀角色的时间线的内容是否有属于上帝视角才知道的部分，如果有将这一部分去除，其他部分保留不变。输出最终的时间线内容"},
        {"role": "user", "content": f"""剧本杀时间线：{fir_timeline}"""},
    ]
    final_timeline=client.chat.completions.create(
        model=long,
        messages=messages_timeline_check,
    ).choices[0].message.content
    return final_timeline
def div_back(role,back):
    messages_add =[
        {"role": "system", "content": f"从下面的剧本杀背景故事中分离出属于角色{role}的背景故事，人称改为第二人称，只输出分离出的背景故事"},
        {"role": "user", "content": f"{back}"},
    ]

    result = client.chat.completions.create(
    
        model=long,
        messages=messages_add ,
    )
    return result.choices[0].message.content

def genrate_clues1(background,timeline,location):
    
    messages_clue_action=[
            {"role": "system", "content": "你将根据下面剧本杀的背景故事与时间线生成有关（凶器、非凶手角色嫌疑行为留下的痕迹、表明死者死亡的模糊时间）的实物证据与对证据的描述（只是对证据特征细节的描述，不是对证据的分析）。结果只输出证据与描述。"},
            {"role": "user", "content": f"""各角色背景故事：{background}，地点：{location}，    各角色时间线：{timeline}"""},
        ]

    clues_action = client.chat.completions.create(
    
        model=long,
        messages=messages_clue_action,
    )
    return clues_action.choices[0].message.content
def genrate_clues2(background,timeline,location):
    messages_clue_movtion=[
            {"role": "system", "content": "你将根据下面剧本杀的背景故事生成一系列表明每个非凶手角色杀人的动机的实物证据与与对证据特征的描述（只是对证据特征细节的描述，不是对证据的分析）。结果只输出证据与描述。"},
            {"role": "user", "content": f"""各角色背景故事：{background}，地点：{location}"""},
        ]

    clues_movtion = client.chat.completions.create(
    
        model=long,
        messages=messages_clue_movtion,
    )
    return clues_movtion .choices[0].message.content
def genrate_clues3(background,timeline,location,clues1):
    messages_clue_killerm=[
            {"role": "system", "content": "你将根据下面剧本杀的背景故事生成属于凶手角色空间的表明凶手角色杀人的动机的实物证据与与对证据特征的描述（只是对证据特征细节的描述，不是对证据的分析），生成的证据及描述要模糊任何与凶器有关的内容。结果只输出证据与描述。"},
            {"role": "user", "content": f"""各角色背景故事：{background}，地点：{location}，证据：{clues1}"""},
        ]

    clues_killerm = client.chat.completions.create(
    
        model=long,
        messages=messages_clue_killerm,
    )
    return clues_killerm.choices[0].message.content
def final_clues(background,timeline,location,clues1,clues2,clues3):

    messages_clues_rooms=[
            {"role": "system", "content": "你将根据下面剧本杀的背景故事与时间线，为每个证据匹配找到它们的地方（需要是一个具体的地点，数量不能超过9个）。输出格式为：地方A：证据A名字 描述：xx  证据B名字 描述：xxx"},
            {"role": "user", "content": f"""各角色背景故事：{background}，地点：{location}。各角色时间线：{timeline}" 。证据：{clues1} {clues2}{clues3}"""},
        ]

    clues_rooms = client.chat.completions.create(
    
        model=long,
        messages=messages_clues_rooms,
    )
    return clues_rooms.choices[0].message.content

def clues_dict(clues):
    evidence_dict={
"医生的房间": {
    '一大堆医疗记录': {
        'description': "这些文件显示，自2002年枪击案以来，这名医生的家人一直患有严重的慢性疾病。",
        'found': False},

    'prohibited_names': ['']
},
"旅行者的房间": {
    '一张照片': {
        'description': "这张照片是2002年的，保存得相当完好，但是有一个成年男人的头像被划掉了，他旁边站了一个小男孩",
        'found': False},
    '一把自制的手枪': {'description': '它看起来有点旧了。', 'found': False},

    'prohibited_names': ['']
},
"厨房": {
    '2002年和2010年枪击案的新闻报道': {
        'description': " 保存得很完好",
        'found': False},

    'prohibited_names': ['']
},
'公共卫生间': {
    '一些碎掉的温度计': {
        'description': '这些温度计像是水银温度计的样式。', 'found': False},
    'prohibited_names': ['']
},
'大厅': {
    "在死者尸体上发现的线索": {
        'description': "一张记录了自2010年以来的多起枪击事件的相册。",
        'found': False},
    '一个空的毒药瓶子': {
        'description': '这种毒药很罕见，有杏仁的气味，能在30分钟内迅速致死。好像是某种氰化物。',
        'found': False},
    '一杯喝了一半的咖啡': {'description': '它好像有淡淡的杏仁味。', 'found': False},
    '一个小医疗箱': {'description': '温度计不见了。', 'found': False},
    'prohibited_names': []
}
}
    clues_jsonl=[
        {"role": "system", "content": "你将把下面剧本杀的地点与证据。整理成例子中的pyhton字典格式"},
        {"role": "user", "content": f"""地点与证据：{clues}    例子：{evidence_dict}"""},
    ]
    clues = client.chat.completions.create(
        model=normal,
        messages=clues_jsonl,
        stream=False
    )
#加一个判断单元，如果不合法重新循环
    return clues.choices[0].message.content


from typing import List, Dict

def ai_talk(role, killer, tp, clues, history):
    if not clues:
        clues = "还没有任何证据被找到"

    if role == killer:
        system_content = {"role": "system", "content": f"你将在一个纯文字驱动的剧本杀中，扮演凶手的角色，不要暴露你行凶的事实,你只需要输出你的角色的会说的话，如果你之前从未发言，你会叙述你在案发前的时间线。你是{role}.下面是你的过去和时间线{tp}，下面是现在已经找到的证据{clues}"}
    else:
        system_content = {"role": "system", "content": f"你将在一个纯文字驱动的剧本杀中，扮演嫌疑人的角色，不要轻易泄露你的嫌疑行为并找到真正的凶手,你只需要输出你的角色的会说的话，如果你之前从未发言，你会叙述你在案发前的时间线。你是{role}.下面是你的过去和时间线{tp}，下面是现在已经找到的证据{clues}"}


    def modify_and_insert_talk(all_talk: List[Dict], target_role_value: str, system_content: Dict) -> List[Dict]:
        modified_talk = [system_content]  #  首先插入 system_content
        for item in all_talk:
            if item["role"] == target_role_value:
                modified_item = {"role": "assistant", "content": item["content"]}
            else:
                modified_item = {"role": "user", "content": item["content"]}
            modified_talk.append(modified_item)
        return modified_talk

    message = modify_and_insert_talk(history, role, system_content)  # 注意这里传入的是 system_content
    print(message)
# 打印清理后的结果
    stream3 = client.chat.completions.create(
    # 替换为您的推理接入点ID，创建方法见 
    model=char,
    messages = message,
    stream=True
)
    for chunk in stream3:
        if not chunk.choices:
            continue
        yield chunk.choices[0].delta.content   
