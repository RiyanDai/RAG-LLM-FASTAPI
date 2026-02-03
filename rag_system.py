# rag_system.py

import os
from groq import Groq
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from hris_knowledge_base import HRIS_DOCUMENTS

class HRISRagSystem:
    def __init__(self, groq_api_key: str):
        """
        Initialize RAG system WITHOUT auto-fetching user data
        User data akan di-set manual via set_user_data()
        """
        self.groq_client = Groq(api_key=groq_api_key)
        self.user_context = {}
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        self.collection = self.chroma_client.get_or_create_collection(
            name="hris_knowledge",
            metadata={"description": "HRIS knowledge base for PT. Gelora Aksara Pratama"}
        )
        
        self.load_documents()
    
    def load_documents(self):
        """Load HRIS documents into ChromaDB"""
        if self.collection.count() > 0:
            return
        
        documents = [doc["content"] for doc in HRIS_DOCUMENTS]
        ids = [doc["id"] for doc in HRIS_DOCUMENTS]
        metadatas = [{"category": doc["category"]} for doc in HRIS_DOCUMENTS]
        
        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
    
    def set_user_data(self, user_data: Dict):
        """
        SET user data dari Flutter (Hive local storage)
        
        Expected format:
        {
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
                "jumlah_tidak_hadir": "0",
                "alpa": "0",
                "terlambat": "2",
                "tidak_checkout": "1",
                "layoff": "0",
                "pulang_cepat": "0",
                "kelebihan_jam": "5"
            }
        }
        """
        self.user_context = user_data
        print(f"User data set: {user_data.get('nama', 'Unknown')} ({user_data.get('nik', 'N/A')})")
    
    def format_user_context(self) -> str:
        """
        FORMAT user data jadi string untuk LLM
        """
        if not self.user_context:
            return "Tidak ada data personal user yang tersedia."
        
        # Data personal
        nama = self.user_context.get('nama', 'N/A')
        nik = self.user_context.get('nik', 'N/A')
        jabatan = self.user_context.get('jabatan', 'N/A')
        departemen = self.user_context.get('departemen', 'N/A')
        bagian = self.user_context.get('bagian', 'N/A')
        sisa_cuti = self.user_context.get('sisa_cuti', '0')
        periode_mulai = self.user_context.get('periode_mulai_cuti', 'N/A')
        periode_akhir = self.user_context.get('periode_akhir_cuti', 'N/A')
        
        # Data absensi
        att = self.user_context.get('attendance', {})
        bulan = att.get('bulan', 'N/A')
        tahun = att.get('tahun', 'N/A')
        
        context_text = f"""
=== DATA KARYAWAN ===
Nama: {nama}
NIK: {nik}
Jabatan: {jabatan}
Departemen: {departemen}
Bagian: {bagian}

CUTI:
- Sisa Cuti: {sisa_cuti} hari
- Periode: {periode_mulai} s/d {periode_akhir}

=== DATA ABSENSI (Periode: {bulan}/{tahun}) ===
RINGKASAN KEHADIRAN:
- Hadir: {att.get('jumlah_hadir', '0')} hari
- Tidak Hadir: {att.get('jumlah_tidak_hadir', '0')} hari
- Alpa: {att.get('alpa', '0')} hari
- Terlambat: {att.get('terlambat', '0')} kali
- Tidak Checkout: {att.get('tidak_checkout', '0')} kali
- Pulang Cepat: {att.get('pulang_cepat', '0')} kali
- Layoff: {att.get('layoff', '0')} hari
- Kelebihan Jam (Lembur): {att.get('kelebihan_jam', '0')} hari

=== END DATA ===
"""
        return context_text
    
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
        """
        Generate response dengan USER CONTEXT + KNOWLEDGE BASE
        """
        
        # Build context dari knowledge base
        kb_context = "\n\n---\n\n".join([doc["content"] for doc in context_docs])
        
        # Ambil user context
        user_context = self.format_user_context()
        
        # System prompt
        system_prompt = f"""
Kamu adalah AI Assistant HRIS untuk PT. Gelora Aksara Pratama.

{user_context}

KNOWLEDGE BASE (Kebijakan & Info Umum):
{kb_context}

INSTRUKSI:
- Jika user tanya tentang DATA PERSONAL mereka (nama, jabatan, absensi, cuti, terlambat, lembur), gunakan DATA KARYAWAN & DATA ABSENSI di atas
- Jika user tanya tentang KEBIJAKAN UMUM (cara cuti, jam kerja, benefit), gunakan KNOWLEDGE BASE
- Jawab dengan Bahasa Indonesia yang formal tapi ramah
- Jika informasi tidak ada, katakan dengan jujur dan arahkan ke HR
- Berikan jawaban yang jelas dan terstruktur

KONTAK HR (gunakan jika perlu escalate):
Email: hr@xyz.com
Phone: (021) 1234-5678 / ext. 100
Jam operasional: 09:00-17:00 WIB
"""

        # Call Groq API
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            return f"Error saat generate response: {str(e)}"
    
    def chat(self, query: str, show_context: bool = False) -> str:
        """
        Main chat function
        """
        # Retrieve context dari knowledge base
        context_docs = self.retrieve_context(query, top_k=3)
        
        # Debug mode
        if show_context:
            print("\n" + "="*60)
            print("USER CONTEXT:")
            print(self.format_user_context())
            print("\nKNOWLEDGE BASE CONTEXT:")
            for doc in context_docs:
                print(f"\n- {doc['metadata'].get('category', 'Unknown')}")
                print(doc['content'][:200] + "...")
            print("="*60 + "\n")
        
        # Generate response
        response = self.generate_response(query, context_docs)
        
        return response