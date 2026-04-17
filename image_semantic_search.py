import os

# ==========================================
# 1. 配置与初始化
# ==========================================
# IMAGE_DIR = "image\\PixPinAutoSave"  # 你的图片存放目录
# 必须在顶层先声明这些全局变量的初始状态，否则后续的 if 判断会报错
ocr_engine = None
embed_model = None
db = None
gTABLE_NAME = "image_index"
DB_PATH = "./image_vector_db"

def _init_engines():
    global ocr_engine, embed_model, db
    
    # 致命防御 1：拦截重复加载 (State Check)
    # 没有这行代码，你每次点击“搜索”按钮，程序都会强行重新读取 2GB 的模型进入内存。
    # 点几次就会导致系统内存溢出（OOM）直接闪退。
    if db is not None:
        return
        
    print("正在预热 AI 引擎 (OCR & Embedding)...")
    
    # 致命防御 2：局部导入 (Local Import)
    # 如果把这些 import 放在文件最顶端，当主程序执行 import image_semantic_search 时，
    # 依然会触发这些重型底层库（如 ONNX 和 PyTorch）的加载，导致你的 UI 界面慢 3-5 秒才弹出来。
    # 必须把它们放在函数内部，实现绝对的按需加载。
    import lancedb
    from rapidocr_onnxruntime import RapidOCR
    from sentence_transformers import SentenceTransformer
    from modelscope import snapshot_download

    ocr_engine = RapidOCR()
    model_dir = snapshot_download('Xorbits/bge-m3')
    embed_model = SentenceTransformer(model_dir)
    db = lancedb.connect(DB_PATH)

# ==========================================
# 2. 批量处理与入库引擎
# ==========================================

def remove_index():
    _init_engines()
    """清除向量数据库索引"""
    if gTABLE_NAME in db.table_names():
        db.drop_table(gTABLE_NAME)
        print(f"已清除索引表: {gTABLE_NAME}")
    else:
        print("索引表不存在，无需清除。")

def ingest_images(target_dir, progress_callback=None):
    
    """
    现在接收 target_dir 参数，由外部（UI）传入路径
    progress_callback: 可选的进度回调函数，签名为 callback(current, total)
    支持递归搜索子文件夹中的图片
    """
    _init_engines() 
    
    if not target_dir or not os.path.exists(target_dir):
        print(f"路径无效: {target_dir}")
        return

    data_list = []
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
    
    # 递归搜索所有图片文件
    image_files = []
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            if f.lower().endswith(valid_extensions):
                image_files.append(os.path.join(root, f))

    if not image_files:
        print(f"在 {target_dir} 及其子文件夹中未找到图片文件。")
        return

    print(f"检测到 {len(image_files)} 张图片，开始处理...")

    for index, path in enumerate(image_files):
        try:
            # 1. 执行 OCR
            result, _ = ocr_engine(path)
            if not result:
                # 触发进度回调
                if progress_callback:
                    progress_callback(index + 1, len(image_files))
                continue
                
            full_text = " ".join([line[1] for line in result])
            if len(full_text.strip()) < 2: # 忽略无意义或过短的内容
                # 触发进度回调
                if progress_callback:
                    progress_callback(index + 1, len(image_files))
                continue

            # 2. 生成向量
            vector = embed_model.encode([full_text])[0].tolist()

            # 3. 构造数据条目：将路径与向量绑定
            data_list.append({
                "vector": vector,
                "text": full_text,
                "image_path": os.path.abspath(path) # 关键：存储绝对路径
            })
            print(f"已处理: {os.path.basename(path)}")
            
            # 触发进度回调
            if progress_callback:
                progress_callback(index + 1, len(image_files))
        except Exception as e:
            print(f"处理失败 {path}: {e}")
            # 触发进度回调
            if progress_callback:
                progress_callback(index + 1, len(image_files))

    # 4. 写入本地向量数据库
    if data_list:
        if gTABLE_NAME in db.table_names():
            db.drop_table(gTABLE_NAME)
        db.create_table(gTABLE_NAME, data=data_list)
        print(f"\n入库完成！共索引 {len(data_list)} 张图片。")

# ==========================================
# 3. 语义搜索函数
# ==========================================
# ==========================================
# 3. 语义搜索函数
# ==========================================
def search_image(query: str, top_k: int = 10):
    """根据语义寻找图片路径，返回字典列表供 GUI 渲染"""
    _init_engines()
    
    if gTABLE_NAME not in db.table_names():
        print("错误：请先运行 ingest_images() 构建索引。")
        # 严谨修改：数据库不存在时必须返回空列表，防止前端 GUI 迭代 None 引发崩溃
        return []

    # 将查询语句向量化
    query_vec = embed_model.encode([query])[0].tolist()
    
    # 在数据库中搜索
    tbl = db.open_table(gTABLE_NAME)
    results = tbl.search(query_vec).limit(top_k).to_pandas()
    
    # 核心修改：创建空列表用于收集结果
    search_results = []
    
    print(f"\n--- 关于 '{query}' 的搜索结果 ---")
    for _, row in results.iterrows():
        distance = row['_distance']
        image_path = row['image_path']
        text_preview = row['text'][:50]
        
        # 依然保留终端打印，方便你进行底层调试
        print(f"匹配度 [距离: {distance:.4f}]")
        print(f"图片路径: {image_path}")
        print(f"识别文字: {text_preview}...") 
        print("-" * 30)
        
        # 核心修改：将每一行结果打包成字典，推入列表
        search_results.append({
            "distance": distance,
            "image_path": image_path,
            "text": text_preview
        })
        
    # 核心修改：将列表返回给调用者（image_window.py）
    return search_results
if __name__ == "__main__":
    # 第一次运行需执行入库，之后可注释掉
    # ingest_images()
    
    # 交互式搜索测试
    while True:
        q = input("\n请输入搜索关键词 (q退出): ")
        if q.lower() == 'q': break
        search_image(q)