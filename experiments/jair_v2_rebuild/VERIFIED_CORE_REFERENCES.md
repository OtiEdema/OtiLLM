# Verified core references for JAIR v2.0 rebuild

The following references have been checked against public primary/authoritative
sources and should form the core of the final Related Work and benchmark
citations. Final BibTeX should be imported from the publisher/venue records
where available.

## Retrieval and adaptive retrieval

**Lewis et al. (2020)**  
Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir
Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen-tau Yih,
Tim Rocktäschel, Sebastian Riedel, and Douwe Kiela.  
*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.*  
NeurIPS 2020 / arXiv:2005.11401.

Use to support the definition of RAG as combining parametric and
non-parametric memory for knowledge-intensive generation.

**Asai et al. (2024)**  
Akari Asai, Zeqiu Wu, Yizhong Wang, Avirup Sil, and Hannaneh Hajishirzi.  
*Self-RAG: Learning to Retrieve, Generate, and Critique through
Self-Reflection.*  
ICLR 2024 / arXiv:2310.11511.

Use to position OtiLLM relative to adaptive retrieval and self-reflection.
Self-RAG adaptively retrieves on demand and uses reflection signals; OtiLLM's
claimed distinction is the broader governed execution decision rather than a
new retrieval model.

## Reasoning and acting

**Yao et al. (2023)**  
Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran,
Karthik Narasimhan, and Yuan Cao.  
*ReAct: Synergizing Reasoning and Acting in Language Models.*  
ICLR 2023 / arXiv:2210.03629.

Use to position the bounded ReAct-style baseline. The manuscript must retain
the limitation that the publication baseline is not a full unrestricted
external-tool ReAct implementation.

## Selective prediction / abstention

**Kamath, Jia, and Liang (2020)**  
Amita Kamath, Robin Jia, and Percy Liang.  
*Selective Question Answering under Domain Shift.*  
ACL 2020, pp. 5684–5696. DOI: 10.18653/v1/2020.acl-main.503.

Use to motivate abstention and the coverage/accuracy trade-off. Their selective
QA formulation explicitly treats answering as many questions as possible while
maintaining high accuracy.

## Policy safety and guardrails

**Bai et al. (2022)**  
Yuntao Bai et al.  
*Constitutional AI: Harmlessness from AI Feedback.*  
arXiv:2212.08073.

Use as background for principle-based policy control/alignment, not as a direct
runtime equivalent of OtiLLM.

**Dong et al. (2024)**  
Yi Dong, Ronghui Mu, Yanghao Zhang, Siqi Sun, Tianle Zhang, Changshun Wu,
Gaojie Jin, Yi Qi, Jinwei Hu, Jie Meng, Saddek Bensalem, and Xiaowei Huang.  
*Safeguarding Large Language Models: A Survey.*  
arXiv:2406.02622.

Use to support the broad guardrail/safeguard landscape and the need for
systematic safety mechanisms.

## XSTest

**Röttger et al. (2024)**  
Paul Röttger, Hannah Kirk, Bertie Vidgen, Giuseppe Attanasio,
Federico Bianchi, and Dirk Hovy.  
*XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large
Language Models.*  
NAACL 2024, pp. 5377–5400. DOI: 10.18653/v1/2024.naacl-long.301.

XSTest contains 250 safe prompts and 200 unsafe contrast prompts. It is designed
to reveal exaggerated safety behaviour, particularly false refusal of safe
prompts. This is the authoritative citation for the 450-item policy benchmark.

## Citation-use constraints

- Do not cite these works as evidence that OtiLLM is the first system to combine
  retrieval, abstention, policy control, or agentic orchestration.
- Use them to establish the neighbouring research areas and then state the
  narrower integrative runtime contribution.
- Do not describe XSTest as a general safety benchmark for all harms; its
  purpose is specifically to probe exaggerated safety and safe/unsafe refusal
  calibration.
- Final references must be rendered using the current JAIR author-year
  bibliography style.
