import os
import json
import base64
import time
from typing import Optional, Dict, Any, List
from pydantic import ValidationError
from common.config import get_groq_api_key
from common.models import ScreenState, UIElement
from common.groq_audit import log_groq_call
from layer4_understanding.schema import ScreenUnderstanding, ElementSemantics

class VlmScreenAnalyzer:
    """
    Production Multimodal Screen Understanding Engine powered by Groq.
    Grounds live screenshot pixels and compact Android UIAutomator hierarchies together
    using Groq's high-speed vision model (qwen/qwen3.6-27b).

    Enforces strict Pydantic schema validation, structural fingerprint caching,
    exponential backoff rate-limit recovery, and self-correcting validation retry loops.
    """

    def __init__(
        self,
        provider: str = "groq",
        api_key: Optional[str] = None,
        model: str = "qwen/qwen3.8-27b"
    ):
        self.provider = provider
        self.model = model
        self.cache: Dict[str, ScreenUnderstanding] = {}
        
        if self.provider == "groq":
            self.api_key = api_key or get_groq_api_key(required=True)
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        elif self.provider == "offline_heuristic":
            # Explicitly preserved only as an offline test fixture for unit tests
            self.api_key = None
            self.client = None
        else:
            raise ValueError(f"Unsupported provider '{provider}'. Use 'groq' for production AI inference or 'offline_heuristic' for unit testing.")

    def analyze_screen(self, screen_state: ScreenState, max_retries: int = 3) -> ScreenUnderstanding:
        """
        Analyzes live Android screen state.
        Checks fingerprint cache first to eliminate duplicate API requests.
        """
        fp = screen_state.fingerprint
        if fp in self.cache:
            return self.cache[fp]

        # Unit test offline fixture path
        if self.provider == "offline_heuristic":
            result = self._offline_heuristic_test_fixture(screen_state)
            self.cache[fp] = result
            return result

        # Production Real Groq Multimodal AI Inference
        result = self._call_groq_multimodal(screen_state, max_retries=max_retries)
        self.cache[fp] = result
        return result

    def _call_groq_multimodal(self, screen_state: ScreenState, max_retries: int = 3) -> ScreenUnderstanding:
        """
        Invokes Groq's multimodal vision model (qwen/qwen3.8-27b / qwen/qwen3.6-27b) with grounded screenshot + UI tree.
        Features self-correction on schema failure and exponential backoff on 429 rate limits.
        """
        # 1. Prepare compact, token-efficient UI tree summary
        compact_tree = []
        for el in screen_state.elements[:40]:
            item = {
                "id": el.element_id,
                "class": el.class_name.split(".")[-1],
                "bounds": [el.bounds.left, el.bounds.top, el.bounds.right, el.bounds.bottom] if el.bounds else None,
                "clickable": el.clickable,
                "editable": el.editable
            }
            if el.text:
                item["text"] = el.text[:60]
            if el.content_desc:
                item["desc"] = el.content_desc[:60]
            compact_tree.append(item)

        ui_tree_json = json.dumps(compact_tree, separators=(',', ':'))

        # 2. Encode screenshot as base64 data URI (guaranteeing >= 32px dimensions required by Groq)
        if screen_state.screenshot_bytes and len(screen_state.screenshot_bytes) > 200:
            b64_img = base64.b64encode(screen_state.screenshot_bytes).decode("utf-8")
        else:
            import io
            from PIL import Image
            dummy = Image.new("RGB", (100, 100), color=(20, 24, 39))
            buf = io.BytesIO()
            dummy.save(buf, format="PNG")
            b64_img = base64.b64encode(buf.getvalue()).decode("utf-8")

        base_prompt = f"""
You are an autonomous reverse-engineering AI perception engine for mobile applications.
Analyze this Android application screen by grounding the visual screenshot together with the UI hierarchy tree.
Extract the true screen purpose, visual element semantics, and form field classifications even if developer labels are absent or cryptic.

Required JSON Output Schema:
{{
  "fingerprint": "{screen_state.fingerprint}",
  "screen_name": "Short human-friendly title of the screen (e.g. Login Screen, Network Hub, Post Composer, Settings)",
  "purpose": "Exactly one clear sentence describing the primary purpose of this screen.",
  "screen_category": "onboarding | authentication | catalog | product_detail | checkout | profile | kyc | settings | general_view",
  "key_actions": ["Primary action 1", "Primary action 2"],
  "elements": [
    {{
      "element_id": "Exact matching element ID from the UI tree",
      "role": "button | text_input | heading | icon | card | tab | badge | image",
      "plain_description": "Plain language explanation grounded in visual appearance and context",
      "form_field_type": "phone | otp | email | password | pan | aadhaar | search | quantity | address | null"
    }}
  ]
}}

Live Android UI Tree Context:
{ui_tree_json}
"""

        current_prompt = base_prompt
        last_error = None

        for attempt in range(max_retries):
            start_time = time.time()
            try:
                # Construct Groq multimodal message payload
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": current_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{b64_img}"
                                }
                            }
                        ]
                    }
                ]

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0.1,
                    max_tokens=2048
                )

                latency_ms = (time.time() - start_time) * 1000
                raw_text = response.choices[0].message.content or "{}"
                parsed_json = json.loads(raw_text)

                # Ensure fingerprint is preserved
                parsed_json["fingerprint"] = screen_state.fingerprint

                # Validate against strict Pydantic schema
                validated = ScreenUnderstanding.model_validate(parsed_json)

                # Auditable API call logging
                log_groq_call(
                    layer="Layer 4 (Screen Understanding)",
                    model=self.model,
                    latency_ms=latency_ms,
                    input_summary={"screen_fp": screen_state.fingerprint, "elements_count": len(screen_state.elements)},
                    output_summary={"screen_name": validated.screen_name, "category": validated.screen_category, "elements_identified": len(validated.elements)},
                    status="success"
                )

                return validated

            except ValidationError as ve:
                last_error = f"Schema ValidationError: {ve}"
                # Append validation error for self-correction in next attempt
                current_prompt = base_prompt + f"\n\nCRITICAL FIX REQUIRED: Your previous JSON response failed validation:\n{ve}\nRegenerate strictly valid JSON."
                time.sleep(1.0)

            except Exception as e:
                last_error = str(e)
                # Check for rate-limit 429
                is_rate_limit = "429" in str(e) or "rate" in str(e).lower()
                sleep_sec = (2 ** attempt) * 2.0 if is_rate_limit else 1.5
                time.sleep(sleep_sec)

        # Log failure if all retries exhausted
        log_groq_call(
            layer="Layer 4 (Screen Understanding)",
            model=self.model,
            latency_ms=0.0,
            input_summary={"screen_fp": screen_state.fingerprint},
            output_summary={},
            status="failed",
            error_message=last_error
        )

        # Surface clear error and flagged incomplete screen profile (never silently substitute hardcoded guess)
        return ScreenUnderstanding(
            fingerprint=screen_state.fingerprint,
            screen_name="Flagged Screen (Incomplete Inference)",
            purpose=f"Flagged for manual review: Groq vision inference failed after {max_retries} attempts ({last_error}).",
            screen_category="general_view",
            elements=[],
            key_actions=[]
        )

    def _offline_heuristic_test_fixture(self, screen_state: ScreenState) -> ScreenUnderstanding:
        """
        EXPLICITLY LABELED OFFLINE TEST FIXTURE.
        Used strictly in unit testing (tests/test_layer4.py) to prevent external network requirements.
        Never called in production exploration.
        """
        elements = screen_state.elements
        screen_name = "Application Screen"
        screen_category = "general_view"
        purpose = "Allows users to view and interact with application features."

        for el in elements:
            if "TextView" in el.class_name and el.bounds and el.bounds.top < 350 and el.text:
                screen_name = el.text.strip().title()
                break

        all_text = " ".join([el.text or "" for el in elements] + [el.content_desc or "" for el in elements]).lower()

        if any(w in all_text for w in ["login", "sign in", "password", "enter phone", "otp"]):
            screen_category = "authentication"
            screen_name = "Login Screen"
            purpose = "Authenticates the user into the mobile application using phone or credentials."
        elif any(w in all_text for w in ["welcome", "get started", "onboarding"]):
            screen_category = "onboarding"
            screen_name = "Splash / Onboarding Screen"
            purpose = "Introduces new users to the features and entry flow of the application."
        elif any(w in all_text for w in ["settings", "preferences"]):
            screen_category = "settings"
            screen_name = "Settings"
            purpose = "Provides application and system configuration controls."

        elements_semantics: List[ElementSemantics] = []
        for el in elements:
            token_str = f"{el.text or ''} {el.content_desc or ''} {el.element_id or ''}".lower()
            if el.editable or "edittext" in el.class_name.lower():
                role = "text_input"
            elif el.clickable or "button" in el.class_name.lower():
                role = "button"
            else:
                role = "heading" if (el.bounds and el.bounds.top < 350) else "text"

            form_type = None
            if any(w in token_str for w in ["phone", "mobile"]):
                form_type = "phone"
            elif any(w in token_str for w in ["otp", "code", "pin"]):
                form_type = "otp"
            elif "email" in token_str:
                form_type = "email"
            elif "password" in token_str:
                form_type = "password"

            elements_semantics.append(ElementSemantics(
                element_id=el.element_id,
                role=role,
                plain_description=f"UI element {el.text or el.content_desc or el.element_id}",
                form_field_type=form_type
            ))

        return ScreenUnderstanding(
            fingerprint=screen_state.fingerprint,
            screen_name=screen_name,
            purpose=purpose,
            screen_category=screen_category,
            elements=elements_semantics,
            key_actions=["Interact with screen controls"]
        )
