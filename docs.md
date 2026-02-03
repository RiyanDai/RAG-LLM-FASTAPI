Perfect! Saya buatkan HRIS Chatbot dengan Streamlit yang siap pakai dengan API key yang Anda berikan! 🚀

📁 Struktur Project
hris-chatbot/
├── .env                        # API key
├── hris_knowledge_base.py      # Knowledge base
├── rag_system.py               # RAG system
├── app.py                      # Streamlit app (MAIN)
└── requirements.txt            # Dependencies

1. File .env
bashGROQ_API_KEY=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

2. File requirements.txt
txtstreamlit
groq
chromadb
sentence-transformers
python-dotenv

3. File hris_knowledge_base.py
python# hris_knowledge_base.py

HRIS_DOCUMENTS = [
    # CUTI
    {
        "id": "cuti_001",
        "category": "cuti",
        "content": """
        KEBIJAKAN CUTI TAHUNAN PT. XYZ
        - Setiap karyawan mendapat 12 hari cuti tahunan per tahun
        - Cuti dapat diambil setelah masa kerja 1 tahun
        - Pengajuan cuti minimal 3 hari kerja sebelum tanggal cuti
        - Cuti yang tidak diambil tidak dapat diuangkan
        - Maksimal cuti berturut-turut adalah 5 hari kerja
        """
    },
    {
        "id": "cuti_002",
        "category": "cuti",
        "content": """
        PROSEDUR PENGAJUAN CUTI
        1. Login ke HRIS Portal di hris.xyz.com
        2. Pilih menu "Leave Request"
        3. Pilih jenis cuti (Annual Leave)
        4. Isi tanggal mulai dan selesai cuti
        5. Tulis alasan/keperluan cuti
        6. Submit dan tunggu approval dari atasan langsung
        7. Notifikasi akan dikirim via email setelah approved/rejected
        """
    },
    {
        "id": "cuti_003",
        "category": "cuti",
        "content": """
        CUTI SAKIT
        - Cuti sakit tidak dibatasi jumlah harinya
        - Untuk cuti sakit 1-2 hari: tidak perlu surat dokter
        - Untuk cuti sakit 3 hari atau lebih: wajib surat dokter
        - Surat dokter dapat di-upload di HRIS Portal atau email ke hr@xyz.com
        - Tetap harus memberitahu atasan langsung di hari yang sama
        """
    },
    {
        "id": "cuti_004",
        "category": "cuti",
        "content": """
        CUTI KHUSUS
        - Cuti melahirkan: 3 bulan (90 hari) untuk karyawan wanita
        - Cuti menikah: 3 hari kerja
        - Cuti kematian keluarga inti: 3 hari kerja
        - Cuti khusus harus disertai bukti (undangan, surat keterangan, dll)
        - Tidak mengurangi jatah cuti tahunan
        """
    },
    
    # JAM KERJA
    {
        "id": "jamkerja_001",
        "category": "jam_kerja",
        "content": """
        JAM KERJA PT. XYZ
        - Senin - Jumat: 09:00 - 18:00 WIB
        - Istirahat makan siang: 12:00 - 13:00 WIB
        - Flexitime untuk clock-in: 08:00 - 10:00 WIB
        - Jika clock-in jam 08:00, bisa pulang jam 17:00
        - Jika clock-in jam 10:00, harus pulang jam 19:00
        - Sabtu-Minggu libur (kecuali ada project khusus)
        """
    },
    {
        "id": "jamkerja_002",
        "category": "jam_kerja",
        "content": """
        KETERLAMBATAN
        - Toleransi keterlambatan: 15 menit (maksimal 3x per bulan)
        - Keterlambatan > 15 menit dihitung sebagai pelanggaran
        - Keterlambatan > 3x per bulan akan mendapat surat peringatan
        - Jika ada kendala (macet, sakit, dll), segera informasikan atasan via WA/email
        """
    },
    {
        "id": "jamkerja_003",
        "category": "jam_kerja",
        "content": """
        WORK FROM HOME (WFH)
        - WFH diperbolehkan maksimal 2 hari per minggu
        - Harus mendapat approval dari atasan minimal H-1
        - Pengajuan WFH via HRIS Portal menu "WFH Request"
        - Tetap harus clock-in/out di HRIS Portal saat WFH
        - Harus available di jam kerja (responsif di Slack/email)
        """
    },
    
    # BENEFIT
    {
        "id": "benefit_001",
        "category": "benefit",
        "content": """
        ASURANSI KESEHATAN PT. XYZ
        - BPJS Kesehatan (wajib, ditanggung perusahaan 100%)
        - Asuransi swasta (provider: Allianz)
        - Coverage outpatient: Rp 5.000.000 per tahun
        - Coverage inpatient: Rp 50.000.000 per tahun
        - Coverage dental: Rp 2.000.000 per tahun
        - Coverage kacamata: Rp 1.000.000 per tahun
        - Tanggungan: Karyawan + 1 (pasangan atau anak)
        """
    },
    {
        "id": "benefit_002",
        "category": "benefit",
        "content": """
        TUNJANGAN PT. XYZ
        - Tunjangan transport: Rp 50.000 per hari kerja masuk kantor
        - Tunjangan makan: Rp 30.000 per hari kerja
        - Tunjangan komunikasi: Rp 200.000 per bulan
        - THR: 1 bulan gaji (dibayar sebelum lebaran)
        - Bonus tahunan: Berdasarkan performa perusahaan (rata-rata 1-2 bulan gaji)
        """
    },
    {
        "id": "benefit_003",
        "category": "benefit",
        "content": """
        BPJS KETENAGAKERJAAN
        - Jaminan Hari Tua (JHT)
        - Jaminan Pensiun (JP)
        - Jaminan Kecelakaan Kerja (JKK)
        - Jaminan Kematian (JKM)
        - Iuran ditanggung perusahaan dan karyawan sesuai ketentuan pemerintah
        """
    },
    
    # ABSENSI
    {
        "id": "absensi_001",
        "category": "absensi",
        "content": """
        SISTEM ABSENSI
        - Clock-in/out menggunakan mesin fingerprint di kantor
        - Untuk WFH: Clock-in/out via HRIS Portal
        - Jangan lupa clock-out sebelum pulang (akan dianggap absent jika tidak clock-out)
        - Lupa absen? Submit manual attendance di HRIS Portal dengan approval atasan
        """
    },
    
    # PAYROLL
    {
        "id": "payroll_001",
        "category": "payroll",
        "content": """
        PENGGAJIAN
        - Gaji dibayar setiap tanggal 25 setiap bulan
        - Jika tanggal 25 jatuh di weekend/libur, dibayar di hari kerja sebelumnya
        - Slip gaji dapat diunduh di HRIS Portal menu "Payslip"
        - Untuk pertanyaan gaji, hubungi tim Payroll: payroll@xyz.com
        """
    },
    
    # KARIR
    {
        "id": "karir_001",
        "category": "karir",
        "content": """
        PENGEMBANGAN KARIR
        - Performance review dilakukan 2x per tahun (Juni dan Desember)
        - Promosi berdasarkan performa dan kompetensi
        - Training budget: Rp 5.000.000 per karyawan per tahun
        - Internal job posting tersedia di HRIS Portal menu "Career"
        """
    },
    
    # KONTAK
    {
        "id": "kontak_001",
        "category": "kontak",
        "content": """
        KONTAK TIM HR PT. XYZ
        - Email umum: hr@xyz.com
        - Telepon: (021) 1234-5678
        - Extension internal: 100
        - Jam operasional: Senin-Jumat 09:00-17:00 WIB
        - Lokasi: Gedung XYZ Lt. 5, Jakarta
        - Head of HR: Ibu Sarah (sarah@xyz.com, ext. 101)
        - HR Generalist: Bapak Andi (andi@xyz.com, ext. 102)
        - Payroll Team: payroll@xyz.com, ext. 103
        """
    },
]

