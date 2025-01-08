import random
import ast
import gradio as gr
import time
from collections import deque
import json
import llm
user_initialized = False
topic_validated = False
count=0
evidence_dict={}
initial_update_list = [gr.update(label="", visible=False) for _ in range(9)]
Toplayer=''
Tocreater=''
human_number=0
all_number=0
role_list=["1"]
ai_list=[]
role_talk=""
human_talk_list =deque([])
first_talk=0
role_list_copy=[]
all_talk= []

timeline_t=0
fir_clue=0
se_clue=0
clues_found=""

role_list_tANDp=[]
role_list_introduct=[]

# {"role": "assistant", "content": ""}
# {"role": "user", "content": prompt}
# {"role": "system", "content": "You are a friendly chatbot"}


def which_ai_say():
    return random.choice(ai_list)

def human_talk(msg,role_state):

    global role_talk
    global all_talk
    role_state=role_state

    all_talk.append({"role": role_state, "content": msg})
    human_talk_list.popleft()
    if human_talk_list:
        role_talk = human_talk_list[0]
        return 0
    #i need < len(human_talk_list)
    while(not human_talk_list and ai_list and not clue_mark ):
        role_talk=which_ai_say()
        tANDp=role_list_tANDp[role_list.index(role_talk)]
        print(all_talk)
        
        killer=role_list[0]
        begin=0
        for word in llm.ai_talk(role_talk,killer,tANDp,clues_found,all_talk):
            if not begin:
                all_talk.append({"role": role_talk, "content": f""})
                begin=begin+1
            all_talk[-1]["content"] = all_talk[-1]["content"]+word

        if  human_talk_list:
            role_talk=human_talk_list[0]
            return 0
        #bot
clue_finish=0
def user_assistant(json_list, role_state,max_lines=20):
    role_state=role_state
    try:
        json_list = json_list.replace("'", '"')
        data = json.loads(json_list)
        if not isinstance(data, list):
            return "Error: Input must be a JSON list of objects."

        aligned_text = ""
        # 添加一个外层的 div，作为大的边框
        aligned_text += f"<div style='border: 2px solid #808080; padding: 10px; border-radius: 10px; margin: 10px;'>"  # 灰色边框
        # 包裹在一个带有固定高度和 overflow 的 div 中
        aligned_text += f"<div style='max-height: {max_lines * 30}px; overflow-y: auto;'>"
        for i, item in enumerate(data):
            if not isinstance(item, dict) or "role" not in item or "content" not in item:
                return "Error: Each item must be an object with 'role' and 'content' fields."
            role = item["role"]
            content = item["content"]
            background_color = "#FFFFFF" if role == role_state else "#EEEEEE"  # A 右，其他左

            if role == role_state:  # role A靠右
                div_style = f"background-color: {background_color}; padding: 5px; border: 1px solid #FFCC99; border-radius: 5px; margin-bottom: 5px; width: fit-content; margin-left: auto;"
            else:  # 其他角色靠左
                div_style = f"background-color: {background_color}; padding: 5px; border: 1px solid #FFCC99; border-radius: 5px; margin-bottom: 5px; width: fit-content;"
            if role==role_state:
                content="我说："+content
            else:
                content=f"{role}说："+content
            aligned_text += f"<div id='line-{i}' style='{div_style}'>{content}</div>"

        aligned_text += "</div>"  # 关闭内部 div
        aligned_text += "</div>"  # 关闭外部 div
        return aligned_text
    except json.JSONDecodeError:
        return "Error: Invalid JSON format."


def if_human_talk(role_state):
    role_state=role_state
    if role_talk==role_state:
        return gr.update(visible=True)
    else:
        return gr.update(visible=False)

#popleft better
def human_talk_add(role_state):
    role_state=role_state
    global human_talk_list
    global clue_finish
    global role_talk
    if role_state==role_talk :
        # human_talk_list.append(role_state)
        return gr.Info("已经在发言了")
    else:
        if  not human_talk_list:
            human_talk_list.append(role_state)
            if  clue_finish:
                role_talk=human_talk_list[0]
                clue_finish=0
            return gr.Info("添加成功")
        if human_talk_list[-1]!=role_state:
            human_talk_list.append(role_state)
            return gr.Info("添加成功")
        if human_talk_list[0]==role_state:
            return gr.Info("马上就能发言了")

        if human_talk_list[-1]==role_state:
            return gr.Info("刚刚添加过了")

    return 0
