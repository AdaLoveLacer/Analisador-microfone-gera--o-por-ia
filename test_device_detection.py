#!/usr/bin/env python
"""Test device detection for Whisper and embeddings."""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("\n" + "="*60)
print("TESTING DEVICE DETECTION")
print("="*60 + "\n")

# Test PyTorch/CUDA
print("[1] Testing PyTorch CUDA Detection...")
try:
    import torch
    print(f"    PyTorch version: {torch.__version__}")
    print(f"    CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"    CUDA device: {torch.cuda.get_device_name(0)}")
        print(f"    CUDA device count: {torch.cuda.device_count()}")
    else:
        print("    ⚠️  CUDA not available - using CPU")
except Exception as e:
    print(f"    ❌ Error: {e}")

print()

# Test Transcriber device detection
print("[2] Testing Transcriber Device Detection...")
try:
    from audio.transcriber import Transcriber
    print("    Creating Transcriber instance...")
    transcriber = Transcriber(model_name="tiny")  # Use tiny for speed
    print(f"    ✓ Transcriber device: {transcriber.device}")
except Exception as e:
    print(f"    ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test ContextAnalyzer device detection
print("[3] Testing ContextAnalyzer Device Detection...")
try:
    from ai.context_analyzer import ContextAnalyzer
    print("    Creating ContextAnalyzer instance...")
    analyzer = ContextAnalyzer()
    print(f"    ✓ ContextAnalyzer device: {analyzer.device}")
except Exception as e:
    print(f"    ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("DEVICE DETECTION TEST COMPLETE")
print("="*60 + "\n")
