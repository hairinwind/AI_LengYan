import os
import re
import sys
import asyncio
import tempfile
import edge_tts

SCRIPTURE_VOICE = "zh-CN-YunxiNeural"     # 经文/原文声音 (云希 - 沉稳庄重男声)
EXPLANATION_VOICE = "zh-CN-YunyangNeural" # 译文/解释声音 (云扬 - 清晰讲解男声)

async def generate_segment_audio_with_retry(text, voice, output_path, rate="-5%", max_retries=3):
    clean_text = text.strip()
    # 忽略纯符号或极其简短无声文本
    if not clean_text or re.match(r'^[^\w\u4e00-\u9fa5]+$', clean_text):
        return False
        
    for attempt in range(1, max_retries + 1):
        try:
            communicate = edge_tts.Communicate(clean_text, voice, rate=rate)
            await communicate.save(output_path)
            return True
        except Exception as e:
            if attempt < max_retries:
                await asyncio.sleep(1.5 * attempt)
            else:
                print(f"    ❌ 警告: 段落 TTS 生成失败 (重试 {max_retries} 次): '{clean_text[:20]}...' 错误: {e}")
                return False
    return False

def parse_markdown_to_segments(content):
    """
    将 Markdown 内容解析为 (role, text) 元组列表，并合并相邻同角色段落
    role: 'scripture' (经文原文) 或 'explanation' (译文解释)
    """
    raw_segments = []
    lines = content.split('\n')
    
    in_code_block = False
    code_block_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # 1. 拦截分割线 (--- 或 --)
        if re.match(r'^-{2,}$', stripped):
            continue
            
        # 2. 处理代码块 (通常出现在 ## 经文 部分)
        if stripped.startswith('```'):
            if in_code_block:
                in_code_block = False
                scripture_text = " ".join(code_block_lines).strip()
                if scripture_text:
                    raw_segments.append(('scripture', scripture_text))
                code_block_lines = []
            else:
                in_code_block = True
                code_block_lines = []
            continue
            
        if in_code_block:
            code_block_lines.append(stripped)
            continue
            
        if not stripped:
            continue
            
        # 3. 清理 Markdown 标题符号 (如 ##, ###)
        clean_line = re.sub(r'^#+\s*', '', stripped)
        
        # 4. 解析粗体 **原文** 与非粗体文本
        matches = list(re.finditer(r'\*\*(.*?)\*\*', clean_line))
        if matches:
            last_idx = 0
            for m in matches:
                start, end = m.span()
                before_text = clean_line[last_idx:start].strip()
                if before_text:
                    raw_segments.append(('explanation', before_text))
                bold_text = m.group(1).strip()
                if bold_text:
                    raw_segments.append(('scripture', bold_text))
                last_idx = end
            after_text = clean_line[last_idx:].strip()
            if after_text:
                raw_segments.append(('explanation', after_text))
        else:
            raw_segments.append(('explanation', clean_line))
            
    # 合并相邻同角色的段落以减少 API 请求频次
    merged_segments = []
    for role, text in raw_segments:
        if merged_segments and merged_segments[-1][0] == role:
            prev_role, prev_text = merged_segments[-1]
            merged_segments[-1] = (prev_role, prev_text + "。" + text)
        else:
            merged_segments.append((role, text))
            
    return merged_segments

async def convert_file(file_path, output_dir):
    if not os.path.exists(file_path):
        print(f"错误: 文件未找到 {file_path}")
        return False
        
    print(f"正在处理文件: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"读取文件失败: {file_path}, 错误: {e}")
        return False
        
    segments = parse_markdown_to_segments(content)
    if not segments:
        print(f"警告: 文件 {file_path} 中未解析出有效文本，跳过。")
        return False
        
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    final_output_mp3 = os.path.join(output_dir, f"{base_name}.mp3")
    
    temp_dir = tempfile.mkdtemp()
    temp_files = []
    
    try:
        for idx, (role, text) in enumerate(segments):
            voice = SCRIPTURE_VOICE if role == 'scripture' else EXPLANATION_VOICE
            temp_file = os.path.join(temp_dir, f"part_{idx:04d}.mp3")
            
            # API 请求间适当缓冲 0.15 秒，避免频率限制
            await asyncio.sleep(0.15)
            
            success = await generate_segment_audio_with_retry(text, voice, temp_file)
            if success:
                temp_files.append(temp_file)
                
        if not temp_files:
            print(f"警告: {file_path} 未成功生成任何音频片段。")
            return False
            
        # 二进制无缝合并 MP3 片段
        with open(final_output_mp3, 'wb') as outfile:
            for tf in temp_files:
                with open(tf, 'rb') as infile:
                    outfile.write(infile.read())
                    
        print(f"✓ 成功生成: {final_output_mp3} (包含 {len(temp_files)} 段音频)")
        return True
    except Exception as e:
        print(f"处理文件 {file_path} 过程抛出异常: {e}")
        return False
    finally:
        for tf in temp_files:
            if os.path.exists(tf):
                try:
                    os.remove(tf)
                except Exception:
                    pass
        if os.path.exists(temp_dir):
            try:
                os.rmdir(temp_dir)
            except Exception:
                pass

async def main():
    if len(sys.argv) < 2:
        print("用法: python3 convert.py <文件路径或目录1> [文件路径或目录2 ...]")
        sys.exit(1)
        
    targets = sys.argv[1:]
    files_to_process = []
    
    for target in targets:
        if os.path.isfile(target):
            parent_dir = os.path.basename(os.path.dirname(os.path.abspath(target)))
            output_dir = os.path.join("audio", parent_dir)
            files_to_process.append((target, output_dir))
        elif os.path.isdir(target):
            dir_name = os.path.basename(os.path.normpath(target))
            output_dir = os.path.join("audio", dir_name)
            for fname in sorted(os.listdir(target)):
                if fname.endswith(".md"):
                    files_to_process.append((os.path.join(target, fname), output_dir))
        else:
            print(f"警告: 路径不存在或无效: {target}")
            
    if not files_to_process:
        print("没有找到需要处理的 .md 文件。")
        return
        
    print(f"共发现 {len(files_to_process)} 个待转换文件，开始执行双音色 TTS 生成...\n")
    for file_path, output_dir in files_to_process:
        await convert_file(file_path, output_dir)
        
    print("\n所有文件转换完成！输出音频存放在 audio/ 目录下。")

if __name__ == "__main__":
    asyncio.run(main())

