import matplotlib.pyplot as plt

def save_default_blank(session_id):
    fig, ax = plt.subplots(figsize=(6,4), dpi=300)
    ax.axis("off")
    ax.text(0.5, 0.5, "No Data Available", ha="center", va="center", fontsize=14, color="gray")
    plt.tight_layout()
<<<<<<< HEAD
    plt.savefig(f"output{session_id}.jpg", dpi=300)
=======
    plt.savefig(f"dir/graph/output{session_id}.jpg", dpi=300)
>>>>>>> ayan2
    plt.close(fig)