4. File rag_system.py
python# rag_system.py

import os
from groq import Groq
import chromadb
from chromadb.config import Settings
from typing import List, Dict
from hris_knowledge_base import HRIS_DOCUMENTS

class HRISRagSystem:
    def __init__(self, groq_api_key: str):
        # Initialize Groq client
        self.groq_client = Groq(api_key=groq_api_key)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="hris_knowledge",
            metadata={"description": "HRIS knowledge base for PT. XYZ"}
        )
        
        # Load documents
        self.load_documents()
    
    def load_documents(self):
        """Load HRIS documents into ChromaDB"""
        # Check if already loaded
        if self.collection.count() > 0:
            return
        
        documents = [doc["content"] for doc in HRIS_DOCUMENTS]
        ids = [doc["id"] for doc in HRIS_DOCUMENTS]
        metadatas = [{"category": doc["category"]} for doc in HRIS_DOCUMENTS]
        
        # Add to ChromaDB
        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
    
    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict]:
        """Retrieve relevant context from vector DB"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        context_docs = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                context_docs.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                })
        
        return context_docs
    
    def generate_response(self, query: str, context_docs: List[Dict]) -> str:
        """Generate response using Groq with retrieved context"""
        
        # Build context string
        context = "\n\n---\n\n".join([doc["content"] for doc in context_docs])
        
        # System prompt
        system_prompt = f"""
