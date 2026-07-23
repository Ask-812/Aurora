import base64, json, urllib.request, sys, time

# Read API keys
keys = []
with open(r'd:\Projects\Aurora_f\.env') as f:
    for line in f:
        line = line.strip()
        if line.startswith('GROQ_API_KEY_') and '=' in line:
            val = line.split('=', 1)[1].strip().strip("'").strip('"')
            if val:
                keys.append(val)

print(f"Loaded {len(keys)} API keys")
key_idx = 0

def ocr_page(page_num):
    global key_idx
    path = f'd:/Projects/Arora/page_{page_num}_small.png'
    with open(path, 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    data = json.dumps({
        'model': 'llama-3.2-90b-vision-preview',
        'messages': [{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'OCR this image completely. Transcribe ALL text exactly as shown, preserving headings, bullet points, tables, formatting. Include every single word and detail. If there are diagrams/flowcharts, describe them textually.'},
                {'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{img_b64}'}}
            ]
        }],
        'max_tokens': 4000,
        'temperature': 0
    }).encode()
    
    for attempt in range(3):
        api_key = keys[key_idx % len(keys)]
        key_idx += 1
        try:
            req = urllib.request.Request(
                'https://api.groq.com/openai/v1/chat/completions',
                data=data,
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
            )
            resp = urllib.request.urlopen(req, timeout=120)
            result = json.loads(resp.read())
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}", file=sys.stderr)
            time.sleep(2)
    return f"[FAILED TO OCR PAGE {page_num}]"

# OCR all 10 pages
all_text = []
for p in range(1, 11):
    print(f"\n{'='*60}")
    print(f"PAGE {p}")
    print(f"{'='*60}")
    text = ocr_page(p)
    print(text)
    all_text.append(text)
    time.sleep(1)

# Save full OCR output
with open(r'd:\Projects\Arora\pdf_ocr_full.txt', 'w', encoding='utf-8') as f:
    for i, t in enumerate(all_text):
        f.write(f"\n{'='*60}\nPAGE {i+1}\n{'='*60}\n{t}\n")
print("\n\nSaved to pdf_ocr_full.txt")
