from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

pitch = (
    "EduConnect is more than just a platform—it's a movement to democratize access to quality education. "
    "In a world where millions are left behind due to barriers of cost, geography, or resources, EduConnect bridges the gap. "
    "Our mission is to empower every learner and educator with the tools, community, and resources needed to thrive in the 21st century.\n\n"
    "Why EduConnect?\n"
    "- Breaks Down Barriers: Free, inclusive, and accessible from anywhere, EduConnect ensures no student is left behind.\n"
    "- Empowers Teachers: Enables educators to reach more students, share resources, and make a measurable impact.\n"
    "- Drives Real Progress: With built-in progress tracking and community forums, learning is engaging, collaborative, and measurable.\n"
    "- Aligned with Global Goals: Directly supports the United Nations SDG 4 for Quality Education, making your participation part of a global movement.\n\n"
    "Join us in shaping the future of education—where every lesson, every resource, and every connection counts."
)

def create_pitch_pdf(path):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 20)
    c.drawString(72, height - 72, "EduConnect Powerful Pitch")
    c.setFont("Helvetica", 12)
    text = c.beginText(72, height - 110)
    for line in pitch.split("\n"):
        text.textLine(line)
    c.drawText(text)
    c.save()

if __name__ == "__main__":
    create_pitch_pdf("docs/pitch_deck.pdf")
