
#let data = json("report_data.json")

#set page(paper: "a4", margin: 2cm)
#set text(font: ("Malgun Gothic", "Noto Sans CJK KR", "Arial", "UnDotum"), size: 11pt, lang: "ko")

// Title
#align(center)[
  #text(size: 24pt, weight: "bold")[대학 진로 가이드 리포트]
  
  #v(1cm)
  #text(size: 14pt)[#data.user_name 님을 위한 맞춤형 분석]
]

#v(2cm)

// Info Box
#rect(width: 100%, radius: 5pt, stroke: 1pt + gray, inset: 1em)[
  *생성 일자:* #data.report_date \
  *관심 분야:* #data.interests
]

#v(1cm)

// Main Content (LLM Generated)
// Main Content (LLM Generated)
#heading(level: 1)[맞춤형 연구 분석]

#for item in data.analysis_results [
  #block(breakable: true)[
    #rect(width: 100%, radius: 8pt, stroke: 1pt + rgb("#333333"), inset: 1.5em)[
      
      // 1. Title Section
      #text(size: 16pt, weight: "bold", fill: rgb("#2c3e50"))[핵심 기술: #item.topic_easy] \
      #v(0.5em)
      #text(size: 11pt, style: "italic", fill: rgb("#7f8c8d"))[(전문 용어: #item.topic_technical)]
      
      #line(length: 100%, stroke: 0.5pt + gray)
      #v(0.5em)

      // 2. Explanation Section
      #text(size: 13pt, weight: "bold")[🧐 이게 뭔가요?] \
      #v(0.5em)
      #text(size: 11pt)[#item.explanation]
      
      #v(1em)

      // 3. Deep Dive Section (Progressive Disclosure)
      #rect(width: 100%, radius: 5pt, fill: rgb("#f8f9fa"), stroke: 0.5pt + gray, inset: 1em)[
        #text(size: 12pt, weight: "bold")[📚 더 깊이 알아보기 (전문가 자료)] \
        #v(0.5em)
        
        *심화 학습 키워드:* #item.deep_dive.keywords.join(", ") \
        #v(0.3em)
        *추천 자료:* #item.deep_dive.recommendations.join(", ") \
        #v(0.3em)
        *관련 기초 지식:* #item.deep_dive.related_concepts.join(", ") \
        #v(0.5em)
        
        #if item.reference_link != "" [
           *참고 링크:* #link(item.reference_link)[#item.reference_link]
        ]
      ]

      #v(1em)

      // 4. Career & Action Plan
      #grid(
        columns: (1fr, 1fr),
        gutter: 1em,
        [
          #text(size: 12pt, weight: "bold")[💼 진로 가이드] \
          - *직업:* #item.career_path.job_title \
          - *관련 기업:* #item.career_path.companies.join(", ") \
          - *연봉 힌트:* #item.career_path.avg_salary_hint
        ],
        [
          #text(size: 12pt, weight: "bold")[🚀 실행 계획] \
          - *추천 과목:* #item.action_item.subjects.join(", ") \
          - *탐구 주제:* #item.action_item.research_topic
        ]
      )
    ]
  ]
  #v(1.5cm)
]

#v(1cm)
#align(center + bottom)[
  #text(size: 10pt, fill: gray)[Univ-Insight AI Agent에 의해 생성된 리포트입니다.]
]
