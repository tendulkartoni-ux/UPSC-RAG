"""
LLM Router — one call_llm() interface over Groq / Anthropic / OpenAI.

Why a router? The user picks a provider in the sidebar. We want the rest of
the app (chat, quiz gen, etc.) to stay provider-agnostic.
"""
from __future__ import annotations
from typing import List, Dict, Optional, Generator
import streamlit as st


def call_llm(messages: List[Dict], temperature: float = 0.3,
             max_tokens: int = 1500, stream: bool = False) -> str | Generator[str, None, None]:
    """
    messages: OpenAI-style [{'role': 'system'|'user'|'assistant', 'content': str}]
    Returns a string if stream=False, else a generator of text deltas.
    """
    provider = st.session_state.get("llm_provider", "Groq (free tier)")
    model = st.session_state.get("llm_model", "llama-3.3-70b-versatile")
    api_key = st.session_state.get("api_key", "").strip()

    if not api_key:
        err = "⚠️ No API key set. Add one in the sidebar."
        return err if not stream else _err_stream(err)

    try:
        if provider == "Groq (free tier)":
            return _call_groq(messages, model, api_key, temperature, max_tokens, stream)
        elif provider == "Anthropic Claude":
            return _call_anthropic(messages, model, api_key, temperature, max_tokens, stream)
        elif provider == "OpenAI":
            return _call_openai(messages, model, api_key, temperature, max_tokens, stream)
    except Exception as e:
        err = f"⚠️ LLM call failed: {type(e).__name__}: {e}"
        return err if not stream else _err_stream(err)


def _err_stream(msg: str) -> Generator[str, None, None]:
    yield msg


# ── Groq ─────────────────────────────────────────────────────────────────────
def _call_groq(messages, model, api_key, temperature, max_tokens, stream):
    from groq import Groq
    client = Groq(api_key=api_key)
    if stream:
        def gen():
            resp = client.chat.completions.create(
                model=model, messages=messages,
                temperature=temperature, max_tokens=max_tokens, stream=True,
            )
            for chunk in resp:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        return gen()
    resp = client.chat.completions.create(
        model=model, messages=messages,
        temperature=temperature, max_tokens=max_tokens,
    )
    return resp.choices[0].message.content


# ── Anthropic ────────────────────────────────────────────────────────────────
def _call_anthropic(messages, model, api_key, temperature, max_tokens, stream):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    # Anthropic API wants system separated from the messages list
    system = ""
    filt = []
    for m in messages:
        if m["role"] == "system":
            system += m["content"] + "\n"
        else:
            filt.append(m)
    if stream:
        def gen():
            with client.messages.stream(
                model=model, system=system or None, messages=filt,
                temperature=temperature, max_tokens=max_tokens,
            ) as s:
                for text in s.text_stream:
                    yield text
        return gen()
    resp = client.messages.create(
        model=model, system=system or None, messages=filt,
        temperature=temperature, max_tokens=max_tokens,
    )
    return resp.content[0].text


# ── OpenAI ───────────────────────────────────────────────────────────────────
def _call_openai(messages, model, api_key, temperature, max_tokens, stream):
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    if stream:
        def gen():
            resp = client.chat.completions.create(
                model=model, messages=messages,
                temperature=temperature, max_tokens=max_tokens, stream=True,
            )
            for chunk in resp:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        return gen()
    resp = client.chat.completions.create(
        model=model, messages=messages,
        temperature=temperature, max_tokens=max_tokens,
    )
    return resp.choices[0].message.content
