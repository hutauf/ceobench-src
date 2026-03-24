#!/usr/bin/env python3
"""Render customer social media post prompts for ALL possible event types.

This script imports the actual generate_social_post logic and renders
the system+user prompts that would be sent to the LLM, WITHOUT calling the LLM.
"""
import json
import sys
import os
import random

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from saas_bench.customer_llm import (
    POST_FORMAT_DIRECTIVES, WRITING_ANGLE_POOL, EVENT_DESCRIPTION_VARIANTS
)

# ── Fake persona + group chars for rendering ──

PERSONA_INDIVIDUAL = {
    'persona_description': 'A resourceful non-profit program coordinator who uses AI to write grant proposals',
    'persona_industry': 'non-profit',
    'persona_role': 'program coordinator',
    'persona_experience': 'mid-career',
    'persona_work_style': 'collaborative',
    'persona_tech_savvy': 'comfortable',
    'persona_communication': 'empathetic',
    'writing_style': 'Heartfelt and mission-driven',
}

PERSONA_ENTERPRISE = {
    'persona_description': 'IT Director at a regional credit union overseeing digital transformation',
    'persona_industry': 'banking',
    'persona_role': 'IT Director',
    'persona_experience': 'senior',
    'persona_work_style': 'methodical',
    'persona_tech_savvy': 'proficient',
    'persona_communication': 'formal',
    'writing_style': 'Professional, compliance-focused',
    'company_culture': 'conservative',
    'company_size_descriptor': 'mid-market',
    'company_decision_style': 'committee-driven',
    'company_primary_concern': 'regulatory compliance',
}

GROUP_D_S03 = {
    'description': 'Non-profit workers at charities, NGOs, and social enterprises. '
                   'Mission-driven and resourceful, operating on tight donation-funded budgets.',
    'social_media_tone': 'Empathetic but firm about value-for-money; frames complaints around mission impact',
}

GROUP_D_E04 = {
    'description': 'Regional banks and credit unions. Trust-focused, regulatory-compliant institutions '
                   'with conservative technology adoption.',
    'social_media_tone': 'Formal and measured; frames complaints around trust, compliance, and fiduciary responsibility',
}

PRODUCT_NAME = 'NovaMind'
COMPANY_NAME = 'NovaMind AI'

# ── Prompt builder (mirrors customer_llm.py generate_social_post logic) ──

def build_persona_context(persona, group_chars, group_id):
    ctx = ""
    if persona.get('persona_description'):
        ctx = f"""
Customer Profile:
- Description: {persona.get('persona_description', '')}
- Industry: {persona.get('persona_industry', 'general')}
- Role: {persona.get('persona_role', 'professional')}
- Experience: {persona.get('persona_experience', 'mid-career')}
- Work Style: {persona.get('persona_work_style', 'balanced')}
- Tech Savviness: {persona.get('persona_tech_savvy', 'comfortable')}
- Communication Style: {persona.get('persona_communication', 'professional')}
- Writing Style: {persona.get('writing_style', 'Professional')}
"""
        if persona.get('company_culture'):
            ctx += f"""
Company Context:
- Size: {persona.get('company_size_descriptor', 'established')}
- Culture: {persona.get('company_culture', 'professional')}
- Decision Style: {persona.get('company_decision_style', 'thorough')}
- Primary Concern: {persona.get('company_primary_concern', 'value')}
"""
    if group_chars:
        ctx += f"""
Customer Segment ({group_id}):
- Description: {group_chars.get('description', '')}
- Social Media Tone: {group_chars.get('social_media_tone', '')}
"""
    return ctx


