
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
#heading(level: 1)[종합 분석]
#data.content

#v(1cm)

// Professor Recommendations
#heading(level: 1)[추천 교수진 및 연구실]

#for prof in data.professors [
  #block(breakable: false)[
    #rect(width: 100%, radius: 5pt, fill: rgb("#f0f8ff"), inset: 1em)[
      #text(size: 12pt, weight: "bold")[#prof.name] (#prof.name_ko) \
      #v(0.5em)
      *연구 분야:* #prof.interests \
      *추천 사유:* #prof.reason
    ]
    #v(0.5em)
  ]
]

#v(2cm)
#align(center + bottom)[
  #text(size: 10pt, fill: gray)[Univ-Insight AI Agent에 의해 생성된 리포트입니다.]
]
