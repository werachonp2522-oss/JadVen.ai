from fastapi import APIRouter
from pydantic import BaseModel
import os
from google import genai

router = APIRouter(prefix="/prompt", tags=["AI Processing"])

class PromptRequest(BaseModel):
    user_message: str

# Use the advanced prompt from the user
MASTER_PROMPT = """
[Role]
คุณคือ "ผู้เชี่ยวชาญด้านการบริหารกำลังคนและจัดตารางเวรพยาบาล (Expert Roster Manager)" ที่มีความแม่นยำสูงมาก หน้าที่ของคุณคือจัดตารางเวรให้ถูกต้องตามกฎระเบียบของโรงพยาบาล 100% โดยคำนึงถึงความปลอดภัยของผู้ป่วยและสวัสดิภาพของพยาบาล

[Context]
นี่คือระบบ JadVen.ai จัดตารางเวรพยาบาลประจำ "แผนก ER"
โดยมีกะการทำงาน (Shifts) ดังนี้:
- M (Morning): 08.00 - 16.00 น.
- E (Evening): 16.00 - 24.00 น.
- N (Night): 24.00 - 08.00 น.
- OFF: วันหยุดพักผ่อน

[Instructions]
ผู้ใช้จะส่งข้อความเกี่ยวกับความต้องการลา หรือปรับเปลี่ยนเวร
จงวิเคราะห์ข้อความแล้วแปลงเป็น JSON format ที่สามารถส่งให้ระบบ OR-Tools ประมวลผลต่อได้

ตัวอย่าง Input: "พยาบาลสมศรีขอลากะทันหันพรุ่งนี้ ช่วยปรับตารางให้หน่อย"
ตัวอย่าง Output (JSON):
{
  "action": "update_rule",
  "nurse_name": "สมศรี",
  "date_offset": 1,
  "shift_assigned": "OFF",
  "reason": "ลากะทันหัน"
}
คืนค่าเฉพาะ JSON เท่านั้น ห้ามมีข้อความอื่นปน
"""

@router.post("/analyze")
def analyze_prompt(request: PromptRequest):
    # Retrieve the API key from environment
    # Ensure GEMINI_API_KEY is correctly set in .env
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return {"status": "error", "message": "Gemini API key not configured properly."}

    try:
        # Initialize the GenAI client with API key
        client = genai.Client(api_key=api_key)
        
        # Combine the Master Prompt system instruction with the user message
        full_prompt = f"{MASTER_PROMPT}\n\n[User Input]\n{request.user_message}"
        
        # Call Gemini 1.5 Pro (gemini-1.5-pro)
        response = client.models.generate_content(
            model='gemini-1.5-pro',
            contents=full_prompt,
        )
        
        return {
            "status": "success",
            "extracted_data": response.text
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
