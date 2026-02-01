#!/usr/bin/env python3
"""
YouTube MP3 Downloader - Main Entry Point

A Python application for downloading audio from YouTube in MP3 format.
Supports bitrates: 128, 192, 320 kbps.
Optimized for use in Russia with proxy support.
"""

import sys


def main():
    """Main entry point."""
    from src.__main__ import main as run_main
    return run_main()


if __name__ == '__main__':
    main()
