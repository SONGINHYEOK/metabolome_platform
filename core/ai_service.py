import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from groq import Groq
    client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
except Exception:
    client = None

SYSTEM_PROMPT = """당신은 '특용작물 대사체 통합 디지털 플랫폼'의 AI 어시스턴트입니다.
한국의 특용작물(인삼, 당귀, 황기, 결명자, 단삼, 상황버섯, 동충하초 등)에 대한 대사체(metabolomics) 전문 지식을 갖고 있습니다.

핵심 역할:
- 대사체 성분(Ginsenoside, Decursin, Astragaloside 등)의 생리활성과 효능 해석
- MSI(Metabolomics Standards Initiative) 기반 동정 신뢰도(L1/L2/L3) 설명
- 산지별·환경별 성분 차이 분석 및 원산지 판별 근거 해설
- 대중이 이해할 수 있는 쉬운 용어로 과학적 내용 전달

주의사항:
- 의학적 진단이나 처방은 제공하지 않습니다
- 데이터에 근거한 객관적 해석을 제공합니다
- 불확실한 내용은 명시적으로 한계를 안내합니다
- 한국어로 답변합니다"""

COMPOUND_INTERPRET_PROMPT = """아래 성분 데이터를 분석하고 JSON 형식으로 해석을 제공하세요.

성분 데이터:
{compound_data}

반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{
  "confidence_assessment": "동정 신뢰도에 대한 평가 (2-3문장)",
  "bioactivity_significance": "생리활성 의의 및 효능 (2-3문장)",
  "origin_contribution": "원산지 기여도 및 산지별 특성 (2-3문장)",
  "one_line_summary": "한줄 요약"
}}"""

DASHBOARD_INTERPRET_PROMPT = """아래 두 작물의 비교 데이터를 분석하고 JSON 형식으로 해석을 제공하세요.

비교 데이터:
{dashboard_data}

반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{
  "comparison_summary": "두 작물 비교 요약 (3-4문장)",
  "environment_impact": "환경이 성분에 미치는 영향 분석 (2-3문장)",
  "usage_insights": {{
    "policy": "정책 활용 인사이트 (1-2문장)",
    "industry": "산업 활용 인사이트 (1-2문장)",
    "farmer": "농업인 활용 인사이트 (1-2문장)"
  }},
  "uncertainty_note": "데이터 한계 및 불확실성 안내 (1-2문장)"
}}"""


def chat_completion(messages):
    """General chat completion with conversation history."""
    if not client:
        return {"error": "GROQ_API_KEY가 설정되지 않았습니다. 환경변수를 확인하세요."}

    try:
        chat_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        chat_messages.extend(messages)

        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=chat_messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return {
            "role": "assistant",
            "content": response.choices[0].message.content,
        }
    except Exception as e:
        logger.exception("Groq chat_completion error")
        return {"error": str(e)}


def interpret_compound(compound_data):
    """Interpret a single compound's data with structured output."""
    if not client:
        return {"error": "GROQ_API_KEY가 설정되지 않았습니다."}

    try:
        prompt = COMPOUND_INTERPRET_PROMPT.format(
            compound_data=json.dumps(compound_data, ensure_ascii=False, indent=2)
        )
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=1024,
        )
        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try extracting JSON from markdown code block
            if "```" in content:
                json_str = content.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
                return json.loads(json_str.strip())
            return {"raw_text": content}
    except Exception as e:
        logger.exception("Groq interpret_compound error")
        return {"error": str(e)}


def interpret_dashboard(dashboard_data):
    """Interpret dashboard comparison data with structured output."""
    if not client:
        return {"error": "GROQ_API_KEY가 설정되지 않았습니다."}

    try:
        prompt = DASHBOARD_INTERPRET_PROMPT.format(
            dashboard_data=json.dumps(dashboard_data, ensure_ascii=False, indent=2)
        )
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=1024,
        )
        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            if "```" in content:
                json_str = content.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
                return json.loads(json_str.strip())
            return {"raw_text": content}
    except Exception as e:
        logger.exception("Groq interpret_dashboard error")
        return {"error": str(e)}
