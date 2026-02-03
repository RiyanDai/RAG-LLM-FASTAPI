# main.py

import os
from dotenv import load_dotenv
from rag_system import HRISRagSystem

# Load environment variables
load_dotenv()

def main():
    # Initialize RAG system
    print("=" * 60)
    print("🚀 HRIS Chatbot with RAG + Groq")
    print("=" * 60)
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        print("❌ Error: GROQ_API_KEY not found in environment variables")
        print("Please create .env file with: GROQ_API_KEY=your_api_key")
        return
    
    rag_system = HRISRagSystem(groq_api_key=groq_api_key)
    
    print("\n✅ System ready!")
    print("=" * 60)
    
    # Chat loop
    while True:
        print("\n" + "=" * 60)
        user_input = input("👤 Tanya HR: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['exit', 'quit', 'keluar']:
            print("\n👋 Terima kasih! Sampai jumpa!")
            break
        
        # Get response
        response = rag_system.chat(user_input, show_context=False)
        
        print(f"\n🤖 HR Assistant:\n{response}")
    
if __name__ == "__main__":
    main()