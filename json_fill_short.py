import base64
import os
import json
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv
from time import sleep

load_result = load_dotenv()
if not load_result:
    raise Exception(".env 檔案載入失敗")

def get_todo_batch(json_files, processed_files):
    docs_path = Path('docs_jmanga')
    todo_batch = []
    
    # 讀取所有 json 檔案
    for json_file in json_files:
        # 跳過已處理的檔案
        if str(json_file) in processed_files:
            continue
            
        with open(json_file, 'r', encoding='utf-8') as f:
            try:
                # print(json_file)
                data = json.load(f)
                if not data.get('short_title'):  # 如果 short_title 是空的
                    todo_batch.append({
                        'file_path': json_file,
                        'title': data['title']
                    })
            except json.JSONDecodeError:
                print(f"Error reading {json_file}")
                continue
            
        if len(todo_batch) >= 50:  # 改為當達到50筆時停止
            break
            
    return todo_batch

def update_json_files(todo_batch, results):
    updated_files = []
    for item, result in zip(todo_batch, results):
        file_path = item['file_path']
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['short_title'] = result['short']
        print(f"{data['short_title']} <-- {data['title']}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        updated_files.append(str(file_path))
    return updated_files

def process_batch(client, todo_batch):
    if not todo_batch:
        return []

    # 構建查詢文本
    query_text = "\n".join(f"title:{item['title']}" for item in todo_batch)
    query_text += "\n\n依每個 title，產生 7個字以下的日文或是3個words的英文"

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=query_text),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_NONE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_NONE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_NONE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_NONE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_CIVIC_INTEGRITY",
                threshold="BLOCK_NONE",
            ),
        ],
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type=genai.types.Type.ARRAY,
            description="包含原始標題和縮短標題的陣列",
            items=genai.types.Schema(
                type=genai.types.Type.OBJECT,
                required=["title", "short"],
                properties={
                    "title": genai.types.Schema(
                        type=genai.types.Type.STRING,
                        description="原始標題",
                    ),
                    "short": genai.types.Schema(
                        type=genai.types.Type.STRING,
                        description="縮短後的標題，必須是 7 個字以下的日文或是 3 個 words 的英文",
                    ),
                },
            ),
        ),
    )

    try:
        response = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if hasattr(chunk, 'text'):
                response += chunk.text
            else:
                print("Warning: Received chunk without text")
                continue

        # 確保回應是有效的 JSON 格式
        if not response.strip().startswith('[') or not response.strip().endswith(']'):
            print("Invalid JSON response format")
            print("Response:", response)
            return []

        try:
            results = json.loads(response)
            if not isinstance(results, list):
                print("Response is not a list")
                print("Response:", response)
                return []
                
            # 驗證每個結果是否符合預期格式
            valid_results = []
            for result in results:
                if isinstance(result, dict) and 'title' in result and 'short' in result:
                    valid_results.append(result)
                else:
                    print(f"Invalid result format: {result}")
                    
            return valid_results

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print("Response:", response)
            return []
            
    except Exception as e:
        print(f"Error during API call: {e}")
        return []

def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    json_files = sorted(Path('docs_jmanga').glob('*.json'))
    processed_files = set()
    batch_count = 0
    retry_count = 0
    max_retries = 3
    
    while True:
        # 取得下一批要處理的檔案
        todo_batch = get_todo_batch(json_files, processed_files)
        
        if not todo_batch:
            print("All files have been processed")
            break
            
        batch_count += 1
        print(f"\nProcessing batch {batch_count} ({len(todo_batch)} files)...")
        
        # 處理這一批檔案
        results = process_batch(client, todo_batch)
        if results:
            # 更新檔案並記錄已處理的檔案
            updated_files = update_json_files(todo_batch, results)
            processed_files.update(updated_files)
            print(f"Successfully processed {len(updated_files)} files in batch {batch_count}")
            retry_count = 0  # 重置重試計數
            
            # 在批次之間暫停一下，避免過度請求
            if len(todo_batch) == 50:
                print("Waiting 5 seconds before next batch...")
                sleep(5)
        else:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Failed to process batch after {max_retries} attempts. Moving to next batch...")
                retry_count = 0
                continue
                
            print(f"Failed to process batch {batch_count}, retrying in 10 seconds... (Attempt {retry_count}/{max_retries})")
            sleep(10)
            continue
            
    print(f"\nCompleted processing all files in {batch_count} batches")
    print(f"Total files processed: {len(processed_files)}")

if __name__ == "__main__":
    generate()
