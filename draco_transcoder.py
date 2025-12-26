#!/usr/bin/env python3
"""
Python wrapper for Draco glTF transcoder using ctypes.

This module provides a simple interface to compress glTF files using Draco compression.
"""

import ctypes
import os
import platform
from ctypes import Structure, c_char_p, c_int


class DracoOptions(Structure):
    """C-compatible struct for Draco compression options."""

    _fields_ = [
        ("quantization_position", c_int),
        ("quantization_tex_coord", c_int),
        ("quantization_normal", c_int),
        ("quantization_color", c_int),
        ("quantization_tangent", c_int),
        ("quantization_weight", c_int),
        ("quantization_generic", c_int),
        ("compression_level", c_int),
    ]


def _load_library():
    """Load the Draco transcoder shared library."""
    system = platform.system().lower()
    lib_name = "draco_transcoder_shared"

    if system == "windows":
        lib_path = f"{lib_name}.dll"
    elif system == "darwin":
        lib_path = f"lib{lib_name}.dylib"
    else:  # Linux and others
        lib_path = f"lib{lib_name}.so"

    # Try to load from current directory first
    if os.path.exists(lib_path):
        return ctypes.CDLL(lib_path)

    # Try to load from build directory (common locations)
    build_dirs = [
        "build",
        "cmake-build-release",
        "cmake-build-debug",
        "../draco_build",
        "../build",
    ]

    for build_dir in build_dirs:
        full_path = os.path.join(build_dir, lib_path)
        if os.path.exists(full_path):
            return ctypes.CDLL(full_path)

    raise RuntimeError(f"Could not find Draco transcoder library: {lib_path}")


# Load the library
_lib = _load_library()

# Configure function signature
_lib.draco_transcode_gltf.argtypes = [c_char_p, c_char_p, ctypes.POINTER(DracoOptions)]
_lib.draco_transcode_gltf.restype = c_int


def compress_gltf(
    input_path, output_path, qp=11, qt=10, qn=8, qc=8, qtg=8, qw=8, qg=8, cl=7
):
    """
    Compress a glTF file using Draco compression.

    Args:
        input_path (str): Path to input glTF file
        output_path (str): Path to output Draco-compressed glTF file
        qp (int): Quantization bits for position attribute (default: 11)
        qt (int): Quantization bits for texture coordinate attribute (default: 10)
        qn (int): Quantization bits for normal vector attribute (default: 8)
        qc (int): Quantization bits for color attribute (default: 8)
        qtg (int): Quantization bits for tangent attribute (default: 8)
        qw (int): Quantization bits for weight attribute (default: 8)
        qg (int): Quantization bits for generic attribute (default: 8)
        cl (int): Compression level [0-10] (default: 7)

    Returns:
        bool: True if compression succeeded, False otherwise

    Raises:
        RuntimeError: If input/output paths are invalid or compression fails
    """
    if not os.path.exists(input_path):
        raise RuntimeError(f"Input file does not exist: {input_path}")

    # Create options struct
    options = DracoOptions()
    options.quantization_position = qp
    options.quantization_tex_coord = qt
    options.quantization_normal = qn
    options.quantization_color = qc
    options.quantization_tangent = qtg
    options.quantization_weight = qw
    options.quantization_generic = qg
    options.compression_level = cl

    # Convert paths to bytes for C
    input_bytes = input_path.encode("utf-8")
    output_bytes = output_path.encode("utf-8")

    # Call the C function
    result = _lib.draco_transcode_gltf(input_bytes, output_bytes, ctypes.byref(options))

    if result == 0:
        return True
    else:
        raise RuntimeError(f"Draco transcoding failed with error code: {result}")


if __name__ == "__main__":
    # Simple test/example
    import sys

    if len(sys.argv) != 3:
        print("Usage: python draco_transcoder.py <input.gltf> <output.gltf>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        compress_gltf(input_file, output_file)
        print(f"Successfully compressed {input_file} to {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
