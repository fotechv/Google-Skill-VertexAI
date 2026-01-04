# import os  # ví dụ import (đã comment vì không dùng)
from dotenv import load_dotenv  # dùng để load biến môi trường từ file .env
from ollama import chat  # hàm để gọi model thông qua Ollama
from transformers import AutoTokenizer

load_dotenv()  # tải các biến môi trường (nếu có)

NUM_RUNS_TIMES = 5  # số lần thử gọi model để tăng xác suất có kết quả mong muốn

# TODO: Fill this in!
# system prompt: mô tả hành vi mong muốn của model
# YOUR_SYSTEM_PROMPT = """
# You are a deterministic text transformation engine.
# Follow user instructions exactly.
# Do not explain.
# Do not add extra text.
# Only output the final result.
# """
# YOUR_SYSTEM_PROMPT = """
# You are a strict text-processing engine.
# """
# YOUR_SYSTEM_PROMPT = """
# You must follow instructions exactly and output only the required text.
# """
# YOUR_SYSTEM_PROMPT = """
# You are a strict text-processing engine.
# You must follow instructions exactly and output only the required text.
# """
# YOUR_SYSTEM_PROMPT = """
# You are a deterministic text transformation engine.
# Follow instructions exactly.
# Only output the final result.
# """
YOUR_SYSTEM_PROMPT = (
    "You are a strict assistant. For any input, output ONLY the reversed letters. "
    # "of the given word in lowercase. No extra text, no punctuation, no quotes, no newlines."
    "For example: abc to cba, test to tset, bao to oab, example to elpmaxe. "
)

# Prompt gửi cho model: yêu cầu đảo chữ trong từ và chỉ output đúng từ đã đảo
USER_PROMPT = """
Reverse the order of letters in the following word. Only output the reversed word, no other text:

httpstatus
"""

EXPECTED_OUTPUT = "sutatsptth"  # kết quả mong đợi của việc đảo chữ "httpstatus"


def demo_your_prompt(system_prompt: str) -> bool:
    """Chạy prompt tối đa NUM_RUNS_TIMES lần và trả về True nếu bất kỳ lần
    nào model trả nội dung trùng với EXPECTED_OUTPUT.

    In ra "SUCCESS" khi tìm được kết quả đúng.
    """
    for idx in range(NUM_RUNS_TIMES):
        # in tiến độ: idx + 1 để hiển thị từ 1 đến NUM_RUNS_TIMES
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")

        messages = [
            # system prompt ảnh hưởng hành vi model
            {"role": "system", "content": system_prompt},
            # prompt chứa nhiệm vụ cần làm
            {"role": "user", "content": USER_PROMPT},
        ]
        # messages=[
        #     {"role": "system", "content": YOUR_SYSTEM_PROMPT},
        #     {"role": "user",
        #      "content": "Reverse the following word: example"},
        #     {"role": "assistant", "content": "elpmaxe"},
        #     {"role": "user", "content": USER_PROMPT},
        # ],
        # messages = [
        #     {"role": "system", "content": YOUR_SYSTEM_PROMPT},
        #     {"role": "user", "content": "abc"},
        #     {"role": "assistant", "content": "cba"},
        #     {"role": "user", "content": "test"},
        #     {"role": "assistant", "content": "tset"},
        #     {"role": "user", "content": USER_PROMPT},
        # ]
        # tokenizer = AutoTokenizer.from_pretrained("mistral-nemo:12b")
        # print(
        #     tokenizer.apply_chat_template(
        #         messages,
        #         tokenize=False
        #     )
        # )

        # gọi API chat của Ollama: truyền model, messages (system + user), và options
        response = chat(
            model="mistral-nemo:12b",  # tên model được sử dụng
            messages=messages,
            # temperature điều chỉnh độ ngẫu nhiên
            options={"temperature": 0.5},
            # options={"temperature": 0.0},
        )
        # lấy nội dung trả về và loại bỏ khoảng trắng hai đầu
        output_text = response.message.content.strip()
        # so sánh kết quả thực tế và mong đợi (cũng loại bỏ khoảng trắng)
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")  # nếu match in SUCCESS
            return True  # trả về True để báo thành công
        else:
            # in ra expected và actual để debug khi không khớp
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    # nếu thử hết vòng lặp mà không khớp thì trả False
    return False


if __name__ == "__main__":
    # khi chạy file trực tiếp, gọi demo với system prompt đã định nghĩa
    demo_your_prompt(YOUR_SYSTEM_PROMPT)
