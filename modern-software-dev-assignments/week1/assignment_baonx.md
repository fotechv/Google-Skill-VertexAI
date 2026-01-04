### Techniques and source files

| Technique                            | Source File                           | Description                                                                                      |
|--------------------------------------|---------------------------------------|--------------------------------------------------------------------------------------------------|
| K-shot prompting                     | [week1/k_shot_prompting.py]           | Chạy nhiều prompts để có kết quả tốt nhất                                                        |
| Chain-of-thought                     | [week1/chain_of_thought.py]           | Suy nghĩ/Giải thích các bước tại sao vậy. mô hình AI suy nghĩ từng bước (step-by-step reasoning) |
| Tool calling                         | [week1/tool_calling.py]               | Cho LLM sử dụng tool nào đó để thực hiện công việc (như search Google,...). Viết prompt hướng dẫn AI tạo tham số chính xác, sau đó dùng tham số đó để gọi tool.                       |
| Self-consistency prompting           | [week1/self_consistency_prompting.py] | Chọn output nào có tỷ lệ giống nhau cao (giữ được nhất quán output của prompt)                   |
| RAG (Retrieval-Augmented Generation) | [week1/rag.py]                        | Dựa trên dữ liệu đưa vào (ví dụ query DB,...)                                                    |
| Reflexion                            | [week1/reflexion.py]                  | Để chính LLM xem xét (suy ngẫm/phản xạ) lại kết quả và tự đánh giá lại                           |
