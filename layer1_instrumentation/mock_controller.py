import io
import time
from typing import Optional, Tuple, Dict, Any
from PIL import Image, ImageDraw, ImageFont
from common.models import Action, ActionType, ScreenState, UIElement, BoundingBox
from layer1_instrumentation.base import IDeviceController

class MockDeviceController(IDeviceController):
    """
    High-fidelity simulated Android App device environment.
    Simulates a 6-screen e-commerce & fintech Android application
    with dynamic content, interactive input fields, OTP/KYC gates,
    realistic XML hierarchy dumps, and synthesized PNG screenshots.
    """

    def __init__(self, width: int = 1080, height: int = 2400):
        self.width = width
        self.height = height
        self.current_screen_id = "splash"
        self.nav_stack = ["splash"]
        self.state_data: Dict[str, Any] = {
            "phone_input": "",
            "otp_input": "",
            "search_query": "",
            "pan_input": "",
            "aadhaar_input": "",
            "is_logged_in": False,
            "kyc_verified": False,
            "cart_items": 0,
            "dynamic_variation": 0  # Can be toggled to simulate dynamic list changes
        }

    def start_app(self, package_name: str, activity_name: Optional[str] = None) -> bool:
        self.current_screen_id = "splash"
        self.nav_stack = ["splash"]
        return True

    def stop_app(self, package_name: str) -> bool:
        self.current_screen_id = "closed"
        return True

    def get_screen_dimensions(self) -> Tuple[int, int]:
        return (self.width, self.height)

    def set_dynamic_variation(self, val: int):
        """Allows tests to alter dynamic content (e.g. list prices/names) without changing structural schema."""
        self.state_data["dynamic_variation"] = val

    def _get_screen_elements(self) -> list[UIElement]:
        scr = self.current_screen_id
        dyn = self.state_data["dynamic_variation"]

        if scr == "splash":
            return [
                UIElement(
                    element_id="splash_logo",
                    class_name="android.widget.ImageView",
                    resource_id="com.revrag.sampleapp:id/iv_logo",
                    content_desc="RevRag Brand Logo",
                    bounds=BoundingBox(left=340, top=600, right=740, bottom=1000),
                    depth=1
                ),
                UIElement(
                    element_id="splash_title",
                    class_name="android.widget.TextView",
                    resource_id="com.revrag.sampleapp:id/tv_title",
                    text="RevRag AI Store",
                    bounds=BoundingBox(left=100, top=1050, right=980, bottom=1150),
                    depth=1
                ),
                UIElement(
                    element_id="splash_subtitle",
                    class_name="android.widget.TextView",
                    resource_id="com.revrag.sampleapp:id/tv_subtitle",
                    text="Autonomous In-App Shopping Experience",
                    bounds=BoundingBox(left=100, top=1180, right=980, bottom=1260),
                    depth=1
                ),
                UIElement(
                    element_id="btn_get_started",
                    class_name="android.widget.Button",
                    resource_id="com.revrag.sampleapp:id/btn_get_started",
                    text="Get Started",
                    bounds=BoundingBox(left=100, top=1800, right=980, bottom=1950),
                    clickable=True,
                    depth=1
                ),
            ]

        elif scr == "login":
            return [
                UIElement(
                    element_id="tv_login_heading",
                    class_name="android.widget.TextView",
                    resource_id="com.revrag.sampleapp:id/tv_login_heading",
                    text="Welcome Back - Login",
                    bounds=BoundingBox(left=80, top=300, right=1000, bottom=400),
                    depth=1
                ),
                UIElement(
                    element_id="edit_phone",
                    class_name="android.widget.EditText",
                    resource_id="com.revrag.sampleapp:id/edit_phone",
                    text=self.state_data["phone_input"] or "Enter 10-digit mobile number",
                    bounds=BoundingBox(left=80, top=500, right=1000, bottom=630),
                    clickable=True,
                    editable=True,
                    depth=1
                ),
                UIElement(
                    element_id="edit_otp",
                    class_name="android.widget.EditText",
                    resource_id="com.revrag.sampleapp:id/edit_otp",
                    text=self.state_data["otp_input"] or "Enter 6-digit OTP",
                    bounds=BoundingBox(left=80, top=680, right=1000, bottom=810),
                    clickable=True,
                    editable=True,
                    depth=1
                ),
                UIElement(
                    element_id="btn_login_submit",
                    class_name="android.widget.Button",
                    resource_id="com.revrag.sampleapp:id/btn_login_submit",
                    text="Verify & Login",
                    bounds=BoundingBox(left=80, top=880, right=1000, bottom=1020),
                    clickable=True,
                    depth=1
                ),
                UIElement(
                    element_id="btn_skip_login",
                    class_name="android.widget.TextView",
                    resource_id="com.revrag.sampleapp:id/btn_skip_login",
                    text="Skip for now",
                    bounds=BoundingBox(left=380, top=1080, right=700, bottom=1160),
                    clickable=True,
                    depth=1
                ),
            ]

        elif scr == "home":
            # Notice how item titles & prices change with dyn, but class_name, resource_id, and hierarchy remain identical
            item1_title = "Sony WH-1000XM5" if dyn == 0 else "Bose QuietComfort Ultra"
            item1_price = "$349.99" if dyn == 0 else "$379.00"
            item2_title = "Apple Watch Ultra 2" if dyn == 0 else "Samsung Galaxy Watch 6"
            item2_price = "$799.00" if dyn == 0 else "$299.99"

            return [
                UIElement(
                    element_id="home_header",
                    class_name="android.widget.TextView",
                    resource_id="com.revrag.sampleapp:id/tv_home_title",
                    text="Explore Products",
                    bounds=BoundingBox(left=60, top=150, right=800, bottom=250),
                    depth=1
                ),
                UIElement(
                    element_id="edit_search",
                    class_name="android.widget.EditText",
                    resource_id="com.revrag.sampleapp:id/edit_search_bar",
                    text=self.state_data["search_query"] or "Search smart gadgets...",
                    bounds=BoundingBox(left=60, top=280, right=1020, bottom=400),
                    clickable=True,
                    editable=True,
                    depth=1
                ),
                # Product Card 1
                UIElement(
                    element_id="card_product_1",
                    class_name="androidx.cardview.widget.CardView",
                    resource_id="com.revrag.sampleapp:id/card_product_1",
                    bounds=BoundingBox(left=60, top=450, right=1020, bottom=780),
                    clickable=True,
                    depth=2
                ),
                UIElement(
                    element_id="tv_product_title_1",
                    class_name="android.widget.TextView",
                    resource_id="com.revrag.sampleapp:id/tv_product_title",
                    text=item1_title,
                    bounds=BoundingBox(left=90, top=480, right=900, bottom=550),
                    depth=3
                ),
                UIElement(
                    element_id="tv_product_price_1",
                    class_name="android.widget.TextView",
                    resource_id="com.revrag.sampleapp:id/tv_product_price",
                    text=item1_price,
                    bounds=BoundingBox(left=90, top=560, right=400, bottom=630),
                    depth=3
                ),
                # Product Card 2
                UIElement(
                    element_id="card_product_2",
                    class_name="androidx.cardview.widget.CardView",
                    resource_id="com.revrag.sampleapp:id/card_product_2",
                    bounds=BoundingBox(left=60, top=820, right=1020, bottom=1150),
                    clickable=True,
                    depth=2
                ),
                UIElement(
                    element_id="tv_product_title_2",
                    class_name="android.widget.TextView",
                    resource_id="com.revrag.sampleapp:id/tv_product_title",
                    text=item2_title,
                    bounds=BoundingBox(left=90, top=850, right=900, bottom=920),
                    depth=3
                ),
                UIElement(
                    element_id="tv_product_price_2",
                    class_name="android.widget.TextView",
                    resource_id="com.revrag.sampleapp:id/tv_product_price",
                    text=item2_price,
                    bounds=BoundingBox(left=90, top=930, right=400, bottom=1000),
                    depth=3
                ),
                # Bottom Navigation Bar
                UIElement(
                    element_id="nav_tab_home",
                    class_name="android.widget.FrameLayout",
                    resource_id="com.revrag.sampleapp:id/nav_home",
                    text="Home",
                    bounds=BoundingBox(left=0, top=2200, right=360, bottom=2400),
                    clickable=True,
                    depth=2
                ),
                UIElement(
                    element_id="nav_tab_cart",
                    class_name="android.widget.FrameLayout",
                    resource_id="com.revrag.sampleapp:id/nav_cart",
                    text=f"Cart ({self.state_data['cart_items']})",
                    bounds=BoundingBox(left=360, top=2200, right=720, bottom=2400),
                    clickable=True,
                    depth=2
                ),
                UIElement(
                    element_id="nav_tab_profile",
                    class_name="android.widget.FrameLayout",
                    resource_id="com.revrag.sampleapp:id/nav_profile",
                    text="Profile",
                    bounds=BoundingBox(left=720, top=2200, right=1080, bottom=2400),
                    clickable=True,
                    depth=2
                ),
            ]

        elif scr == "product_detail":
            return [
                UIElement(
                    element_id="btn_back_detail",
                    class_name="android.widget.ImageButton",
                    resource_id="com.revrag.sampleapp:id/btn_back",
                    content_desc="Back",
                    bounds=BoundingBox(left=40, top=120, right=160, bottom=240),
                    clickable=True,
                    depth=1
                ),
                UIElement(
                    element_id="tv_detail_title",
                    class_name="android.widget.TextView",
                    resource_id="com.revrag.sampleapp:id/tv_detail_title",
                    text="Flagship ANC Smart Headset",
                    bounds=BoundingBox(left=60, top=300, right=1020, bottom=420),
                    depth=1
                ),
                UIElement(
                    element_id="tv_detail_desc",
                    class_name="android.widget.TextView",
                    resource_id="com.revrag.sampleapp:id/tv_detail_desc",
                    text="Industry-leading noise canceling with dual processors and 8 microphones for superior clear sound.",
                    bounds=BoundingBox(left=60, top=450, right=1020, bottom=700),
                    depth=1
                ),
                UIElement(
                    element_id="btn_add_to_cart",
                    class_name="android.widget.Button",
                    resource_id="com.revrag.sampleapp:id/btn_add_to_cart",
                    text="Add to Cart - $349.99",
                    bounds=BoundingBox(left=80, top=1900, right=1000, bottom=2050),
                    clickable=True,
                    depth=1
                ),
            ]

        elif scr == "profile":
            return [
                UIElement(
                    element_id="btn_back_profile",
                    class_name="android.widget.ImageButton",
                    resource_id="com.revrag.sampleapp:id/btn_back_profile",
                    content_desc="Back",
                    bounds=BoundingBox(left=40, top=120, right=160, bottom=240),
                    clickable=True,
                    depth=1
                ),
                UIElement(
                    element_id="tv_user_name",
                    class_name="android.widget.TextView",
                    resource_id="com.revrag.sampleapp:id/tv_user_name",
                    text="Alex Agent",
                    bounds=BoundingBox(left=80, top=320, right=800, bottom=420),
                    depth=1
                ),
                UIElement(
                    element_id="tv_kyc_badge",
                    class_name="android.widget.TextView",
                    resource_id="com.revrag.sampleapp:id/tv_kyc_status",
                    text="KYC Status: Verified" if self.state_data["kyc_verified"] else "KYC Status: Pending Verification",
                    bounds=BoundingBox(left=80, top=450, right=900, bottom=530),
                    depth=1
                ),
                UIElement(
                    element_id="btn_verify_kyc",
                    class_name="android.widget.Button",
                    resource_id="com.revrag.sampleapp:id/btn_verify_kyc",
                    text="Complete KYC Verification",
                    bounds=BoundingBox(left=80, top=600, right=1000, bottom=730),
                    clickable=True,
                    depth=1
                ),
                UIElement(
                    element_id="btn_logout",
                    class_name="android.widget.Button",
                    resource_id="com.revrag.sampleapp:id/btn_logout",
                    text="Log Out",
                    bounds=BoundingBox(left=80, top=1900, right=1000, bottom=2030),
                    clickable=True,
                    depth=1
                ),
            ]

        elif scr == "kyc":
            return [
                UIElement(
                    element_id="btn_back_kyc",
                    class_name="android.widget.ImageButton",
                    resource_id="com.revrag.sampleapp:id/btn_back_kyc",
                    content_desc="Back",
                    bounds=BoundingBox(left=40, top=120, right=160, bottom=240),
                    clickable=True,
                    depth=1
                ),
                UIElement(
                    element_id="tv_kyc_header",
                    class_name="android.widget.TextView",
                    resource_id="com.revrag.sampleapp:id/tv_kyc_header",
                    text="Identity Verification (KYC)",
                    bounds=BoundingBox(left=80, top=300, right=1000, bottom=400),
                    depth=1
                ),
                UIElement(
                    element_id="edit_pan",
                    class_name="android.widget.EditText",
                    resource_id="com.revrag.sampleapp:id/edit_pan_number",
                    text=self.state_data["pan_input"] or "Enter 10-character PAN",
                    bounds=BoundingBox(left=80, top=480, right=1000, bottom=600),
                    clickable=True,
                    editable=True,
                    depth=1
                ),
                UIElement(
                    element_id="edit_aadhaar",
                    class_name="android.widget.EditText",
                    resource_id="com.revrag.sampleapp:id/edit_aadhaar_number",
                    text=self.state_data["aadhaar_input"] or "Enter Last 4 digits of Aadhaar",
                    bounds=BoundingBox(left=80, top=650, right=1000, bottom=770),
                    clickable=True,
                    editable=True,
                    depth=1
                ),
                UIElement(
                    element_id="btn_submit_kyc",
                    class_name="android.widget.Button",
                    resource_id="com.revrag.sampleapp:id/btn_submit_kyc",
                    text="Submit KYC for Approval",
                    bounds=BoundingBox(left=80, top=850, right=1000, bottom=980),
                    clickable=True,
                    depth=1
                ),
            ]

        return []

    def get_ui_tree(self) -> str:
        import xml.sax.saxutils as saxutils
        elements = self._get_screen_elements()
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<hierarchy rotation="0">']
        xml_lines.append(f'  <node index="0" text="" class="android.widget.FrameLayout" package="com.revrag.sampleapp" bounds="[0,0][{self.width},{self.height}]">')
        for i, el in enumerate(elements):
            b = el.bounds
            bounds_str = f"[{b.left},{b.top}][{b.right},{b.bottom}]"
            res_id = saxutils.escape(el.resource_id or "")
            txt = saxutils.escape(el.text or "")
            cdesc = saxutils.escape(el.content_desc or "")
            clk = "true" if el.clickable else "false"
            edt = "true" if el.editable else "false"
            xml_lines.append(
                f'    <node index="{i+1}" text="{txt}" resource-id="{res_id}" class="{el.class_name}" '
                f'content-desc="{cdesc}" clickable="{clk}" focused="{edt}" bounds="{bounds_str}" />'
            )
        xml_lines.append('  </node>')
        xml_lines.append('</hierarchy>')
        return "\n".join(xml_lines)

    def take_screenshot(self) -> bytes:
        img = Image.new("RGB", (self.width, self.height), color=(18, 20, 29)) # Sleek dark mode #12141D
        draw = ImageDraw.Draw(img)

        # Draw status bar
        draw.rectangle([0, 0, self.width, 80], fill=(26, 29, 41))

        elements = self._get_screen_elements()
        for el in elements:
            b = el.bounds
            # Render Buttons
            if "Button" in el.class_name:
                draw.rounded_rectangle([b.left, b.top, b.right, b.bottom], radius=16, fill=(99, 102, 241), outline=(129, 140, 248), width=2)
                if el.text:
                    draw.text((b.left + 30, b.top + (b.height // 2) - 15), el.text, fill=(255, 255, 255))
            # Render EditText
            elif "EditText" in el.class_name:
                draw.rounded_rectangle([b.left, b.top, b.right, b.bottom], radius=12, fill=(30, 35, 52), outline=(79, 70, 229), width=2)
                txt = el.text or "Placeholder..."
                draw.text((b.left + 25, b.top + (b.height // 2) - 15), txt, fill=(160, 174, 192))
            # Render CardView
            elif "CardView" in el.class_name:
                draw.rounded_rectangle([b.left, b.top, b.right, b.bottom], radius=20, fill=(26, 32, 44), outline=(45, 55, 72), width=1)
            # Render Bottom Navigation
            elif "FrameLayout" in el.class_name and b.top >= 2000:
                draw.rectangle([b.left, b.top, b.right, b.bottom], fill=(22, 27, 39), outline=(40, 48, 68), width=1)
                if el.text:
                    draw.text((b.left + 60, b.top + 70), el.text, fill=(190, 200, 220))
            # Render TextViews
            elif "TextView" in el.class_name:
                txt = el.text or ""
                color = (248, 250, 252) if "title" in (el.resource_id or "") or "heading" in (el.resource_id or "") else (203, 213, 225)
                draw.text((b.left, b.top + 10), txt, fill=color)

        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue()

    def perform_action(self, action: Action) -> bool:
        elements = self._get_screen_elements()

        # Check back action
        if action.action_type == ActionType.BACK:
            if len(self.nav_stack) > 1:
                self.nav_stack.pop()
                self.current_screen_id = self.nav_stack[-1]
                return True
            return False

        target_el: Optional[UIElement] = None
        if action.target_element_id:
            for el in elements:
                if el.element_id == action.target_element_id:
                    target_el = el
                    break

        # Match by bounds center if target_bounds provided
        if not target_el and action.target_bounds:
            cx, cy = action.target_bounds.center
            for el in elements:
                b = el.bounds
                if b.left <= cx <= b.right and b.top <= cy <= b.bottom:
                    target_el = el
                    break

        if action.action_type == ActionType.INPUT_TEXT:
            if target_el:
                res_id = target_el.resource_id or ""
                if "phone" in res_id:
                    self.state_data["phone_input"] = action.input_text or ""
                elif "otp" in res_id:
                    self.state_data["otp_input"] = action.input_text or ""
                elif "search" in res_id:
                    self.state_data["search_query"] = action.input_text or ""
                elif "pan" in res_id:
                    self.state_data["pan_input"] = action.input_text or ""
                elif "aadhaar" in res_id:
                    self.state_data["aadhaar_input"] = action.input_text or ""
                return True
            return False

        if action.action_type == ActionType.TAP:
            if not target_el:
                return False

            res_id = target_el.resource_id or ""
            elem_id = target_el.element_id

            if self.current_screen_id == "splash":
                if "get_started" in res_id or elem_id == "btn_get_started":
                    self.current_screen_id = "login"
                    self.nav_stack.append("login")
                    return True

            elif self.current_screen_id == "login":
                if "btn_login_submit" in res_id or "btn_skip_login" in res_id:
                    self.state_data["is_logged_in"] = True
                    self.current_screen_id = "home"
                    self.nav_stack.append("home")
                    return True

            elif self.current_screen_id == "home":
                if "card_product" in res_id or "card_product" in elem_id:
                    self.current_screen_id = "product_detail"
                    self.nav_stack.append("product_detail")
                    return True
                elif "nav_profile" in res_id or elem_id == "nav_tab_profile":
                    self.current_screen_id = "profile"
                    self.nav_stack.append("profile")
                    return True

            elif self.current_screen_id == "product_detail":
                if "btn_back" in res_id or elem_id == "btn_back_detail":
                    self.nav_stack.pop()
                    self.current_screen_id = self.nav_stack[-1]
                    return True
                elif "btn_add_to_cart" in res_id or elem_id == "btn_add_to_cart":
                    self.state_data["cart_items"] += 1
                    return True

            elif self.current_screen_id == "profile":
                if "btn_back" in res_id or elem_id == "btn_back_profile":
                    self.nav_stack.pop()
                    self.current_screen_id = self.nav_stack[-1]
                    return True
                elif "btn_verify_kyc" in res_id or elem_id == "btn_verify_kyc":
                    self.current_screen_id = "kyc"
                    self.nav_stack.append("kyc")
                    return True
                elif "btn_logout" in res_id or elem_id == "btn_logout":
                    self.current_screen_id = "login"
                    self.nav_stack = ["login"]
                    return True

            elif self.current_screen_id == "kyc":
                if "btn_back" in res_id or elem_id == "btn_back_kyc":
                    self.nav_stack.pop()
                    self.current_screen_id = self.nav_stack[-1]
                    return True
                elif "btn_submit_kyc" in res_id or elem_id == "btn_submit_kyc":
                    self.state_data["kyc_verified"] = True
                    self.nav_stack.pop()
                    self.current_screen_id = "profile"
                    return True

        return True

    def get_screen_state(self) -> ScreenState:
        from layer2_perception.normalizer import parse_ui_hierarchy
        from layer2_perception.fingerprinter import compute_structural_fingerprint

        xml_tree = self.get_ui_tree()
        elements = parse_ui_hierarchy(xml_tree, self.width, self.height)
        fingerprint = compute_structural_fingerprint(elements)
        screenshot = self.take_screenshot()

        return ScreenState(
            fingerprint=fingerprint,
            activity_name=f"com.revrag.sampleapp.{self.current_screen_id.capitalize()}Activity",
            elements=elements,
            screenshot_bytes=screenshot,
            raw_xml=xml_tree,
            width=self.width,
            height=self.height
        )
