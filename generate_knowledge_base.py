"""
generate_knowledge_base.py
Generates the 6 fictional TechMart Electronics knowledge-base PDFs
used by the RAG pipeline. Run once to populate knowledge_base/.
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from pathlib import Path

OUT_DIR = Path("knowledge_base")
OUT_DIR.mkdir(exist_ok=True)

styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], spaceAfter=14)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], spaceAfter=8, spaceBefore=14)
body = ParagraphStyle("body", parent=styles["BodyText"], spaceAfter=10, leading=15)


def make_pdf(filename: str, title: str, sections: list[tuple[str, str]]):
    doc = SimpleDocTemplate(str(OUT_DIR / filename), pagesize=letter,
                             topMargin=0.75*inch, bottomMargin=0.75*inch)
    flow = [Paragraph(title, h1), Spacer(1, 6)]
    for heading, text in sections:
        flow.append(Paragraph(heading, h2))
        flow.append(Paragraph(text, body))
    doc.build(flow)
    print(f"✓ {filename}")


# ─── 1. FAQ.pdf ────────────────────────────────────────────────────────────────
make_pdf("FAQ.pdf", "TechMart Electronics — Frequently Asked Questions", [
    ("What are your support hours?",
     "Our support team is available Monday through Friday, 9 AM to 6 PM EST. "
     "TechMart Ultra subscribers have access to a 24/7 emergency support line."),
    ("How do I contact support?",
     "You can reach us by email at support@techmart.com, by phone at "
     "1-800-TECHMART (1-800-832-4627), or via live chat at techmart.com/chat."),
    ("Where is TechMart headquartered?",
     "TechMart Electronics is headquartered at 500 Innovation Drive, San Jose, CA 95101."),
    ("Do you offer student discounts?",
     "Yes, students with a valid .edu email address receive 15% off any TechMart device."),
    ("How do I check system status?",
     "Visit status.techmart.com for real-time updates on outages and scheduled maintenance."),
])

# ─── 2. RefundPolicy.pdf ───────────────────────────────────────────────────────
make_pdf("RefundPolicy.pdf", "TechMart Electronics — Refund Policy", [
    ("Standard Refund Window",
     "Customers may request a full refund within 30 days of purchase, no questions asked, "
     "provided the device is returned in its original packaging where possible."),
    ("Extended Refund Window",
     "Between 31 and 60 days after purchase, customers are eligible for a 50% partial refund, "
     "subject to manager approval and device condition inspection."),
    ("Digital Subscriptions",
     "Premium subscription refunds ($19.99/month or $179.99/year) follow the same 30-day "
     "full-refund policy. Pro-rated refunds are not offered after the 30-day window."),
    ("Refund Processing Time",
     "Approved refunds are processed within 5-7 business days and credited to the original "
     "payment method."),
    ("Non-Refundable Items",
     "Gift cards, custom-configured devices, and digital downloads after activation are non-refundable."),
])

# ─── 3. ShippingPolicy.pdf ─────────────────────────────────────────────────────
make_pdf("ShippingPolicy.pdf", "TechMart Electronics — Shipping Policy", [
    ("Shipping Options",
     "We offer Free Standard Shipping (5-7 business days), Express Shipping for $12.99 "
     "(2 business days), and Overnight Shipping for $24.99 (next business day)."),
    ("International Shipping",
     "TechMart currently ships to the United States, Canada, and the United Kingdom. "
     "International orders may incur customs fees not covered by TechMart."),
    ("Order Tracking",
     "Tracking numbers are emailed within 24 hours of order confirmation and can be "
     "monitored at techmart.com/track."),
    ("Delayed or Lost Shipments",
     "If a shipment is delayed beyond the estimated window by more than 3 business days, "
     "customers are eligible for a shipping fee refund and priority reshipment."),
])

# ─── 4. Warranty.pdf ───────────────────────────────────────────────────────────
make_pdf("Warranty.pdf", "TechMart Electronics — Warranty Information", [
    ("Standard Warranty",
     "All TechMart devices include a 1-year limited warranty covering manufacturing "
     "defects and hardware malfunctions under normal use."),
    ("TechMart Care (Extended Warranty)",
     "For $29, customers can extend their warranty to 2 years total, which also covers "
     "one instance of accidental damage with a $49 service fee."),
    ("What's Not Covered",
     "Warranty does not cover damage from misuse, unauthorized repairs, water damage "
     "(unless under TechMart Care), or cosmetic wear."),
    ("Filing a Warranty Claim",
     "Claims can be filed at techmart.com/warranty or by calling support. Most claims "
     "are resolved within 5-10 business days, including repair or replacement shipping."),
])

# ─── 5. Pricing.pdf ────────────────────────────────────────────────────────────
make_pdf("Pricing.pdf", "TechMart Electronics — Pricing Guide", [
    ("TechMart Lite — $149",
     "Entry-level device featuring HD 1080p capture, basic editing tools, support for "
     "2 connected devices, and 50GB of complimentary cloud storage."),
    ("TechMart Pro — $299 (Best Seller)",
     "Our most popular model. Includes 4K capture, advanced AI-powered editing tools, "
     "support for 5 connected devices, and 500GB of cloud storage."),
    ("TechMart Ultra — $499",
     "Our flagship device with 8K capture, professional-grade AI tools, unlimited "
     "connected devices, 2TB cloud storage, and 24/7 priority support."),
    ("Premium Software Subscription",
     "$19.99 per month or $179.99 per year (saving approximately 25%). Unlocks advanced "
     "AI editing, unlimited cloud backups, and priority feature access."),
    ("Add-Ons",
     "TechMart Care extended warranty: $29. Cloud Boost (+1TB storage): $9.99/month."),
])

# ─── 6. UserManual.pdf ─────────────────────────────────────────────────────────
make_pdf("UserManual.pdf", "TechMart Electronics — User Manual (Quick Start)", [
    ("Getting Started",
     "Unbox your TechMart device, charge fully via the included USB-C cable, and "
     "download the TechMart Companion App from techmart.com/download."),
    ("System Requirements",
     "Companion App requires Windows 10 or later, macOS 12 or later, Android 11 or "
     "later, or iOS 15 or later."),
    ("Common Error Codes",
     "ERR_001 (Authentication failure): reset your password. ERR_002 (Corrupted "
     "installation): reinstall the app. ERR_003 (Server timeout): check status.techmart.com. "
     "ERR_004 (License mismatch): contact billing support."),
    ("Troubleshooting Steps",
     "1) Clear app cache and restart. 2) Reinstall the latest version. 3) Verify system "
     "requirements are met. 4) Run built-in diagnostics via Settings > Help > Run Diagnostics. "
     "5) If unresolved after these steps, contact Technical Support for Tier-2 escalation."),
    ("Updating Firmware",
     "Firmware updates are pushed automatically when the device is connected to Wi-Fi "
     "and charging. Manual updates can be triggered via the Companion App settings menu."),
])

print("\nAll 6 knowledge base PDFs generated in knowledge_base/")
