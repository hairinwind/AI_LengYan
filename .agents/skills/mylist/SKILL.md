---
name: mylist
description: '列出当前工作区中所有自定义技能/命令及其描述。显示 my* 及相关自定义命令清单。'
---

# 列出自定义命令 (MyList)

用于扫描并列出当前工作区的所有自定义技能（Skills）与可用指令（Instructions）。

## 执行流程 (Workflow)
1. 扫描工作区自定义根目录 `.agents/skills/` 下的所有技能子目录。
2. 读取各技能目录中的 `SKILL.md`，提取 frontmatter 元数据（`name` 与 `description`）。
3. 汇总并输出格式清晰的指令列表。

## 示例输出格式
```text
可用自定义指令列表 (Available Custom Instructions):

- /myinit: 初始化佛经文本格式。为"逐句白话译文"部分中的每一段经文添加**标记和---分割符。
- /mynext <章节号>: 生成下一个佛经学习文档，自动递增序号。
- /mytts <路径>: 批量将 Markdown 经文与译文转换为双发音人 MP3 音频。
- /mylist: 列出当前所有可用自定义指令清单。
- /study_fojing: 佛经学习文本格式化技能。
```
