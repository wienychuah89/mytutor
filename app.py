import asyncio
import io
import os
import edge_tts
from google import genai
from google.genai import types
import speech_recognition as sr
import streamlit as st

# ================= 页面配置 =================
st.set_page_config(
    page_title="AI 英语口语私教",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ================= 预设场景 Prompt 库 =================
PROMPTS = {
    "日常闲聊 (Casual Chit-Chat)": """
    Act as a friendly peer catching up with me over coffee.
    1. Speak in casual, natural English.
    2. Keep replies concise (1-3 sentences) so we can maintain a flowing back-and-forth dialogue.
    3. If I make a grammar or expression mistake, put a short '[Tip: ...]' before your response.
    """,
    "外企求职面试 (Job Interview)": """
    Act as a professional and friendly interviewer for a global tech company.
    1. Conduct the interview step-by-step. Ask ONE realistic question at a time and wait for my response.
    2. If my response has grammar flaws or sounds unnatural, add a 1-sentence tip '[Tip: ...]' to show a more native/professional way to say it, then ask the next question.
    """,
    "出国旅行与海关 (Travel & Customs)": """
    Act as an airport customs officer at an international airport.
    1. Ask standard entry questions (purpose, duration, accommodation).
    2. Speak in realistic everyday English, keeping replies under 2 sentences.
    3. If I make a mistake, add a brief '[Tip: ...]' before continuing.
    """,
    "雅思口语模拟 (IELTS Speaking)": """
    Act as an official IELTS Speaking examiner.
    1. Ask Part 1 or Part 2 style questions one by one.
    2. Provide constructive feedback on vocabulary, fluency, and grammar when helpful.
    """,
}

VOICES = {
    "美音 - 温暖女声 (Jenny)": "en-US-JennyNeural",
    "美音 - 自然男声 (Guy)": "en-US-GuyNeural",
    "英音 - 优雅女声 (Sonia)": "en-GB-SoniaNeural",
}

# ================= 读取后台 Secrets =================
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "pea6125")
ADMIN_KEYS = list(st.secrets.get("ADMIN_GEMINI_KEYS", []))

# ================= 初始化 Session 状态 =================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_key_idx" not in st.session_state:
    st.session_state.current_key_idx = 0


# ================= 侧边栏：权限与设置 =================
with st.sidebar:
    st.header("🔐 访问授权")

    user_password = st.text_input(
        "管理员密码 (Password)",
        type="password",
        placeholder="输入授权密码启用专属通道",
    )

    active_keys = []
    if user_password == ADMIN_PASSWORD and ADMIN_KEYS:
        st.success("✅ 已授权：已激活后台专属 API 通道")
        active_keys = ADMIN_KEYS
    else:
        if user_password:
            st.warning("密码错误，请使用个人 API Key")
        custom_key = st.text_input(
            "个人 Gemini API Key",
            type="password",
            placeholder="AI Studio 获取的 API Key (AIzaSy...)",
        )
        if custom_key.strip():
            active_keys = [custom_key.strip()]
        else:
            st.info("💡 请输入密码或提供个人 API Key 后开始练习")

    st.divider()
    st.header("⚙️ 对话场景与发音")
    selected_scenario = st.selectbox("选择练习场景", list(PROMPTS.keys()))
    selected_voice = VOICES[st.selectbox("朗读发音", list(VOICES.keys()))]

    if st.button("🗑️ 清空对话记录", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ================= 智能轮换调用函数 =================
def call_gemini(prompt_text, system_instruction, keys):
    if not keys:
        raise Exception("请先在左侧输入正确的密码或填写个人 API Key！")

    attempts = len(keys)
    last_error = ""

    for _ in range(attempts):
        active_key = keys[st.session_state.current_key_idx % len(keys)]
        try:
            client = genai.Client(api_key=active_key)
            contents = [
                {"role": m["role"], "parts": [{"text": m["content"]}]}
                for m in st.session_state.messages
            ]
            contents.append(
                {"role": "user", "parts": [{"text": prompt_text}]}
            )

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                ),
            )

            # 调用成功，自动切换到下一个 Key 分担压力
            st.session_state.current_key_idx = (
                st.session_state.current_key_idx + 1
            ) % len(keys)
            return response.text

        except Exception as e:
            last_error = str(e)
            # 遇到限流或错误时，静默切换下一个 key 继续尝试
            st.session_state.current_key_idx = (
                st.session_state.current_key_idx + 1
            ) % len(keys)

    raise Exception(f"所有可用 API Key 额度均已耗尽或请求失败: {last_error}")


# ================= 辅助函数：TTS 与 STT =================
async def text_to_speech(text: str, voice: str) -> bytes:
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data


def transcribe_audio(audio_bytes: bytes) -> str:
    r = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio = r.record(source)
        return r.recognize_google(audio, language="en-US")
    except Exception:
        return ""


# ================= 主页面交互 =================
#st.title("🎙️ AI 英语口语私教")
st.markdown(f'<h1 style="font-size: 18px;">🎙️ AI 英语口语私教</h1>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "audio" in msg and msg["audio"]:
            st.audio(msg["audio"], format="audio/mp3")

audio_prompt = st.audio_input("🎙️ 点击录音开始练习")
text_prompt = st.chat_input("或在此输入英文...")

user_input = ""
if audio_prompt is not None:
    audio_bytes = audio_prompt.read()
    if st.session_state.get("last_audio_bytes") != audio_bytes:
        st.session_state.last_audio_bytes = audio_bytes
        with st.spinner("🎧 识别中..."):
            recognized_text = transcribe_audio(audio_bytes)
            if recognized_text:
                user_input = recognized_text
elif text_prompt:
    user_input = text_prompt

if user_input:
    if not active_keys:
        st.warning("⚠️ 请在左侧侧边栏输入密码或个人 API Key 后再开始对话。")
    else:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("🤖 正在思考..."):
                try:
                    reply_text = call_gemini(
                        user_input, PROMPTS[selected_scenario], active_keys
                    )
                    st.write(reply_text)

                    audio_bytes = asyncio.run(
                        text_to_speech(reply_text, selected_voice)
                    )
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": reply_text,
                            "audio": audio_bytes,
                        }
                    )
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
