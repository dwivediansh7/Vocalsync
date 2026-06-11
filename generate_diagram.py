import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(1, 1, figsize=(10, 14))
ax.set_xlim(0, 10)
ax.set_ylim(0, 14)
ax.axis('off')
fig.patch.set_facecolor('#FFFFFF')

def draw_box(ax, x, y, w, h, text, subtext='', color='#E8E4FF', text_color='#2D1B8E'):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                          facecolor=color, edgecolor='#999', linewidth=0.8)
    ax.add_patch(box)
    if subtext:
        ax.text(x + w/2, y + h*0.62, text, ha='center', va='center',
                fontsize=11, fontweight='bold', color=text_color)
        ax.text(x + w/2, y + h*0.28, subtext, ha='center', va='center',
                fontsize=8.5, color='#555')
    else:
        ax.text(x + w/2, y + h/2, text, ha='center', va='center',
                fontsize=11, fontweight='bold', color=text_color)

def draw_arrow(ax, x, y1, y2):
    ax.annotate('', xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle='->', color='#666', lw=1.5))

# Title
ax.text(5, 13.4, 'VocalSync AI — Architecture', ha='center', va='center',
        fontsize=15, fontweight='bold', color='#1a1a1a')

# Boxes
draw_box(ax, 2.5, 12.2, 5, 0.8, 'Video Input',
         'mp4 · avi · mov · mkv (max 10 min)', '#F1EFEA', '#2c2c2a')
draw_arrow(ax, 5, 12.2, 11.5)
draw_box(ax, 2, 10.8, 6, 0.9, '1. Audio Extraction',
         'ffmpeg · mono 16kHz WAV', '#EEEDFE', '#3C3489')
draw_arrow(ax, 3.2, 10.8, 10.1)
draw_arrow(ax, 6.8, 10.8, 10.1)

draw_box(ax, 0.3, 9.0, 4, 0.9, '2. Transcription',
         'OpenAI Whisper base', '#E1F5EE', '#085041')
draw_box(ax, 5.7, 9.0, 4, 0.9, '3. Speaker Diarization',
         'pyannote.audio 3.1', '#FAECE7', '#4A1B0C')

draw_arrow(ax, 2.3, 9.0, 8.3)
draw_arrow(ax, 7.7, 9.0, 8.3)

draw_box(ax, 1.5, 7.2, 7, 0.9, '4. Speaker Assignment',
         'Merge transcript + diarization segments', '#EEEDFE', '#3C3489')
draw_arrow(ax, 5, 7.2, 6.5)

draw_box(ax, 2, 5.6, 6, 0.9, '5. Translation',
         'deep-translator · 10 languages', '#FAEEDA', '#412402')
draw_arrow(ax, 5, 5.6, 4.9)

draw_box(ax, 2, 4.0, 6, 0.9, '6. Voice Synthesis',
         'gTTS · unique voice per speaker', '#E1F5EE', '#085041')
draw_arrow(ax, 5, 4.0, 3.3)

draw_box(ax, 2, 2.4, 6, 0.9, '7. Audio-Video Sync',
         'ffmpeg · frame-accurate overlay', '#EEEDFE', '#3C3489')
draw_arrow(ax, 5, 2.4, 1.7)

draw_box(ax, 2.5, 0.8, 5, 0.8, 'Dubbed Video Output',
         'Downloadable mp4', '#F1EFEA', '#2c2c2a')

# API sidebar
sidebar = FancyBboxPatch((8.9, 2.4), 0.9, 9.4, boxstyle="round,pad=0.1",
                          facecolor='#F8F8FF', edgecolor='#AAA',
                          linewidth=0.8, linestyle='--')
ax.add_patch(sidebar)
ax.text(9.35, 7.1, 'FastAPI + SQLite\nAsync job tracking\nProgress 0→100%',
        ha='center', va='center', fontsize=7.5, color='#555', rotation=90)

plt.tight_layout()
plt.savefig('architecture.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Saved architecture.png")