def build_event_context_text(post_type, event_context):
    if post_type == 'perceived_quality_penalty' and event_context:
        event_type = event_context.get('event_type', 'unknown')
        variants = EVENT_DESCRIPTION_VARIANTS.get(event_type)
        if variants:
            event_desc = variants[0]  # Use first variant for determinism
        else:
            event_desc = "I'm having issues with the service"
        return f"""
IMPORTANT - This post is about a SPECIFIC ISSUE:
What happened: {event_desc}
This is frustrating the customer RIGHT NOW. The post should specifically mention this problem.
"""

    elif post_type == 'satisfaction_change' and event_context:
        direction = event_context.get('change_direction', 'changed')
        reasons = event_context.get('reasons', [])
        reason_descriptions = {
            'overload': 'the service becoming slow',
            'outage': 'service downtime',
            'unresolved_issue': 'poor support response',
            'quota_exceeded': 'hitting usage limits',
            'quality_downgrade': 'quality getting worse',
            'good_service': 'consistently good service'
        }
        reason_texts = [reason_descriptions.get(r, r) for r in reasons]
        reasons_str = ', '.join(reason_texts) if reason_texts else 'recent experience'

        if direction == 'improved':
            return f"""
IMPORTANT - This post is about IMPROVING experience:
The customer's satisfaction has been improving due to: {reasons_str}
The post should reflect this positive change - things are getting better!
"""
        else:
            return f"""
IMPORTANT - This post is about DECLINING experience:
The customer's satisfaction has been declining due to: {reasons_str}
The post should reflect this frustration - things are getting worse!
"""

    elif post_type == 'unmet_promises' and event_context:
        promises = event_context.get('promises', [])
        promises_str = '; '.join(promises[:3]) if promises else 'various commitments'
        return f"""
IMPORTANT - This post is about BROKEN PROMISES:
The company made promises during sales/negotiations that were not fulfilled.
Broken promises: {promises_str}
The customer feels deceived and wants to warn others. The post should be a warning to potential customers about unfulfilled commitments.
"""

    elif post_type == 'competitor_product' and event_context:
        comp_desc = event_context.get('competitor_event_description',
                                      'A competitor launched a notable update')
        variants = EVENT_DESCRIPTION_VARIANTS.get('competitor_product', [])
        angle = variants[0] if variants else "I'm seeing better options in the market"
        return f"""
IMPORTANT - This post is about a COMPETITOR PRODUCT:
Context: {comp_desc}
Customer angle: {angle}
The customer is comparing the competitor's offering to {PRODUCT_NAME}. They may be considering switching,
impressed by the competitor, or warning others. The post should specifically discuss the competitor's
advantages and how {PRODUCT_NAME} compares — positively or negatively depending on the customer's satisfaction.
If the customer is satisfied (satisfaction > 0), they might acknowledge the competitor but express loyalty.
If dissatisfied (satisfaction < 0), they might actively consider switching or recommend the competitor.
"""

    return ""


def render_prompt(label, post_type, event_context, persona, group_chars, group_id,
                  satisfaction, sentiment):
    persona_context = build_persona_context(persona, group_chars, group_id)
    event_context_text = build_event_context_text(post_type, event_context)

    format_directive = POST_FORMAT_DIRECTIVES[0]  # Deterministic
    writing_angle = WRITING_ANGLE_POOL[0]

    system_prompt = f"""You are simulating a customer of {COMPANY_NAME}, a SaaS company offering {PRODUCT_NAME}.

Generate a realistic social media post from this customer's perspective.

{persona_context}
{event_context_text}
Post Format: {format_directive}
Writing Angle: {writing_angle}

Guidelines:
- Match the customer's writing style and tone
- The post should reflect a {sentiment} experience
- Customer satisfaction level: {satisfaction:.0%}
- Keep it brief (under 150 words, or shorter if the post format calls for it)
- Keep it authentic — vary your style, length, and structure
- Don't be generic - include specific details that make it feel real
{"- IMPORTANT: Focus on the specific issue/event described above" if event_context_text else ""}

Output ONLY the post text, nothing else."""

    user_prompt = f"Write a {sentiment} social media post about your experience with {PRODUCT_NAME}."

    return label, system_prompt, user_prompt


# ── Define all 11 event types ──

ALL_PROMPTS = []

# 1. perceived_quality_penalty — overload
ALL_PROMPTS.append(render_prompt(
    "1. perceived_quality_penalty (overload) — D_S03 Individual",
    'perceived_quality_penalty',
    {'event_type': 'overload', 'penalty': 0.15},
    PERSONA_INDIVIDUAL, GROUP_D_S03, 'D_S03',
    satisfaction=0.30, sentiment='negative',
))

# 2. perceived_quality_penalty — outage
ALL_PROMPTS.append(render_prompt(
    "2. perceived_quality_penalty (outage) — D_S03 Individual",
    'perceived_quality_penalty',
    {'event_type': 'outage', 'penalty': 0.25},
    PERSONA_INDIVIDUAL, GROUP_D_S03, 'D_S03',
    satisfaction=0.20, sentiment='negative',
))

