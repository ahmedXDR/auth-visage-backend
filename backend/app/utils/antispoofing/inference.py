import argparse
import os
import pathlib

import onnxruntime as ort  # type: ignore
import torch
from PIL import Image
from torchvision import transforms

from app.core.config import settings

# -----------------------------------------------------------------------------
# Pre-processing identical to training
# -----------------------------------------------------------------------------
_preprocess = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]
)


def load_sequence(seq_dir: str) -> torch.Tensor:
    """Read & transform all frames in `seq_dir`, return Tx3x224x224 tensor."""
    frame_paths = sorted(
        [
            os.path.join(seq_dir, f)
            for f in os.listdir(seq_dir)
            if f.lower().endswith((".jpg", ".png", ".jpeg", ".bmp"))
        ]
    )
    if not frame_paths:
        raise ValueError(f"No images found in {seq_dir}")
    frames = [_preprocess(Image.open(p).convert("RGB")) for p in frame_paths]
    return torch.stack(frames)  # (T, 3, 224, 224)


def pad_sequences(tensors, value=0.0):
    """Pad tensors along time dim so they all share the same length."""
    lengths = [t.shape[0] for t in tensors]
    max_len = max(lengths)
    padded = []
    for t in tensors:
        if t.shape[0] == max_len:
            padded.append(t)
        else:
            pad_frames = t[-1:].repeat(max_len - t.shape[0], 1, 1, 1)
            padded.append(torch.cat([t, pad_frames], dim=0))
    return torch.stack(padded)  # (B, T, 3, 224, 224)


def parse_args():
    p = argparse.ArgumentParser("ONNX liveness inference")
    p.add_argument(
        "--onnx_model",
        type=str,
        default="weights\\antispoofing_model.onnx",
        help="Path to exported ONNX model",
    )
    p.add_argument(
        "--sequence_path",
        nargs="+",
        required=True,
        help="One or more folder(s) containing frames of a clip",
    )
    p.add_argument(
        "--batch_size",
        type=int,
        default=1,
        help="How many sequences to process at once",
    )
    return p.parse_args()


def infer_liveness_from_frames(
    list_of_frame_lists: list[list[Image.Image]],
) -> list[float]:
    """
    Run liveness detection on a batch of frame sequences.

    Args:
        list_of_frame_lists: List of frame sequences (each sequence is a list
        of PIL.Image.Image).
        onnx_model_path: Path to the ONNX model.

    Returns:
        List of liveness scores, one per sequence.
    """
    # Load ONNX model
    sess = ort.InferenceSession(
        str(object=pathlib.Path(settings.LIVENESS_MODEL_PATH).expanduser()),
        providers=["CPUExecutionProvider"],
    )
    input_name = sess.get_inputs()[0].name
    output_name = sess.get_outputs()[0].name

    # Preprocess and pad
    seq_tensors = [
        torch.stack([_preprocess(img.convert("RGB")) for img in frames])
        for frames in list_of_frame_lists
    ]
    batch_tensor = pad_sequences(seq_tensors)  # B×T×3×224×224
    batch_np = batch_tensor.numpy().astype("float32")

    # Run inference
    scores = sess.run([output_name], {input_name: batch_np})[0]  # B×1

    scores = [float(score) * 10 for score in scores]
    scores = [max(0.0, min(1.0, score)) for score in scores]
    return scores


def main():
    args = parse_args()

    # 1) Load ONNX model ------------------------------------------------------
    sess = ort.InferenceSession(
        str(pathlib.Path(args.onnx_model).expanduser()),
        providers=["CPUExecutionProvider"],
    )
    input_name = sess.get_inputs()[0].name  # 'input'
    output_name = sess.get_outputs()[0].name  # 'prob'

    # 2) Iterate over sequences in user-defined batches ----------------------
    seq_paths = [pathlib.Path(p) for p in args.sequence_path]
    for i in range(0, len(seq_paths), args.batch_size):
        batch_dirs = seq_paths[i : i + args.batch_size]

        # read & (optionally) pad clips so they have equal length
        seq_tensors = [load_sequence(str(d)) for d in batch_dirs]
        batch_tensor = pad_sequences(seq_tensors)  # B×T×3×224×224
        # ONNX Runtime expects NHWC by default; our export kept NCTHW,
        # so we only need to convert to numpy
        batch_np = batch_tensor.numpy().astype("float32")

        # 3) Run inference ----------------------------------------------------
        scores = sess.run([output_name], {input_name: batch_np})[0]  # B×1

        # 4) Show results -----------------------------------------------------
        for dir_path, score in zip(batch_dirs, list(scores), strict=True):
            print(f"{dir_path.name}: liveness_score={float(score):.4f}")


if __name__ == "__main__":
    main()
