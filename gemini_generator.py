"""Gemini integration: builds the prompt and returns the generated legal text."""
import re
import time

from config import GEMINI_API_KEY, GEMINI_MODEL, MOCK_MODE

# Prefer the newer `google-genai` SDK; fall back to `google-generativeai` (used in the docs).
try:
    from google import genai as _new_genai
except ImportError:  # pragma: no cover
    _new_genai = None
try:
    import google.generativeai as _legacy_genai
except ImportError:  # pragma: no cover
    _legacy_genai = None


class ConfigError(RuntimeError):
    """Missing API key / SDK."""


class GenerationError(RuntimeError):
    """The model call failed."""


def split_terms(terms: str) -> list:
    """Split semicolon / newline separated terms into a clean list."""
    return [t.strip(" -\t") for t in re.split(r"[;\n]", terms or "") if t.strip(" -\t")]


class GeminiDocumentGenerator:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or GEMINI_MODEL
        self._client = None

    # ---------- prompt ----------
    def build_prompt(self, document_type, parties, terms, dates) -> str:
        term_lines = "\n".join(f"- {t}" for t in split_terms(terms)) or "- (none supplied; use standard market terms)"
        return (
            f"You are an experienced legal drafter. Draft a comprehensive, professional legal "
            f"document titled '{document_type}'.\n\n"
            f"Involved parties: {parties}\n"
            f"Effective date: {dates}\n"
            f"Terms and conditions that MUST each appear as clauses:\n{term_lines}\n\n"
            "Formatting rules:\n"
            "- Output plain text only. Do NOT use markdown symbols such as #, * or **.\n"
            "- First line is the document title. Then the preamble/recitals.\n"
            "- Put each section heading on its own line as a number and name ending in a colon, "
            "e.g. '1. Services:', followed by its paragraphs.\n"
            "- Cover as relevant: definitions, obligations, payment/consideration, term and termination, "
            "confidentiality, intellectual property, dispute resolution, governing law, entire agreement, severability.\n"
            "- End with 'IN WITNESS WHEREOF' and a signature block using lines of underscores.\n"
            "- Use [square-bracket placeholders] for any detail not provided. Never invent facts.\n"
            "- Ensure formal legal structure with multiple sections and legal clauses.\n"
            "- Return only the document, with no commentary before or after."
        )

    # ---------- model call ----------
    def _call_model(self, prompt: str) -> str:
        if _new_genai is not None:
            if self._client is None:
                self._client = _new_genai.Client(api_key=GEMINI_API_KEY)
            resp = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"temperature": 0.4, "max_output_tokens": 8192},
            )
            return resp.text
        if _legacy_genai is not None:
            _legacy_genai.configure(api_key=GEMINI_API_KEY)
            model = _legacy_genai.GenerativeModel(self.model_name)
            return model.generate_content(
                prompt, generation_config={"temperature": 0.4, "max_output_tokens": 8192}
            ).text
        raise ConfigError("No Gemini SDK installed. Run: pip install -r requirements.txt")

    def generate_document(self, document_type, parties, terms, dates) -> str:
        if MOCK_MODE:
            return self._mock(document_type, parties, terms, dates)
        if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
            raise ConfigError("GEMINI_API_KEY is not set. Add it to the .env file (or set LEGALEASE_MOCK=1 to test).")

        prompt = self.build_prompt(document_type, parties, terms, dates)
        last_err = None
        for attempt in range(3):
            try:
                text = self._call_model(prompt)
                if text and text.strip():
                    return text
                last_err = "The model returned an empty response."
            except ConfigError:
                raise
            except Exception as exc:  # network, quota, bad model name...
                last_err = str(exc)
            time.sleep(1.5 * (attempt + 1))
        raise GenerationError(f"Gemini request failed: {last_err}")

    # ---------- offline sample ----------
    @staticmethod
    def _mock(document_type, parties, terms, dates) -> str:
        clauses = "\n".join(
            f"- {t}" for t in split_terms(terms)
        ) or "- Standard terms apply."
        return f"""{document_type}

This Agreement is made effective as of {dates} (the "Effective Date").

Between:
{parties}

WITNESSETH:

WHEREAS, the parties wish to set out the terms of their relationship; and

NOW, THEREFORE, in consideration of the mutual covenants herein, the parties agree as follows:

1. Scope of Agreement:

The parties agree to the obligations described in this {document_type}.

2. Specific Terms:

{clauses}

3. Confidentiality:

Each party shall keep the other party's confidential information secret and use it only for this Agreement.

4. Term and Termination:

This Agreement begins on the Effective Date and continues until terminated by either party on written notice.

5. Governing Law:

This Agreement is governed by the laws of [State / Country].

6. Entire Agreement and Severability:

This Agreement is the entire agreement of the parties. If any provision is unenforceable, the rest remains in effect.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.

______________________________
[Party 1 Signature]

______________________________
[Party 2 Signature]