# 3. perceived_quality_penalty — issue (unresolved support)
ALL_PROMPTS.append(render_prompt(
    "3. perceived_quality_penalty (issue) — D_S03 Individual",
    'perceived_quality_penalty',
    {'event_type': 'issue', 'penalty': 0.09},
    PERSONA_INDIVIDUAL, GROUP_D_S03, 'D_S03',
    satisfaction=0.40, sentiment='negative',
))

# 4. perceived_quality_penalty — quota
ALL_PROMPTS.append(render_prompt(
    "4. perceived_quality_penalty (quota) — D_S03 Individual",
    'perceived_quality_penalty',
    {'event_type': 'quota', 'penalty': 0.12},
    PERSONA_INDIVIDUAL, GROUP_D_S03, 'D_S03',
    satisfaction=0.35, sentiment='negative',
))

# 5. perceived_quality_penalty — contract_dissatisfaction (enterprise)
ALL_PROMPTS.append(render_prompt(
    "5. perceived_quality_penalty (contract_dissatisfaction) — D_E04 Enterprise",
    'perceived_quality_penalty',
    {'event_type': 'contract_dissatisfaction', 'penalty': 0, 'locked_in': True},
    PERSONA_ENTERPRISE, GROUP_D_E04, 'D_E04',
    satisfaction=-0.15, sentiment='negative',
))

# 6. satisfaction_change — improved
ALL_PROMPTS.append(render_prompt(
    "6. satisfaction_change (improved) — D_S03 Individual",
    'satisfaction_change',
    {'change_direction': 'improved', 'change_amount': 0.05, 'reasons': ['good_service']},
    PERSONA_INDIVIDUAL, GROUP_D_S03, 'D_S03',
    satisfaction=0.75, sentiment='positive',
))

# 7. satisfaction_change — declined
ALL_PROMPTS.append(render_prompt(
    "7. satisfaction_change (declined) — D_S03 Individual",
    'satisfaction_change',
    {'change_direction': 'declined', 'change_amount': 0.08,
     'reasons': ['overload', 'unresolved_issue']},
    PERSONA_INDIVIDUAL, GROUP_D_S03, 'D_S03',
    satisfaction=0.35, sentiment='negative',
))

# 8. customer_cancel (churned) — no special handler, falls through to general
ALL_PROMPTS.append(render_prompt(
    "8. customer_cancel (churned customer) — D_S03 Individual",
    'customer_cancel',  # No handler in generate_social_post — treated as general
    {'event_type': 'customer_cancel', 'reason': 'RELIABILITY_CHANGE'},
    PERSONA_INDIVIDUAL, GROUP_D_S03, 'D_S03',
    satisfaction=-0.10, sentiment='negative',
))

# 9. competitor_product
ALL_PROMPTS.append(render_prompt(
    "9. competitor_product — D_S03 Individual",
    'competitor_product',
    {'competitor_event_description': 'RivalAI launched a free tier specifically for non-profits with grant-writing templates'},
    PERSONA_INDIVIDUAL, GROUP_D_S03, 'D_S03',
    satisfaction=0.45, sentiment='negative',
))

# 10. unmet_promises (enterprise)
ALL_PROMPTS.append(render_prompt(
    "10. unmet_promises — D_E04 Enterprise",
    'unmet_promises',
    {'promises': [
        'Promised SOC 2 Type II audit report within 30 days of signing',
        'Guaranteed 99.99% uptime SLA for banking-grade reliability',
        'Said on-premises deployment option would be available by Q2',
    ]},
    PERSONA_ENTERPRISE, GROUP_D_E04, 'D_E04',
    satisfaction=0.25, sentiment='negative',
))

# 11. general_satisfaction (no event — default)
ALL_PROMPTS.append(render_prompt(
    "11. general_satisfaction (no event, default) — D_S03 Individual",
    'general_satisfaction',
    None,
    PERSONA_INDIVIDUAL, GROUP_D_S03, 'D_S03',
    satisfaction=0.65, sentiment='positive',
))


# ── Output ──

SEP = "=" * 80

for label, system_prompt, user_prompt in ALL_PROMPTS:
    print(SEP)
    print(f"  {label}")
    print(SEP)
    print()
    print("SYSTEM:")
    print(system_prompt)
    print()
    print("USER:")
    print(user_prompt)
    print()
    print()
