"""
AI Assistant for Price Sense AI
Provides natural language explanations and answers questions
"""

import os
from typing import Dict, List

def get_ai_assistant():
    """
    Get AI assistant instance (requires OpenAI API key)
    Returns None if API key not configured
    """
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("⚠️ OpenAI API key not found. AI Assistant will be disabled.")
        return None
    
    try:
        from openai import OpenAI
        return AIAssistant(api_key)
    except ImportError:
        print("⚠️ OpenAI library not installed. Run: pip install openai")
        return None


class AIAssistant:
    """AI-powered assistant for explaining promotions"""
    
    def __init__(self, api_key: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        
    def explain_analysis(self, result: Dict) -> str:
        """Generate natural language explanation of analysis results"""
        
        prompt = f"""
        Explain this promotion analysis in simple, business-friendly language:
        
        Product: {result['product']['name']}
        Discount: {result['discount_pct']}%
        Duration: {result['duration_days']} days
        
        Results:
        - Net Profit: ${result['financial']['net_profit']:,.2f}
        - ROI: {result['financial']['roi_pct']:.1f}%
        - Sales Lift: {result['lift']['lift_pct']}%
        - Risk Score: {result['risks']['risk_score']}/100
        - Recommendation: {result['recommendation']['decision']}
        
        Provide a brief, executive-level summary (3-4 sentences) highlighting the key insights.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a business analyst explaining promotion results."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"Could not generate AI explanation: {str(e)}"
    
    def answer_question(self, result: Dict, question: str, chat_history: List) -> str:
        """Answer questions about the analysis"""
        
        context = f"""
        Analysis Context:
        Product: {result['product']['name']}
        Current Analysis: {result['discount_pct']}% discount for {result['duration_days']} days
        Net Profit: ${result['financial']['net_profit']:,.2f}
        ROI: {result['financial']['roi_pct']:.1f}%
        Lift: {result['lift']['lift_pct']}%
        Recommendation: {result['recommendation']['decision']}
        """
        
        messages = [
            {"role": "system", "content": "You are a pricing strategy expert helping with promotion decisions."},
            {"role": "assistant", "content": context}
        ]
        
        # Add chat history
        messages.extend(chat_history[-6:])  # Last 3 exchanges
        
        # Add current question
        messages.append({"role": "user", "content": question})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"Could not generate answer: {str(e)}"
