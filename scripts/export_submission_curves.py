from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator


PROJECT_ROOT = Path(r"D:\space_intelligent")
FIG_DIR = PROJECT_ROOT / "docs" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

A_LOG = PROJECT_ROOT / "outputs" / "object_a_3dgs" / "train_quality_resume.log"
B_EVENT = PROJECT_ROOT / "external" / "threestudio" / "outputs" / "object_b_text3d" / (
    r"a_cute_toy_robot,_white_ceramic_body,_round_head,_two_glowing_blue_eyes,_simple_silhouette,_centered,_studio_lighting"
) / "tb_logs" / "version_5" / "events.out.tfevents.1781884959.ahinte.28912.0"
C_EVENT = PROJECT_ROOT / "external" / "threestudio" / "outputs" / "object_c_zero123" / (
    r"[64]_foreground.png"
) / "tb_logs" / "version_0" / "events.out.tfevents.1781780791.ahinte.33472.0"


def save_plot(x, y, title: str, xlabel: str, ylabel: str, out_path: Path) -> None:
    plt.figure(figsize=(7.2, 4.2))
    plt.plot(x, y, linewidth=1.8)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(out_path, dpi=220)
    plt.close()


def export_a_loss() -> None:
    pattern = re.compile(r"(\d+)/7000.*loss=([0-9.]+)")
    steps = []
    losses = []
    text = A_LOG.read_text(encoding="utf-8", errors="ignore").replace("\r", "\n")
    for line in text.splitlines():
        match = pattern.search(line)
        if match:
            steps.append(int(match.group(1)))
            losses.append(float(match.group(2)))
    if steps and losses:
        save_plot(
            steps,
            losses,
            "Object A Training Loss",
            "Iteration",
            "Loss",
            FIG_DIR / "curve_a_training_loss.png",
        )


def load_scalar_series(event_file: Path, tag: str):
    ea = EventAccumulator(str(event_file))
    ea.Reload()
    events = ea.Scalars(tag)
    return [e.step for e in events], [e.value for e in events]


def export_b_curves() -> None:
    steps, loss = load_scalar_series(B_EVENT, "train/loss_sds")
    save_plot(
        steps,
        loss,
        "Object B SDS Loss",
        "Step",
        "Loss",
        FIG_DIR / "curve_b_training_loss.png",
    )
    steps, lr = load_scalar_series(B_EVENT, "lr-Adam/geometry")
    save_plot(
        steps,
        lr,
        "Object B Geometry Learning Rate",
        "Step",
        "Learning Rate",
        FIG_DIR / "curve_b_learning_rate.png",
    )


def export_c_curves() -> None:
    steps, loss = load_scalar_series(C_EVENT, "train/loss")
    save_plot(
        steps,
        loss,
        "Object C Training Loss",
        "Step",
        "Loss",
        FIG_DIR / "curve_c_training_loss.png",
    )
    steps, lr = load_scalar_series(C_EVENT, "lr-Adam")
    save_plot(
        steps,
        lr,
        "Object C Learning Rate",
        "Step",
        "Learning Rate",
        FIG_DIR / "curve_c_learning_rate.png",
    )


def export_notice_panel() -> None:
    fig = plt.figure(figsize=(7.2, 3.0))
    plt.axis("off")
    text = (
        "Validation metric curves are not available in the preserved local logs.\n"
        "Current report uses exported local TensorBoard training curves.\n"
        "If the course strictly requires WandB/SwanLab validation charts,\n"
        "please sync the experiment records to those platforms before final submission."
    )
    plt.text(0.02, 0.75, text, fontsize=11, va="top")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "curve_validation_notice.png", dpi=220)
    plt.close(fig)


def main() -> None:
    export_a_loss()
    export_b_curves()
    export_c_curves()
    export_notice_panel()
    print(f"Exported figures to: {FIG_DIR}")


if __name__ == "__main__":
    main()