def fir_talk(role_state):
    role_state=role_state
    global human_talk_list
    global first_talk
    global role_talk
    if not first_talk:
        first_talk=1
        result = list(set(role_list) - set(ai_list))


        role_talk=random.choice(result)
        human_talk_list.append(role_state)

def validate_begin_page(topic, location, relationship):
    global topic_validated
    if not (topic and location and relationship):
        return gr.Warning("主题、地点和人物关系不能为空")
    else:
        topic_validated = True
        return "ok"

def update_human_slider(total_people, human_people):
    return gr.update(maximum=total_people, value=min(human_people, total_people))


def update_total_people(human_people, total_people):
    return gr.update(value=max(human_people, total_people))


def get_update(state):
    return str(state)


def remove_button():
    return gr.update(visible=False)

def topic_remove_button():
    if topic_validated:
        return gr.update(visible=False)
    else:return gr.update(visible=True)

def show_button():

    return gr.update(visible=True)

def if_show_button():
    global topic_validated
    if topic_validated:
        return gr.update(visible=True)
    else:
        return gr.update(visible=False)



# def llm(topic, location, relationship):
#     data = ["Hello", "this", "is", "a", "streaming", "output", "example"]
#     time.sleep(0.5)
#     yield f"topic: {topic}, {location}{relationship}Output: {data[0]}"
#     for item in data[1:]:
#         yield f"{item}"
#         time.sleep(1)  # 模拟延迟

def parse_list_response(result):
    global role_list
    while True:
        list_response = llm.to_role_list(result)
         # 调用生成响应的函数
        try:
            # 确保内容是字符串，且可以安全解析
            roles = ast.literal_eval(list_response.strip())
            if isinstance(roles, list):  # 确保解析的结果是合法的列表
                role_list=roles[:]
                print("Parsed roles:", roles)
                break  # 解析成功，退出循环
            else:
                print("Parsed content is not a list, retrying...")
        except (SyntaxError, ValueError) as e:
            print("Failed to parse model response:", e, "Retrying...{}")
strs=["正在生成角色背景故事","正在丰富角色背景","正在生成角色时间线","正在生成证据","正在汇总证据字典"]
def generate_story(topic, location, relationship,nums):
    global Tocreater
    global Toplayer
    global role_list
    global ai_list
    global evidence_dict
    global role_list_copy
    nums=str(nums)
    idex=0
    final_back=""
    final_timeline=""
    Toplayer=Toplayer+strs[idex]+"\n"
    idex=idex+1
    for chunk in llm.llm_background_1(topic, location, relationship,nums):
        Tocreater=Tocreater+chunk

    result1n=Tocreater
    Toplayer=Toplayer+strs[idex]+"\n"
    idex=idex+1
    for chunk in llm.llm_background_2(result1n):
        Tocreater=Tocreater+chunk
        final_back=final_back+chunk
    #genrate role_list
    parse_list_response(final_back)
    role_list_copy = role_list[:]
    random.shuffle(role_list_copy)
    for role in role_list:
        role_list_introduct.append(llm.get_introduct(role,final_back))
    Toplayer=Toplayer+strs[idex]+"\n"
    idex=idex+1
    for chunk in llm.timeline_1(final_back,location):
        Tocreater=Tocreater+chunk
        final_timeline=final_timeline+chunk
    

    #分离每个角色的时间线与背景故事
    for role in role_list:
       
        role_back=llm.div_back(role,final_back)
        Tocreater=Tocreater+role_back
        role_list_tANDp.append(role_back)
        role_time=llm.div_timeline(role,final_timeline)
        Tocreater=Tocreater+role_time
        role_list_tANDp[-1]=role_list_tANDp[-1]+"\n"+role_time
    ai_list=role_list[:]
    Toplayer=Toplayer+strs[idex]+"\n"
    idex=idex+1
    Tocreater=Tocreater+"\n"
    clue1=llm.genrate_clues1(final_back,final_timeline,location)
    Tocreater=Tocreater+clue1
    clue2=llm.genrate_clues2(final_back,final_timeline,location)
    Tocreater=Tocreater+clue2
    clue3=llm.genrate_clues3(final_back,final_timeline,location,clue1)
    Tocreater=Tocreater+clue3
    final_clue=llm.final_clues(final_back,final_timeline,location,clue1,clue2,clue3)
    
    while not evidence_dict:
        json_string = llm.clues_dict(final_clue)

        try:
  # 去掉json_string的多余换行符，防止ast.literal_eval()解析失败。
            json_string = json_string.strip()
            data_dict = ast.literal_eval(json_string)
            evidence_dict=data_dict 
            print(data_dict)
            print(type(data_dict))
        except Exception as e:
            print(f"ast.literal_eval 转换失败: {e}")
    Tocreater=Tocreater+"\n"+json_string
