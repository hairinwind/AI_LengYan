---
name: mytts
description: Convert Markdown text files into dual-voice MP3 audio using Edge-TTS. Supports scripture (bold text) and explanation (plain text) voice switching.
---

# MyTTS - 文本转音频技能 (Text-to-Speech Skill)

本 Skill 专用于将含有“经文原文”与“白话译文”的 Markdown 文件批量转换为双发音人的 MP3 音频文件。

## 指令触发 (Instruction Trigger)

用户可通过指令 `/mytts <文件或目录路径>` 触发文本转音频任务。

例如：
* `/mytts 8/楞严经-第八章-0010.md`
* `/mytts 8`
* `/mytts 8 9`

## 发音人配置 (Voice Configuration)

* **经文原文（粗体 `**文本**` 或代码块）**：`zh-CN-YunxiNeural`（云希，沉稳庄重男声）
* **译文解说（普通段落文本）**：`zh-CN-YunyangNeural`（云扬，清晰解说声）

## 依赖与执行 (Dependencies & Execution)

核心转换脚本位于 `scripts/convert.py`，依赖 Python 库 `edge-tts`。
转换结果将按章节自动输出至 `audio/<章节目录>/` 下。
