"""
LakeTiticaca
============

The Kernel-level AI of RealityStateOS.

LakeTiticaca does not sit above the Kernel the way Intelligence (009) sits
above the rest of the stack — it sits AT Kernel level (002_KERNEL), meaning
it has the same trust/privilege as the scheduler and security kernel
themselves. Its job is to bring reasoning and knowledge to bear on the
Kernel's own decisions: what runs next, what's allowed to touch what, and
how the system's understanding of itself evolves over time.

Core cognition loop: Observe -> Interpret -> Align -> Reason -> Evolve.
Kernel services it wraps: Scheduler, SecurityKernel, EventBus, Storage.

This package is intended to serve as the primary runtime library for the
Rounsaville-AI platform, embedded here as RealityStateOS's Kernel AI.

Author:
    Joseph Michael Rounsaville

Copyright:
    (c) Joseph Michael Rounsaville. All rights reserved.

License:
    Proprietary. See RealityStateOS/LICENSE.md and OWNERSHIP.md.
"""

from .main import LakeTiticaca

__title__ = "LakeTiticaca"
__package_name__ = "laketiticaca"
__version__ = "0.1.0"
__author__ = "Joseph Michael Rounsaville"
__license__ = "Proprietary"

__all__ = [
    "LakeTiticaca",
]
