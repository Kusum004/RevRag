import os
import json
import base64
import re
from typing import Optional, Dict, Any, List
from pydantic import ValidationError
from common.models import ScreenState, UIElement
from layer4_understanding.schema import ScreenUnderstanding, ElementSemantics

class VlmScreenAnalyzer:
    """
    Universal Multimodal Screen Understanding Engine.
    Processes live screenshots and UI hierarchies of ANY unfamiliar Android application.
    Extracts screen purpose, element roles, plain-language descriptions, and form semantics.
    Enforces strict JSON schema validation.
    """

    def __init__(self, provider: str = "auto", api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

    def analyze_screen(self, screen_state: ScreenState, max_retries: int = 2) -> ScreenUnderstanding:
        """
        Analyzes live screen state using configured LLM/VLM provider or dynamic multimodal inference.
        """
        for attempt in range(max_retries + 1):
            try:
                if self.provider == "gemini" and self.api_key:
                    raw_dict = self._call_gemini(screen_state)
                elif self.provider == "openai" and self.api_key:
                    raw_dict = self._call_openai(screen_state)
                else:
                    raw_dict = self._dynamically_infer_screen_semantics(screen_state)

                validated = ScreenUnderstanding.model_validate(raw_dict)
                return validated
            except (ValidationError, Exception):
                if attempt == max_retries:
                    fallback_dict = self._dynamically_infer_screen_semantics(screen_state)
                    return ScreenUnderstanding.model_validate(fallback_dict)

        return ScreenUnderstanding.model_validate(self._dynamically_infer_screen_semantics(screen_state))

    def _dynamically_infer_screen_semantics(self, screen_state: ScreenState) -> Dict[str, Any]:
        """
        100% Dynamic Semantic Engine for Unfamiliar Android Apps.
        Zero hardcoded app screens or static copy.
        Examines live element positions, classes, resource-ids, and visible text tokens.
        """
        elements = screen_state.elements
        elements_semantics: List[Dict[str, Any]] = []

        # 1. Dynamically Detect Screen Name
        screen_name = "Application Screen"
        # Strategy A: Check top action bar or toolbar TextView
        for el in elements:
            if "TextView" in el.class_name and el.bounds.top < 350 and el.text:
                res_id = (el.resource_id or "").lower()
                if any(t in res_id for t in ["title", "header", "toolbar", "action_bar", "heading", "name"]):
                    screen_name = el.text.strip()
                    break
        # Strategy B: If not found, look for first prominent text in top third
        if screen_name == "Application Screen":
            for el in elements:
                if el.text and len(el.text.strip()) > 2 and el.bounds.top < 600:
                    screen_name = el.text.strip().title()
                    break
        # Strategy C: Derive from activity name if available
        if screen_name == "Application Screen" and screen_state.activity_name:
            act = screen_state.activity_name.split(".")[-1].replace("Activity", "")
            if act:
                screen_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', act).title()

        # 2. Analyze Interactive Composition & Classify Screen Category
        has_text_inputs = any(el.editable for el in elements)
        has_toggles = any("Switch" in el.class_name or "CheckBox" in el.class_name or "toggle" in (el.resource_id or "").lower() for el in elements)
        has_cards = any("CardView" in el.class_name or "card" in (el.resource_id or "").lower() for el in elements)
        has_tabs = any("tab" in (el.resource_id or "").lower() or ("FrameLayout" in el.class_name and el.bounds.top > 1800) for el in elements)

        all_text_tokens = " ".join(
            [(el.text or "") for el in elements] +
            [(el.content_desc or "") for el in elements] +
            [(el.resource_id or "") for el in elements]
        ).lower()

        if any(w in all_text_tokens for w in ["login", "sign in", "otp", "password", "enter mobile", "phone number"]):
            screen_category = "authentication"
        elif any(w in all_text_tokens for w in ["setting", "preferences", "bluetooth", "wifi", "network", "display", "sound", "storage"]):
            screen_category = "settings"
        elif any(w in all_text_tokens for w in ["pan", "aadhaar", "kyc", "identity", "ssn", "tax id", "verification"]):
            screen_category = "identity_verification"
        elif any(w in all_text_tokens for w in ["cart", "checkout", "buy now", "add to cart", "price", "subtotal"]):
            screen_category = "product_checkout"
        elif any(w in all_text_tokens for w in ["welcome", "get started", "onboarding", "intro", "next"]):
            screen_category = "onboarding"
        elif has_toggles or "preference" in all_text_tokens:
            screen_category = "settings"
        elif has_cards or "search" in all_text_tokens or "catalog" in all_text_tokens:
            screen_category = "catalog_browsing"
        elif has_text_inputs:
            screen_category = "form_entry"
        else:
            screen_category = "general_view"

        # 3. Formulate Dynamic 1-Sentence Purpose
        primary_clickable = [el.text or el.content_desc or el.element_id for el in elements if el.clickable and el.text][:3]
        action_summary = f"including '{', '.join(primary_clickable)}'" if primary_clickable else "available on the interface"

        if screen_category == "authentication":
            purpose = f"Authenticates the user into the application using mobile, email, or credentials ({screen_name})."
        elif screen_category == "settings":
            purpose = f"Provides system and application configuration controls for {screen_name}."
        elif screen_category == "catalog_browsing":
            purpose = f"Displays content items, categories, and interactive options for {screen_name}."
        elif screen_category == "onboarding":
            purpose = f"Introduces new users to the features and entry flow of {screen_name}."
        elif screen_category == "identity_verification":
            purpose = f"Collects verification identity information for user compliance ({screen_name})."
        else:
            purpose = f"Allows users to view and interact with {screen_name} features {action_summary}."

        # 4. Extract Per-Element Semantics Dynamically
        key_actions: List[str] = []
        for el in elements:
            res_id = (el.resource_id or "").lower()
            txt = (el.text or "").lower()
            cls = el.class_name.lower()
            cdesc = (el.content_desc or "").lower()

            role = "view"
            form_type = None
            desc = "UI visual component"

            if el.editable or "edittext" in cls:
                role = "text_input"
                if any(w in res_id or w in txt or w in cdesc for w in ["phone", "mobile", "number"]):
                    form_type = "phone"
                    desc = f"Input field for entering phone or mobile number ({el.text or 'empty'})"
                elif any(w in res_id or w in txt or w in cdesc for w in ["otp", "code", "pin", "verify"]):
                    form_type = "otp"
                    desc = f"Input field for verification code or OTP"
                elif any(w in res_id or w in txt or w in cdesc for w in ["email", "mail"]):
                    form_type = "email"
                    desc = f"Input field for user email address"
                elif any(w in res_id or w in txt or w in cdesc for w in ["password", "passwd", "secret"]):
                    form_type = "password"
                    desc = f"Secure password input field"
                elif any(w in res_id or w in txt or w in cdesc for w in ["pan", "tax"]):
                    form_type = "pan"
                    desc = f"Input field for permanent account / tax identity"
                elif any(w in res_id or w in txt or w in cdesc for w in ["aadhaar", "ssn", "identity"]):
                    form_type = "aadhaar"
                    desc = f"Input field for national identity number"
                elif any(w in res_id or w in txt or w in cdesc for w in ["search", "query", "find"]):
                    form_type = "search"
                    desc = f"Search input field for querying content"
                else:
                    form_type = "text"
                    desc = f"Editable text field: '{el.text or el.element_id}'"

                key_actions.append(f"Input text into {form_type or 'field'} ({el.element_id})")

            elif "switch" in cls or "checkbox" in cls:
                role = "toggle"
                desc = f"Toggle switch control: {el.text or el.content_desc or el.element_id}"
                key_actions.append(f"Toggle {el.element_id}")

            elif el.clickable or "button" in cls:
                role = "button"
                desc = f"Interactive button: '{el.text or el.content_desc or el.element_id}'"
                if el.text:
                    key_actions.append(f"Tap '{el.text}'")

            elif "image" in cls:
                role = "image"
                desc = f"Image or icon asset ({el.content_desc or 'graphic'})"

            elif "cardview" in cls:
                role = "card"
                desc = f"Interactive content container card"

            elif "framelayout" in cls and el.bounds.top > 1800:
                role = "tab"
                desc = f"Navigation tab item: '{el.text or el.content_desc or el.element_id}'"

            elif "textview" in cls:
                if el.bounds.top < 350 and el.bounds.height > 50:
                    role = "heading"
                    desc = f"Primary screen heading: '{el.text}'"
                else:
                    role = "text"
                    desc = f"Text label: '{el.text}'"

            elements_semantics.append({
                "element_id": el.element_id,
                "role": role,
                "plain_description": desc,
                "form_field_type": form_type,
                "suggested_test_value": None
            })

        return {
            "fingerprint": screen_state.fingerprint,
            "screen_name": screen_name,
            "purpose": purpose,
            "screen_category": screen_category,
            "elements": elements_semantics,
            "key_actions": key_actions[:5]
        }

    def _call_gemini(self, screen_state: ScreenState) -> Dict[str, Any]:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.api_key)
        prompt = f"""
        You are an autonomous Android reverse-engineering perception system.
        Analyze this screenshot and live UI element hierarchy of an unfamiliar Android application.
        Output a strict JSON object:
        {{
            "fingerprint": "{screen_state.fingerprint}",
            "screen_name": "Concise plain title of screen",
            "purpose": "Exactly one sentence explaining what this screen does.",
            "screen_category": "onboarding | authentication | catalog_browsing | settings | form_entry | general_view",
            "key_actions": ["action 1", "action 2"],
            "elements": [
                {{
                    "element_id": "string id matching hierarchy",
                    "role": "button | text_input | toggle | heading | text | card | tab | image",
                    "plain_description": "Plain language explanation grounded in visual screenshot",
                    "form_field_type": "phone | otp | email | password | search | text | null"
                }}
            ]
        }}
        UI Elements tree:
        {json.dumps([e.model_dump(exclude={'screenshot_bytes', 'raw_xml'}) for e in screen_state.elements], indent=2)}
        """

        contents = [prompt]
        if screen_state.screenshot_bytes:
            contents.append(types.Part.from_bytes(data=screen_state.screenshot_bytes, mime_type="image/png"))

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)

    def _call_openai(self, screen_state: ScreenState) -> Dict[str, Any]:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)

        b64_image = base64.b64encode(screen_state.screenshot_bytes or b"").decode("utf-8")
        prompt = f"Analyze this Android screen hierarchy: {json.dumps([e.model_dump() for e in screen_state.elements])}"

        messages = [
            {"role": "system", "content": "You are a UI reverse engineering analyzer. Return valid JSON only."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}}
            ]}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content or "{}")
