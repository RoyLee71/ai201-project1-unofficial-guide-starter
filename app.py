# app.py
import gradio as gr
from query import ask


def handle_query(question):
    """Wrapper for the Gradio interface."""
    if not question.strip():
        return "Please enter a question.", ""

    result  = ask(question)
    answer  = result["answer"]
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return answer, sources


# ── Gradio UI ─────────────────────────────────────────────────────────────────
with gr.Blocks(title="The Unofficial Guide — Off-Campus Housing") as demo:

    gr.Markdown("""
    # 🏠 The Unofficial Guide: Off-Campus Housing
    Ask questions about real student experiences with off-campus housing —
    landlords, leases, security deposits, hidden costs, and more.
    *Answers are grounded in real student accounts. Sources cited in every response.*
    """)

    with gr.Row():
        with gr.Column(scale=3):
            question_input = gr.Textbox(
                label="Your question",
                placeholder="e.g. What do students say about getting their security deposit back?",
                lines=2,
            )
        with gr.Column(scale=1):
            submit_btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer_output = gr.Textbox(
            label="Answer",
            lines=10,
            interactive=False,
        )

    with gr.Row():
        sources_output = gr.Textbox(
            label="Retrieved from",
            lines=4,
            interactive=False,
        )

    gr.Markdown("""
    ### Try these questions:
    - What do students say about landlord response time for maintenance?
    - What are the most common reasons students lose their security deposit?
    - What hidden costs beyond rent do students get surprised by?
    - What advice do students give about signing a lease for the first time?
    - What pest problems do students most commonly report in off-campus apartments?
    """)

    # Wire both the button click and Enter key to the same handler
    submit_btn.click(
        fn=handle_query,
        inputs=question_input,
        outputs=[answer_output, sources_output],
    )
    question_input.submit(
        fn=handle_query,
        inputs=question_input,
        outputs=[answer_output, sources_output],
    )

if __name__ == "__main__":
    demo.launch()