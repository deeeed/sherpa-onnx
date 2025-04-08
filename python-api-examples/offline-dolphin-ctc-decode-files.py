#!/usr/bin/env python3

"""
This file shows how to use a non-streaming CTC model from Dolphin
to decode files.

Please download model files from
https://github.com/k2-fsa/sherpa-onnx/releases/tag/asr-models
"""

from pathlib import Path
import time

import sherpa_onnx
import soundfile as sf


def create_recognizer():
    model = "./sherpa-onnx-dolphin-base-ctc-multi-lang-int8-2025-04-02/model.int8.onnx"
    tokens = "./sherpa-onnx-dolphin-base-ctc-multi-lang-int8-2025-04-02/tokens.txt"
    test_wav = (
        "./sherpa-onnx-dolphin-base-ctc-multi-lang-int8-2025-04-02/test_wavs/0.wav"
    )

    if not Path(model).is_file() or not Path(test_wav).is_file():
        raise ValueError(
            """Please download model files from
            https://github.com/k2-fsa/sherpa-onnx/releases/tag/asr-models
            """
        )
    return (
        sherpa_onnx.OfflineRecognizer.from_dolphin_ctc(
            model=model,
            tokens=tokens,
            debug=True,
        ),
        test_wav,
    )


def main():
    recognizer, wave_filename = create_recognizer()

    audio, sample_rate = sf.read(wave_filename, dtype="float32", always_2d=True)
    audio = audio[:, 0]  # only use the first channel

    # audio is a 1-D float32 numpy array normalized to the range [-1, 1]
    # sample_rate does not need to be 16000 Hz

    start = time.time()
    stream = recognizer.create_stream()
    stream.accept_waveform(sample_rate, audio)
    recognizer.decode_stream(stream)
    end = time.time()

    print(wave_filename)
    print(stream.result)

    elapsed_seconds = end - start
    audio_duration = len(audio) / sample_rate
    real_time_factor = elapsed_seconds / audio_duration

    print(f"Elapsed seconds: {elapsed_seconds:.3f}")
    print(f"Audio duration in seconds: {audio_duration:.3f}")
    print(f"RTF: {elapsed_seconds:.3f}/{audio_duration:.3f} = {real_time_factor:.3f}")


if __name__ == "__main__":
    main()
