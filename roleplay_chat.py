# 导入所需库：OpenAI客户端、异常处理、环境变量操作、时间处理
from openai import OpenAI, AuthenticationError, APIConnectionError, APITimeoutError
import os
from dotenv import load_dotenv
from datetime import datetime

# 加载.env文件中的环境变量（包含API密钥）
load_dotenv()
os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"
# 从环境变量中获取OpenAI API密钥
api_key = os.getenv("OPENAI_API_KEY")

# 检查API密钥是否存在
if not api_key:
    print("错误：未找到API密钥")
    print("请检查：1. .env文件是否存在 2. 文件中是否有'OPENAI_API_KEY=你的密钥'")
    exit()  # 密钥不存在时退出程序

# 初始化OpenAI客户端
try:
    client = OpenAI(
        api_key=api_key,  # 使用获取到的API密钥
        timeout=60.0      # 设置请求超时时间为60秒
    )
except Exception as e:
    print(f"客户端初始化失败：{str(e)}")
    exit()  # 初始化失败时退出程序

def start_chat():
    # 角色设定：伦敦的英国路人，用自然英语对话
    character_setting = """
    You are a regular British passer-by in London. You speak natural English with a slight British accent (e.g., using "mate", "cheers", "lovely" in daily conversation).
    Your personality: friendly, casual, and a bit chatty. You can talk about everyday topics like weather, food, public transport, or local events.
    Avoid using overly formal language. Respond naturally as if having a real chat on the street.
    Always reply in English.
    """
    
    # 初始化对话历史（用于向API传递上下文）
    messages = [{"role": "system", "content": character_setting}]
    
    # 初始化对话记录列表（用于保存到文件）
    chat_history = []
    # 记录对话开始时间
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_history.append(f"对话开始时间：{start_time}\n")
    chat_history.append("角色设定：伦敦普通路人（英语对话）\n")
    chat_history.append("-----------------------------------\n")
    
    # 打印启动信息
    print("English Chat with British Passer-by")
    print("I say: Hi there!")
    print("Tip: Type 'exit' to end the conversation")
    print("-----------------------------------")
    
    # 初始用户消息
    initial_user_msg = "Hi there!"
    messages.append({"role": "user", "content": initial_user_msg})
    chat_history.append(f"You: {initial_user_msg}\n")  # 记录初始消息
    
    try:
        # 第一次调用API获取回复
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 使用的AI模型
            messages=messages,      # 对话历史上下文
            temperature=0.8         # 回复随机性（0-1，越高越灵活）
        )
        
        # 提取并显示AI回复
        ai_reply = response.choices[0].message.content
        print(f"Passer-by：{ai_reply}")
        messages.append({"role": "assistant", "content": ai_reply})
        chat_history.append(f"Passer-by: {ai_reply}\n")  # 记录AI回复
        
        # 多轮对话循环
        while True:
            user_input = input("You：")  # 获取用户输入
            current_time = datetime.now().strftime("%H:%M:%S")  # 当前时间
            chat_history.append(f"[{current_time}] You: {user_input}\n")  # 记录用户输入
            
            # 检查是否退出对话
            if user_input.lower() in ["bye", "exit"]:
                bye_msg = "Passer-by: Cheers, mate! Have a good day!"
                print(bye_msg)
                chat_history.append(f"[{datetime.now().strftime('%H:%M:%S')}] {bye_msg}\n")
                break  # 跳出循环，结束对话
            
            # 将用户输入加入对话历史
            messages.append({"role": "user", "content": user_input})
            
            # 调用API获取回复（带错误处理）
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.8
                )
            except AuthenticationError:
                error_msg = "密钥错误：API密钥无效或已过期"
                print(error_msg)
                print("请检查.env文件中的密钥是否正确，或重新生成密钥")
                chat_history.append(f"\n错误：{error_msg}\n")
                break
            except APIConnectionError:
                error_msg = "网络连接错误：无法连接到OpenAI服务器"
                print(error_msg)
                print("请检查网络是否正常，或尝试切换网络（如手机热点）")
                chat_history.append(f"\n错误：{error_msg}\n")
                break
            except APITimeoutError:
                error_msg = "请求超时：服务器未在规定时间内响应"
                print(error_msg)
                print("可能是网络延迟过高，请稍后再试")
                chat_history.append(f"\n错误：{error_msg}\n")
                break
            except Exception as e:
                error_msg = f"其他错误：{str(e)}"
                print(error_msg)
                chat_history.append(f"\n错误：{error_msg}\n")
                break
            
            # 处理并记录AI回复
            ai_reply = response.choices[0].message.content
            print(f"Passer-by：{ai_reply}")
            messages.append({"role": "assistant", "content": ai_reply})
            chat_history.append(f"[{datetime.now().strftime('%H:%M:%S')}] Passer-by: {ai_reply}\n")
    
    # 捕获第一次API调用的错误
    except AuthenticationError:
        error_msg = "密钥错误：API密钥无效或已过期"
        print(error_msg)
        print("请检查.env文件中的密钥是否正确，或重新生成密钥")
        chat_history.append(f"\n错误：{error_msg}\n")
    except APIConnectionError:
        error_msg = "网络连接错误：无法连接到OpenAI服务器"
        print(error_msg)
        print("请检查网络是否正常，或尝试切换网络（如手机热点）")
        chat_history.append(f"\n错误：{error_msg}\n")
    except APITimeoutError:
        error_msg = "请求超时：服务器未在规定时间内响应"
        print(error_msg)
        print("可能是网络延迟过高，请稍后再试")
        chat_history.append(f"\n错误：{error_msg}\n")
    except Exception as e:
        error_msg = f"其他错误：{str(e)}"
        print(error_msg)
        chat_history.append(f"\n错误：{error_msg}\n")
    
    # 无论对话正常结束还是出错，都保存记录
    finally:
        # 记录对话结束时间
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat_history.append(f"\n-----------------------------------")
        chat_history.append(f"对话结束时间：{end_time}")
        
        # 生成唯一文件名（用时间戳避免重名）
        filename = f"chat_record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        # 获取当前脚本所在目录（确保文件保存在同级目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, filename)
        
        # 写入文件
        try:
            # 用with语句打开文件，自动处理关闭
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(chat_history)  # 将列表中的所有内容写入文件
            print(f"\n对话记录已保存至：{file_path}")
        except Exception as e:
            print(f"\n保存对话记录失败：{str(e)}")

# 启动程序
if __name__ == "__main__":
    start_chat()