chioce_mark=0#置为1时，显示可以下一步按钮
clue_mark=0

def if_show_button_chioce():
    if chioce_mark:
        return gr.update(visible=True)

def change_chioce():
    global chioce_mark
    chioce_mark=1

def save_numeber(human,all):
    global  human_number
    global all_number
    human_number=human
    all_number=all
def list_update():
    return gr.update(choices=role_list)


def upup(role_state):
    role_state=role_state
    if clue_mark>=len(role_list)-len(ai_list):
        return gr.update(visible=True),str(chioce_mark),Tocreater,Toplayer,gr.update(visible=True)
    if count >= human_number and  len(role_state)>0 :
        return gr.update(visible=True),str(chioce_mark),Tocreater,Toplayer,gr.update(visible=False)
    else:
        return gr.update(visible=False), str(chioce_mark), Tocreater, Toplayer,gr.update(visible=False)
def next_page():
    return gr.update(visible=False),gr.update(visible=True)
def spe_next_page():
    global user_initialized
    if not user_initialized:
        user_initialized=True
        return gr.update(visible=False),gr.update(visible=True),gr.update(visible=False)
    else:
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)


def handle_mode_change(mode):
    if mode == "玩家模式":
        return gr.update(visible=True), gr.update(visible=False)
    elif mode == "开发者模式":
        return gr.update(visible=False), gr.update(visible=True)
    else:
        return gr.update(visible=False),gr.update(visible=False)
def role_change(role):
    for index,value in enumerate(role_list):
        if role==value:
            return gr.update(value=role_list_introduct[index])
def role_info(role_state):
    role_state=role_state
    for index,value in enumerate(role_list):
        if role_state==value:
            return gr.update(value=role_list_tANDp[index])
def human_player_add(role_radio,role_state):
    role_state=role_state
    #if  in ai_list remove   if not in ai_list return message
    global ai_list
    if role_radio in ai_list:
            ai_list.remove(role_radio)
            global count
            count=count+1
            role_state=role_radio
            return 0,role_state,gr.update(visible=False)
    else:
        return gr.Warning("角色已被选择"),role_state,gr.update(visible=True)
def fortest(role_state):

    test=str(role_list)+"  "+str(ai_list)+" rolestate:"+role_state+"  human_talk_list: "+str(human_talk_list)+"  talk_role:  "+role_talk
    return str(test)
def search_evidence(room):
    global clues_found
    global evidence_dict
    unsolved_evidences = [evidence for evidence, details in evidence_dict[room].items()
                          if isinstance(details, dict) and not details['found'] and evidence != 'prohibited_names']


    if unsolved_evidences:
        clues_found=""
        selected_evidence = random.choice(unsolved_evidences)
        evidence_dict[room][selected_evidence]['found'] = True
        # evidence = evidence + f"{room}: {selected_evidence} - {evidence_dict[room][selected_evidence]['description']}\n"
        clues_found=clues_found+f"在{room}找到了{selected_evidence} - {evidence_dict[room][selected_evidence]['description']}"+"\n"
        return gr.Info(f"你在{room}找到了{selected_evidence} - {evidence_dict[room][selected_evidence]['description']}")

    # If all evidence has been found, return that nothing was found
    return gr.Info(f"你在这里什么也没找到")
def update_gradio_list():
    """
    根据房间信息字典更新 gradio.update 列表。

    Args:
        update_list:  由 gradio.update 对象组成的列表.
        room_info_dict: 包含房间信息的字典.

    Returns:
        更新后的 gradio.update 列表.
    """
    global evidence_dict
    global initial_update_list
 
    
    for i, room_name in enumerate( evidence_dict.keys()):
        if i < len(initial_update_list):
          initial_update_list[i] = gr.update(value=room_name, visible=True)
        else: #如果给的字典键的数量多于预设的列表长度，就打印一个warning
           print (f"Warning: More keys in `room_info_dict` than elements in `update_list`. Ignoring room: {room_name}")
    
    for i in range(len(initial_update_list)): #如果预设的列表长度多于字典的键的数量，就让多余的键保持不可见
      if i >= len( evidence_dict):
          initial_update_list[i] = gr.update(value="",visible=False)

    return initial_update_list
def clue_mark_c():
    global clue_mark
    clue_mark=clue_mark+1