Kamu adalah AI Assistant HRIS untuk PT. XYZ Indonesia.

KONTEKS DOKUMEN:
{context}

INSTRUKSI:
- Jawab pertanyaan user berdasarkan KONTEKS DOKUMEN di atas
- Gunakan Bahasa Indonesia yang formal tapi ramah
- Jika informasi tidak ada di konteks, katakan dengan jujur dan arahkan ke HR
- Berikan jawaban yang jelas dan terstruktur
- Gunakan emoji secukupnya untuk memperjelas (✅❌📧📞⏰)

KONTAK HR (gunakan jika perlu escalate):
📧 Email: hr@xyz.com
📞 Phone: (021) 1234-5678 / ext. 100
⏰ Jam operasional: 09:00-17:00 WIB
"""

        # Call Groq API
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            return f"❌ Error saat generate response: {str(e)}"
    
    def chat(self, query: str) -> str:
        """Main chat function"""
        # Retrieve context
        context_docs = self.retrieve_context(query, top_k=3)
        
        # Generate response
        response = self.generate_response(query, context_docs)
        
        return response

5. File app.py (STREAMLIT APP) ⭐
python# app.py

import streamlit as st
from rag_system import HRISRagSystem
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="HRIS Chatbot PT. XYZ",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
    }
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🤖 HRIS Chatbot PT. XYZ")
st.markdown("**Asisten Virtual HR** - Tanya apa saja tentang kebijakan HR, cuti, benefit, dan lainnya!")

# Initialize RAG system
@st.cache_resource
def init_rag_system():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.error("❌ GROQ_API_KEY tidak ditemukan di file .env")
        st.stop()
    
    with st.spinner("🔄 Memuat AI Assistant..."):
        return HRISRagSystem(groq_api_key=groq_api_key)

rag_system = init_rag_system()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Welcome message
    st.session_state.messages.append({
        "role": "assistant",
        "content": """Halo! 👋 Saya asisten virtual HR PT. XYZ.

Saya bisa membantu Anda dengan:
✅ Informasi cuti (tahunan, sakit, khusus)
✅ Jam kerja dan WFH
✅ Benefit dan asuransi
✅ Absensi dan payroll
✅ Pengembangan karir

