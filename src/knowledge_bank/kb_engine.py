"""
Knowledge Bank Engine - Extracts company intelligence from documents

This engine is domain-agnostic and adaptively extracts intelligence from
various knowledge bank formats (PDFs, docs, structured/unstructured text).

Supports two extraction modes:
  1. RAG-lite: PDF → Semantic Chunking → LLM (Groq) → TF-IDF Cosine Ranking → Structured Extraction
  2. Regex Fallback: Pattern-matching heuristics for when no LLM is available
"""

import json
import re
import os
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.llm_utils import call_llm_with_retry, parse_json_response

# Optional RAG-lite dependencies
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class KnowledgeBankEngine:
    """Extracts and structures company knowledge from text documents.

    Supports RAG-lite mode (PDF + LLM) and regex fallback mode.
    """

    def __init__(self, config_path: str = 'config/config.yaml'):
        self.north_star = None
        self.feature_goal_map = None
        self.tone_hook_matrix = None
        self.detected_domain = None
        self.rag_mode_used = False

        # Load config for tones and other configurable values
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            self.config = {}

        # Get communication config with defaults
        comm_config = self.config.get('communication', {})
        self.allowed_tones = comm_config.get('allowed_tones', [
            'encouraging', 'friendly', 'aspirational', 'urgent',
            'celebratory', 'motivational', 'supportive'
        ])
        self.forbidden_tones = comm_config.get('forbidden_tones', [
            'aggressive', 'desperate', 'salesy', 'guilt-tripping',
            'condescending', 'pushy'
        ])
        self.tone_by_lifecycle = comm_config.get('tone_by_lifecycle', {
            'trial': ['encouraging', 'friendly', 'aspirational', 'supportive'],
            'paid': ['celebratory', 'friendly', 'aspirational', 'motivational'],
            'churned': ['friendly', 'urgent', 'aspirational', 'curious'],
            'inactive': ['curious', 'friendly', 'inviting']
        })

        # KB / RAG config
        kb_config = self.config.get('knowledge_bank', {})
        self.kb_mode = kb_config.get('mode', 'auto')  # auto | rag | regex
        self.llm_model = kb_config.get('llm_model', 'llama-3.1-8b-instant')
        self.rag_top_chunks = kb_config.get('rag_top_chunks', 15)
        self.rag_vocab_size = kb_config.get('rag_vocab_size', 25)

        # Initialize Groq client if available
        self.groq_client = None
        api_key = os.environ.get("GROQ_API_KEY", "")
        if api_key and GROQ_AVAILABLE:
            try:
                self.groq_client = Groq(api_key=api_key)
            except Exception:
                pass

    # ===================================================================
    # PUBLIC API
    # ===================================================================

    def process_knowledge_bank(self, kb_text_or_pdf: str) -> Dict[str, Any]:
        """
        Process knowledge bank text/PDF and extract all intelligence.

        If a PDF path is provided and RAG-lite dependencies are available,
        uses the RAG-lite pipeline. Otherwise falls back to regex extraction.

        Args:
            kb_text_or_pdf: Raw text OR path to a PDF file

        Returns:
            dict: Structured knowledge bank data
        """
        kb_text = kb_text_or_pdf
        pdf_path = None

        # Check if input is a PDF path
        if kb_text_or_pdf and Path(kb_text_or_pdf).suffix.lower() == '.pdf' and Path(kb_text_or_pdf).exists():
            pdf_path = kb_text_or_pdf

        # Decide mode
        use_rag = False
        if self.kb_mode == 'rag':
            use_rag = True
        elif self.kb_mode == 'auto':
            use_rag = (self.groq_client is not None and SKLEARN_AVAILABLE)
        # mode == 'regex' → use_rag stays False

        if use_rag and pdf_path and PYMUPDF_AVAILABLE:
            print("\n   [RAG] Using RAG-lite pipeline (PDF -> LLM -> TF-IDF)")
            return self._process_rag_lite(pdf_path)
        elif use_rag and not pdf_path and self.groq_client:
            # Have LLM but no PDF — extract text, still try RAG on raw text
            print("\n   [RAG] Using RAG-lite pipeline (Text -> LLM -> TF-IDF)")
            return self._process_rag_lite_from_text(kb_text)
        else:
            print("\n   [Regex] Using regex-based extraction (no LLM)")
            return self._process_regex(kb_text)

    # ===================================================================
    # RAG-LITE PIPELINE
    # ===================================================================

    def _process_rag_lite(self, pdf_path: str) -> Dict[str, Any]:
        """Full RAG-lite pipeline from PDF."""
        self.rag_mode_used = True

        # Step 1: Extract text from PDF
        raw_text = self._extract_text_from_pdf(pdf_path)
        return self._process_rag_lite_from_text(raw_text)

    def _process_rag_lite_from_text(self, raw_text: str) -> Dict[str, Any]:
        """RAG-lite pipeline from raw text.

        Two-step LLM pipeline:
          Step 1: Domain detection + vocabulary extraction (VOCAB_PROMPT)
          Step 2: Full intelligence extraction using top TF-IDF chunks (SYSTEM_PROMPT + USER_PROMPT)
        """
        self.rag_mode_used = True

        # Dynamic Scaling: Proportionate to document size
        word_count = len(raw_text.split())
        self.rag_vocab_size = min(60, 20 + (word_count // 500))
        self.rag_top_chunks = min(30, 10 + (word_count // 1000))
        print(f"   [RAG] Input size: {word_count} words. Scaled params: vocab={self.rag_vocab_size}, chunks={self.rag_top_chunks}")

        # Step 2: Semantic chunking
        chunks = self._semantic_chunking(raw_text)
        print(f"   [RAG] Created {len(chunks)} semantic chunks")

        # Step 3: LLM Call 1 — Extract domain + dynamic vocabulary
        domain, vocab = self._llm_extract_domain_vocab(raw_text)
        self.detected_domain = domain
        print(f"   [RAG] Detected domain: {domain}")
        print(f"   [RAG] Extracted {len(vocab)} vocabulary terms")

        # Step 4: TF-IDF cosine ranking
        top_chunks = self._rank_chunks_cosine(chunks, vocab)
        print(f"   [RAG] Selected top {len(top_chunks)} relevant chunks")

        # Step 5: LLM Call 2 — Structured intelligence extraction
        #         Uses detected domain + vocabulary from Step 3
        extracted = self._llm_extract_intelligence(top_chunks, domain, vocab)

        # Build structured outputs from LLM extraction
        self.north_star = self._build_north_star_from_rag(extracted)
        self.feature_goal_map = self._build_feature_goal_map_from_rag(extracted)
        self.tone_hook_matrix = self._build_tone_hook_matrix_from_rag(extracted, raw_text)

        return {
            'north_star': self.north_star,
            'feature_goal_map': self.feature_goal_map,
            'tone_hook_matrix': self.tone_hook_matrix,
            'detected_domain': self.detected_domain
        }

    def _extract_text_from_pdf(self, path: str) -> str:
        """Extract text from PDF using PyMuPDF."""
        print(f"   [RAG] Extracting text from PDF: {path}")
        try:
            doc = fitz.open(path)
            text = " ".join([page.get_text("text") for page in doc])
            doc.close()
            return text
        except Exception as e:
            print(f"   [WARN] PDF extraction failed: {e}, using fallback text")
            return "Company provides core platform features for user engagement and retention."

    def _semantic_chunking(self, text: str, n_sents: int = 5) -> List[str]:
        """Split text into overlapping semantic chunks."""
        sents = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        step = max(1, n_sents - 2)  # Overlap of 2 sentences
        for i in range(0, len(sents), step):
            chunk_txt = " ".join(sents[i:i + n_sents]).strip()
            if len(chunk_txt.split()) > 15:
                chunks.append(chunk_txt)
        return chunks

    def _llm_extract_domain_vocab(self, text: str) -> tuple:
        """LLM Call 1: Extract domain and dynamic vocabulary using VOCAB_PROMPT."""
        if not self.groq_client:
            return self._detect_domain(text), []

        VOCAB_TERMS = self.rag_vocab_size
        # Use first ~3000 chars as document abstract for vocab extraction
        doc_abstract = text[:3000]

        prompt = f"""You are a business analyst smart intelligence product manager.
Tailor your thinking as follows:
-Create a thinking and mind map of the product/industry/firm/profit-based institution from the details provided
-make your understanding of the working model from the institution
-use these to comprehend further
-for domain recognition take instances of real world companies that frequently use these particular approaches like zomato for food delivery,blinkit for ecommerce,bookmyshow for entertainment,ola for cab services,etc
Read the document abstract below and return ONLY a JSON object containing two keys:
1. "domain": A tailor-made, highly specific 1-3 word business domain or industry for this document (e.g. 'B2B SaaS', 'Telemedicine Gamification', 'Consumer Fintech').
2. "vocabulary": A JSON array of exactly {VOCAB_TERMS} short business/KPI phrases (1-4 words each) that are the most analytically relevant for this specific document — metrics, strategic themes, behavioral concepts, or research variables.

No generic words. No markdown. Just the JSON object.

ABSTRACT:
{doc_abstract}

Example format: {{"domain": "EdTech Engagement", "vocabulary": ["brand awareness", "retention"]}}"""

        try:
            raw = call_llm_with_retry(
                system_prompt="You are a business analyst. Return valid JSON only.",
                user_prompt=prompt,
                temperature=0.3,
            )
            if not raw:
                return self._detect_domain(text), []
            data = parse_json_response(raw)
            if not data:
                data = json.loads(raw)
            domain = data.get('domain', 'Generic')
            vocab = data.get('vocabulary', [])
            # Normalize domain to our standard categories
            domain_normalized = self._normalize_domain(domain)
            return domain_normalized, vocab[:VOCAB_TERMS]
        except Exception as e:
            print(f"   [WARN] LLM vocab extraction failed: {e}")
            return self._detect_domain(text), []

    def _normalize_domain(self, domain_str: str) -> str:
        """Normalize LLM-returned domain string to standard category."""
        d = domain_str.lower()
        if any(kw in d for kw in ['edtech', 'education', 'learning', 'tutor']):
            return 'edtech'
        elif any(kw in d for kw in ['fintech', 'finance', 'banking', 'payment']):
            return 'fintech'
        elif any(kw in d for kw in ['health', 'fitness', 'wellness', 'medical', 'telemedicine']):
            return 'health'
        elif any(kw in d for kw in ['entertainment', 'streaming', 'media', 'video']):
            return 'entertainment'
        elif any(kw in d for kw in ['ecommerce', 'commerce', 'shopping', 'retail', 'delivery', 'food']):
            return 'ecommerce'
        elif any(kw in d for kw in ['social', 'community', 'network']):
            return 'social'
        elif any(kw in d for kw in ['saas', 'b2b', 'enterprise']):
            return 'saas'
        return 'generic'

    def _rank_chunks_cosine(self, chunks: List[str], vocab: List[str]) -> List[Dict]:
        """Rank chunks by TF-IDF cosine similarity against vocabulary."""
        if not chunks or not vocab or not SKLEARN_AVAILABLE:
            # Fallback: return first N chunks
            return [{"text": c, "score": 0.5} for c in chunks[:self.rag_top_chunks]]

        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        try:
            X_chunks = vectorizer.fit_transform(chunks)
            X_vocab = vectorizer.transform(vocab)
            sim_scores = sklearn_cosine_similarity(X_chunks, X_vocab).mean(axis=1)
            top_idx = np.argsort(sim_scores)[::-1][:self.rag_top_chunks]
            return [{"text": chunks[i], "score": float(sim_scores[i])} for i in top_idx]
        except Exception:
            return [{"text": c, "score": 0.5} for c in chunks[:self.rag_top_chunks]]

    def _llm_extract_intelligence(self, top_chunks: List[Dict], detected_domain: str, dynamic_vocab: List[str] = None) -> Dict:
        """LLM Call 2: Extract structured intelligence from top-ranked chunks.

        Uses the comprehensive SYSTEM_PROMPT + USER_PROMPT provided by the user.
        Extracts: North Star Metric, Feature→Goal Mapping, Allowed Tones, Behavioral Hooks (Octalysis).
        """
        if not self.groq_client:
            return {}

        if dynamic_vocab is None:
            dynamic_vocab = []

        context = "\n---\n".join([c['text'] for c in top_chunks])

        # Mark chunks that contain statistics
        context_with_markers = ""
        for c in top_chunks:
            txt = c['text']
            has_stats = bool(re.search(r'\d+%|\d+\.\d+|statistics|data|metric', txt, re.IGNORECASE))
            prefix = "📊 " if has_stats else ""
            context_with_markers += f"{prefix}{txt}\n========================\n"

        system_prompt = f"""You are a senior business intelligence analyst and product strategist.
Structure your thinking strictly as folllows:
-stick strictly to the domain and supplement from the information given below
-Think like an owner of the company to get layman metrics, the most simple yet most effective metrics demanded below.The metrics whichever you give must be quantifiable by the product/company realistically(use real world simililar products/domain products to structure your thinking)
-Create your perspective of the working of the company/product strictly with respect to only the data given below
-use all of the above to give conclusions which must be enriched with the thinking and synopsis
Domain: [{detected_domain.upper()}].
Key document themes identified: {', '.join(dynamic_vocab[:12])}

Rules:
1. Extract ONLY information explicitly stated or directly implied in the chunks as evidence,dont add information but you can create your thinking to fill the missing pieces without assumptions.
2. NEVER hallucinate metrics, features, or findings not in the text.
3. When making a claim, include an 'evidence' key with a verbatim quote from the chunk,the evidence should not be the full chunk but only a short crisp summary of the core evidence.
4. If a field is absent in the text, use null — never guess.
5. Respond with a single valid JSON object only. No markdown, no prose.

WHAT TO EXTRACT
----------------------------------------

1️ NORTH STAR METRIC

The North Star Metric is the single most important metric the company optimizes for.
It represents the core value delivered to users.
Think as an owner of the company to get layman metrics, the most simple yet most effective metrics demanded below.The metrics whichever you give must be quantifiable by the product/company realistically(use real world simililar products/domain products to structure your thinking)

If no clear North Star metric exists, return null values.
-Never give abstract wordings which seem important,even if you feel something very important,express it as quantifiable easily using the companys framework.Prefer numbers,rates,expressions or entities quantifiable which most importantly influences the performances
-strictly return only in the form of counts,numbers,rates entities or maximixable quantities which can be computed(think thrice that your view matches this)
-i strictly dont want abstract capabilities or ablilities
----------------------------------------

2️ FEATURE → GOAL MAPPING

Extract product or marketing features and the user goal they serve,this list should be exhaustive of the pdf.
Strictly dont extract architecture,data pipelines and and datasets,we need goals not capabilities of the system
If a feature description only explains technical capability,rewrite the goal as the user or business outcome it enables.I strictly dont want any technical pipeline elements,backend engines,architectures,pipelines ingesters or anything heavily technical in the goal section
It should be strictly the features catering to user not any developer or technician.Think as a user consuming the product/firm

Feature examples:
- tools
- dashboards
- algorithms
- services
- product capabilities

Goal examples:
- reduce fraud
- improve diagnostic accuracy
- increase engagement
- enable faster decisions

Each mapping should connect:

FEATURE → USER VALUE / BUSINESS GOAL

----------------------------------------

3️ ALLOWED TONES

Based on the domain and language used in the document, infer 3–5 communication tones suitable for the brand.
Tone refers to the **style of language used when communicating with users**.
Here think like a psychological and linguistic expert extracting information from features,goals and language expressions 
Do NOT infer tone purely from the industry domain-this is very important.

Instead, determine tone by analyzing **how the company writes**, based on:

• sentence structure  
• vocabulary  
• claims style  
• use of statistics or research  
• emotional vs factual language  

Examples of tones include:

scientific  
professional  
authoritative  
educational  
supportive  
analytical  
data-driven  
friendly  
reassuring  

Return tones which suits a notification platform for the specific product/domain inferred from the context

----------------------------------------

You are analyzing product documentation to identify **behavioral hooks** using the **Octalysis Framework**.

The Octalysis framework, created by Yu-kai Chou, explains **why users repeatedly engage with a product** by identifying the **core motivations that drive user behavior**.

Your goal is to detect **product behaviors that activate these motivations**.

A behavioral hook represents a **repeatable user interaction with a product feature that triggers motivation and produces value or feedback**.

Hooks must describe **user behavior**, not internal system operations.

-------------------------------------------------
OCTALYSIS FRAMEWORK — 8 MOTIVATIONAL DRIVES
-------------------------------------------------

1. Epic Meaning & Calling  
Users feel they are contributing to a greater purpose, mission, or impact.

2. Development & Accomplishment  
Users feel progress, mastery, achievement, or improvement in their performance.

3. Empowerment of Creativity & Feedback  
Users experiment, explore strategies, simulate options, and receive feedback on their actions.

4. Ownership & Possession  
Users control, customize, manage, or improve something they perceive as theirs (data, dashboards, assets).

5. Social Influence & Relatedness  
Users interact with others through collaboration, recognition, mentorship, competition, or belonging.

6. Scarcity & Impatience  
Users are motivated by limited access, exclusivity, or waiting to unlock something valuable.

7. Unpredictability & Curiosity  
Users explore unknown information, discover insights, or investigate patterns.

8. Loss & Avoidance  
Users act to prevent negative outcomes, risks, missed opportunities, or deterioration.

-------------------------------------------------
DRIVE CLASSIFICATION GUIDELINES
-------------------------------------------------

Use the following reasoning rules when mapping behaviors to motivational drives:

• If the behavior prevents risk, failure, or deterioration → **Loss & Avoidance**

• If the behavior involves discovering patterns, exploring unknown data, or investigating information → **Unpredictability & Curiosity**

• If the behavior involves testing strategies, experimenting with scenarios, or comparing outcomes → **Empowerment of Creativity & Feedback**

• If the behavior improves skill, mastery, performance, or measurable progress → **Development & Accomplishment**

-------------------------------------------------
WHAT YOU MUST EXTRACT
-------------------------------------------------

Identify **behavioral hooks** present in the product documentation.

Each hook must contain:

• octalysis_drive  
• hook_name  
• trigger  
• reward  
• feature_source  
• evidence

Definitions:

trigger  
The **event experienced by the user** that initiates engagement.

reward  
The **value, insight, or feedback** the user gains from the interaction.

feature_source  
The **product feature or capability** that enables the behavior.

evidence  
A **verbatim quote from the document** that supports the hook.

-------------------------------------------------
IMPORTANT EXTRACTION RULES
-------------------------------------------------

• Hooks must describe **user behavior**, not backend system operations.  
• Avoid technical descriptions such as model processing or data pipelines.  
• Triggers must represent **events experienced by the user** (alerts, dashboards, simulations, insights).  
• Rewards must represent **user-perceived value or feedback**.  
• Only include hooks that are **clearly supported by text evidence**.  
• If the motivational drive cannot be confidently determined, **exclude the hook**.  

Return minimum 4 to maximum 6 hooks.

-------------------------------------------------
INTERNAL REASONING PROCESS (DO NOT OUTPUT)
-------------------------------------------------

Perform the following reasoning steps internally before generating the answer:

1. Scan the document for **motivational signals** indicating user engagement with product features.

2. Identify the **product feature** responsible for enabling the behavior.

3. Determine the **behavioral loop**:
   feature → trigger → user action → reward.

4. Map the behavior to the **most appropriate Octalysis motivational drive** using the classification rules.

5. Validate that the behavior represents a **clear user interaction** rather than a technical system function.

6. Confirm that a **verbatim evidence quote** from the text supports the hook.

7. Discard weak, speculative, or unsupported hooks.


Before returning the final answer, verify that each hook follows this logic:

feature → trigger → reward → motivational drive

Triggers must describe events experienced by the user 
(e.g., alerts, dashboards, simulations, explanations).

System inputs such as sensor data, data ingestion, or model processing 
must never be used as triggers.

DOCUMENT CHUNKS

{context}
"""

        user_prompt = f"""Extract a complete PM + analyst intelligence report from the chunks below.

JSON schema:
{{
  "company_name": "string or null",
  "domain": "{detected_domain}",
  "north_star_metric": {{
    "name": "string or null",
    "definition": "string or null",
    "why_it_matters": "string or null",
    "evidence": "verbatim quote from chunks"
  }},
  "feature_goal_mapping": [
    {{"feature": "product or marketing feature", "goal": "user need it serves","evidence": "verbatim quote from document"}}
  ],
  "allowed_tones": ["tone1","tone2","tone3","tone4"],
  "behavioral_hooks": [
    {{
      "hook": "name of behavior pattern (Octolysis)",
      "octolysis": "actual octolysis metric",
      "trigger": "what initiates behavior",
      "reward": "what value user receives",
      "evidence": "verbatim quote"
    }}
  ]
}}

DOCUMENT CHUNKS (📊 = contains statistics):
========================
{context_with_markers}
========================
Return JSON only:"""

        try:
            raw = call_llm_with_retry(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
            )
            if not raw:
                return {}
            result = parse_json_response(raw)
            if not result:
                result = json.loads(raw)
            print(f"   [RAG] LLM extraction complete -- company: {result.get('company_name', 'N/A')}")
            return result
        except Exception as e:
            print(f"   [WARN] LLM intelligence extraction failed: {e}")
            return {}

    def _build_north_star_from_rag(self, extracted: Dict) -> Dict:
        """Build north_star dict from RAG-extracted data (richer schema with evidence)."""
        ns = extracted.get('north_star_metric', {})
        if not ns:
            ns = {}

        name = ns.get('name', None)
        definition = ns.get('definition', None)
        why = ns.get('why_it_matters', None)
        evidence = ns.get('evidence', None)

        # Fallback to domain-based defaults if LLM returned nulls
        if not name:
            domain = self.detected_domain or 'generic'
            domain_metrics = {
                'edtech': "Weekly Active Learners",
                'fintech': "Monthly Transaction Volume",
                'health': "Daily Active Health Users",
                'entertainment': "Content Engagement Hours",
                'ecommerce': "Purchase Conversion Rate",
                'social': "Daily Active Connections",
                'saas': "Monthly Recurring Revenue",
                'generic': "Daily Active Users"
            }
            name = domain_metrics.get(domain, "Daily Active Users")

        if not definition:
            definition = f"Primary success metric measuring {self.detected_domain or 'product'} performance"

        if not why:
            why = f"Core indicator of {self.detected_domain or 'product'} success and value delivery"

        # Extract key drivers from feature_goal_mapping
        features = extracted.get('feature_goal_mapping', [])
        key_drivers = [f.get('feature', 'Core Feature') for f in features[:5]] if features else ["User engagement", "Feature adoption", "Retention"]

        return {
            "north_star_metric": name,
            "definition": definition,
            "why_it_matters": why,
            "evidence": evidence,
            "measurement": f"Metric tracking for {name}",
            "key_drivers": key_drivers
        }

    def _build_feature_goal_map_from_rag(self, extracted: Dict) -> Dict:
        """Build feature_goal_map dict from RAG-extracted data (richer schema with evidence)."""
        features = []
        for idx, item in enumerate(extracted.get('feature_goal_mapping', [])):
            fname = item.get('feature', f'Feature_{idx}')
            fgoal = item.get('goal', 'user_engagement')
            fevidence = item.get('evidence', '')
            fid = re.sub(r'[^a-z0-9_]', '', fname.lower().replace(' ', '_'))
            features.append({
                "feature_name": fname,
                "feature_id": fid,
                "primary_goal": fgoal,
                "evidence": fevidence,
                "secondary_goals": ["engagement", "retention", "satisfaction"],
                "user_segments_most_relevant": ["all"],
                "engagement_driver_score": round(0.75 + (idx * 0.03), 2),
                "description": f"Feature enabling {fname.lower()} functionality"
            })

        if not features:
            features = self._get_default_features("")

        return {"features": features}

    def _build_tone_hook_matrix_from_rag(self, extracted: Dict, raw_text: str) -> Dict[str, Any]:
        """Build the tone/hook matrix from LLM-extracted data.

        Uses the LLM-extracted allowed_tones and behavioral_hooks instead of
        static config-based generation.
        """
        domain = getattr(self, 'detected_domain', 'generic')

        # Get LLM-inferred tones, fall back to config
        llm_tones = extracted.get('allowed_tones', [])
        if llm_tones and len(llm_tones) >= 3:
            allowed_tones = llm_tones
        else:
            allowed_tones = self.allowed_tones

        # Build Octalysis hooks from LLM extraction
        llm_hooks = extracted.get('behavioral_hooks', [])
        octalysis_hooks = {}

        # Map LLM hooks into the standard Octalysis structure
        drive_map = {
            'epic meaning': 'epic_meaning', 'epic meaning & calling': 'epic_meaning',
            'accomplishment': 'accomplishment', 'development & accomplishment': 'accomplishment',
            'development and accomplishment': 'accomplishment',
            'empowerment': 'empowerment', 'empowerment of creativity & feedback': 'empowerment',
            'empowerment of creativity and feedback': 'empowerment',
            'ownership': 'ownership', 'ownership & possession': 'ownership',
            'ownership and possession': 'ownership',
            'social influence': 'social_influence', 'social influence & relatedness': 'social_influence',
            'social influence and relatedness': 'social_influence',
            'scarcity': 'scarcity', 'scarcity & impatience': 'scarcity',
            'scarcity and impatience': 'scarcity',
            'unpredictability': 'unpredictability', 'unpredictability & curiosity': 'unpredictability',
            'unpredictability and curiosity': 'unpredictability',
            'loss avoidance': 'loss_avoidance', 'loss & avoidance': 'loss_avoidance',
            'loss and avoidance': 'loss_avoidance',
        }

        for hook in llm_hooks:
            octolysis = hook.get('octolysis', hook.get('hook', ''))
            drive_key = drive_map.get(octolysis.lower().strip(), None)
            if not drive_key:
                # Try partial match
                for k, v in drive_map.items():
                    if k in octolysis.lower():
                        drive_key = v
                        break
            if not drive_key:
                continue

            if drive_key not in octalysis_hooks:
                octalysis_hooks[drive_key] = {
                    "description": octolysis,
                    "hooks": [],
                    "best_for_segments": ["all"]
                }

            octalysis_hooks[drive_key]["hooks"].append({
                "hook_name": hook.get('hook', ''),
                "trigger": hook.get('trigger', ''),
                "reward": hook.get('reward', ''),
                "feature_source": hook.get('feature_source', ''),
                "evidence": hook.get('evidence', '')
            })

        # Fill in any missing Octalysis drives with generic defaults
        all_drives = {
            'epic_meaning': 'Be part of something bigger',
            'accomplishment': 'Make progress and achieve',
            'empowerment': 'Have control and experiment',
            'ownership': 'Build something valuable',
            'social_influence': 'Others are doing it',
            'scarcity': 'Limited time or availability',
            'unpredictability': 'What will happen next',
            'loss_avoidance': "Don't lose what you have"
        }
        hook_examples = self._generate_hook_examples(domain)

        for drive, desc in all_drives.items():
            if drive not in octalysis_hooks:
                octalysis_hooks[drive] = {
                    "description": desc,
                    "examples": hook_examples.get(drive, []),
                    "best_for_segments": ["all"]
                }

        matrix = {
            "allowed_tones": allowed_tones,
            "forbidden_tones": self.forbidden_tones,
            "tone_by_lifecycle": self.tone_by_lifecycle,
            "detected_domain": domain,
            "octalysis_hooks": octalysis_hooks,
            "hooks_by_segment": {
                "achievers": ["accomplishment", "ownership", "loss_avoidance"],
                "social_competitors": ["social_influence", "accomplishment", "scarcity"],
                "casual_learners": ["unpredictability", "empowerment", "epic_meaning"],
                "at_risk_churners": ["loss_avoidance", "scarcity", "social_influence"],
                "dormant_users": ["unpredictability", "epic_meaning", "empowerment"]
            }
        }

        return matrix

    # ===================================================================
    # REGEX FALLBACK PIPELINE (original logic)
    # ===================================================================

    def _process_regex(self, kb_text: str) -> Dict[str, Any]:
        """Process KB using regex/heuristic extraction (original approach)."""
        self.detected_domain = self._detect_domain(kb_text)

        self.north_star = self._extract_north_star(kb_text)
        self.feature_goal_map = self._extract_feature_goal_map(kb_text)
        self.tone_hook_matrix = self._extract_tone_hook_matrix(kb_text)

        return {
            'north_star': self.north_star,
            'feature_goal_map': self.feature_goal_map,
            'tone_hook_matrix': self.tone_hook_matrix,
            'detected_domain': self.detected_domain
        }

    def _detect_domain(self, text: str) -> str:
        """
        Detect the domain/industry from KB text for context-aware extraction.
        Returns: 'edtech', 'fintech', 'entertainment', 'ecommerce', 'health', 'social', or 'generic'
        """
        text_lower = text.lower()

        domain_indicators = {
            'edtech': ['learn', 'education', 'course', 'lesson', 'practice', 'exercise', 'quiz', 'tutor', 'student', 'teacher', 'skill'],
            'fintech': ['payment', 'transaction', 'wallet', 'money', 'bank', 'finance', 'loan', 'credit', 'invest', 'transfer'],
            'entertainment': ['watch', 'stream', 'video', 'movie', 'show', 'content', 'music', 'play', 'episode', 'series'],
            'ecommerce': ['shop', 'buy', 'cart', 'order', 'product', 'delivery', 'price', 'sale', 'discount', 'checkout'],
            'health': ['health', 'fitness', 'workout', 'exercise', 'diet', 'wellness', 'medical', 'doctor', 'patient', 'prescription'],
            'social': ['friend', 'follow', 'post', 'share', 'comment', 'like', 'message', 'connect', 'network', 'community']
        }

        scores = {}
        for domain, keywords in domain_indicators.items():
            scores[domain] = sum(1 for kw in keywords if kw in text_lower)

        best_domain = max(scores, key=scores.get)
        return best_domain if scores[best_domain] >= 2 else 'generic'

    def _extract_north_star(self, text: str) -> Dict[str, Any]:
        """Extract North Star metric from KB using pattern matching"""

        metric_name = None

        key_metrics_match = re.search(r"(?:key metrics?|north star)[\s\S]{0,500}?([A-Z][^.\n]{10,80}(?:retention|conversion|engagement|revenue|growth|active users))", text, re.IGNORECASE)

        if key_metrics_match:
            candidate = key_metrics_match.group(1).strip()
            candidate = re.sub(r'^[*•\-\d\.\s]+', '', candidate)
            candidate = re.sub(r'\s+', ' ', candidate)
            if len(candidate) > 10 and len(candidate) < 100:
                metric_name = candidate

        if not metric_name:
            patterns = [
                r"north star(?:\s+metric)?(?:\s+is)?:\s*([A-Z][^.\n]{10,80})",
                r"primary metric:\s*([A-Z][^.\n]{10,80})",
                r"goal:\s*\*?\*?([^*\n]{10,80}(?:retention|conversion|engagement))\*?\*?",
            ]

            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    candidate = match.group(1).strip()
                    candidate = re.sub(r'^[*•\-\s]+', '', candidate)
                    if len(candidate) > 10 and len(candidate) < 100:
                        metric_name = candidate
                        break

        if not metric_name or len(metric_name) < 10:
            text_lower = text.lower()
            domain = self.detected_domain or 'generic'

            domain_metrics = {
                'edtech': "Weekly Active Learners",
                'fintech': "Transaction Volume",
                'health': "Daily Active Health Users",
                'entertainment': "Content Engagement Hours",
                'ecommerce': "Purchase Conversion Rate",
                'social': "Daily Active Connections",
                'generic': "Daily Active Users"
            }
            metric_name = domain_metrics.get(domain, "Daily Active Users")

        definition = self._extract_definition(text, metric_name)
        why_matters = self._extract_rationale(text, metric_name)

        north_star = {
            "north_star_metric": metric_name,
            "definition": definition,
            "why_it_matters": why_matters,
            "measurement": f"Metric tracking for {metric_name}",
            "key_drivers": self._extract_key_drivers(text)
        }

        return north_star

    def _extract_definition(self, text: str, metric: str) -> str:
        """Extract definition of the metric"""
        metrics_section = re.search(r"(?:key metrics?)([\s\S]{0,800}?)(?:\n#{1,3}\s|\Z)", text, re.IGNORECASE)

        if metrics_section:
            section = metrics_section.group(1)
            metric_pattern = rf"{re.escape(metric[:20])}[^\n]*?\n\s*[*•\-]?\s*([A-Z][^.\n]{{20,150}})"
            match = re.search(metric_pattern, section, re.IGNORECASE)
            if match:
                defn = match.group(1).strip('* \t')
                if len(defn) > 20:
                    return defn

        if 'retention' in metric.lower():
            return "Percentage of users who remain active and engaged over time"
        elif 'conversion' in metric.lower():
            return "Rate at which trial users convert to paying customers"
        elif 'engagement' in metric.lower():
            return "Users who actively interact with core features daily"
        else:
            return "Primary success metric measuring product-market fit"

    def _extract_rationale(self, text: str, metric: str) -> str:
        """Extract why the metric matters"""
        goal_match = re.search(r"goal:?\s*\*?\*?([^*\n]{15,100})\*?\*?", text, re.IGNORECASE)
        if goal_match:
            return f"Drives {goal_match.group(1).strip().lower()}"

        if 'retention' in metric.lower():
            return "Indicates product stickiness and long-term value creation"
        elif 'conversion' in metric.lower():
            return "Validates product-market fit and monetization effectiveness"
        elif 'engagement' in metric.lower():
            return "Measures active usage and habit formation, leading to retention"
        elif 'revenue' in metric.lower():
            return "Direct indicator of business sustainability and growth"
        else:
            return "Core indicator of product success and user satisfaction"

    def _extract_key_drivers(self, text: str) -> List[str]:
        """Extract key drivers from text"""
        drivers = []

        metrics_section = re.search(r"(?:key metrics?|metrics?|kpis?)[\s:]*\n([\s\S]{0,500}?)(?:\n#{1,3}\s|\n\*\*[A-Z]|\Z)", text, re.IGNORECASE)

        if metrics_section:
            section_text = metrics_section.group(1)
            driver_patterns = [
                r"[*•\-]\s+\*?\*?([^*\n]{15,}?)(?:\*?\*?\s*$|\*?\*?\n)",
                r"^\d+\.\s+([^.\n]{15,})$"
            ]

            for pattern in driver_patterns:
                matches = re.findall(pattern, section_text, re.MULTILINE)
                for match in matches:
                    cleaned = match.strip().strip('*').strip()
                    if len(cleaned) > 15 and len(cleaned) < 100:
                        drivers.append(cleaned)

        if not drivers:
            goal_match = re.search(r"goal:?\s*\*?\*?([^*\n]{15,})\*?\*?", text, re.IGNORECASE)
            if goal_match:
                drivers.append(goal_match.group(1).strip())

        if not drivers:
            text_lower = text.lower()
            if 'retention' in text_lower:
                drivers.append("User retention and engagement")
            if 'conversion' in text_lower:
                drivers.append("Trial to paid conversion")
            if 'engagement' in text_lower:
                drivers.append("Daily active engagement")

        if not drivers:
            drivers = ["User engagement", "Feature adoption", "Retention"]

        drivers = list(dict.fromkeys(drivers))[:5]
        return drivers

    def _extract_feature_goal_map(self, text: str) -> Dict[str, List[Dict]]:
        """Extract feature-to-goal mappings from KB text using multiple adaptive strategies."""
        features = []
        feature_names = []

        section_patterns = [
            r"(?:features?|achieved through|capabilities|key functionality|product offerings?)[\ s:]*\n([\s\S]{0,1200}?)(?:\n#{1,3}\s|\n\*\*[A-Z]|\Z)",
            r"(?:what we offer|how it works|our solution)[\ s:]*\n([\s\S]{0,1200}?)(?:\n#{1,3}\s|\Z)",
            r"(?:product|app|platform) (?:includes?|provides?|offers?)([\s\S]{0,800}?)(?:\n#{1,3}\s|\Z)"
        ]

        for pattern in section_patterns:
            section_match = re.search(pattern, text, re.IGNORECASE)
            if section_match:
                section_text = section_match.group(1)
                bullet_patterns = [
                    r"[*•\-]\s+([A-Z][^*\n]{5,80})",
                    r"\d+[.)\s]+([A-Z][^\n]{5,80})",
                    r"\*\*([^*]{5,50})\*\*",
                ]
                for bp in bullet_patterns:
                    matches = re.findall(bp, section_text)
                    for match in matches:
                        cleaned = match.strip().strip('*').strip()
                        if 5 < len(cleaned) < 80 and cleaned not in feature_names:
                            feature_names.append(cleaned)
                if feature_names:
                    break

        if not feature_names:
            noun_phrase_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}(?:\s+(?:Feature|Tool|System|Module|Engine|Dashboard|Analytics|Practice|Mode))?)\b"
            matches = re.findall(noun_phrase_pattern, text)
            for match in matches:
                if 5 < len(match) < 60 and match not in feature_names:
                    feature_names.append(match)

        if not feature_names:
            feature_names = self._infer_features_from_domain(text)

        for idx, feature_name in enumerate(feature_names[:8]):
            feature_id = re.sub(r'[^a-z0-9_]', '', feature_name.lower().replace(' ', '_'))
            features.append({
                "feature_name": feature_name.strip(),
                "feature_id": feature_id,
                "primary_goal": self._infer_goal_from_feature(feature_name, text),
                "secondary_goals": self._infer_secondary_goals(feature_name, text),
                "user_segments_most_relevant": ["all"],
                "engagement_driver_score": round(0.75 + (idx * 0.03), 2),
                "description": self._generate_feature_description(feature_name, text)
            })

        if not features:
            features = self._get_default_features(text)

        return {"features": features}

    def _infer_features_from_domain(self, text: str) -> List[str]:
        """Infer likely features based on detected domain."""
        text_lower = text.lower()
        features = []
        domain = getattr(self, 'detected_domain', None) or 'generic'

        domain_features = {
            'edtech': {
                'patterns': {
                    'ai|tutor|mentor': 'AI Tutor',
                    'leaderboard|rank|compete': 'Leaderboard',
                    'streak|daily|habit': 'Streak System',
                    'coin|reward|point': 'Rewards System',
                    'exercise|practice|quiz': 'Practice Exercises',
                    'progress|report|analytics': 'Progress Reports',
                    'gamif': 'Gamification Features'
                },
                'defaults': ['Learning Modules', 'Practice Mode', 'Progress Tracking']
            },
            'fintech': {
                'patterns': {
                    'wallet|balance': 'Digital Wallet',
                    'payment|pay': 'Payments',
                    'transfer|send': 'Money Transfer',
                    'cashback|reward': 'Cashback Rewards',
                    'bill|recharge': 'Bill Payments',
                    'invest|mutual|stock': 'Investments'
                },
                'defaults': ['Wallet', 'Payments', 'Transactions']
            },
            'entertainment': {
                'patterns': {
                    'recommend|discover': 'Recommendations',
                    'watchlist|save': 'Watchlist',
                    'download|offline': 'Downloads',
                    'profile|account': 'User Profiles',
                    'search|browse': 'Content Discovery'
                },
                'defaults': ['Content Library', 'Streaming', 'Personalization']
            },
            'ecommerce': {
                'patterns': {
                    'cart|basket': 'Shopping Cart',
                    'wishlist|save': 'Wishlist',
                    'checkout|buy': 'Checkout',
                    'track|delivery': 'Order Tracking',
                    'review|rating': 'Reviews & Ratings'
                },
                'defaults': ['Product Catalog', 'Shopping Cart', 'Order Management']
            },
            'health': {
                'patterns': {
                    'workout|exercise': 'Workouts',
                    'track|log': 'Activity Tracking',
                    'goal|target': 'Goal Setting',
                    'remind|notification': 'Health Reminders',
                    'meal|diet|nutrition': 'Nutrition Tracking'
                },
                'defaults': ['Activity Tracking', 'Health Dashboard', 'Goals']
            },
            'social': {
                'patterns': {
                    'feed|timeline': 'News Feed',
                    'message|chat': 'Messaging',
                    'profile|account': 'User Profiles',
                    'friend|connect': 'Connections',
                    'group|community': 'Communities'
                },
                'defaults': ['Feed', 'Messaging', 'Profiles']
            },
            'generic': {
                'patterns': {},
                'defaults': ['Core Feature', 'User Dashboard', 'Notifications']
            }
        }

        config = domain_features.get(domain, domain_features['generic'])

        for pattern, feature_name in config['patterns'].items():
            if re.search(pattern, text_lower):
                features.append(feature_name)

        if len(features) < 3:
            for default in config['defaults']:
                if default not in features:
                    features.append(default)
                    if len(features) >= 5:
                        break

        return features

    def _infer_goal_from_feature(self, feature_name: str, text: str) -> str:
        """Infer primary goal from feature name (domain-generic)."""
        feature_lower = feature_name.lower()

        goal_mapping = {
            'tutor': 'skill_development', 'learn': 'skill_development',
            'course': 'knowledge_acquisition', 'practice': 'skill_mastery',
            'exercise': 'skill_development', 'quiz': 'knowledge_assessment',
            'leaderboard': 'competitive_engagement', 'streak': 'habit_formation',
            'coin': 'gamification_engagement', 'reward': 'motivation',
            'badge': 'achievement_recognition', 'progress': 'self_improvement',
            'report': 'performance_awareness',
            'wallet': 'financial_convenience', 'payment': 'transaction_completion',
            'transfer': 'money_movement', 'invest': 'wealth_growth',
            'cashback': 'savings_motivation', 'bill': 'utility_management',
            'content': 'entertainment', 'watch': 'content_consumption',
            'stream': 'content_access', 'recommend': 'content_discovery',
            'download': 'offline_access', 'playlist': 'content_curation',
            'cart': 'purchase_facilitation', 'wishlist': 'purchase_planning',
            'checkout': 'purchase_completion', 'track': 'order_visibility',
            'review': 'social_proof',
            'workout': 'fitness_improvement', 'diet': 'health_management',
            'goal': 'achievement_tracking', 'reminder': 'behavior_reinforcement',
            'friend': 'social_connection', 'message': 'communication',
            'feed': 'content_consumption', 'community': 'belonging',
            'dashboard': 'information_access', 'notification': 'engagement',
            'profile': 'identity_expression', 'setting': 'personalization',
            'search': 'discovery', 'ai': 'personalized_experience'
        }

        for keyword, goal in goal_mapping.items():
            if keyword in feature_lower:
                return goal

        return 'user_engagement'

    def _generate_feature_description(self, feature_name: str, text: str) -> str:
        """Generate a meaningful description for the feature based on context"""
        feature_lower = feature_name.lower()

        escaped_name = re.escape(feature_name[:15])
        context_match = re.search(rf"{escaped_name}[^.]*?([A-Z][^.]+\.)", text, re.IGNORECASE)
        if context_match:
            desc = context_match.group(1).strip()
            if 20 < len(desc) < 150:
                return desc

        description_templates = {
            'tutor': 'AI-powered tutoring for personalized learning',
            'streak': 'Daily engagement tracking to build habits',
            'leaderboard': 'Competitive ranking to motivate users',
            'reward': 'Incentive system to drive engagement',
            'wallet': 'Digital wallet for seamless transactions',
            'payment': 'Quick and secure payment processing',
            'content': 'Rich content library for user engagement',
            'workout': 'Guided workout routines for fitness',
            'feed': 'Personalized content feed',
            'message': 'Real-time messaging functionality',
            'cart': 'Shopping cart for purchase management',
            'track': 'Real-time tracking and monitoring',
        }

        for keyword, desc in description_templates.items():
            if keyword in feature_lower:
                return desc

        return f"Feature enabling {feature_name.lower()} functionality"

    def _infer_secondary_goals(self, feature_name: str, text: str) -> List[str]:
        """Infer secondary goals"""
        return ["engagement", "retention", "satisfaction"]

    def _get_default_features(self, text: str) -> List[Dict]:
        """Get default features when extraction fails"""
        return [
            {
                "feature_name": "Core Feature",
                "feature_id": "core_feature",
                "primary_goal": "user_engagement",
                "secondary_goals": ["retention", "satisfaction"],
                "user_segments_most_relevant": ["all"],
                "engagement_driver_score": 0.80,
                "description": "Primary product feature"
            }
        ]

    def enrich_features_from_data(self, columns: List[str]) -> None:
        """Enrich feature_goal_map using feature columns detected in user data CSV."""
        if not self.feature_goal_map:
            self.feature_goal_map = {"features": []}

        existing_ids = {f['feature_id'] for f in self.feature_goal_map.get('features', [])}
        has_only_default = existing_ids == {'core_feature'}

        # Map explicit feature_* columns
        new_features = []
        for col in columns:
            if not col.startswith('feature_'):
                continue
            fname = col.replace('feature_', '').replace('_used', '').replace('_viewed', '').replace('_', ' ').title()
            fid = col.replace('feature_', '').replace('_used', '').replace('_viewed', '')
            if fid not in existing_ids:
                new_features.append({
                    "feature_name": fname,
                    "feature_id": fid,
                    "primary_goal": self._infer_goal_from_feature(fname, ""),
                    "secondary_goals": ["engagement", "retention", "satisfaction"],
                    "user_segments_most_relevant": ["all"],
                    "engagement_driver_score": 0.80,
                    "description": self._generate_feature_description(fname, "")
                })
                existing_ids.add(fid)

        # Infer features from behavioral columns
        behavioral_map = {
            'streak': ('Streak System', 'streak_system', 'habit_formation'),
            'coins': ('Rewards System', 'rewards_system', 'gamification_engagement'),
            'exercise': ('Practice Exercises', 'practice_exercises', 'skill_development'),
            'gamification': ('Gamification', 'gamification', 'competitive_engagement'),
        }
        for keyword, (fname, fid, goal) in behavioral_map.items():
            if any(keyword in c.lower() for c in columns) and fid not in existing_ids:
                new_features.append({
                    "feature_name": fname,
                    "feature_id": fid,
                    "primary_goal": goal,
                    "secondary_goals": ["engagement", "retention", "satisfaction"],
                    "user_segments_most_relevant": ["all"],
                    "engagement_driver_score": 0.78,
                    "description": self._generate_feature_description(fname, "")
                })
                existing_ids.add(fid)

        if new_features:
            if has_only_default:
                self.feature_goal_map['features'] = new_features
            else:
                self.feature_goal_map['features'].extend(new_features)
            print(f"   [OK] Enriched feature map with {len(new_features)} features from data columns")

    def _extract_tone_hook_matrix(self, text: str) -> Dict[str, Any]:
        """
        Extract allowed tones and behavioral hooks.
        Tones come from config; Octalysis 8 Core Drives are universal behavioral
        psychology principles (Yu-kai Chou, 2015) and are standardized.
        """
        domain = getattr(self, 'detected_domain', 'generic')
        hook_examples = self._generate_hook_examples(domain)

        matrix = {
            "allowed_tones": self.allowed_tones,
            "forbidden_tones": self.forbidden_tones,
            "tone_by_lifecycle": self.tone_by_lifecycle,
            "detected_domain": domain,
            "octalysis_hooks": {
                "epic_meaning": {
                    "description": "Be part of something bigger",
                    "examples": hook_examples.get('epic_meaning', ["Join millions of users", "Transform your life", "Unlock your potential"]),
                    "best_for_segments": ["aspirational", "purpose_driven"]
                },
                "accomplishment": {
                    "description": "Make progress and achieve",
                    "examples": hook_examples.get('accomplishment', ["Complete your goal", "Reach the milestone", "Earn rewards"]),
                    "best_for_segments": ["achievers", "goal_oriented"]
                },
                "empowerment": {
                    "description": "Have control and experiment",
                    "examples": hook_examples.get('empowerment', ["Choose your path", "Customize your experience", "Do it your way"]),
                    "best_for_segments": ["casual", "explorers"]
                },
                "ownership": {
                    "description": "Build something valuable",
                    "examples": hook_examples.get('ownership', ["Your progress", "Your collection", "Your achievements"]),
                    "best_for_segments": ["achievers", "collectors"]
                },
                "social_influence": {
                    "description": "Others are doing it",
                    "examples": hook_examples.get('social_influence', ["Join top users", "See what others do", "Compare with friends"]),
                    "best_for_segments": ["social", "community_driven"]
                },
                "scarcity": {
                    "description": "Limited time or availability",
                    "examples": hook_examples.get('scarcity', ["Only hours left", "Last chance", "Limited offer"]),
                    "best_for_segments": ["achievers", "fomo_driven"]
                },
                "unpredictability": {
                    "description": "What will happen next",
                    "examples": hook_examples.get('unpredictability', ["Unlock surprise", "Discover something new", "See what's next"]),
                    "best_for_segments": ["explorers", "casual"]
                },
                "loss_avoidance": {
                    "description": "Don't lose what you have",
                    "examples": hook_examples.get('loss_avoidance', ["Don't lose progress", "Maintain your status", "Keep your streak"]),
                    "best_for_segments": ["achievers", "at_risk"]
                }
            },
            "hooks_by_segment": {
                "achievers": ["accomplishment", "ownership", "loss_avoidance"],
                "social_competitors": ["social_influence", "accomplishment", "scarcity"],
                "casual_learners": ["unpredictability", "empowerment", "epic_meaning"],
                "at_risk_churners": ["loss_avoidance", "scarcity", "social_influence"],
                "dormant_users": ["unpredictability", "epic_meaning", "empowerment"]
            }
        }

        return matrix

    def _generate_hook_examples(self, domain: str) -> Dict[str, List[str]]:
        """Generate domain-specific examples for Octalysis hooks"""

        domain_examples = {
            'edtech': {
                'epic_meaning': ["Join 1M+ learners", "Transform your skills", "Unlock your potential"],
                'accomplishment': ["Complete 10 lessons", "Reach 7-day streak", "Earn 100 coins"],
                'empowerment': ["Choose your topic", "Learn at your pace", "Customize your path"],
                'ownership': ["Your 500 coins", "Your 30-day streak", "Your certificates"],
                'social_influence': ["Beat the leaderboard", "Join top learners", "Compete with friends"],
                'scarcity': ["Only 3 hours left", "Limited seats", "Today's bonus expires"],
                'unpredictability': ["Unlock surprise reward", "Daily bonus waiting", "New content unlocked"],
                'loss_avoidance': ["Streak will break", "Don't lose progress", "Maintain your rank"]
            },
            'fintech': {
                'epic_meaning': ["Join millions saving smart", "Financial freedom awaits", "Be money smart"],
                'accomplishment': ["Saved ₹10,000", "100 transactions done", "Gold member unlocked"],
                'empowerment': ["Your money, your rules", "Invest your way", "Control your finances"],
                'ownership': ["Your savings: ₹50K", "Your cashback earned", "Your portfolio"],
                'social_influence': ["Friends using this", "Top savers this month", "Trusted by millions"],
                'scarcity': ["Offer ends tonight", "Limited cashback", "Last chance for bonus"],
                'unpredictability': ["Scratch and win", "Surprise cashback", "Lucky draw entry"],
                'loss_avoidance': ["Cashback expiring", "Don't miss savings", "Bill overdue"]
            },
            'entertainment': {
                'epic_meaning': ["Join the community", "Be part of the fandom", "Experience the best"],
                'accomplishment': ["Watched 100 hours", "Completed the series", "Top fan badge"],
                'empowerment': ["Watch anywhere", "Your playlist", "Skip the ads"],
                'ownership': ["Your watchlist", "Your favorites", "Your downloads"],
                'social_influence': ["Trending now", "Friends are watching", "Most popular"],
                'scarcity': ["Leaving soon", "Limited release", "Premium only"],
                'unpredictability': ["New releases", "Surprise drop", "What's next"],
                'loss_avoidance': ["Continue watching", "Don't miss finale", "Expires soon"]
            },
            'ecommerce': {
                'epic_meaning': ["Shop smart, save big", "Join happy shoppers", "Best deals await"],
                'accomplishment': ["100 orders placed", "Platinum member", "Top reviewer"],
                'empowerment': ["Shop your way", "Easy returns", "Your choices"],
                'ownership': ["Your wishlist", "Your rewards", "Your savings"],
                'social_influence': ["Best seller", "Highly rated", "Others bought"],
                'scarcity': ["Only 3 left", "Sale ends soon", "Flash deal"],
                'unpredictability': ["Mystery discount", "Surprise offer", "Lucky coupon"],
                'loss_avoidance': ["Price drop alert", "Cart expiring", "Almost sold out"]
            },
            'health': {
                'epic_meaning': ["Join the healthy movement", "Transform your life", "Be your best self"],
                'accomplishment': ["30-day streak", "Goal achieved", "Personal best"],
                'empowerment': ["Your fitness journey", "Your pace", "Your goals"],
                'ownership': ["Your progress", "Your records", "Your achievements"],
                'social_influence': ["Top performers", "Friends active", "Community challenge"],
                'scarcity': ["Challenge ends soon", "Limited spots", "This week only"],
                'unpredictability': ["New workout unlocked", "Bonus points", "Surprise reward"],
                'loss_avoidance': ["Streak at risk", "Don't lose progress", "Stay on track"]
            }
        }

        return domain_examples.get(domain, {
            'epic_meaning': ["Join millions", "Be part of something big", "Transform your experience"],
            'accomplishment': ["Complete goals", "Earn rewards", "Level up"],
            'empowerment': ["Your way", "Your choice", "Customize"],
            'ownership': ["Your progress", "Your achievements", "Your journey"],
            'social_influence': ["Others are here", "Join top users", "Trending"],
            'scarcity': ["Limited time", "Act now", "Ends soon"],
            'unpredictability': ["Surprise waiting", "Discover more", "What's next"],
            'loss_avoidance': ["Don't miss out", "Keep going", "Stay active"]
        })

    def save_outputs(self, output_dir: str):
        """Save extracted knowledge to JSON files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        with open(output_path / 'company_north_star.json', 'w', encoding='utf-8') as f:
            json.dump(self.north_star, f, indent=2, ensure_ascii=False)

        with open(output_path / 'feature_goal_map.json', 'w', encoding='utf-8') as f:
            json.dump(self.feature_goal_map, f, indent=2, ensure_ascii=False)

        with open(output_path / 'allowed_tone_hook_matrix.json', 'w', encoding='utf-8') as f:
            json.dump(self.tone_hook_matrix, f, indent=2, ensure_ascii=False)

        # Save detected domain for iteration1 to reload
        kb_meta = {'detected_domain': self.detected_domain or 'generic'}
        with open(output_path / 'kb_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(kb_meta, f, indent=2, ensure_ascii=False)

        mode_label = "RAG-lite" if self.rag_mode_used else "Regex"
        print(f"[OK] Knowledge Bank outputs saved to {output_dir} (mode: {mode_label})")