with gr.Blocks() as demo:
    role_state = gr.State(value="")
    
    with gr.Tab("互动"):
        with gr.Column(visible=True) as first_page:
            begin = gr.Textbox(value="hello")
            To_begin=gr.Button("下一步", visible=True)

        with gr.Column(visible=False) as begin_page:
            with gr.Row():
                topic = gr.Textbox(label="主题", visible=True)
            with gr.Row():
                location = gr.Textbox(label="地点", visible=True)
            with gr.Row():
                relationship = gr.Textbox(label="人物关系", visible=True)

            total_people_slider = gr.Slider(minimum=3, maximum=6, step=1, value=4, label="剧本人数")
            human_slider = gr.Slider(minimum=1, maximum=6, step=1, value=1, label="玩家人数")
            with gr.Row():
                topic_button = gr.Button("提交主题")
                To_generate_page=gr.Button("下一步", visible=False)
            total_people_slider.change(
                fn=update_human_slider,
                inputs=[total_people_slider, human_slider],
                outputs=human_slider,
            )

            human_slider.change(
                fn=update_total_people,
                inputs=[human_slider, total_people_slider],
                outputs=total_people_slider,
            )
        with gr.Column(visible=False) as generate_page:
            mode_radio = gr.Radio(choices=["玩家模式", "开发者模式"])
            player = gr.Textbox(label="玩家模式", visible=False,lines=5)
            creater = gr.Textbox(label="开发者模式", visible=False)
            To_role_page=gr.Button("下一步",visible=False)
            # with gr.Row():
            #     generate_button = gr.Button("choice role",visible=False)
        with gr.Column(visible=False) as role_page:

            role_radio = gr.Radio(choices=role_list_copy ,label="选择角色", value=role_list[0])
            introduction=gr.Textbox(label="角色简介",lines=5, max_lines=10)

            role_button = gr.Button("finish")
            To_talk_page=gr.Button("下一步",visible=False)
        with gr.Column(visible=False) as talk_page:
        
            json_input = gr.Textbox(lines=5, max_lines=10, label="Input JSON List")
            max_lines_slider = gr.Slider(minimum=1, maximum=10, step=1, value=20, label="Max Lines")
       
            html_output = gr.HTML(label="Output Text")




            with gr.Row():


                msg = gr.Textbox(label="输入消息", scale=18,visible=False)

                submit_btn = gr.Button("我要发言", scale=1)
                clue_pre_btn=gr.Button("准备搜证", scale=1,visible=True)
                clue_btn=gr.Button("搜证", scale=1,visible=False)
                vote_btn=gr.Button("准备投票", scale=1,visible=True)
        with gr.Column(visible=False) as evidence_page:
            with gr.Row():
                evidence_button1 = gr.Button("evidence",visible=False)
                evidence_button2 = gr.Button("evidence",visible=False)
                evidence_button3 = gr.Button("evidence",visible=False)
            with gr.Row():
                evidence_button4 = gr.Button("evidence",visible=False)
                evidence_button5 = gr.Button("evidence",visible=False)
                evidence_button6 = gr.Button("evidence",visible=False)
            with gr.Row():
                evidence_button7 = gr.Button("evidence",visible=False)
                evidence_button8 = gr.Button("evidence",visible=False)
                evidence_button9 = gr.Button("evidence",visible=False)
            evidence_button=gr.Button("搜证完成",visible=True)
    with gr.Tab("角色剧本"):
        juben=gr.Textbox(lines=10)
    with gr.Tab("已经搜到的证据"):
        find_clues=gr.Textbox(lines=10)
        evidence_button1.click(search_evidence,evidence_button1,evidence_button1).then(lambda:clues_found,None,find_clues)
        evidence_button2.click(search_evidence,evidence_button2,evidence_button1).then(lambda:clues_found,None,find_clues)
        evidence_button3.click(search_evidence,evidence_button3,evidence_button1).then(lambda:clues_found,None,find_clues)
        evidence_button4.click(search_evidence,evidence_button4,evidence_button1).then(lambda:clues_found,None,find_clues)
        evidence_button5.click(search_evidence,evidence_button5,evidence_button1).then(lambda:clues_found,None,find_clues)
        evidence_button6.click(search_evidence,evidence_button6,evidence_button1).then(lambda:clues_found,None,find_clues)
        evidence_button7.click(search_evidence,evidence_button7,evidence_button1).then(lambda:clues_found,None,find_clues)
        evidence_button8.click(search_evidence,evidence_button8,evidence_button1).then(lambda:clues_found,None,find_clues)
        evidence_button9.click(search_evidence,evidence_button9,evidence_button1).then(lambda:clues_found,None,find_clues)
        
        out_button=[evidence_button1,evidence_button2,evidence_button3,evidence_button4,evidence_button5,evidence_button6,evidence_button7,evidence_button8,evidence_button9]
        msg.submit(lambda : gr.update(visible=False),None,msg).then(
        human_talk,[msg,role_state],None ).then(
        lambda: "", None, [msg]
        )
        submit_btn.click(human_talk_add,role_state,[submit_btn])

        inputs = [json_input,  role_state,max_lines_slider]


        topic_button.click(   fn=validate_begin_page, inputs=[topic, location, relationship], outputs=None).then(
           topic_remove_button,None,topic_button  
        ).then(
            fn=if_show_button, inputs=None, outputs=To_generate_page) \
            .then(
            fn=save_numeber,
            inputs=[human_slider, total_people_slider],
            outputs=None)\
            .then(
            fn=generate_story, inputs=[topic, location, relationship,total_people_slider], outputs=None)\
            .then(
            fn=change_chioce,inputs=None,outputs=None
            ).then(
                update_gradio_list, inputs=None, outputs=out_button
            )
        choice_update=gr.Textbox(visible=False,value="0")

        json_input.change(user_assistant, inputs=inputs, outputs=html_output)
        # role_state.change(fn=show_button, inputs=None, outputs=To_talk_page)
        choice_update.change(fn=if_show_button_chioce,inputs=None,outputs=To_role_page)\
            .then(
            fn=list_update,inputs=None,outputs=role_radio
        )
        mode_radio.change(
            fn=handle_mode_change, inputs=mode_radio, outputs=[player,creater]
        )
        role_radio.change(
            fn=role_change, inputs=role_radio, outputs=[introduction]
        )
        clue_pre_btn.click(remove_button,None,clue_pre_btn).then(
            clue_mark_c,None,None
        )
        To_begin.click(
            fn=remove_button,inputs=None,outputs=To_begin).then(
            fn=spe_next_page, inputs=None, outputs=[first_page,begin_page,generate_page])
        To_generate_page.click(
            fn=remove_button, inputs=None, outputs=To_generate_page).then(
            fn=next_page, inputs=None, outputs=[begin_page, generate_page])
        To_role_page.click(
            fn=remove_button, inputs=None, outputs=To_role_page).then(
            fn=next_page, inputs=None, outputs=[generate_page,role_page ])
        clue_btn.click(
            fn=remove_button, inputs=None, outputs=clue_btn).then(
            fn=next_page, inputs=None, outputs=[talk_page,evidence_page ])
        def zero_mark():
            global clue_mark
            global clue_finish
            clue_finish=1
            clue_mark=0
        evidence_button.click(
            fn=remove_button, inputs=None, outputs=evidence_button
            ).then(
             zero_mark,None,None   
            ).then(
            fn=next_page, inputs=None, outputs=[evidence_page,talk_page ])
        a = gr.Textbox(visible=False)
        role_button.click(
            fn=human_player_add,
            inputs=[role_radio,role_state],
            outputs=[a,role_state,role_button]
        ).then(role_info,role_state,juben)
        To_talk_page.click(fir_talk,role_state,None).then(
            fn=remove_button, inputs=None, outputs=To_generate_page).then(
            fn=next_page, inputs=None, outputs=[role_page,talk_page])
        test = gr.Textbox()
        # demo.load(fortest, inputs=role_state, outputs=test, every=1)
        upup_t= gr.Timer(1,active=True)
        upup_t.tick(upup, inputs=role_state, outputs=[To_talk_page,choice_update,creater,player,clue_btn])

        if_human_talk_t=gr.Timer(0.5,active=True)
        if_human_talk_t.tick(if_human_talk, inputs=role_state, outputs=msg)
        all_talk_t=gr.Timer(0.5,active=True)
        false=gr.Textbox(visible=False)
        all_talk_t.tick(lambda :all_talk, inputs=None, outputs=json_input)
        false.change(user_assistant, inputs=inputs, outputs=html_output )
        
        # demo.load(upup, inputs=role_state, outputs=[To_talk_page,choice_update,creater,player], every=1)
        # demo.load(if_human_talk, inputs=role_state, outputs=msg, every=0.5)
        # demo.load(lambda :all_talk, inputs=None, outputs=json_input, every=0.5)
        
        test_t=gr.Timer(1,active=True)
        test_t.tick(fortest, inputs=role_state, outputs=test)
        
demo.launch()