Silakan tanya apa saja! 😊"""
    })

# Sidebar
with st.sidebar:
    st.header("ℹ️ Informasi")
    
    st.markdown("### 🔧 Teknologi")
    st.markdown("""
    - **RAG**: Retrieval-Augmented Generation
    - **LLM**: Groq (Llama 3.3 70B)
    - **Vector DB**: ChromaDB
    - **Frontend**: Streamlit
    """)
    
    st.markdown("---")
    
    st.markdown("### 📞 Kontak HR")
    st.markdown("""
    - 📧 hr@xyz.com
    - ☎️ (021) 1234-5678
    - 📍 Ext. 100
    - ⏰ Senin-Jumat, 09:00-17:00
    """)
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### 🚀 Pertanyaan Cepat")
    
    quick_questions = [
        "Cara ajukan cuti?",
        "Jam kerja berapa?",
        "Benefit apa saja?",
        "WFH berapa hari?",
        "Cara claim asuransi?"
    ]
    
    for question in quick_questions:
        if st.button(question, key=f"quick_{question}"):
            st.session_state.quick_question = question
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Hapus Riwayat Chat", type="secondary"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Riwayat chat telah dihapus. Silakan mulai percakapan baru! 😊"
        }]
        st.rerun()
    
    st.markdown("---")
    st.caption("© 2024 PT. XYZ Indonesia")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle quick question button
if "quick_question" in st.session_state:
    prompt = st.session_state.quick_question
    del st.session_state.quick_question
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("💭 Sedang berpikir..."):
            response = rag_system.chat(prompt)
            st.markdown(response)
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Chat input
if prompt := st.chat_input("💬 Ketik pertanyaan Anda di sini..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("💭 Sedang berpikir..."):
            response = rag_system.chat(prompt)
            st.markdown(response)
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Footer
st.markdown("---")
st.caption("💡 **Tips**: Tanya tentang cuti, jam kerja, benefit, WFH, atau kebijakan HR lainnya!")

📦 Cara Install & Run
Step 1: Install Dependencies
bashpip install -r requirements.txt
Step 2: Run Streamlit App
bashstreamlit run app.py
```

### **Step 3: Buka Browser**

Otomatis akan terbuka di: **http://localhost:8501**

---

## **🎨 Fitur Streamlit App**

✅ **Chat Interface** modern & responsive  
✅ **Sidebar** dengan info & quick questions  
✅ **Welcome message** otomatis  
✅ **Loading spinner** saat AI berpikir  
✅ **Clear chat** button  
✅ **Quick question buttons** untuk pertanyaan umum  
✅ **Custom styling** dengan CSS  
✅ **Emoji support** untuk UI lebih menarik  

---

## **🧪 Test dengan Pertanyaan Ini**

1. "Bagaimana cara mengajukan cuti?"
2. "Jam kerja berapa?"
3. "Benefit apa saja yang ada?"
4. "WFH boleh berapa hari?"
5. "Cara claim asuransi gimana?"

---

## **📸 Screenshot Preview**

Tampilan akan seperti ini:
```
🤖 HRIS Chatbot PT. XYZ
Asisten Virtual HR - Tanya apa saja tentang kebijakan HR, cuti, benefit, dan lainnya!

┌─────────────────────────────────────┐
│ 🤖 Assistant                         │
│ Halo! 👋 Saya asisten virtual HR... │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 💬 Ketik pertanyaan Anda di sini... │
└─────────────────────────────────────┘




---

# Dokumentasi API (HRIS Chatbot)

API REST untuk mengonsumsi HRIS Chatbot dari Flutter, Postman, atau client lain.

---

## Menjalankan API

```bash
# Dari folder project
uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

- **Base URL:** `http://127.0.0.1:8000`
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

Pastikan file `.env` berisi `GROQ_API_KEY`.

---

## Endpoints

### 1. Root – Info API

| Method | URL   | Deskripsi   |
|--------|-------|-------------|
| **GET** | `/`   | Info layanan & versi |

**Response (200):**
```json
{
  "service": "HRIS Chatbot API",
  "version": "2.0.0",
  "docs": "/docs",
  "health": "/health",
  "chat": "POST /chat"
}
```

---

### 2. Health Check

| Method | URL      | Deskripsi        |
|--------|----------|------------------|
| **GET** | `/health` | Cek status server |

**Response (200):**
```json
{
  "status": "ok",
  "service": "hris-chatbot-api"
}
```

---

### 3. Chat – Kirim Pertanyaan ke HR Assistant

| Method | URL    | Deskripsi                          |
|--------|--------|------------------------------------|
| **POST** | `/chat` | Kirim pertanyaan + konteks user (RAG) |

**Request Headers:**
- `Content-Type: application/json`
- `Accept: application/json`

**Request Body:**

| Field       | Type   | Wajib | Deskripsi                                      |
|------------|--------|-------|-------------------------------------------------|
| `message`  | string | ✅    | Pertanyaan user (min 1 karakter)                |
| `user_data`| object | ✅    | Data user dari Flutter (Hive) untuk konteks AI  |

**Contoh Body (Postman / raw JSON):**

```json
{
  "message": "Berapa kali saya terlambat bulan ini?",
  "user_data": {
    "nama": "John Doe",
    "nik": "123456",
    "jabatan": "Software Engineer",
    "departemen": "IT",
    "bagian": "Development",
    "sisa_cuti": "12",
    "periode_mulai_cuti": "2024-01-01",
    "periode_akhir_cuti": "2024-12-31",
    "attendance": {
      "bulan": "02",
      "tahun": "2026",
      "jumlah_hadir": "20",
      "terlambat": "2"
    }
  }
}
```

**Contoh minimal (jika Flutter belum kirim user_data lengkap):**

```json
{
  "message": "Cara ajukan cuti?",
  "user_data": {}
}
```

**Response (200):**

| Field     | Type   | Deskripsi                    |
|-----------|--------|------------------------------|
| `success` | bool   | `true` jika sukses           |
| `message` | string | Jawaban dari HR assistant    |
| `query`   | string | Pertanyaan yang dikirim      |

**Contoh Response:**
```json
{
  "success": true,
  "message": "Berdasarkan data absensi Anda di periode 02/2026, Anda terlambat 2 kali.",
  "query": "Berapa kali saya terlambat bulan ini?"
}
```

---

## Kode Error

| Kode | Arti                | Penyebab umum                          |
|------|---------------------|----------------------------------------|
| **422** | Validation Error   | `message` kosong, atau `user_data` tidak ada |
| **500** | Server Error       | `GROQ_API_KEY` belum di-set atau error internal |

**Contoh response error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Contoh response error (500):**
```json
{
  "detail": "Error memproses chat: ..."
}
```

---

## Test di Postman

1. **Method:** `POST`
2. **URL:** `http://127.0.0.1:8000/chat`
3. **Headers:**  
   - `Content-Type` = `application/json`
4. **Body** → pilih **raw** → **JSON**, isi:
   ```json
   {
     "message": "Jam kerja berapa?",
     "user_data": {}
   }
   ```
5. Klik **Send**. Jawaban ada di field `message` di response.

---

## Ringkasan

| Item          | Nilai                                                    |
|---------------|----------------------------------------------------------|
| Base URL      | `http://127.0.0.1:8000`                                  |
| Chat endpoint | `POST /chat`                                             |
| Body          | `{ "message": "...", "user_data": { ... } }`            |
| Response      | `{ "success", "message", "query" }`                       |

---

# Menjalankan Aplikasi

## RUN API

```bash
uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

## RUN WEB (Streamlit)

```bash
# 1. Hapus cache lama (optional)
pip uninstall sentence-transformers -y

# 2. Install dependencies baru
pip install streamlit groq chromadb python-dotenv

# 3. Run
streamlit run app.py
```