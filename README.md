# 🎙️ AI 英语口语私教 (AI Spoken English Tutor)

基于 **Streamlit**、**Google Gemini 3.6 Flash** 与 **Edge TTS** 构建的实时英语口语对话 Web 应用。支持电脑及手机浏览器端原生录音、智能语法纠错、多场景角色扮演与多 API 自动负载均衡。

---

## ✨ 项目特色

- **🗣️ 原生语音交互**：基于手机与电脑浏览器的原生麦克风录音，无需繁琐硬件配置，点按即可开练。
- **🧠 原生多模态理解**：接入 Google Gemini 3.6 Flash，支持直接理解音频输入，抗口音、识别准、响应快。
- **🔊 自然拟真发音**：集成微软 Edge 神经网络语音（Edge-TTS），提供美音、英音等多角色自然语音实时播报。
- **🎯 丰富场景切换**：
  - **日常闲聊** (Casual Chit-Chat)
  - **外企求职面试** (Job Interview)
  - **出国旅行与海关** (Travel & Customs)
  - **雅思口语模拟** (IELTS Speaking)
  - **自定义 Prompt** (Custom Scenario)
- **🔐 权限管理与多 Key 轮询**：
  - 支持管理员密码授权解锁后台专属 API 通道。
  - 支持多个 Gemini API Key 智能轮换（Round-Robin），单 Key 限流（429）时自动无缝故障转移。
  - 支持免密模式下输入个人 API Key 使用。

---

## 🛠️ 技术栈

- **前端 / 应用框架**：[Streamlit](https://streamlit.io/)
- **大语言模型 (LLM)**：[Google GenAI SDK](https://github.com/google-gemini/generative-ai-python) (`gemini-3.6-flash`)
- **语音合成 (TTS)**：[edge-tts](https://github.com/rany2/edge-tts)
- **部署平台**：Streamlit Community Cloud

---

## 🚀 快速开始

### 1. 本地运行

1. **克隆仓库并安装依赖**：
   ```bash
   git clone [https://github.com/wienychuah89/mytutor.git](https://github.com/wienychuah89/mytutor.git)
   cd mytutor
   pip install -r requirements.txt
