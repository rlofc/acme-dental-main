"""Tool that can answer questions from a knowledge-base"""

import json
from textwrap import dedent
from typing import Any

from langchain.tools import BaseTool

DATA = {
    "What services do you offer?": dedent(
        """\
        Acme Dental currently offers routine dental check-ups only.
        A check-up includes an oral examination and general assessment of your dental health."""
    ),
    "How long is a check-up appointment?": dedent(
        """\
        Each dental check-up appointment is 30 minutes."""
    ),
    "Is this appointment with a real dentist?": dedent(
        """\
        Yes. Acme Dental has one dentist, and all check-ups are completed by that dentist."""
    ),
    "Can I request a specific dentist?": dedent(
        """\
        There’s only one dentist at Acme Dental, so every booking is automatically scheduled with them."""
    ),
    "Do you offer emergency appointments?": dedent(
        """\
        Acme Dental is focused on routine check-ups only and does not offer emergency dental treatment.
        If you have severe pain, swelling, or bleeding, please contact emergency dental services in your area."""
    ),
    "How do I book an appointment?": dedent(
        """\
        You can book directly through our chat assistant. It will:
        - show available times
        - help you choose a slot
        - ask for your name + email
        - confirm your booking instantly"""
    ),
    "Do I need to create an account to book?": dedent(
        """\
        No account is required. We only need:
        - Full name
        - Email address"""
    ),
    "Do you accept walk-ins?": dedent(
        """\
        At the moment, we do not accept walk-ins.
        All visits must be booked in advance."""
    ),
    "Can I reschedule my appointment?": dedent(
        """\
        Yes — you can reschedule anytime by messaging the assistant with something like:
        “I need to reschedule my check-up”
        We’ll find your booking and offer new available time slots."""
    ),
    "How do I cancel my appointment?": dedent(
        """\
        You can cancel by messaging the assistant:
        “Cancel my appointment”
        Once confirmed, we’ll process the cancellation and send you a confirmation message."""
    ),
    "Will I get a confirmation after booking?": dedent(
        """\
        Yes — after booking you’ll receive a confirmation with:
        - Date & time
        - Appointment duration (30 minutes)
        - Booking details"""
    ),
    "What if I didn't receive my confirmation email?": dedent(
        """\
        First, check your spam/junk folder.
        If you still don’t see it, message the assistant with:
        “I didn’t get my confirmation email”
        We’ll help you verify your booking details."""
    ),
    "Can I book a follow-up appointment?": dedent(
        """\
        Yes — just tell the assistant:
        “Book another check-up appointment”
        and it will show available times again."""
    ),
    "Can I book for someone else?": dedent(
        """\
        Yes — you can book on behalf of someone else.
        Just provide their full name and email address when asked."""
    ),
    "What should I bring to my appointment?": dedent(
        """\
        Please bring:
        - A valid photo ID
        - Any relevant medical information (if applicable)
        - Your insurance details (if you have them)"""
    ),
    "How early should I arrive?": dedent(
        """\
        We recommend arriving 5–10 minutes early so you have time to settle in."""
    ),
    "What happens if I'm late?": dedent(
        """\
        If you’re running late, please message us as soon as possible.
        We’ll do our best to accommodate you, but the appointment may need to be rescheduled
        if we can’t complete the check-up within the 30-minute slot."""
    ),
    "Is my personal information secure?": dedent(
        """\
        We only collect the minimum details needed to manage your appointment (name + email)
        and use them solely for scheduling and confirmations."""
    ),
    "How much does a dental check-up cost?": dedent(
        """\
        A standard dental check-up at Acme Dental costs €60."""
    ),
    "What is included in the check-up price?": dedent(
        """\
        The €60 check-up includes:
        - A full oral examination
        - Gum health check
        - A review of any concerns you mention
        - Basic recommendations for next steps (if needed)"""
    ),
    "Is an X-ray included in the check-up cost?": dedent(
        """\
        No — Acme Dental check-ups do not include X-rays.
        If X-rays are required, the dentist will explain next steps and options."""
    ),
    "Do you offer discounts?": dedent(
        """\
        Yes — we offer:
        - Student discount: €50 check-up (valid student ID required)
        - Senior discount (65+): €50 check-up

        Discounts cannot be combined."""
    ),
    "How do I pay for my appointment?": dedent(
        """\
        You can pay:
        - In-clinic by card
        - Contactless payment
        - Cash (exact amount preferred)"""
    ),
    "Do you require a deposit to book?": dedent(
        """\
        No deposit is required for routine check-ups.
        You only need your name and email to confirm the booking."""
    ),
    "What is your cancellation policy?": dedent(
        """\
        You can cancel or reschedule free of charge up to 24 hours before your appointment.
        Cancellations made less than 24 hours in advance may incur a €20 late cancellation fee."""
    ),
    "What happens if I miss my appointment?": dedent(
        """\
        If you don’t attend without notice (“no-show”), a €20 no-show fee may apply.
        You can still rebook through the assistant afterwards."""
    ),
    "Do you accept dental insurance?": dedent(
        """\
        Acme Dental can provide a receipt for your visit, which you may be able to claim through
        your insurance provider.
        We do not process insurance claims directly."""
    ),
    "Can I get a receipt or invoice?": dedent(
        """\
        Yes — we provide receipts for all appointments.
        If you need an invoice with specific details, please ask at reception during your visit."""
    ),
}


class CheckWhatOtherQuestionsCanWeAnswer(BaseTool):
    name: str = "check_other_questions_we_can_answer"
    description: str = "List a set of additional questions we have predefined answers to."

    def _run(self, input_str: str) -> list[str]:
        return DATA.keys()

    async def _arun(self, input_str: str) -> dict[str, Any]:
        raise NotImplementedError("Async not implemented")


class GetReadyAnswerToQuestions(BaseTool):
    name: str = "get_predefined_answer_to_other_questions"
    description: str = (
        "Returns a predefined answer to other questions we can answer to.\n"
        "Input should be a JSON string with keys:\n"
        "  - 'question' (required): One of the questions returned from check_other_questions_we_can_answer and\n"
        "    that matches the user question."
    )

    def _run(self, input_str: str) -> str:
        try:
            payload = json.loads(input_str) if input_str else {}
        except json.JSONDecodeError:
            payload = {}

        question = payload.get("question")
        if question in DATA:
            return DATA[question]
        else:
            return "I'm afraid I have no answer to this."

    async def _arun(self, input_str: str) -> dict[str, Any]:
        raise NotImplementedError("Async not implemented")
