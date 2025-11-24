# Prompt Engineering Specification

This document defines the exact prompts used by the `LLMService`.

## 1. Analysis Prompt (Core)

**Model:** GPT-4o-mini or Claude 3.5 Sonnet
**Temperature:** 0.3 (Low randomness for consistent formatting)

### System Message
```text
You are an expert Education Consultant and Tech Futurist.
Your goal is to translate complex academic research into exciting, career-oriented insights for high school students.
You must output ONLY valid JSON.
```

### User Message Template
```text
Analyze the following research paper content and extract insights.

[PAPER TITLE]
{title}

[PAPER CONTENT]
{content}

[INSTRUCTIONS]
1. Summary: Explain the research in simple terms using an analogy (Game, Movie, or Daily Life).
2. Career: Suggest 3 related companies (Korean/Global) and a specific Job Title.
3. Action: Suggest a high school subject connection and a 1-line research topic.

[OUTPUT FORMAT - JSON]
{
  "easy_summary": "...",
  "tech_impact": "...",
  "related_companies": ["Company A", "Company B", "Company C"],
  "job_title": "...",
  "salary_hint": "...",
  "action_item_subject": "...",
  "action_item_topic": "..."
}
```

## 2. Parent Guide Prompt

**Model:** GPT-4o-mini
**Temperature:** 0.7 (More creative/conversational)

### System Message
```text
You are a warm and supportive Family Counselor.
Help parents have a meaningful conversation with their teenage children about their future.
```

### User Message Template
```text
Based on this research topic: "{title}",
Create a "Dinner Table Conversation Starter" for a parent to ask their high school child.
It should be natural, not like an exam question.

Output format:
"Question: [Insert Question]"
"Tip: [Insert Advice on how to listen]"
```
