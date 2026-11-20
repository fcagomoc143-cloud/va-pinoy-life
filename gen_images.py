"""Generate anime post images with Codex (ChatGPT image gen), 5 parallel workers.
python gen_images.py            -> generates missing static/img/<slug>.png
"""
import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).parent
IMG = ROOT / "static" / "img"
REF = IMG / "test-anime.png"
CHAR = ("Mia, the same character as in the reference image: a Filipina virtual assistant in her late 20s, "
        "long wavy dark-brown hair in a messy half-bun with an orange scrunchie, warm brown skin, brown eyes, "
        "navy button-up shirt over a white tee, black headset with orange accents")
STYLE = ("Clean modern Japanese anime illustration, slice-of-life film still, soft cinematic lighting, detailed background. "
         "Colors dominated by deep navy and white with small orange accents. Landscape 3:2. "
         "No readable text, no letters, no logos, no watermarks.")

SCENES = {
    "ano-ang-virtual-assistant": "Mia waves hello at the viewer from her home desk, laptop open with a video call, friendly welcoming pose, morning light.",
    "paano-maging-va-kahit-walang-experience": "Mia as a nervous but determined beginner studying online courses on her laptop at a small table, notebook full of notes, sunrise through the window.",
    "va-vs-ea-pagkakaiba": "Split composition: left side Mia doing many small tasks with sticky notes, right side Mia confidently managing a CEO's schedule on two monitors.",
    "va-equipment-at-internet-setup": "Mia proudly arranging her work setup: laptop, external monitor, headset, router and a small UPS on a tidy desk.",
    "saan-maghahanap-ng-va-job": "Mia browsing many job listings on her laptop with a magnifying glass icon floating, excited expression, coffee beside her.",
    "paano-gumawa-ng-va-resume": "Mia polishing a one-page resume on her laptop, a printed resume in her hand, satisfied smile.",
    "va-interview-tanong-at-sagot": "Mia in a video interview on her laptop, sitting upright and confident, a ring light glowing, neat background.",
    "unang-linggo-sa-va-job": "Mia on her first day, slightly overwhelmed but smiling, onboarding checklist and welcome messages on screen, plant and mug on desk.",
    "paano-makipag-usap-sa-boss-abroad": "Mia on a friendly video call with a foreign businessman shown on her laptop screen, both smiling, world map on the wall.",
    "time-zone-survival-guide-night-shift-va": "Mia working the night shift at 2am, moonlight and city lights outside, several wall clocks showing different time zones, cozy lamp.",
    "mga-tools-na-ginagamit-ko-araw-araw-bilang-ea": "Top-down view of Mia's desk with laptop, phone, planner, headset and floating app-style icons around her, organized and productive.",
    "google-workspace-basics-para-sa-va": "Mia collaborating on shared documents and spreadsheets on a big monitor, colorful cloud folders floating around.",
    "outlook-tips-at-tricks-na-nakakatipid-ng-oras": "Mia sorting a flood of envelope-shaped emails into neat folders with a flick of her hand, stopwatch floating nearby.",
    "calendar-management-para-sa-busy-na-boss": "Mia calmly arranging colorful meeting blocks on a giant floating calendar like puzzle pieces.",
    "inbox-zero-method-para-sa-va": "Mia triumphantly raising her arms as the last email flies away, empty inbox glowing on her laptop, confetti of paper envelopes.",
    "paano-gamitin-ang-ai-para-bumilis-sa-va-work": "Mia working side by side with a cute friendly holographic AI helper robot, a small padlock symbol showing privacy.",
    "canva-para-sa-va-mga-madalas-ipagawa": "Mia designing colorful social media graphics on a drawing tablet, design cards floating around her.",
    "paano-gumawa-ng-sop": "Mia writing a step-by-step guide, numbered steps flowing from her laptop like a staircase of glowing cards.",
    "notion-vs-trello-vs-asana-para-sa-task-management": "Mia choosing between three floating boards of task cards, thoughtful pose with a finger on her chin.",
    "travel-booking-at-itinerary-para-sa-boss": "Mia planning a trip with a globe, plane tickets, a passport and a hotel key card on her desk, airplane flying past the window.",
    "magkano-dapat-rate-mo-bilang-va": "Mia confidently setting her price on a calculator, coins and a rising bar chart floating beside her.",
    "paano-humingi-ng-raise-sa-foreign-client": "Mia taking a deep breath before a video call, holding a neat performance report, encouraging warm light.",
    "paano-tumanggap-ng-bayad-wise-paypal-payoneer": "Mia happily receiving a payment notification on her phone, money flowing from a globe into her phone as glowing light.",
    "tax-para-sa-freelancer-sa-pilipinas": "Mia organizing receipts and forms in a neat folder with a calculator, calm and responsible, a Philippine government building silhouette outside.",
    "mula-part-time-hanggang-full-time-va": "Mia leaving a busy office building in the evening and arriving at her cozy home office, transition scene with a path between them.",
    "paano-makahanap-ng-long-term-client": "Mia shaking hands through her laptop screen with a happy client, a growing plant on her desk symbolizing a long relationship.",
    "paano-iwasan-ang-scam-na-va-job-posts": "Mia inspecting a suspicious job post with a magnifying glass, a shadowy hooded figure behind the screen, red warning glow.",
    "paano-mag-specialize-at-tumaas-ang-kita": "Mia climbing a staircase of skill badges toward a bright door, determined expression.",
    "isang-araw-sa-buhay-ko-bilang-ea-ng-ceo-sa-canada": "Mia at her desk at night in the Philippines while a snowy Canadian city skyline appears on her video call screen.",
    "paano-iwasan-ang-burnout-bilang-va": "Mia stretching and resting on a balcony with tea and plants after closing her laptop, peaceful sunset.",
    "about": "Mia smiling warmly at the viewer, sitting at her home desk, Philippine flag on a shelf, welcoming portrait.",
    "home": "Wide scene: Mia at her desk by a big window at night, city lights, cat sleeping nearby, laptop glowing, cozy and inspiring.",
}


def run(slug):
    out = IMG / f"{slug}.png"
    if out.exists():
        return slug, "skip"
    prompt = (f"Use your built-in image generation tool to create ONE image, using the attached image ONLY as the character reference (face, hair, outfit). Do NOT copy its room, furniture, window, cat, camera angle or composition; build a new setting and composition that fits the scene. "
              f"Then copy the generated PNG into the current directory as {slug}.png. "
              f"Scene: {SCENES[slug]} Character: {CHAR}. Style: {STYLE} Reply only with the saved file path.")
    cmd = [shutil.which("codex"), "exec", "-m", "gpt-6-sol", "-c", "model_reasoning_effort=low", "--skip-git-repo-check",
           "--dangerously-bypass-approvals-and-sandbox", "-C", str(IMG), "-i", str(REF), "--", prompt]
    for attempt in range(2):
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        if out.exists():
            return slug, "ok"
    return slug, "FAIL " + r.stdout[-200:] + r.stderr[-300:]


if __name__ == "__main__":
    slugs = sys.argv[1:] or list(SCENES)
    with ThreadPoolExecutor(5) as ex:
        for slug, status in ex.map(run, slugs):
            print(slug, status, flush=True)
