from typing import List, Optional
from pydantic import BaseModel, Field

class ElementSemantics(BaseModel):
    element_id: str
    role: str = Field(description="UI role: button, text_input, heading, icon, card, tab, badge, image")
    plain_description: str = Field(description="Human readable plain-language explanation of what this element represents or does")
    form_field_type: Optional[str] = Field(default=None, description="phone, otp, email, password, pan, aadhaar, search, quantity, address, or none")
    suggested_test_value: Optional[str] = None

class ScreenUnderstanding(BaseModel):
    fingerprint: str
    screen_name: str = Field(description="Short human-friendly title of the screen e.g. Login Screen, Home Feed")
    purpose: str = Field(description="Exactly one sentence describing the core purpose of this screen")
    screen_category: str = Field(description="onboarding, authentication, catalog, product_detail, checkout, profile, kyc, settings")
    elements: List[ElementSemantics] = Field(default_factory=list)
    key_actions: List[str] = Field(default_factory=list, description="Primary user actions available on this screen")
